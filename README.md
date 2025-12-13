# Ultimate OCR & LLM Parser (v3.3)

[![English](https://img.shields.io/badge/lang-English-blue)](#english-version) [![Français](https://img.shields.io/badge/lang-Français-red)](#version-française)

Please scroll down for the French version.
*Veuillez descendre pour la version française.*

---

<a name="english-version"></a>
## 🇬🇧 English Version

This project automatically extracts and structures text from PDF files or images (PNG, JPG, etc.) using Tesseract OCR and intelligent post-processing with a local LLM (Ollama). It detects the document type (Resume/CV, Invoice, Form, Generic) and generates an adapted structured JSON output.

### Prerequisites

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
    *   Activate it (Windows: `venv\Scripts\activate` | Unix: `source venv/bin/activate`)
    *   Install dependencies: `pip install -r requirements.txt`

### Usage

#### 🎨 GUI Interface (Recommended)
Launch the modern graphical interface:
```bash
python ocr_gui.py
```
Or simply run **`scripts/start_gui.bat`** on Windows.

**Features:**
*   ✨ Drag & Drop support
*   🎯 Intuitive document type and model selection
*   📊 Real-time processing logs
*   💾 Easy JSON export and copy

#### 💻 Command Line (CLI)
```bash
# Basic Extraction
python ocr_extractor.py input/my_document.pdf

# Force Document Type (cv, facture, formulaire)
python ocr_extractor.py input/resume.pdf --type cv

# Specify LLM Model
python ocr_extractor.py input/doc.pdf --model llama3.2
```

### Project Structure
```
projet_ocr_fst/
│
├── ocr_extractor.py      # Core Logic (OCR + LLM)
├── ocr_gui.py            # GUI Application (CustomTkinter)
├── requirements.txt      # Python Dependencies
├── README.md             # Documentation (EN/FR)
├── scripts/              # Utility scripts (start/build)
├── docs/                 # Documentation & Reports (LaTeX)
├── diagrams/             # Project visual diagrams
├── input/                # Source Documents
└── output/               # Structured Results (JSON)
```

### Key Features
*   **Hybrid Extraction**: Native PDF text extraction with automatic fallback to OCR (Tesseract) for scans.
*   **Smart Classification**: Keywords-based heuristic to detect document type.
*   **LLM Parsing**: Uses local AI (Llama 3.2 via Ollama) to clean, correct, and structure raw text.
*   **100% Local**: No data is sent to the cloud.

---

<a name="version-française"></a>
## 🇫🇷 Version Française

Ce projet permet d'extraire et de structurer automatiquement le texte de fichiers PDF ou images (PNG, JPG, etc.) grâce à l'OCR (Tesseract) et à un post-traitement intelligent avec un LLM local (Ollama). Il détecte le type de document (CV, facture, formulaire, générique) et génère un JSON structuré adapté.

### Prérequis

1.  **Tesseract OCR**
    *   Windows : [Télécharger ici](https://github.com/UB-Mannheim/tesseract/wiki)
    *   Linux : `sudo apt-get install tesseract-ocr`
    *   macOS : `brew install tesseract`
    *   *Note : Vérifiez que le chemin d'installation est correct dans le script.*

2.  **Ollama**
    *   [Installer Ollama](https://ollama.ai/download)
    *   Démarrer Ollama et télécharger le modèle : `ollama pull llama3.2`

3.  **Python 3.11+**
    *   Créez un environnement virtuel : `python -m venv venv`
    *   Activez-le (Windows: `venv\Scripts\activate` | Unix: `source venv/bin/activate`)
    *   Installez les dépendances : `pip install -r requirements.txt`

### Utilisation

#### 🎨 Interface Graphique (Recommandé)
Lancez l'interface graphique moderne :
```bash
python ocr_gui.py
```
Ou lancez simplement **`scripts/start_gui.bat`** sur Windows.

**Fonctionnalités :**
*   ✨ Support Glisser-Déposer (Drag & Drop)
*   🎯 Sélection intuitive du type et du modèle
*   📊 Logs de traitement en temps réel
*   💾 Export et copie facile du JSON

#### 💻 Ligne de Commande (CLI)
```bash
# Extraction basique
python ocr_extractor.py input/mon_document.pdf

# Forcer le type de document (cv, facture, formulaire)
python ocr_extractor.py input/mon_cv.pdf --type cv

# Spécifier le modèle LLM
python ocr_extractor.py input/doc.pdf --model llama3.2
```

### Structure du Projet
```
projet_ocr_fst/
│
├── ocr_extractor.py      # Cœur Logique (OCR + LLM)
├── ocr_gui.py            # Application GUI (CustomTkinter)
├── requirements.txt      # Dépendances Python
├── README.md             # Documentation (EN/FR)
├── scripts/              # Scripts utilitaires (lancement/build)
├── docs/                 # Rapports et Présentations (LaTeX)
├── diagrams/             # Diagrammes du projet
├── input/                # Documents source
└── output/               # Résultats structurés (JSON)
```

### Fonctionnalités Clés
*   **Extraction Hybride** : Extraction native du texte PDF avec bascule automatique vers OCR (Tesseract) pour les scans.
*   **Classification Intelligente** : Détection heuristique du type de document par mots-clés.
*   **Parsing LLM** : Utilisation d'une IA locale (Llama 3.2 via Ollama) pour nettoyer, corriger et structurer le texte brut.
*   **JSON Structuré** : Schéma de sortie garanti pour CVs, Factures, etc.
*   **100% Local** : Aucune donnée n'est envoyée dans le cloud.

---
*Project developed for FST Settat - Ultimate OCR & LLM Parser v3.3*
