# Ultimate OCR & LLM Parser (v3.3)

This project automatically extracts and structures text from PDF files or images (PNG, JPG, etc.) using Tesseract OCR and intelligent post-processing with a local LLM (Ollama). It detects the document type (Resume/CV, Invoice, Form, Generic) and generates an adapted structured JSON output.

## Prerequisites

1.  **Tesseract OCR**
    *   Windows: [Download here](https://github.com/UB-Mannheim/tesseract/wiki)
    *   Linux: `sudo apt-get install tesseract-ocr`
    *   macOS: `brew install tesseract`
    *   *Note: Ensure the installation path is correct or update it in the script if necessary.*

2.  **Ollama**
    *   [Install Ollama](https://ollama.ai/download)
    *   Start Ollama and pull a model: `ollama pull llama3.2`

3.  **Python 3.11+**
    *   Create a virtual environment: `python -m venv venv`
    *   Activate it:
        *   Windows: `venv\Scripts\activate`
        *   Linux/macOS: `source venv/bin/activate`
    *   Install dependencies: `pip install -r requirements.txt`

## Usage

### 🎨 GUI Interface (Recommended)

Launch the modern graphical interface:
```bash
python ocr_gui.py
```
Or simply run `start_gui.bat` on Windows.

**Features:**
*   ✨ Drag & Drop support
*   🎯 Intuitive document type and model selection
*   📊 Real-time processing logs
*   💾 Easy JSON export and copy

### 💻 Command Line (CLI)

**Basic Extraction:**
```bash
python ocr_extractor.py input/my_document.pdf
```

**Advanced Options:**
*   **Force Document Type:**
    ```bash
    python ocr_extractor.py input/resume.pdf --type cv
    python ocr_extractor.py input/invoice.pdf --type facture
    ```
*   **Specify LLM Model:**
    ```bash
    python ocr_extractor.py input/doc.pdf --model llama3.2
    ```
*   **Custom Output Directory:**
    ```bash
    python ocr_extractor.py input/img.png --output my_results
    ```

## Project Structure

```
projet_ocr_fst/
│
├── ocr_extractor.py      # Core Logic (OCR + LLM)
├── ocr_gui.py            # GUI Application (CustomTkinter)
├── requirements.txt      # Python Dependencies
├── README.md             # Documentation
├── tools/                # Generation Scripts (Schemas/Images)
├── input/                # Source Documents
└── output/               # Structured Results (JSON)
```

## Supported Formats
*   **PDF** (Multi-page support)
*   **Images**: PNG, JPG, JPEG, BMP, TIFF

## Key Features
*   **Hybrid Extraction**: Native PDF text extraction with automatic fallback to OCR (Tesseract) for scans.
*   **Smart Classification**: Keywords-based heuristic to detect document type.
*   **LLM Parsing**: Uses local AI (Llama 3.2 via Ollama) to clean, correct, and structure raw text.
*   **Structured JSON**: guaranteed output schema for Resumes, Invoices, etc.
*   **100% Local**: No data is sent to the cloud.

## JSON Examples

###  Resume (CV)
```json
{
   "candidat": {"nom": "John Doe", "email": "john@example.com", "telephone": "+123456789"},
   "competences": {"langages": ["Python", "C++"], "outils": ["Git", "Docker"]},
   "experience": [{"poste": "Senior Dev", "entreprise": "TechCorp", "dates": "2020-2023"}]
}
```

### Invoice (Facture)
```json
{
   "document": {"numero": "INV-2023-001", "date_emission": "2023-10-25"},
   "totaux": {"total_ht": 1000.0, "total_tva": 200.0, "total_ttc": 1200.0}
}
```

---
*Project developed for FST Settat - Ultimate OCR & LLM Parser v3.3*
