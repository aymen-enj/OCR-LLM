# Projet OCR Intelligent - Présentation

## 📋 Résumé du Projet

**Titre:** Système d'Extraction OCR Intelligent avec Post-traitement LLM

**Objectif:** Développer une application Python capable d'extraire le texte de documents scannés (PDF, images) avec correction automatique des erreurs OCR et structuration intelligente des données en format JSON.

---

## 🛠️ Technologies et Outils Utilisés

### 1. **Technologies de Base**

#### **OCR (Optical Character Recognition)**
- **Tesseract OCR** : Moteur OCR open-source
  - Chemin d'installation: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - Langues supportées: Français + Anglais (fra+eng)
  - Rôle: Extraction du texte brut depuis les images/PDF

#### **Python et Bibliothèques**
- **Python 3.x** : Langage de programmation principal
- **pytesseract (v0.3.10)** : Interface Python pour Tesseract OCR
- **pdf2image (v1.16.3)** : Conversion PDF → Images pour traitement OCR
- **Pillow (v10.1.0)** : Manipulation d'images (PIL)
- **opencv-python (v4.8.1.78)** : Traitement d'images avancé

#### **LLM (Large Language Model)**
- **Ollama** : Plateforme pour exécuter des LLM en local
  - Modèle utilisé: **llama3.2** (par défaut)
  - Autres modèles supportés: mistral, etc.
  - Rôle: Post-traitement intelligent pour correction OCR et structuration

#### **Traitement de Données**
- **JSON** : Format de sortie structuré
- **RegEx** : Patterns pour corrections OCR de base
- **argparse** : Interface en ligne de commande

---

## 🏗️ Architecture du Projet

### Structure des Fichiers

```
projet_ocr_fst/
│
├── ocr_extractor.py          # Script principal (778 lignes)
├── requirements.txt          # Dépendances Python
├── README.md                 # Documentation complète
├── PRESENTATION_PROJET.md    # Ce document
│
├── input/                    # Documents sources
│   ├── CV_Aymen_Ennaji.pdf
│   ├── modele_de_facture.pdf
│   └── rempli.pdf
│
└── output/                   # Résultats générés
    ├── *_extracted.txt      # Texte brut OCR
    └── *_cleaned.json       # JSON structuré
```

---

## 🔄 Processus Complet de A à Z

### **Étape 1 : Préparation de l'Environnement**

```bash
# 1. Installation de Tesseract OCR (Windows)
#    Téléchargé depuis: https://github.com/UB-Mannheim/tesseract/wiki
#    Installé dans: C:\Program Files\Tesseract-OCR\

# 2. Installation d'Ollama
#    Téléchargé et installé sur le PC local
#    Modèle téléchargé: ollama pull llama3.2

# 3. Création de l'environnement Python
python -m venv venv
venv\Scripts\activate

# 4. Installation des dépendances
pip install -r requirements.txt
```

### **Étape 2 : Extraction OCR (Texte Brut)**

#### **2.1 Pour les Images (PNG, JPG, etc.)**
```python
def extract_text_from_image(image_path):
    # 1. Ouvrir l'image avec PIL
    image = Image.open(image_path)
    
    # 2. Extraire le texte avec Tesseract OCR
    text = pytesseract.image_to_string(image, lang='fra+eng')
    
    # 3. Retourner le texte brut
    return text
```

#### **2.2 Pour les PDF**
```python
def extract_text_from_pdf(pdf_path):
    # 1. Convertir chaque page PDF en image
    images = convert_from_path(pdf_path)
    
    # 2. Extraire le texte de chaque page avec OCR
    all_text = []
    for image in images:
        text = pytesseract.image_to_string(image, lang='fra+eng')
        all_text.append(text)
    
    # 3. Combiner toutes les pages
    return "\n\n".join(all_text)
```

**Résultat:** Fichier `*_extracted.txt` contenant le texte brut OCR (avec erreurs potentielles)

---

### **Étape 3 : Pré-traitement (Corrections de Base)**

```python
def pre_process_ocr_text(text):
    # Corrections automatiques via RegEx
    corrections = {
        'Dipl6mé' → 'Diplômé',
        'lnformation' → 'Information',
        'Node,js' → 'Node.js',
        'Expressjjs' → 'Express.js',
        # ... etc
    }
    # Applique les corrections
    return corrected_text
```

**Objectif:** Corriger les erreurs OCR les plus évidentes avant le LLM

---

