
import json

with open(r'd:\GitHub\my_repo\BLEnD-CultureRAG\sources\sites_intent_mapping_V6.json', 'r', encoding='utf-8') as f:
    lines = f.readlines()

countries = [
    "France", "Spain", "Bulgaria", "Saudi Arabia", "Egypt", "China", 
    "Sri Lanka", "Greece", "South Korea", "Iran", "Mexico", "Ecuador"
]

for i, line in enumerate(lines):
    for country in countries:
        if f'"country_name": "{country}"' in line:
            print(f"{country}: {i+1}")
