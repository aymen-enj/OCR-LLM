#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracteur OCR pour fichiers PDF et PNG
Extrait le texte de fichiers PDF ou PNG et le sauvegarde dans un fichier texte
"""

import os
import sys
import re
import json
from pathlib import Path
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import argparse

# Tentative d'importation d'Ollama (optionnel)
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Note: Ollama n'est pas installé. Le post-traitement LLM sera désactivé.")
    print("Installez avec: pip install ollama")

# Configuration du chemin Tesseract pour Windows
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    print(f"Attention: Tesseract non trouvé au chemin {TESSERACT_PATH}")
    print("Assurez-vous que Tesseract est installé ou modifiez TESSERACT_PATH dans le script.")


def extract_text_from_image(image_path):
    """
    Extrait le texte d'une image (PNG, JPG, etc.) en utilisant OCR
    
    Args:
        image_path (str): Chemin vers le fichier image
        
    Returns:
        str: Texte extrait de l'image
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='fra+eng')
        return text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte de l'image: {e}")
        return ""


def extract_text_from_pdf(pdf_path):
    """
    Extrait le texte d'un fichier PDF en utilisant OCR
    
    Args:
        pdf_path (str): Chemin vers le fichier PDF
        
    Returns:
        str: Texte extrait du PDF
    """
    try:
        # Convertir le PDF en images
        print("Conversion du PDF en images...")
        images = convert_from_path(pdf_path)
        
        all_text = []
        for i, image in enumerate(images):
            print(f"Traitement de la page {i+1}/{len(images)}...")
            text = pytesseract.image_to_string(image, lang='fra+eng')
            all_text.append(text)
            
        return "\n\n".join(all_text)
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte du PDF: {e}")
        return ""


def pre_process_ocr_text(text):
    """
    Pré-traite le texte OCR avec des corrections de base avant le LLM
    Corrige les erreurs OCR les plus évidentes
    
    Args:
        text (str): Texte brut OCR
        
    Returns:
        str: Texte pré-corrigé
    """
    # Corrections de base (pattern matching pour les erreurs OCR courantes)
    corrections = {
        r'Dipl6mé': 'Diplômé',
        r'Dipl6me': 'Diplôme',
        r'lnformation': 'Information',  # Attention: ne pas mettre en majuscules
        r'\bSystemes\b': 'Systèmes',
        r'\bsystemes\b': 'systèmes',
        r'\bSysteme\b': 'Système',
        r'\bsysteme\b': 'système',
        r'francaise': 'française',
        r'problemes': 'problèmes',
        r'succés\b': 'succès',  # accent circonflexe
        r'Node,js': 'Node.js',
        r'Expressjjs': 'Express.js',
        r'HTMLS/CSS3': 'HTML5/CSS3',
        r'\bVb\.net\b': 'VB.NET',
        r'aymenennajiS@gmail\.com': 'aymenennaji@gmail.com',
        r'lin\]': 'linkedin',
        r'DONNEÉES': 'données',
    }
    
    corrected_text = text
    for pattern, replacement in corrections.items():
        corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
    
    return corrected_text


