# ════════════════════════════════════════════════════════════════════════════
# BUILD KB VIA API (WITH CALL LOGGING)
# ════════════════════════════════════════════════════════════════════════════

t0 = tic("Build KB via API")

import re
import time
import json
import csv
from tqdm.auto import tqdm
from datetime import datetime

def generate_queries(item: dict):
    """
    Generate clean search queries.
    Returns: List of 3-4 clean search strings
    """
    queries = []
    
    # Extract metadata
    country_code = item.get('country', '')
    intent = item.get('intent', 'others')
    question = item.get('question', '')
    
    country_name = COUNTRY_NAMES.get(country_code, country_code)
    
    if not question or not country_name:
        return [country_name] if country_name else []
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1: Clean the question
    # ═══════════════════════════════════════════════════════════════════════
    question_clean = re.sub(r'[^\w\s]', ' ', question.lower())
    
    filler_words = {
        'what', 'which', 'who', 'where', 'when', 'how', 'why',
        'is', 'are', 'was', 'were', 'been', 'being',
        'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'with',
        'has', 'have', 'had', 'does', 'do', 'did',
        'this', 'that', 'these', 'those'
    }
    
    words = question_clean.split()
    meaningful_words = [w for w in words if w not in filler_words and len(w) > 2]
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 2: Generate queries
    # ═══════════════════════════════════════════════════════════════════════
    
    # Query 1: First 3-5 meaningful words + country
    if len(meaningful_words) >= 1:
        query = ' '.join(meaningful_words[:5])
        queries.append(f"{query} {country_name}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3: Pattern matching
    # ═══════════════════════════════════════════════════════════════════════
    patterns = {
        'national': r'\b(national \w+)',
        'official': r'\b(official \w+)',
        'traditional': r'\b(traditional \w+)',
        'famous': r'\b(famous \w+)',
        'capital': r'\b(capital)',
        'currency': r'\b(currency)',
        'language': r'\b(language)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, question_clean)
        if match:
            queries.append(f"{match.group(1)} {country_name}")
            break
            
    # Always include country name as fallback for WikiVoyage
    queries.append(country_name)
    
    # Deduplicate and Clean
    seen = set()
    unique = []
    
    for q in queries:
        q = ' '.join(q.split())  # Normalize spaces
        q_norm = q.lower().strip()
        
        # Remove "Singapore Singapore" type errors
        if country_name:
            double_country = f"{country_name} {country_name}"
            if double_country.lower() in q_norm:
                q = q.replace(double_country, country_name)
                q_norm = q.lower().strip()
                
        if q_norm not in seen and len(q) > 2:
            seen.add(q_norm)
            unique.append(q)
            
    return unique[:4]

# ═══════════════════════════════════════════════════════════
# KB DEDUPLICATION SYSTEM
# ═══════════════════════════════════════════════════════════

def get_chunk_signature(country: str, query: str, source: str) -> str:
    """
    Create unique signature for a chunk fetch.
    
    Args:
        country: Country code (e.g., 'SG')
        query: Search query
        source: Source type ('wikipediaapi', 'wikidata', etc.)
    
    Returns:
        Unique hash for this fetch
    """
    key = f"{country}|{query}|{source}".lower()
    return hashlib.md5(key.encode()).hexdigest()


def check_chunks_exist(kb_chunks: list, country: str, query: str, source: str) -> bool:
    """
    Check if chunks for this query already exist in KB.
    
    Returns:
        True if chunks exist (skip API call)
        False if no chunks (make API call)
    """
    # Create signature for this fetch
    signature = get_chunk_signature(country, query, source)
    
    # Check if any chunk matches this signature
    for chunk in kb_chunks:
        chunk_country = chunk.get('country', '')
        chunk_query = chunk.get('query', '')
        chunk_source = chunk.get('source', '')
        
        chunk_sig = get_chunk_signature(chunk_country, chunk_query, chunk_source)
        
        if chunk_sig == signature:
            return True  # Found existing chunks
    
    return False  # No existing chunks


def get_existing_chunk_count(kb_chunks: list, country: str, query: str, source: str) -> int:
    """Count how many chunks exist for this query."""
    signature = get_chunk_signature(country, query, source)
    
    count = 0
    for chunk in kb_chunks:
        chunk_sig = get_chunk_signature(
            chunk.get('country', ''),
            chunk.get('query', ''),
            chunk.get('source', '')
        )
        if chunk_sig == signature:
            count += 1
    
    return count

print("✅ KB Deduplication system loaded")

def build_kb_via_api(entitydata, max_questions=None, log_calls=True, use_dedup=True):
    """
    Build KB with deduplication - skip if chunks already exist.
    
    Args:
        entitydata: List of question dicts
        max_questions: Limit number of questions (None = all)
        log_calls: Whether to log API calls
        use_dedup: Whether to skip existing chunks (True = skip, False = fetch all)
    """
    
    kb_chunks = []
    calllog = []  # ✅ Initialize always
    
    data_to_process = entitydata[:max_questions] if max_questions else entitydata
    
    print(f"📥 Processing {len(data_to_process)} questions...")
    if use_dedup:
        print(f"✅ Deduplication ENABLED - will skip existing chunks")
    else:
        print(f"⚠️  Deduplication DISABLED - will fetch all")
    
    # Initialize APIs
    wiki = WikipediaAPI()
    voyage = WikiVoyageAPI()
    wikidata = WikidataAPI()
    
    # Stats tracking
    stats = {
        'api_calls': 0,
        'cache_hits': 0,
        'skipped_dedups': 0,
        'new_chunks': 0
    }
    
    try:
        for idx, item in enumerate(tqdm(data_to_process, desc="Building KB")):
            
            # Generate queries
            queries = generate_queries(item)
            
            intent = item.get('intent', 'others')
            country = COUNTRYNAMES.get(item.get('country', ''), item.get('country', ''))
            question = item.get('question', '')
            
            # 1. Determine Sources
            intent_config = INTENTROUTING.get(intent, INTENTROUTING.get('others', {}))
            base_sources = intent_config.get('sources', ['wiki-en'])
            
            # Force add Wikidata and WikiVoyage if not present
            sources = list(set(base_sources + ['wikivoyage-en', 'wikidata']))
            
            # 2. Iterate Queries
            for query in queries:
                
                # --- Wikipedia ---
                if 'wiki-en' in sources:
                    
                    # ✅ Check if chunks exist
                    if use_dedup and check_chunks_exist(kb_chunks, country, query, 'wikipediaapi'):
                        existing_count = get_existing_chunk_count(kb_chunks, country, query, 'wikipediaapi')
                        stats['skipped_dedups'] += 1
                        
                        if log_calls:
                            calllog.append({
                                'item_index': idx,
                                'question': question,
                                'country': country,
                                'intent': intent,
                                'source': 'wikipediaapi',
                                'query': query,
                                'results_count': existing_count,
                                'status': 'DEDUP_SKIP',
                                'titles_found': []
                            })
                        continue  # Skip API call
                    
                    # Make API call (chunks don't exist)
                    res = wiki.search_and_extract(query, max_results=10)
                    
                    # Add metadata to chunks
                    for r in res:
                        r['country'] = country
                        r['intent'] = intent
                        r['query'] = query
                    
                    kb_chunks.extend(res)
                    stats['api_calls'] += 1
                    stats['new_chunks'] += len(res)
                    
                    # Log the call
                    if log_calls:
                        calllog.append({
                            'item_index': idx,
                            'question': question,
                            'country': country,
                            'intent': intent,
                            'source': 'wikipediaapi',
                            'query': query,
                            'results_count': len(res),
                            'status': 'API_CALL',
                            'titles_found': [r['title'] for r in res]
                        })
                
                # --- WikiVoyage (Targeted) ---
                if 'wikivoyage-en' in sources:
                    voyage_query = country if len(query.split()) < 3 else query
                    
                    # ✅ Check if chunks exist
                    if use_dedup and check_chunks_exist(kb_chunks, country, voyage_query, 'wikivoyageapi'):
                        existing_count = get_existing_chunk_count(kb_chunks, country, voyage_query, 'wikivoyageapi')
                        stats['skipped_dedups'] += 1
                        
                        if log_calls:
                            calllog.append({
                                'item_index': idx,
                                'question': question,
                                'country': country,
                                'intent': intent,
                                'source': 'wikivoyageapi',
                                'query': voyage_query,
                                'results_count': existing_count,
                                'status': 'DEDUP_SKIP',
                                'titles_found': []
                            })
                        continue  # Skip API call
                    
                    # Make API call
                    res = voyage.search_and_extract(voyage_query, max_results=1)
                    
                    # Add metadata
                    for r in res:
                        r['country'] = country
                        r['intent'] = intent
                        r['query'] = voyage_query
                    
                    kb_chunks.extend(res)
                    stats['api_calls'] += 1
                    stats['new_chunks'] += len(res)
                    
                    # Log the call
                    if log_calls:
                        calllog.append({
                            'item_index': idx,
                            'question': question,
                            'country': country,
                            'intent': intent,
                            'source': 'wikivoyageapi',
                            'query': voyage_query,
                            'results_count': len(res),
                            'status': 'API_CALL',
                            'titles_found': [r['title'] for r in res]
                        })
                
                # --- Wikidata (Targeted) ---
                if 'wikidata' in sources:
                    wd_query = query.replace(country, '').strip()
                    if not wd_query:
                        wd_query = country
                    
                    # ✅ Check if chunks exist
                    if use_dedup and check_chunks_exist(kb_chunks, country, wd_query, 'wikidata'):
                        existing_count = get_existing_chunk_count(kb_chunks, country, wd_query, 'wikidata')
                        stats['skipped_dedups'] += 1
                        
                        if log_calls:
                            calllog.append({
                                'item_index': idx,
                                'question': question,
                                'country': country,
                                'intent': intent,
                                'source': 'wikidata',
                                'query': wd_query,
                                'results_count': existing_count,
                                'status': 'DEDUP_SKIP',
                                'titles_found': []
                            })
                        continue  # Skip API call
                    
                    # Make API call
                    res = wikidata.search_and_extract(wd_query, country=country, max_results=1)
                    
                    # Add metadata
                    for r in res:
                        r['country'] = country
                        r['intent'] = intent
                        r['query'] = wd_query
                    
                    kb_chunks.extend(res)
                    stats['api_calls'] += 1
                    stats['new_chunks'] += len(res)
                    
                    # Log the call
                    if log_calls:
                        calllog.append({
                            'item_index': idx,
                            'question': question,
                            'country': country,
                            'intent': intent,
                            'source': 'wikidata',
                            'query': wd_query,
                            'results_count': len(res),
                            'status': 'API_CALL',
                            'titles_found': [r['title'] for r in res]
                        })
                
                # Rate limit between queries
                time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user. Saving progress...")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
    finally:
        wiki.close()
        voyage.close()
        wikidata.close()
    
    # 3. Deduplicate final KB (remove exact duplicates)
    unique_chunks = []
    seen_hashes = set()
    
    for chunk in kb_chunks:
        h = hash(f"{chunk['source']}|{chunk['title']}")
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique_chunks.append(chunk)
    
    kb_chunks = unique_chunks
    
    # Print summary
    print(f"\n✅ KB built: {len(kb_chunks)} chunks")
    print(f"   Wikipedia: {sum(1 for c in kb_chunks if c['source'] == 'wikipediaapi')}")
    print(f"   WikiVoyage: {sum(1 for c in kb_chunks if c['source'] == 'wikivoyageapi')}")
    print(f"   Wikidata: {sum(1 for c in kb_chunks if c['source'] == 'wikidata')}")
    
    # Print deduplication stats
    print(f"\n📊 Deduplication Stats:")
    print(f"   API calls made: {stats['api_calls']}")
    print(f"   Skipped (already exist): {stats['skipped_dedups']}")
    print(f"   New chunks added: {stats['new_chunks']}")
    print(f"   Efficiency: {stats['skipped_dedups']/(stats['api_calls']+stats['skipped_dedups'])*100:.1f}% calls avoided")
    
    # 4. Save Call Logs
    if log_calls and calllog:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_path = f"api_call_log_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(calllog, f, indent=2, ensure_ascii=False)
        print(f"\n📝 Call log saved: {json_path}")
        
        # Save as CSV
        csv_path = f"api_call_log_{timestamp}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'item_index', 'question', 'country', 'intent', 
                'source', 'query', 'results_count', 'status', 'titles_found'
            ])
            writer.writeheader()
            for row in calllog:
                row_copy = row.copy()
                row_copy['titles_found'] = ', '.join(row_copy['titles_found'])
                writer.writerow(row_copy)
        print(f"📝 Call log saved: {csv_path}")
        
        # Print call statistics
        print(f"\n📊 Call Statistics:")
        print(f"   Total entries: {len(calllog)}")
        print(f"   API calls: {sum(1 for c in calllog if c['status'] == 'API_CALL')}")
        print(f"   Dedup skips: {sum(1 for c in calllog if c['status'] == 'DEDUP_SKIP')}")
        print(f"   Successful calls: {sum(1 for c in calllog if c['status'] == 'API_CALL' and c['results_count'] > 0)}")
        print(f"   Zero-result calls: {sum(1 for c in calllog if c['status'] == 'API_CALL' and c['results_count'] == 0)}")
        
        # By source
        by_source = {}
        for call in calllog:
            src = call['source']
            status = call['status']
            
            if src not in by_source:
                by_source[src] = {'total': 0, 'api_calls': 0, 'dedups': 0, 'successful': 0}
            
            by_source[src]['total'] += 1
            
            if status == 'API_CALL':
                by_source[src]['api_calls'] += 1
                if call['results_count'] > 0:
                    by_source[src]['successful'] += 1
            elif status == 'DEDUP_SKIP':
                by_source[src]['dedups'] += 1
        
        print(f"\n   By Source:")
        for src, stats_src in by_source.items():
            api = stats_src['api_calls']
            dedups = stats_src['dedups']
            succ = stats_src['successful']
            total = stats_src['total']
            
            print(f"   {src}: {api} API calls, {dedups} skipped, {succ} successful")
    
    return kb_chunks, calllog

print("✅ build_kb_via_api loaded with deduplication")
  

# Execute
kb_chunks, call_log = build_kb_via_api(entity_data, max_questions=None, log_calls=True)

# Show sample
print("\n📋 Sample KB Chunks:")
for chunk in kb_chunks[:3]:
    print(f"\n  Title: {chunk['title']}")
    print(f"  Source: {chunk['source']}")
    print(f"  Text: {chunk['text'][:100]}...")

toc("Build KB via API", t0)