### **Étape 4 : Détection Automatique du Type de Document**

```python
def detect_document_type(text):
    # Analyse des mots-clés pour détecter:
    # - CV: curriculum, vitae, compétences, formation
    # - Facture: facture, invoice, TVA, HT, TTC
    # - Formulaire: formulaire, nom, prénom, adresse
    # - General: par défaut
    return detected_type
```

**Résultat:** Type de document détecté automatiquement ou spécifié par l'utilisateur

---

### **Étape 5 : Post-traitement Intelligent avec LLM**

#### **5.1 Génération du JSON Structuré (OPTIMISÉ)**

**Nouvelle approche optimisée:** Un seul appel LLM qui fait tout en une fois !

```python
def extract_json_from_ocr_text(raw_text, doc_type):
    # 1. Pré-traitement avec corrections de base
    pre_processed = pre_process_ocr_text(raw_text)
    
    # 2. Génération du prompt adapté au type de document
    prompt = get_json_prompt_from_ocr(pre_processed, doc_type)
    #    Ce prompt intègre:
    #    - Instructions de correction OCR
    #    - Structure JSON attendue selon le type
    #    - Instructions d'extraction structurée
    
    # 3. Appel unique à Ollama (correction + extraction en une étape)
    response = ollama.generate(model='llama3.2', prompt=prompt)
    
    # 4. Extraction et parsing du JSON
    json_data = json.loads(response['response'])
    
    return json_data
```

**Avantages:**
- ✅ **2x plus rapide** : Un seul appel LLM au lieu de deux
- ✅ **Meilleure qualité** : Correction et extraction dans la même étape
- ✅ **Optimisé** : Pas d'étape intermédiaire de texte nettoyé

---

### **Étape 6 : Structures JSON selon le Type**

#### **Pour les CV:**
```json
{
  "a_propos_de_moi": {
    "nom": "...",
    "titre": "...",
    "telephone": "...",
    "email": "...",
    "github": "...",
    "linkedin": "..."
  },
  "langues": [...],
  "education": [...],
  "experiences_professionnelles": [...],
  "competences_techniques": {...},
  "soft_skills": [...],
  "loisirs": [...]
}
```

#### **Pour les Factures:**
```json
{
  "en_tete": {
    "fournisseur": {...},
    "client": {...}
  },
  "details": {...},
  "articles": [...],
  "totaux": {...}
}
```

#### **Pour les Formulaires:**
```json
{
  "titre": "...",
  "sections": [...],
  "tous_les_champs": [...],
  "signature": {...}
}
```

---

## 🔧 Fonctionnalités Principales

### 1. **Extraction OCR Multi-format**
- ✅ PDF (multi-pages)
- ✅ Images: PNG, JPG, JPEG, BMP, TIFF

### 2. **Correction Automatique des Erreurs OCR**
- ✅ Correction via RegEx (pré-traitement)
- ✅ Correction intelligente via LLM (post-traitement)
- ✅ Exemples de corrections:
  - "Dipl6mé" → "Diplômé"
  - "lnformation" → "Information"
  - "Node,js" → "Node.js"

### 3. **Détection Automatique du Type de Document**
- ✅ CV
- ✅ Facture
- ✅ Formulaire
- ✅ Général (détection automatique par mots-clés)

### 4. **Structuration Intelligente**
- ✅ Organisation logique du contenu
- ✅ Conservation de la hiérarchie (sections, sous-sections)
- ✅ Extraction des informations clés

### 5. **Export JSON Structuré**
- ✅ Format JSON standard
- ✅ Structure adaptée au type de document
- ✅ Données prêtes pour traitement automatique

---

## 📊 Exemple d'Utilisation

### **Commande de base:**
```bash
python ocr_extractor.py input/CV_Aymen_Ennaji.pdf
```

### **Processus automatique:**
1. **OCR** → Extraction du texte brut → `CV_Aymen_Ennaji_extracted.txt`
2. **Détection** → Type de document: "cv" (automatique)
3. **LLM** → Correction OCR + Extraction JSON (une seule étape)
4. **Résultat** → `CV_Aymen_Ennaji_cleaned.json`

### **Options avancées:**
```bash
# Spécifier le type de document
python ocr_extractor.py facture.pdf --type facture

# Choisir le modèle LLM
python ocr_extractor.py document.pdf --model mistral

# Désactiver le LLM (OCR uniquement)
python ocr_extractor.py document.pdf --no-llm
```