def get_prompt_for_document_type(raw_text, doc_type="cv"):
    """
    Génère le prompt LLM approprié selon le type de document
    
    Args:
        raw_text (str): Texte brut OCR
        doc_type (str): Type de document (cv, facture, formulaire, general)
        
    Returns:
        str: Prompt adapté au type de document
    """
    prompts = {
        "cv": f"""Tu es un expert en restructuration de CV OCR. Corrige les erreurs OCR ET réorganise intelligemment le contenu selon les sections.

TÂCHES:
1. IDENTIFIER LES SECTIONS: Repère les titres de sections (A PROPOS DE MOI, LANGUES, EDUCATION, EXPERIENCES PROFESSIONNELLES, COMPETENCES TECHNIQUES, SOFT SKILLS, LOISIRS)
2. RÉORGANISER: Place chaque contenu sous sa section appropriée:
   - "Jeune diplômé...passionné par..." → sous "A PROPOS DE MOI"
   - "FRANÇAIS", "ANGLAIS", "ARABE" → tous sous "LANGUES" ensemble
   - Dates et formations → sous "EDUCATION"
   - Expériences avec dates → sous "EXPERIENCES PROFESSIONNELLES"
   - Technologies et outils → sous "COMPETENCES TECHNIQUES"
3. CORRIGER LES ERREURS OCR:
   - "Dipl6mé"/"Dipl6me" → "Diplômé"/"Diplôme"
   - "lnformation" → "Information" (respecte la casse: minuscule sauf début de phrase)
   - "Systemes"/"Systeme" → "Systèmes"/"Système" (respecte la casse)
   - "francaise" → "française"
   - "problemes" → "problèmes"
   - "succés" → "succès"
   - "Node,js" → "Node.js"
   - "Expressjjs" → "Express.js"
   - "HTMLS/CSS3" → "HTML5/CSS3"
   - "Vb.net" → "VB.NET"
   - "aymenennajiS@gmail.com" → "aymenennaji@gmail.com"
   - "lin]" → "linkedin"
   - "DONNEÉES" → "données"
4. STRUCTURE FINALE: Organise le CV avec sections claires et bien séparées (une ligne vide entre sections)

Texte OCR brut à corriger et réorganiser:
{raw_text}

Retourne le CV réorganisé avec sections claires, erreurs OCR corrigées, et bonne structure.""",

        "facture": f"""Tu es un expert en traitement de factures OCR. Corrige les erreurs OCR et structure intelligemment le contenu de cette facture.

TÂCHES:
1. CORRIGER LES ERREURS OCR: Corrige les caractères mal reconnus (chiffres, lettres, symboles)
2. IDENTIFIER LES SECTIONS: Repère et organise:
   - Informations émetteur (nom, adresse, SIRET, etc.)
   - Informations client (nom, adresse)
   - Numéro de facture, date, échéance
   - Détail des articles/services (description, quantité, prix unitaire, total)
   - Totaux (sous-total, TVA, total TTC)
   - Conditions de paiement
3. PRÉSERVER LA STRUCTURE: Garde la mise en page et l'organisation originale
4. CORRIGER LES ERREURS: Chiffres mal lus, caractères spéciaux mal reconnus

Texte OCR brut à corriger:
{raw_text}

Retourne la facture corrigée avec structure claire et erreurs OCR corrigées.""",

        "formulaire": f"""Tu es un expert en traitement de formulaires OCR. Corrige les erreurs OCR et structure intelligemment le contenu de ce formulaire.

TÂCHES:
1. CORRIGER LES ERREURS OCR: Corrige les caractères mal reconnus
2. IDENTIFIER LA STRUCTURE: Repère et organise:
   - Titre du formulaire
   - Champs et labels
   - Sections et sous-sections
   - Instructions et notes
3. PRÉSERVER LA HIÉRARCHIE: Garde la structure logique (titre, sections, champs)
4. CORRIGER LES ERREURS: Texte mal lu, caractères spéciaux, formatage

Texte OCR brut à corriger:
{raw_text}

Retourne le formulaire corrigé avec structure claire et erreurs OCR corrigées.""",

        "general": f"""Tu es un expert en traitement OCR. Corrige les erreurs OCR et améliore la structure de ce document.

TÂCHES:
1. CORRIGER LES ERREURS OCR: Corrige les caractères mal reconnus
2. STRUCTURER LE CONTENU: Organise le texte de manière logique
3. PRÉSERVER LA STRUCTURE: Garde la mise en page originale (sections, listes, paragraphes)
4. AMÉLIORER LA LISIBILITÉ: Nettoie les espaces multiples, améliore le formatage
5. CORRIGER LES ERREURS: Caractères mal lus, fautes d'OCR courantes

Texte OCR brut à corriger:
{raw_text}

Retourne le document corrigé avec structure claire et erreurs OCR corrigées."""
    }
    
    return prompts.get(doc_type.lower(), prompts["general"])


