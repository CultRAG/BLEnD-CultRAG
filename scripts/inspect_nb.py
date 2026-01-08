import json
import io

path = r"d:\GitHub\my_repo\BLEnD-CultureRAG\notebooks\BLEnD_CultureRAG.ipynb"
out_path = r"d:\GitHub\my_repo\BLEnD-CultureRAG\scripts\nb_audit.txt"

with open(path, "r", encoding="utf-8") as f:
    nb = json.load(f)

with open(out_path, "w", encoding="utf-8") as out:
    out.write(f"Total cells: {len(nb['cells'])}\n")
    for i, cell in enumerate(nb['cells']):
        ctype = cell['cell_type']
        source = "".join(cell.get('source', [])).strip()
        summary = source[:200].replace('\n', ' ')
        out.write(f"CELL {i:2} [{ctype}] {summary}...\n")
        
        # Check for model loading specific keywords
        if "AutoModelForCausalLM" in source:
            out.write(f"  --> FOUND MODEL LOADING KEYWORD IN CELL {i}\n")
        if "SentenceTransformer" in source:
            out.write(f"  --> FOUND EMBEDDING MODEL KEYWORD IN CELL {i}\n")
        if "pd.read_csv" in source:
            out.write(f"  --> FOUND DATA LOADING KEYWORD IN CELL {i}\n")
