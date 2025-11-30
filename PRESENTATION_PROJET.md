
# Ultimate OCR & LLM Parser - Présentation

## 📋 Résumé du Projet

**Titre:** Système d'Extraction OCR Intelligent avec Post-traitement LLM


**Objectif:** Extraire et structurer automatiquement le texte de documents PDF ou images (PNG, JPG, etc.) avec correction intelligente des erreurs OCR et génération d'un JSON structuré selon le type de document (CV, facture, formulaire, générique).

---

## 🛠️ Technologies et Outils Utilisés


### 1. **Technologies et Outils**

- **OCR** : Tesseract OCR (via pytesseract, pdf2image, Pillow, OpenCV)
- **LLM** : Ollama (modèle par défaut : llama3.2, autres modèles supportés)
- **Python 3.x** et bibliothèques : argparse, json, rich, etc.
- **Structuration** : JSON, détection automatique du type, enrichissement par regex

---

## 🏗️ Architecture du Projet


### Structure des Fichiers

```
projet_ocr_fst/
│
├── ocr_extractor.py          # Script principal
├── requirements.txt          # Dépendances Python
├── README.md                 # Documentation
├── PRESENTATION_PROJET.md    # Présentation
│
├── input/                    # Documents sources
└── output/                   # Résultats JSON structuré
  ├── nom_fichier_data.json # Résultat final
  └── ...
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


### **Étape 2 : Extraction OCR et Markdown**

- Pour les PDF :
  - Extraction du texte en Markdown avec PyMuPDF4LLM
  - Si le texte est insuffisant, fallback OCR (conversion PDF → images → OCR sur chaque page)
- Pour les images :
  - OCR direct avec pytesseract
- Prétraitement des images (rotation, contraste) pour améliorer la qualité

---


### **Étape 3 : Détection automatique du type de document**

- Analyse heuristique par mots-clés pondérés (CV, facture, formulaire, générique)
- Peut être forcé par l'option `--type`

---


### **Étape 4 : Analyse LLM et structuration JSON**

- Construction d'un prompt dynamique selon le type détecté
- Appel au modèle Ollama pour correction et extraction structurée en une seule étape
- Génération d'un JSON strict selon le schéma cible (CV, facture, formulaire, générique)

---


### **Étape 5 : Correction et enrichissement des données**

- Extraction d'emails, téléphones, LinkedIn, IBAN par regex
- Injection dans le JSON si le LLM les a manqués

---

## 🔧 Fonctionnalités Principales


## 🔧 Fonctionnalités Principales

- Extraction OCR multi-format (PDF, images)
- Détection automatique du type de document (CV, facture, formulaire, générique)
- Structuration intelligente des données avec LLM (Ollama)
- Export JSON structuré selon le type détecté
- Correction et enrichissement des données (emails, téléphones, IBAN, etc.)

---

## 📊 Exemple d'Utilisation


### Exemple d'utilisation

```bash
python ocr_extractor.py input/CV_Aymen_Ennaji.pdf
python ocr_extractor.py input/facture.pdf --type facture
python ocr_extractor.py input/document.pdf --model mistral
python ocr_extractor.py input/image.png --output output
```

---

## 🎯 Résultats Obtenus


### Exemple de résultat JSON (CV)
```json
{
  "candidat": {
    "nom": "Ennaji Aymen",
    "email": "aymenennaji@gmail.com",
    "telephone": "0626424451",
    "liens": ["linkedin.com/in/aymen-ennaji"]
  },
  "profil_synthese": "Développeur Web & Systèmes d'Information...",
  "competences": {
    "langages": ["Python", "JavaScript"],
    "outils": ["Node.js", "Express.js"],
    "soft_skills": ["Autonomie", "Esprit d'équipe"]
  },
  "experience": [{"poste": "...", "entreprise": "...", "dates": "...", "missions": ["..."]}],
  "education": [{"diplome": "...", "ecole": "...", "annee": "..."}]
}
```

---

## ⚡ Optimisations Implémentées


### Optimisations
- Passage direct OCR → JSON (un seul appel LLM)
- Correction et enrichissement par regex
- Détection automatique du type

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
- Tesseract OCR : https://github.com/tesseract-ocr/tesseract
- Ollama : https://ollama.ai/
- pytesseract : https://github.com/madmaze/pytesseract
- pdf2image : https://github.com/Belval/pdf2image

---


## 📝 Conclusion

Ce projet intègre OCR et LLM pour une extraction et structuration intelligente de documents variés. Il détecte automatiquement le type, corrige les erreurs, enrichit les données, et exporte un JSON prêt à l'emploi pour l'automatisation ou l'intégration.