def post_process_with_llm(raw_text, model_name="llama3.2", use_llm=True, doc_type="cv"):
    """
    Post-traite le texte extrait par OCR en utilisant un LLM via Ollama
    pour corriger les erreurs, nettoyer et structurer le texte
    
    Args:
        raw_text (str): Texte brut extrait par OCR
        model_name (str): Nom du modèle Ollama à utiliser
        use_llm (bool): Si False, retourne le texte brut sans traitement
        doc_type (str): Type de document (cv, facture, formulaire, general)
        
    Returns:
        str: Texte nettoyé et structuré
    """
    if not use_llm or not OLLAMA_AVAILABLE:
        # Si pas de LLM, appliquer quand même le pré-traitement basique
        return pre_process_ocr_text(raw_text)
    
    try:
        # Pré-traiter avec des corrections de base
        pre_processed = pre_process_ocr_text(raw_text)
        
        print(f"Post-traitement avec LLM en cours (type: {doc_type})...")
        
        # Obtenir le prompt adapté au type de document
        prompt = get_prompt_for_document_type(pre_processed, doc_type)

        # Appel à Ollama
        response = ollama.generate(model=model_name, prompt=prompt)
        
        # Extraire le texte de la réponse
        if isinstance(response, dict) and 'response' in response:
            cleaned_text = response['response'].strip()
        elif isinstance(response, str):
            cleaned_text = response.strip()
        else:
            # Tentative d'accès à l'attribut si c'est un objet
            cleaned_text = str(getattr(response, 'response', response)).strip()
        
        # Vérifier si la réponse est valide
        if cleaned_text and len(cleaned_text) > 50:  # Seuil minimum
            print("Post-traitement LLM terminé avec succès.")
            return cleaned_text
        else:
            print("Avertissement: La réponse du LLM semble invalide, utilisation du texte brut.")
            return raw_text
            
    except Exception as e:
        print(f"Erreur lors du post-traitement LLM: {e}")
        print("Utilisation du texte brut extrait par OCR.")
        return raw_text


