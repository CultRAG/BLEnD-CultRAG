
import json
import concurrent.futures
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import socket
import re
import ssl

INPUT_FILE = 'sources/sites_intent_mapping_V7.json'
OUTPUT_FILE = 'sources/sites_intent_mapping_V7.json'

print("Starting final validation script...", flush=True)

# Context to ignore SSL errors if necessary (sometimes scrapers ignore them, but better to be strict? 
# User said "web scrapper cannot access", usually scrapers verify SSL. 
# But let's allow unverified SSL if it returns content, to be slightly lenient on misconfigured certs if the site works.)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BAD_TITLES = [
    "domain for sale", "parked domain", "under construction", 
    "404", "not found", "access denied", "suspended", 
    "buy this domain", "hugedomains", "godaddy", "namecheap",
    "site not found"
]

def fix_url(url):
    if not url.startswith('http'):
        return 'https://' + url
    return url

def check_site(source_entry):
    url = source_entry.get('url')
    if not url:
        return None

    full_url = fix_url(url)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = Request(full_url, headers=headers)
        
        # Timeout 5 seconds
        with urlopen(req, timeout=5, context=ctx) as response:
            if response.status == 200:
                # Read first chunk to check for "parked" pages
                chunk = response.read(10000).decode('utf-8', errors='ignore').lower()
                
                # Check title
                title_match = re.search(r'<title>(.*?)</title>', chunk, re.DOTALL)
                if title_match:
                    title = title_match.group(1).strip()
                    for bad in BAD_TITLES:
                        if bad in title:
                            print(f"[-] Removed (Bad Title): {url} [{title}]", flush=True)
                            return None
                
                # print(f"[+] Kept: {url}", flush=True)
                return source_entry
            else:
                print(f"[-] Removed (Status {response.status}): {url}", flush=True)
                return None
            
    except Exception as e:
        print(f"[-] Removed (Error: {e}): {url}", flush=True)
        return None

def process_source_list(source_list):
    valid_sources = []
    # High concurrency for speed
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_source = {executor.submit(check_site, src): src for src in source_list}
        for future in concurrent.futures.as_completed(future_to_source):
            try:
                result = future.result()
                if result:
                    valid_sources.append(result)
            except Exception:
                pass
    return valid_sources

def main():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}", flush=True)
        return

    print("Processing Global Intent Sources...", flush=True)
    if "global_intent_sources" in data:
        for intent, sections in data["global_intent_sources"].items():
            for section in ["primary", "fallback"]:
                if section in sections:
                     original_len = len(sections[section])
                     sections[section] = process_source_list(sections[section])
                     if len(sections[section]) < original_len:
                         print(f"  {intent}/{section}: {original_len} -> {len(sections[section])}", flush=True)

    print("Processing Country Specific Sources...", flush=True)
    if "country_specific_sources" in data:
        countries = list(data["country_specific_sources"].keys())
        for country in countries:
            print(f"Scanning {country}...", flush=True)
            country_data = data["country_specific_sources"][country]
            
            # Pattern 1: priority_sources list
            if isinstance(country_data, dict) and "priority_sources" in country_data and isinstance(country_data["priority_sources"], list):
                for item in country_data["priority_sources"]:
                    if "sources" in item:
                        item["sources"] = process_source_list(item["sources"])
            
            # Pattern 2: Direct intent dictionary
            elif isinstance(country_data, dict):
                 for key, sections in country_data.items():
                    # Check if this key holds source lists (primary/fallback)
                    if isinstance(sections, dict) and ("primary" in sections or "fallback" in sections):
                       for section in ["primary", "fallback"]:
                           if section in sections:
                               sections[section] = process_source_list(sections[section])

    print("Saving cleaned JSON...", flush=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Done.", flush=True)

if __name__ == "__main__":
    main()
