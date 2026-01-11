"""
Script to add tic/toc timing to all cells in a Jupyter notebook
"""
import json
import sys

def add_timing_to_notebook(notebook_path):
    """Add tic/toc timing to all code cells in notebook"""
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    cells = nb['cells']
    cell_number = 1
    cells_modified = 0
    
    for i, cell in enumerate(cells):
        if cell['cell_type'] != 'code':
            continue
            
        source = ''.join(cell['source'])
        
        # Skip if already has timing
        if 't0 = tic(' in source or 'tic("Cell' in source:
            # But make sure it has toc at the end
            if 'toc(' not in source:
                lines = cell['source']
                if lines and lines[-1].strip() != '':
                    lines.append('\n')
                lines.append(f'\ntoc("Cell {cell_number}", t0)\n')
                cells_modified += 1
            cell_number += 1
            continue
        
        # Skip timing utilities cell itself
        if 'def tic(name):' in source or 'TIMING UTILITIES' in source:
            continue
        
        # Get cell description from comments
        first_lines = source.strip().split('\n')[:3]
        cell_desc = f"Cell {cell_number}"
        for line in first_lines:
            if '# =' in line or '# ─' in line:
                # Extract description from header
                clean = line.strip('#= ─').strip()
                if clean and len(clean) < 60:
                    cell_desc = clean
                    break
        
        # Add timing
        lines = cell['source']
        
        # Insert tic at start
        lines.insert(0, f't0 = tic("Cell {cell_number}: {cell_desc}")\n\n')
        
        # Add toc at end
        if lines[-1].strip() != '':
            lines.append('\n')
        lines.append(f'\ntoc("Cell {cell_number}: {cell_desc}", t0)\n')
        
        cells_modified += 1
        cell_number += 1
    
    # Save modified notebook
    output_path = notebook_path
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    
    print(f"✅ Modified {cells_modified} cells")
    print(f"   Output: {output_path}")

if __name__ == "__main__":
    notebook_path = r"c:\Users\LawLight\OneDrive\Desktop\semevals\semeval-task-7 (10).ipynb"
    add_timing_to_notebook(notebook_path)
