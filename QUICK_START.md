# 🚀 Démarrage Rapide - Interface GUI

## Lancement Immédiat

```bash
# 1. Activer l'environnement virtuel
venv\Scripts\activate

# 2. Lancer l'interface
python ocr_gui.py
```

## Utilisation en 4 Étapes

### 1️⃣ Sélectionner un Fichier
- **Glissez-déposez** un PDF ou une image
- OU **cliquez** sur la zone pour parcourir

### 2️⃣ Configurer (Optionnel)
- **Type** : Laissez "auto" pour détection automatique
- **Modèle** : "llama3.2" est recommandé
- **Sortie** : "output" par défaut

### 3️⃣ Traiter
- Cliquez sur **"🚀 Traiter le document"**
- Attendez la fin (barre de progression)

### 4️⃣ Consulter & Exporter
- Consultez le JSON formaté
- **Sauvegardez** dans un fichier personnalisé
- OU **Copiez** dans le presse-papier

## 📝 Exemples de Fichiers

Testez avec les exemples fournis :
```
input/CV_Aymen_Ennaji.pdf        → Type: CV
input/modele_de_facture.pdf      → Type: Facture
input/formulaire.pdf             → Type: Formulaire
```

## ⚙️ Prérequis

Assurez-vous que :
- ✅ **Ollama est lancé** (`ollama serve`)
- ✅ **Modèle téléchargé** (`ollama pull llama3.2`)
- ✅ **Tesseract installé** (voir README.md)

## 💡 Astuces

### Pour de Meilleurs Résultats
- 📄 Utilisez des **PDF de qualité** (300 DPI minimum)
- 🎯 Documents **bien scannés** et **lisibles**
- 🌍 Texte en **français** ou **anglais**

### En Cas de Problème
- ❌ **Erreur Ollama** → Vérifiez que `ollama serve` est lancé
- ❌ **Erreur Tesseract** → Vérifiez l'installation
- ❌ **Format non supporté** → Utilisez PDF, PNG ou JPG

## 🎨 Personnalisation

### Modèles LLM Disponibles
- `llama3.2` → **Recommandé**, rapide et précis
- `mistral` → Alternative performante
- `llama2` → Version précédente
- `codellama` → Spécialisé code

Téléchargez d'autres modèles :
```bash
ollama pull <nom_du_modele>
```

### Dossier de Sortie
Changez le dossier pour organiser vos exports :
- `output/` → Défaut
- `resultats/` → Personnalisé
- `C:\Mes Documents\OCR\` → Chemin absolu

## 📊 Comprendre les Résultats

### Structure JSON par Type

**CV** :
```json
{
  "candidat": {...},
  "profil_synthese": "...",
  "competences": {...},
  "experience": [...],
  "education": [...]
}
```

**Facture** :
```json
{
  "document": {...},
  "emetteur": {...},
  "client": {...},
  "articles": [...],
  "totaux": {...}
}
```

**Formulaire** :
```json
{
  "titre_formulaire": "...",
  "champs_reemplis": [...],
  "cases_cochees": [...],
  "blocs_texte_libre": [...],
  "statut_signature": "..."
}
```

## 🔄 Workflow Complet

```
Fichier PDF/Image
      ↓
[Glisser-Déposer dans GUI]
      ↓
[Extraction OCR + Markdown]
      ↓
[Détection Type Auto]
      ↓
[Analyse LLM (llama3.2)]
      ↓
[Enrichissement Regex]
      ↓
[Affichage JSON]
      ↓
[Export / Copie]
```

## 📞 Support

### Documentation
- 📖 [README.md](file:///c:/Users/aymen/OneDrive/Desktop/projet_ocr_fst/README.md) - Documentation complète
- 🎨 [GUI_GUIDE.md](file:///c:/Users/aymen/OneDrive/Desktop/projet_ocr_fst/GUI_GUIDE.md) - Guide interface
- 📋 [PRESENTATION_PROJET.md](file:///c:/Users/aymen/OneDrive/Desktop/projet_ocr_fst/PRESENTATION_PROJET.md) - Présentation technique

### Fichiers Générés
- `output/<filename>_data.json` → Résultat automatique
- Sauvegarde personnalisée via bouton 💾

## 🎉 Prêt !

Vous êtes maintenant prêt à utiliser l'interface graphique OCR !

**Commande rapide** : `python ocr_gui.py`
