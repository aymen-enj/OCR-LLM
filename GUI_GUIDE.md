# 🎨 Interface Graphique - Guide d'Utilisation

## Aperçu de l'Interface

![Interface OCR GUI](C:/Users/aymen/.gemini/antigravity/brain/75b864f3-d0e0-49b5-bd91-78bbe5581093/ocr_gui_screenshot_1765496953572.png)

---

## Lancement de l'Interface

```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Lancer l'interface graphique
python ocr_gui.py
```

## Fonctionnalités

### 📁 Sélection de Fichiers
- **Glisser-déposer** : Faites glisser un fichier PDF, PNG ou JPG dans la zone prévue
- **Parcourir** : Cliquez sur la zone pour ouvrir l'explorateur de fichiers

### ⚙️ Configuration

1. **Type de document** :
   - `auto` : Détection automatique (recommandé)
   - `cv` : Force le traitement comme CV
   - `facture` : Force le traitement comme facture
   - `formulaire` : Force le traitement comme formulaire

2. **Modèle LLM** :
   - `llama3.2` : Modèle par défaut (recommandé)
   - `mistral` : Alternative performante
   - `llama2` : Version précédente
   - `codellama` : Spécialisé dans le code

3. **Dossier de sortie** :
   - Personnalisez l'emplacement des fichiers JSON générés
   - Par défaut : `output/`

### 🚀 Traitement

1. Sélectionnez un fichier
2. Configurez les options (optionnel)
3. Cliquez sur "🚀 Traiter le document"
4. Attendez la fin du traitement (barre de progression)

### 📊 Résultats

- **Affichage** : Le JSON structuré s'affiche automatiquement
- **💾 Sauvegarder** : Enregistrez le résultat dans un fichier personnalisé
- **📋 Copier** : Copiez le JSON dans le presse-papier
- **🗑️ Effacer** : Réinitialisez l'interface

## Captures d'écran

L'interface comprend :
- **Panneau gauche** : Configuration et contrôles
- **Panneau droit** : Affichage des résultats JSON
- **Barre de progression** : Suivi en temps réel
- **Status** : Messages d'état du traitement

## Thème

L'interface utilise un **thème sombre** moderne et professionnel.

## Support

Formats supportés :
- ✅ PDF (multi-pages)
- ✅ PNG
- ✅ JPG / JPEG

## Astuce

Pour les meilleurs résultats :
- Utilisez des documents scannés en **haute qualité** (300 DPI minimum)
- Assurez-vous qu'**Ollama est lancé** avant de démarrer l'interface
- Vérifiez que le **modèle est téléchargé** (`ollama pull llama3.2`)
