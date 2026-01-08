# BLEnD-CultureRAG

BLEnD-CultureRAG is a retrieval-augmented cultural reasoning system. This system evaluates the cultural awareness of language models by selecting culturally appropriate answers to English multiple-choice questions.

## 📂 Project Structure

```bash
BLEnD-CultureRAG/
├── data/                   # Input datasets, ground truth, and knowledge base files
├── docs/                   # Detailed documentation and implementation guides
├── notebooks/              # Jupyter notebooks for running the pipeline (Colab/Kaggle compatible)
├── output/                 # Generated predictions and evaluation results
├── scripts/                # Utility scripts for evaluation and data conversion
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## 🚀 Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ridash2005/BLEnD-CultureRAG.git
    cd BLEnD-CultureRAG
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```

## 🏃 Usage

### 1. Run the Pipeline
The core logic resides in `notebooks/BLEnD_CultureRAG.ipynb`. You can run this locally or upload it to Google Colab / Kaggle.
- Ensure `data/` files are accessible to the notebook (if running locally).
- If running on Colab, follow the instructions in the notebook to mount data.

### 2. Evaluate Results
Once predictions are generated (saved to `output/`), run the evaluation script to compare against ground truth.

```bash
python scripts/evaluate_results.py
```

This script will:
- Read predictions from `output/`
- Compare them against `data/answers.tsv`
- Print accuracy metrics to the console
- Save correct answers to `output/correct_answers_*.tsv`

### 3. Convert Cache Files (Optional)
To convert pickle cache files to readable JSON:
```bash
python scripts/convert_pkl_to_json.py
```

## 📄 Documentation
For detailed implementation details, see [docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md).

## 📊 Data Files
- `questions.tsv`: The input questions.
- `answers.tsv`: Ground truth answers.
- `kb_chunks.pkl`: Knowledge base chunks (pickle format).
- `wiki_cache.pkl`: Cached Wikipedia pages.

> **Note**: This repository uses a `data/` and `output/` structure. The notebook and scripts have been configured to output results to the `output/` directory and read data from `data/`. Please allow file overwrites if re-running experiments to avoid duplicate file creation (e.g. `file (1).tsv`).

## 📜 License
[MIT License](LICENSE)