---

## 🎯 Résultats Obtenus

### **Avant (OCR brut):**
```
A PROPOS DE MOI
ENNAJI AYMEN
Développeur Web & Systémes d'lnformation
& 0626424451 & aymenennajiS@gmail.com
lin] linkedin.com/in/aymen-ennaji
LANGUES
Jeune dipl6mé en Développement des Systemes d'Information
...
```

### **Après (JSON structuré):**
```json
{
  "a_propos_de_moi": {
    "nom": "Ennaji Aymen",
    "titre": "Développeur Web & Systèmes d'Information",
    "telephone": "0626424451",
    "email": "aymenennaji@gmail.com",
    "linkedin": "linkedin.com/in/aymen-ennaji"
  },
  "langues": [
    {"langue": "Français", "niveau": "Courant"},
    {"langue": "Anglais", "niveau": "Technique"},
    {"langue": "Arabe", "niveau": "Langue maternelle"}
  ],
  "education": [...],
  "experiences_professionnelles": [...]
}
```

**Corrections automatiques:**
- ✅ "dipl6mé" → "Diplômé"
- ✅ "lnformation" → "Information"
- ✅ "Systemes" → "Systèmes"
- ✅ "aymenennajiS" → "aymenennaji"
- ✅ "lin]" → "linkedin"

---

## ⚡ Optimisations Implémentées

### 1. **Passage Direct OCR → JSON**
- **Avant:** OCR → Texte nettoyé → JSON (2 appels LLM)
- **Après:** OCR → JSON (1 seul appel LLM)
- **Gain:** 2x plus rapide

### 2. **Pré-traitement RegEx**
- Corrections rapides avant le LLM
- Réduction des erreurs courantes

### 3. **Détection Automatique**
- Évite de spécifier le type manuellement
- Adaptation automatique du traitement

---

## 📈 Points Forts du Projet

1. **✅ Extraction OCR précise** : Support multi-format (PDF, images)
2. **✅ Correction intelligente** : LLM pour corriger les erreurs OCR
3. **✅ Structuration automatique** : Organisation logique du contenu
4. **✅ Export JSON** : Format standard pour traitement automatique
5. **✅ Multi-types de documents** : CV, factures, formulaires, etc.
6. **✅ Détection automatique** : Reconnaissance du type de document
7. **✅ Optimisation** : Traitement rapide (un seul appel LLM)
8. **✅ Qualité** : Correction et extraction en une étape

---

## 🔬 Défis Rencontrés et Solutions

### **Défi 1: Erreurs OCR fréquentes**
**Problème:** Caractères mal reconnus (6→ô, l→I, etc.)

**Solution:** 
- Pré-traitement RegEx pour corrections rapides
- Post-traitement LLM pour corrections intelligentes

### **Défi 2: Structure mélangée après OCR**
**Problème:** Sections mélangées, texte non structuré

**Solution:**
- Prompts LLM spécifiques par type de document
- Instructions détaillées pour réorganisation intelligente

### **Défi 3: Temps de traitement long**
**Problème:** 2 appels LLM séquentiels (nettoyage + JSON)

**Solution:**
- Optimisation: Un seul appel LLM qui fait correction + extraction
- Gain de temps: 2x plus rapide

---

## 💡 Améliorations Futures Possibles

1. **Interface graphique** : GUI avec drag & drop
2. **API REST** : Service web pour intégration
3. **Traitement par lots** : Traiter plusieurs fichiers en une fois
4. **Support de plus de formats** : Word, Excel, etc.
5. **Apprentissage automatique** : Modèle spécifique pour OCR

---

## 📚 Références Techniques

- **Tesseract OCR:** https://github.com/tesseract-ocr/tesseract
- **Ollama:** https://ollama.ai/
- **pytesseract:** https://github.com/madmaze/pytesseract
- **pdf2image:** https://github.com/Belval/pdf2image

---

## 📝 Conclusion

Ce projet démontre l'intégration réussie de **technologies OCR** et **LLM** pour créer un système d'extraction intelligent. 

**Principales réalisations:**
- ✅ Système complet et fonctionnel
- ✅ Support multi-types de documents
- ✅ Correction automatique des erreurs
- ✅ Export structuré en JSON
- ✅ Optimisations pour performance

**Technologies maîtrisées:**
- OCR (Tesseract)
- LLM (Ollama)
- Python et bibliothèques
- Traitement de documents
- Structuration de données