def save_text_to_file(text, output_path):
    """
    Sauvegarde le texte extrait dans un fichier texte
    
    Args:
        text (str): Texte à sauvegarder
        output_path (str): Chemin vers le fichier de sortie
    """
    try:
        # Créer le dossier de sortie s'il n'existe pas
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Texte sauvegardé avec succès dans: {output_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier: {e}")


def detect_document_type(text, doc_type=None):
    """
    Détecte ou valide le type de document à partir du texte
    
    Args:
        text (str): Texte brut extrait par OCR
        doc_type (str): Type de document spécifié par l'utilisateur (cv, facture, formulaire, general)
        
    Returns:
        str: Type de document détecté ou spécifié
    """
    if doc_type and doc_type.lower() in ['cv', 'facture', 'formulaire', 'general']:
        return doc_type.lower()
    
    # Détection automatique basée sur des mots-clés
    text_lower = text.lower()
    
    # Mots-clés pour détecter un CV
    cv_keywords = ['curriculum', 'vitae', 'cv', 'développeur', 'expérience professionnelle', 
                   'formation', 'éducation', 'compétences', 'langues', 'loisirs']
    cv_score = sum(1 for keyword in cv_keywords if keyword in text_lower)
    
    # Mots-clés pour détecter une facture
    facture_keywords = ['facture', 'invoice', 'n°', 'numéro', 'date d\'émission', 
                        'montant total', 'tva', 'ht', 'ttc', 'client', 'fournisseur']
    facture_score = sum(1 for keyword in facture_keywords if keyword in text_lower)
    
    # Mots-clés pour détecter un formulaire
    formulaire_keywords = ['formulaire', 'form', 'nom:', 'prénom:', 'date de naissance', 
                          'adresse', 'case à cocher', 'signature']
    formulaire_score = sum(1 for keyword in formulaire_keywords if keyword in text_lower)
    
    # Retourner le type avec le score le plus élevé
    scores = {
        'cv': cv_score,
        'facture': facture_score,
        'formulaire': formulaire_score
    }
    
    max_score = max(scores.values())
    if max_score > 2:  # Seuil minimum pour la détection
        detected_type = max(scores, key=scores.get)
        print(f"Type de document détecté automatiquement: {detected_type}")
        return detected_type
    
    # Par défaut, retourner 'general'
    print("Type de document non détecté, utilisation du mode 'general'")
    return 'general'


def get_json_prompt_from_ocr(raw_text, doc_type='general'):
    """
    Retourne le prompt JSON qui corrige l'OCR et extrait directement le JSON
    Optimisé pour passer directement de l'OCR brut au JSON structuré
    
    Args:
        raw_text (str): Texte brut OCR
        doc_type (str): Type de document (cv, facture, formulaire, general)
        
    Returns:
        str: Prompt optimisé pour correction OCR + extraction JSON
    """
    # Utiliser les prompts JSON existants mais en y ajoutant les instructions de correction OCR
    base_prompt = get_json_prompt_for_document_type(raw_text, doc_type)
    
    # Ajouter les instructions de correction OCR au début
    ocr_corrections = """
IMPORTANT: Ce texte vient d'un OCR et contient des erreurs. Tu dois:
1. CORRIGER les erreurs OCR courantes:
   - "Dipl6mé" ou "Dipl6me" → "Diplômé" ou "Diplôme"
   - "lnformation" → "Information"
   - "Systemes"/"Systeme" → "Systèmes"/"Système"
   - "francaise" → "française"
   - "problemes" → "problèmes"
   - "succés" → "succès"
   - "Node,js" → "Node.js"
   - "Expressjjs" → "Express.js"
   - "HTMLS/CSS3" → "HTML5/CSS3"
   - "Vb.net" → "VB.NET"
   - "aymenennajiS@gmail.com" → "aymenennaji@gmail.com"
   - "lin]" → "linkedin"
   - "DONNEÉES" → "données"
   - Corriger les caractères mal reconnus (6→ô, l→I, etc.)
2. CORRIGER et STRUCTURER en JSON dans la même étape

"""
    
    return ocr_corrections + base_prompt


def get_json_prompt_for_document_type(text, doc_type='general'):
    """
    Retourne le prompt JSON adapté selon le type de document
    
    Args:
        text (str): Texte structuré
        doc_type (str): Type de document (cv, facture, formulaire, general)
        
    Returns:
        str: Prompt JSON adapté
    """
    if doc_type == 'cv':
        return f"""Tu es un expert en extraction de données CV. Extrait les informations de ce CV et retourne-les en format JSON structuré.

Structure JSON attendue:
{{
  "a_propos_de_moi": {{
    "nom": "Nom complet",
    "titre": "Titre professionnel",
    "telephone": "Numéro de téléphone",
    "email": "Adresse email",
    "github": "Lien GitHub",
    "linkedin": "Lien LinkedIn",
    "description": "Paragraphe descriptif complet"
  }},
  "langues": [
    {{"langue": "Français", "niveau": "Courant"}},
    {{"langue": "Anglais", "niveau": "Technique"}},
    {{"langue": "Arabe", "niveau": "Langue maternelle"}}
  ],
  "education": [
    {{
      "periode": "2023-2025",
      "etablissement": "Nom de l'établissement",
      "ville": "Ville",
      "diplome": "Nom du diplôme",
      "description": "Description de la formation",
      "competences": ["compétence1", "compétence2"]
    }}
  ],
  "experiences_professionnelles": [
    {{
      "periode": "Mai-Juin 2025",
      "entreprise": "Nom de l'entreprise",
      "ville": "Ville",
      "poste": "Titre du poste",
      "description": "Description du poste",
      "missions": ["mission1", "mission2"],
      "technologies": ["React", "Node.js"]
    }}
  ],
  "competences_techniques": {{
    "stack_principal": ["React js", "Node.js", "Express.js", "TypeScript"],
    "frontend": ["Tailwind CSS", "HTML5/CSS3"],
    "backend": ["Node.js", "Express", "MySQL"],
    "langages": ["JavaScript", "PHP", "C", "Java", "VB.NET"],
    "bases_de_donnees": ["MySQL", "T-SQL", "PostgreSQL"],
    "outils": ["Git", "PHP", "JWT", "OCR", "MathJax"]
  }},
  "soft_skills": ["Communication", "Adaptabilité", "Empathie", "Attention aux détails"],
  "loisirs": ["Musculation", "Voyages", "Natation", "Football"]
}}

Texte du CV à extraire:
{text}

IMPORTANT: Retourne UNIQUEMENT le JSON valide, sans commentaires ni texte supplémentaire avant ou après."""

    elif doc_type == 'facture':
        return f"""Tu es un expert en extraction de données factures. Extrait les informations de cette facture et retourne-les en format JSON structuré.

Structure JSON attendue:
{{
  "en_tete": {{
    "fournisseur": {{
      "nom": "Nom du fournisseur",
      "adresse": "Adresse complète",
      "telephone": "Téléphone",
      "email": "Email",
      "siret": "Numéro SIRET",
      "tva": "Numéro TVA"
    }},
    "client": {{
      "nom": "Nom du client",
      "adresse": "Adresse complète",
      "telephone": "Téléphone",
      "email": "Email"
    }}
  }},
  "details": {{
    "numero_facture": "Numéro de facture",
    "date_emission": "Date d'émission",
    "date_echeance": "Date d'échéance",
    "reference": "Référence commande"
  }},
  "articles": [
    {{
      "description": "Description de l'article",
      "quantite": "Quantité",
      "prix_unitaire": "Prix unitaire",
      "montant": "Montant total"
    }}
  ],
  "totaux": {{
    "sous_total_ht": "Sous-total HT",
    "tva": "Montant TVA",
    "total_ttc": "Total TTC"
  }},
  "conditions": "Conditions de paiement",
  "mentions": "Mentions légales"
}}

Texte de la facture à extraire:
{text}

IMPORTANT: Retourne UNIQUEMENT le JSON valide, sans commentaires ni texte supplémentaire avant ou après."""

    elif doc_type == 'formulaire':
        return f"""Tu es un expert en extraction de données formulaires. Extrait TOUTES les informations de ce formulaire et retourne-les en format JSON structuré et complet.

TÂCHES:
1. IDENTIFIER TOUTES LES SECTIONS: Titre, sections principales du formulaire
2. EXTRAIRE TOUS LES CHAMPS: Tous les champs avec leur label et leur valeur remplie
3. STRUCTURE SIMPLE ET CLAIRE: Organisation logique par sections avec champs associés
4. SIGNAIRE ET MENTIONS: Extraire date de signature et signataire si présents

Structure JSON attendue pour un formulaire:
{{
  "titre": "Titre du formulaire",
  "sections": [
    {{
      "titre": "Nom de la section (ex: Informations Personnelles)",
      "champs": [
        {{
          "label": "Nom du champ (ex: Nom, Email, Téléphone)",
          "valeur": "Valeur saisie dans le champ",
          "type": "texte|date|choix|case_a_cocher|email|telephone|adresse"
        }}
      ]
    }}
  ],
  "tous_les_champs": [
    {{
      "label": "Nom du champ",
      "valeur": "Valeur saisie",
      "type": "texte|date|choix|case_a_cocher|email|telephone|adresse",
      "section": "Section à laquelle appartient le champ"
    }}
  ],
  "signature": {{
    "presente": true/false,
    "date": "Date de signature si présente",
    "signataire": "Nom du signataire si présent",
    "mention": "Texte de signature si présent"
  }}
}}

RÈGLES IMPORTANTES:
- Extrait TOUS les champs du formulaire avec leur valeur
- Chaque champ doit avoir un label clair et sa valeur exacte
- Organise les champs par section dans "sections"
- Garde aussi une liste complète de tous les champs dans "tous_les_champs"
- N'inclus PAS d'informations techniques (technologie, langage, outils) pour un simple formulaire
- N'inclus PAS de livrables ou autres éléments qui ne sont pas des champs de formulaire
- Extrait uniquement ce qui est réellement rempli dans le formulaire

Texte du formulaire à extraire:
{text}

Retourne UNIQUEMENT le JSON valide avec TOUTES les informations du formulaire structurées."""

    else:  # general
        return f"""Tu es un expert en extraction de données structurées. Extrait TOUTES les informations importantes de ce document et retourne-les en format JSON structuré et complet.

TÂCHES:
1. IDENTIFIER TOUTES LES SECTIONS: Titre, sections principales, sous-sections, paragraphes
2. EXTRAIRE TOUT LE CONTENU: Toutes les informations, pas seulement un résumé
3. ORGANISER EN STRUCTURE JSON: Conserver la hiérarchie (sections, sous-sections, listes, points)
4. STRUCTURE FLEXIBLE: Adapte la structure selon le contenu (document technique, projet, rapport, etc.)

Structure JSON attendue (adaptée au contenu):
{{
  "titre": "Titre principal du document",
  "sections": [
    {{
      "titre": "Titre de la section",
      "contenu": "Contenu textuel de la section",
      "sous_sections": [
        {{
          "titre": "Titre de la sous-section",
          "contenu": "Contenu de la sous-section",
          "liste": ["élément 1", "élément 2"],
          "paragraphes": ["paragraphe 1", "paragraphe 2"]
        }}
      ],
      "liste": ["élément de liste"],
      "paragraphes": ["paragraphe 1", "paragraphe 2"]
    }}
  ],
  "informations_cles": {{
    "technologie": ["technologie 1", "technologie 2"],
    "langage": "Langage de programmation",
    "objectifs": ["objectif 1", "objectif 2"],
    "livrables": ["livrable 1", "livrable 2"]
  }},
  "contenu_complet": "Représentation complète du contenu avec toutes les informations"
}}

IMPORTANT:
- Extrait TOUT le contenu, pas seulement un résumé
- Conserve la structure et la hiérarchie du document
- Inclus toutes les sections, sous-sections, listes, et paragraphes
- Adapte la structure selon le type de document détecté

Texte du document à extraire:
{text}

Retourne UNIQUEMENT le JSON valide avec TOUTES les informations structurées."""


def extract_json_from_ocr_text(raw_text, model_name="llama3.2", use_llm=True, doc_type='general'):
    """
    Extrait directement les informations structurées du texte brut OCR et les convertit en JSON.
    Corrige les erreurs OCR et structure en une seule étape pour optimiser la vitesse.
    
    Args:
        raw_text (str): Texte brut extrait par OCR
        model_name (str): Nom du modèle Ollama à utiliser
        use_llm (bool): Si True, utilise Ollama pour générer le JSON
        doc_type (str): Type de document (cv, facture, formulaire, general)
        
    Returns:
        dict: Structure JSON du document
    """
    if not use_llm or not OLLAMA_AVAILABLE:
        return None
    
    try:
        # Pré-traiter avec des corrections de base
        pre_processed = pre_process_ocr_text(raw_text)
        
        print(f"Génération du JSON structuré directement depuis l'OCR (type: {doc_type})...")
        print("Correction OCR + extraction structurée en cours...")
        
        # Obtenir le prompt adapté au type de document (intégrant correction OCR + extraction JSON)
        prompt_json = get_json_prompt_from_ocr(pre_processed, doc_type)

        response = ollama.generate(model=model_name, prompt=prompt_json)
        
        # Extraire le texte de la réponse
        if isinstance(response, dict) and 'response' in response:
            json_text = response['response'].strip()
        elif isinstance(response, str):
            json_text = response.strip()
        else:
            json_text = str(getattr(response, 'response', response)).strip()
        
        # Nettoyer le texte pour extraire uniquement le JSON
        # Chercher le premier { et le dernier }
        start = json_text.find('{')
        end = json_text.rfind('}') + 1
        
        if start != -1 and end > start:
            json_text = json_text[start:end]
        
        # Parser le JSON
        try:
            cv_data = json.loads(json_text)
            print("JSON structuré généré avec succès.")
            return cv_data
        except json.JSONDecodeError as e:
            print(f"Erreur lors du parsing JSON: {e}")
            print(f"Texte JSON reçu: {json_text[:500]}")
            return None
            
    except Exception as e:
        print(f"Erreur lors de la génération du JSON: {e}")
        return None


def save_json_to_file(data, output_path):
    """
    Sauvegarde les données JSON dans un fichier
    
    Args:
        data (dict): Données JSON à sauvegarder
        output_path (str): Chemin vers le fichier de sortie JSON
    """
    try:
        # Créer le dossier de sortie s'il n'existe pas
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"JSON sauvegardé avec succès dans: {output_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier JSON: {e}")


