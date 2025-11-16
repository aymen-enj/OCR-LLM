# Projet OCR - Extraction de Texte avec Post-traitement LLM

Ce projet permet d'extraire le texte de fichiers PDF ou PNG en utilisant la technologie OCR (Reconnaissance Optique de Caractères) et d'améliorer la qualité du texte extrait grâce à un post-traitement avec un LLM (via Ollama).

## Prérequis

Avant d'utiliser ce projet, vous devez installer Tesseract OCR sur votre système :

### Windows
1. Téléchargez l'installateur depuis : https://github.com/UB-Mannheim/tesseract/wiki
2. Installez Tesseract (notez le chemin d'installation)
3. Ajoutez Tesseract à votre PATH système ou modifiez le chemin dans le script si nécessaire

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-fra  # Pour le français
```

### macOS
```bash
brew install tesseract
brew install tesseract-lang  # Pour les langues supplémentaires
```

## Installation

1. Clonez ou téléchargez ce projet

2. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
```

3. Activez l'environnement virtuel :
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

5. Assurez-vous qu'Ollama est installé et fonctionnel :
   - Vérifiez qu'Ollama est en cours d'exécution
   - Téléchargez un modèle si nécessaire : `ollama pull llama3.2`

## Utilisation

### Utilisation de base
```bash
python ocr_extractor.py document.pdf
```

### Spécifier un fichier de sortie
```bash
python ocr_extractor.py image.png -o resultat.txt
```

### Traiter un PDF avec post-traitement LLM (par défaut)
```bash
python ocr_extractor.py mon_document.pdf -o output/texte_cleaned.txt
```

### Utiliser un modèle Ollama spécifique
```bash
python ocr_extractor.py document.pdf --model llama3.2
# ou
python ocr_extractor.py document.pdf --model mistral
```

### Désactiver le post-traitement LLM (OCR uniquement)
```bash
python ocr_extractor.py document.pdf --no-llm
```

### Spécifier le type de document
```bash
# CV (par défaut pour les CV)
python ocr_extractor.py cv.pdf --type cv

# Facture
python ocr_extractor.py facture.pdf --type facture

# Formulaire
python ocr_extractor.py formulaire.pdf --type formulaire

# Mode général (détection automatique si non spécifié)
python ocr_extractor.py document.pdf --type general
```

## Structure du projet

```
projet_ocr_fst/
│
├── ocr_extractor.py      # Script principal d'extraction OCR
├── requirements.txt      # Dépendances Python
├── README.md            # Documentation
├── input/               # Dossier pour les fichiers d'entrée (à créer)
└── output/              # Dossier pour les fichiers de sortie (créé automatiquement)
    ├── nom_fichier_extracted.txt    # Texte brut OCR
    ├── nom_fichier_cleaned.txt      # Texte structuré et corrigé
    └── nom_fichier_cleaned.json     # JSON structuré (si LLM activé)
```

## Formats supportés

- **PDF** : Fichiers PDF (multi-pages)
- **Images** : PNG, JPG, JPEG, BMP, TIFF

## Fonctionnalités

### Post-traitement LLM avec Ollama

Le script utilise maintenant **Ollama** pour post-traiter le texte extrait par OCR. Cette fonctionnalité :

- ✅ **Corrige les erreurs d'OCR** : "Dipl6mé" → "Diplômé", "lnformation" → "Information"
- ✅ **Nettoie le texte** : Supprime les espaces multiples et lignes vides excessives
- ✅ **Structure le contenu** : Organise le texte de manière logique et lisible
- ✅ **Améliore la présentation** : Formate le texte pour une meilleure lisibilité
- ✅ **Génère un JSON structuré** : Extrait les informations du CV et les sauvegarde en format JSON

Le post-traitement LLM est **activé par défaut**. Si vous préférez utiliser uniquement l'OCR, utilisez l'option `--no-llm`.

### Export JSON

Quand le post-traitement LLM est activé, le script génère automatiquement un fichier JSON structuré selon le type de document :

#### Pour les CV :
- **A propos de moi** : Nom, titre, coordonnées, description
- **Langues** : Liste des langues avec niveaux
- **Education** : Formations avec dates, établissements, diplômes
- **Expériences professionnelles** : Postes avec dates, entreprises, missions, technologies
- **Compétences techniques** : Stack principal, frontend, backend, langages, bases de données, outils
- **Soft skills** : Compétences comportementales
- **Loisirs** : Centres d'intérêt

#### Pour les factures :
- **En-tête** : Informations fournisseur et client
- **Détails** : Numéro de facture, dates, références
- **Articles** : Détail des articles/services avec quantités et prix
- **Totaux** : Sous-total HT, TVA, Total TTC
- **Conditions** : Conditions de paiement et mentions légales

#### Pour les formulaires :
- **Titre** : Titre du formulaire
- **Champs** : Liste des champs avec labels, valeurs et types
- **Signature** : Date et signataire

### Détection automatique du type de document

Le script peut **détecter automatiquement** le type de document à partir du contenu :
- **CV** : Détecté par mots-clés (curriculum vitae, expérience professionnelle, formation, compétences)
- **Facture** : Détecté par mots-clés (facture, invoice, TVA, HT, TTC, client, fournisseur)
- **Formulaire** : Détecté par mots-clés (formulaire, nom, prénom, adresse, signature)

Vous pouvez aussi forcer le type avec l'option `--type`.

### Langues supportées

Par défaut, le script utilise le français et l'anglais (`fra+eng`) pour l'OCR. Pour modifier les langues, éditez le paramètre `lang` dans les fonctions `extract_text_from_image` et `extract_text_from_pdf`.

Le LLM peut traiter plusieurs langues selon le modèle utilisé (llama3.2 supporte français et anglais).

Pour voir les langues disponibles dans Tesseract :
```bash
tesseract --list-langs
```

## Notes importantes

- Pour les PDF, le script convertit chaque page en image avant l'extraction OCR, ce qui peut prendre du temps pour les documents volumineux
- La qualité de l'extraction dépend de la qualité de l'image/PDF source
- Les documents scannés nécessitent généralement un prétraitement pour de meilleurs résultats
- Le post-traitement LLM peut prendre plus de temps mais améliore significativement la qualité du texte extrait
- Assurez-vous qu'Ollama est en cours d'exécution avant d'utiliser le post-traitement LLM

