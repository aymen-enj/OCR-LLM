
# Ultimate OCR & LLM Parser (v3.3)

Ce projet permet d'extraire et de structurer automatiquement le texte de fichiers PDF ou images (PNG, JPG, etc.) grâce à l'OCR (Tesseract) et à un post-traitement intelligent avec un LLM local (Ollama). Il détecte le type de document (CV, facture, formulaire, générique) et génère un JSON structuré adapté.


## Prérequis

1. **Tesseract OCR**
   - Windows : [Installer ici](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux : `sudo apt-get install tesseract-ocr tesseract-ocr-fra`
   - macOS : `brew install tesseract tesseract-lang`
   - Vérifiez le chemin d'installation ou modifiez-le dans le script si besoin.

2. **Ollama**
   - [Installer Ollama](https://ollama.ai/download)
   - Démarrer Ollama et télécharger un modèle : `ollama pull llama3.2`

3. **Python 3.x**
   - Créez un environnement virtuel : `python -m venv venv`
   - Activez-le :
     - Windows : `venv\Scripts\activate`
     - Linux/macOS : `source venv/bin/activate`
   - Installez les dépendances : `pip install -r requirements.txt`


## Utilisation

### 🎨 Interface Graphique (Recommandé)

Lancez l'interface graphique moderne :
```bash
python ocr_gui.py
```

**Fonctionnalités :**
- ✨ Glisser-déposer de fichiers
- 🎯 Sélection intuitive du type et du modèle
- 📊 Affichage en temps réel des résultats
- 💾 Export et copie faciles

Consultez [GUI_GUIDE.md](file:///c:/Users/aymen/OneDrive/Desktop/projet_ocr_fst/GUI_GUIDE.md) pour plus de détails.

### 💻 Ligne de Commande

## Utilisation


### Extraction et structuration automatique
```bash
python ocr_extractor.py input/mon_document.pdf
```

### Options principales
- Forcer le type de document :
   ```bash
   python ocr_extractor.py input/cv.pdf --type cv
   python ocr_extractor.py input/facture.pdf --type facture
   python ocr_extractor.py input/formulaire.pdf --type formulaire
   ```
- Spécifier le modèle Ollama :
   ```bash
   python ocr_extractor.py input/document.pdf --model llama3.2
   python ocr_extractor.py input/document.pdf --model mistral
   ```
- Changer le dossier de sortie :
   ```bash
   python ocr_extractor.py input/image.png --output output
   ```


## Structure du projet

```
projet_ocr_fst/
│
├── ocr_extractor.py      # Script principal
├── requirements.txt      # Dépendances Python
├── README.md             # Documentation
├── PRESENTATION_PROJET.md# Présentation détaillée
├── input/                # Fichiers d'entrée
└── output/               # Fichiers de sortie (JSON structuré)
   ├── nom_fichier_data.json        # Résultat final structuré
   └── ...
```


## Formats supportés
- PDF (multi-pages)
- Images : PNG, JPG, JPEG


## Fonctionnalités principales

- Extraction OCR multi-format (PDF, images)
- Détection automatique du type de document (CV, facture, formulaire, générique)
- Structuration intelligente des données avec LLM (Ollama)
- Export JSON structuré selon le type détecté
- Correction et enrichissement des données (emails, téléphones, IBAN, etc.)

### Structure JSON générée

#### CV
```json
{
   "candidat": {"nom": "...", "email": "...", "telephone": "...", "liens": [...]},
   "profil_synthese": "...",
   "competences": {"langages": [...], "outils": [...], "soft_skills": [...]},
   "experience": [{"poste": "", "entreprise": "", "dates": "", "missions": [...]}],
   "education": [{"diplome": "", "ecole": "", "annee": ""}]
}
```

#### Facture
```json
{
   "document": {"type": "Facture", "numero": "", "date_emission": ""},
   "emetteur": {"nom": "", "adresse": "", "siret": "", "iban": ""},
   "client": {"nom": "", "adresse": ""},
   "articles": [{"description": "", "qte": 0, "prix_unitaire": 0, "total_ligne": 0}],
   "totaux": {"total_ht": 0.0, "total_tva": 0.0, "total_ttc": 0.0, "devise": "EUR/USD/MAD"}
}
```

#### Formulaire
```json
{
   "titre_formulaire": "",
   "champs_reemplis": [{"label": "...", "valeur": "..."}],
   "cases_cochees": ["..."],
   "blocs_texte_libre": [...],
   "statut_signature": "Signé / Non Signé"
}
```


## Notes importantes
- La détection du type de document est automatique par défaut (`--type auto`)
- Le script convertit chaque page PDF en image si besoin (OCR fallback)
- La qualité dépend du document source
- Ollama doit être lancé avant d'utiliser le script
- Les résultats sont sauvegardés en JSON dans le dossier `output/`

