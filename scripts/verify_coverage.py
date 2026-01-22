
import csv
import json
import requests
import concurrent.futures
from collections import defaultdict
import ssl
from urllib.parse import urlparse

QUESTIONS_FILE = 'data/questions.tsv'
JSON_FILE = 'sources/sites_intent_mapping_V7.json'

def get_required_countries():
    countries = set()
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            parts = row['id'].split('_')
            if len(parts) > 0:
                code = parts[0].split('-')[-1] # Handle en-GB -> GB, US -> US
                countries.add(code)
    return countries

def load_mapping():
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_coverage(required_countries, data):
    mapped_countries = set(data.get("country_specific_sources", {}).keys())
    missing = required_countries - mapped_countries
    
    empty_countries = []
    for country in mapped_countries:
        if country not in required_countries: continue # Skip extra countries
        
        c_data = data["country_specific_sources"][country]
        source_count = 0
        
        # Count sources
        if isinstance(c_data, dict):
             if "priority_sources" in c_data:
                 for item in c_data["priority_sources"]:
                     source_count += len(item.get("sources", []))
             else:
                 for key, val in c_data.items():
                     if isinstance(val, dict): # intent -> primary/fallback
                         source_count += len(val.get("primary", [])) + len(val.get("fallback", []))
        
        if source_count == 0:
            empty_countries.append(country)
            
    return missing, empty_countries

def main():
    print("Analyzing coverage...")
    required = get_required_countries()
    print(f"Required countries: {sorted(list(required))}")
    
    data = load_mapping()
    missing, empty = check_coverage(required, data)
    
    print(f"Missing Countries (No Key): {missing}")
    print(f"Empty Countries (Key exists, no sources): {empty}")
    
    if not missing and not empty:
        print("ALL COUNTRIES COVERED AND HAVE SOURCES.")
    else:
        print("ACTION REQUIRED: Need to refill missing/empty countries.")

if __name__ == "__main__":
    main()