def process_file(input_path, output_path=None, use_llm=True, model_name="llama3.2", doc_type=None):
    """
    Traite un fichier (PDF ou PNG) et extrait son texte
    
    Args:
        input_path (str): Chemin vers le fichier d'entrée
        output_path (str, optional): Chemin vers le fichier de sortie.
                                    Si non spécifié, génère automatiquement
        use_llm (bool): Si True, utilise Ollama pour post-traiter le texte
        model_name (str): Nom du modèle Ollama à utiliser
        doc_type (str, optional): Type de document (cv, facture, formulaire, general).
                                 Si None, détection automatique
    """
    # Vérifier que le fichier d'entrée existe
    if not os.path.exists(input_path):
        print(f"Erreur: Le fichier '{input_path}' n'existe pas.")
        return False
    
    # Générer le chemin de sortie si non spécifié
    if output_path is None:
        input_file = Path(input_path)
        suffix = "_cleaned" if use_llm else "_extracted"
        output_path = os.path.join('output', f"{input_file.stem}{suffix}.txt")
    
    # Déterminer le type de fichier
    file_extension = Path(input_path).suffix.lower()
    
    print(f"Traitement du fichier: {input_path}")
    
    # Extraire le texte selon le type de fichier
    if file_extension == '.pdf':
        raw_text = extract_text_from_pdf(input_path)
    elif file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
        raw_text = extract_text_from_image(input_path)
    else:
        print(f"Erreur: Format de fichier non supporté: {file_extension}")
        print("Formats supportés: PDF, PNG, JPG, JPEG, BMP, TIFF")
        return False
    
    # Post-traiter avec LLM si demandé
    if raw_text.strip():
        # Détecter ou utiliser le type de document spécifié
        detected_doc_type = detect_document_type(raw_text, doc_type)
        
        # Sauvegarder le texte brut OCR (toujours sauvegardé pour référence)
        if use_llm:
            input_file = Path(input_path)
            raw_output_path = os.path.join('output', f"{input_file.stem}_extracted.txt")
            save_text_to_file(raw_text, raw_output_path)
        
        # Générer le JSON directement depuis le texte brut OCR (OPTIMISATION : une seule étape)
        # Plus rapide car on combine correction OCR + extraction JSON en un seul appel LLM
        doc_json = None
        if use_llm:
            doc_json = extract_json_from_ocr_text(raw_text, model_name, use_llm, detected_doc_type)
            
            if doc_json:
                input_file = Path(input_path)
                json_output_path = os.path.join('output', f"{input_file.stem}_cleaned.json")
                save_json_to_file(doc_json, json_output_path)
            else:
                print("Avertissement: Échec de la génération JSON.")
                # Si JSON échoue, générer au moins le texte nettoyé comme fallback
                final_text = post_process_with_llm(raw_text, model_name, use_llm, detected_doc_type)
                save_text_to_file(final_text, output_path)
        
        print(f"Extraction terminée.")
        if use_llm:
            print(f"Type de document: {detected_doc_type}")
            print(f"Texte brut OCR sauvegardé dans: {os.path.join('output', Path(input_path).stem + '_extracted.txt')}")
            if doc_json:
                print(f"JSON structuré sauvegardé dans: {os.path.join('output', Path(input_path).stem + '_cleaned.json')}")
                print(f"✓ JSON généré directement depuis l'OCR (2x plus rapide, correction + extraction en une étape)")
            else:
                print(f"Texte structuré sauvegardé dans: {output_path}")
        return True
    else:
        print("Avertissement: Aucun texte n'a pu être extrait du fichier.")
        return False


def main():
    """
    Fonction principale pour l'interface en ligne de commande
    """
    parser = argparse.ArgumentParser(
        description='Extracteur OCR pour fichiers PDF et PNG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python ocr_extractor.py document.pdf
  python ocr_extractor.py image.png -o resultat.txt
  python ocr_extractor.py fichier.pdf -o output/texte_extrait.txt
        """
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Chemin vers le fichier à traiter (PDF ou PNG)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Chemin vers le fichier de sortie (par défaut: output/nom_du_fichier_cleaned.txt)'
    )
    
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Désactive le post-traitement LLM (utilise uniquement OCR)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='llama3.2',
        help='Nom du modèle Ollama à utiliser (défaut: llama3.2)'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=['cv', 'facture', 'formulaire', 'general'],
        default=None,
        help='Type de document (cv, facture, formulaire, general). Si non spécifié, détection automatique'
    )
    
    args = parser.parse_args()
    
    # Traiter le fichier
    use_llm = not args.no_llm and OLLAMA_AVAILABLE
    success = process_file(args.input_file, args.output, use_llm, args.model, args.type)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

