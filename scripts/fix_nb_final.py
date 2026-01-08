#!/usr/bin/env python3
import json
import os

path = r"d:\GitHub\my_repo\BLEnD-CultureRAG\notebooks\BLEnD_CultureRAG.ipynb"

def fix_notebook_final():
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    # We need to insert the model loading cell.
    # Stage 11 is markdown at CELL 21. 
    # Let's insert the code cell after CELL 21.
    
    model_loading_code = [
        "# ============================================================================\n",
        "# LOAD LLM: Llama-3.1-8B-Instruct (4-bit Quantized)\n",
        "# ============================================================================\n",
        "from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig\n",
        "import torch\n",
        "\n",
        "# Configuration for 4-bit quantization\n",
        "bnb_config = BitsAndBytesConfig(\n",
        "    load_in_4bit=True,\n",
        "    bnb_4bit_quant_type=\"nf4\",\n",
        "    bnb_4bit_compute_dtype=torch.float16,\n",
        "    bnb_4bit_use_double_quant=True,\n",
        ")\n",
        "\n",
        "model_id = \"meta-llama/Llama-3.1-8B-Instruct\"\n",
        "\n",
        "print(f\"🤖 Loading model: {model_id}...\")\n",
        "\n",
        "tokenizer = AutoTokenizer.from_pretrained(model_id)\n",
        "model = AutoModelForCausalLM.from_pretrained(\n",
        "    model_id,\n",
        "    quantization_config=bnb_config,\n",
        "    device_map=\"auto\",\n",
        "    trust_remote_code=True\n",
        ")\n",
        "\n",
        "print(\"✅ Model loaded successfully!\")\n",
        "print(f\"   Device: {model.device}\")\n"
    ]
    
    model_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": model_loading_code
    }
    
    # Insert at index 22 (pushing everything down)
    nb['cells'].insert(22, model_cell)
    
    # Now fix path inconsistencies
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            
            # Fix 1: Index build cell (loads KB)
            if "with open('kb_chunks.pkl', 'rb')" in source:
                cell['source'] = [line.replace("'kb_chunks.pkl'", "'../data/kb_chunks.pkl'") for line in cell['source']]
                print("Fixed KB loading path in one cell.")
            
            # Fix 2: Predictions path (check if any use /kaggle/working/)
            if "/kaggle/working/" in source:
                cell['source'] = [line.replace("/kaggle/working/", "../output/") for line in cell['source']]
                print("Fixed Kaggle output path to local output path.")
    
    # Update the logic: Model loading MUST be before inference
    # Current inference is CELL 20 (now 21 after insertion)
    # Model loading inserted at 22.
    # WE MUST MOVE IT.
    
    # Let's find the inference cell more reliably
    inference_idx = -1
    for i, cell in enumerate(nb['cells']):
        if "run_experiment_safe(" in "".join(cell.get('source', [])):
            inference_idx = i
            break
    
    if inference_idx != -1:
        print(f"Found inference at cell {inference_idx}")
        # Insert model loading before inference
        # If model loading is at 22, and inference is at 21... wait.
        # Let's just pop the model loading cell and insert it before inference.
        model_cell_to_move = nb['cells'].pop(22)
        nb['cells'].insert(inference_idx, model_cell_to_move)
        print(f"Moved model loading to cell {inference_idx}")
        
        # Also need a markdown header for it
        header_cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 9.5 Load LLM (Quantized)\n", "\n", "Loading the model before the inference loop.\n"]
        }
        nb['cells'].insert(inference_idx, header_cell)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    
    print("Notebook flow and paths fixed.")

if __name__ == "__main__":
    fix_notebook_final()
