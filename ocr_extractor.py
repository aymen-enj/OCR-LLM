#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultimate OCR & LLM Parser (v3.3 - Auto-Detection Enabled)
"""

import os
import sys
import re
import json
import argparse
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
from collections import Counter

# --- DEPENDANCES ---
try:
    import pymupdf4llm
    import fitz  # PyMuPDF
    from PIL import Image, ImageEnhance
    import pytesseract
    from pdf2image import convert_from_path
    import cv2
    import numpy as np
    import ollama
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.json import JSON
    from rich.panel import Panel
    from rich.progress import track
except ImportError as e:
    sys.exit(f"❌ Dépendances manquantes : pip install pymupdf4llm pymupdf pytesseract pdf2image pillow ollama opencv-python-headless numpy rich")

# --- CONFIG ---
console = Console()
logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", 
    handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
)
logger = logging.getLogger("ocr_v3_3")

if os.name == 'nt':
    possibles = [r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]
    for p in possibles:
        if os.path.exists(p): pytesseract.pytesseract.tesseract_cmd = p; break

# --- NOUVELLE CLASSE DE DETECTION ---
class DocumentClassifier:
    """Algorithme heuristique pour deviner le type de document"""
    
    def detect(self, text: str) -> str:
        text = text.lower()
        
        # Mots-clés pondérés
        keywords = {
            "cv": [
                "curriculum", "expérience", "experience", "formation", "éducation", 
                "education", "compétences", "skills", "langues", "profil", "hobbies", 
                "loisirs", "stage", "freelance", "bachelor", "master", "diplôme"
            ],
            "facture": [
                "facture", "invoice", "devis", "tva", "ht", "ttc", "total", 
                "siret", "siren", "iban", "bic", "paiement", "échéance", "montant", 
                "prix unitaire", "qty", "quantité", "article"
            ],
            "formulaire": [
                "formulaire", "cerfa", "demande de", "je soussigné", "signature", 
                "fait à", "le :", "cocher la case", "réservé à l'administration", 
                "numéro de dossier", "déclaration", "attestation", "nom :", "prénom :"
            ]
        }
        
        scores = Counter()
        
        for category, words in keywords.items():
            for word in words:
                # On compte les occurrences (max 5 points par mot pour éviter le spam)
                count = text.count(word)
                scores[category] += min(count, 5) 
        
        # Bonus contextuels
        if "total" in text and ("€" in text or "$" in text or "dhs" in text):
            scores["facture"] += 5
        
        if "linkedin.com" in text or "github.com" in text:
            scores["cv"] += 5

        best_match = scores.most_common(1)[0]
        
        # Seuil de confiance minimal
        if best_match[1] < 2:
            return "generique"
            
        return best_match[0]

class RegexBooster:
    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, Any]:
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        
        phone_pattern = r'(?:\+33|0|\+212)\s*[1-9](?:[\s.-]*\d{2}){4}'
        phones = re.findall(phone_pattern, text)
        
        linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
        linkedins = re.findall(linkedin_pattern, text)

        return {
            "email": emails[0] if emails else None,
            "telephone": phones[0] if phones else None,
            "linkedin": linkedins[0] if linkedins else None
        }

class ImageProcessor:
    def preprocess_for_ocr(self, img_pil: Image.Image) -> Image.Image:
        img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        coords = np.column_stack(np.where(gray > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45: angle = -(90 + angle)
        else: angle = -angle
        if abs(angle) > 0.5:
            (h, w) = img.shape[:2]
            M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
            img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        pil_img = Image.fromarray(gray)
        enhancer = ImageEnhance.Contrast(pil_img)
        return enhancer.enhance(1.6)

class SmartExtractor:
    def __init__(self):
        self.img_processor = ImageProcessor()
    
    def extract(self, file_path: Path) -> str:
        ext = file_path.suffix.lower()
        if ext == '.pdf': return self._handle_pdf(file_path)
        elif ext in ['.jpg', '.png', '.jpeg']: return self._handle_image(file_path)
        else: raise ValueError(f"Format non supporté: {ext}")

    def _handle_pdf(self, pdf_path: Path) -> str:
        try:
            md_text = pymupdf4llm.to_markdown(str(pdf_path))
            if len(re.sub(r'\s+', '', md_text)) > 50:
                return f"--- CONTENU MARKDOWN ---\n{md_text}"
            return self._ocr_fallback(pdf_path)
        except Exception:
            return self._ocr_fallback(pdf_path)

    def _ocr_fallback(self, pdf_path: Path) -> str:
        logger.warning("Mode OCR activé (PDF Image)")
        images = convert_from_path(str(pdf_path), dpi=300)
        full_text = []
        for i, img in enumerate(track(images, description="OCR en cours...")):
            processed = self.img_processor.preprocess_for_ocr(img)
            txt = pytesseract.image_to_string(processed, lang='fra+eng', config='--psm 4')
            full_text.append(f"## PAGE {i+1}\n{txt}")
        return "\n".join(full_text)

    def _handle_image(self, img_path: Path) -> str:
        return pytesseract.image_to_string(Image.open(img_path), lang='fra+eng')

class LLMOrchestrator:
    def __init__(self, model: str):
        self.model = model

    def analyze(self, text: str, doc_type: str) -> Dict:
        # 1. Selection du Schéma
        schemas = {
            "cv": {
                "candidat": {"nom": "A déduire", "email": "", "telephone": "", "liens": []},
                "profil_synthese": "Copier le texte d'intro",
                "competences": {"langages": [], "outils": [], "soft_skills": []},
                "experience": [{"poste": "", "entreprise": "", "dates": "", "missions": []}],
                "education": [{"diplome": "", "ecole": "", "annee": ""}]
            },
            "facture": {
                "document": {"type": "Facture/Devis", "numero": "", "date_emission": ""},
                "emetteur": {"nom": "", "adresse": "", "siret": "", "iban": ""},
                "client": {"nom": "", "adresse": ""},
                "articles": [{"description": "", "qte": 0, "prix_unitaire": 0, "total_ligne": 0}],
                "totaux": {"total_ht": 0.0, "total_tva": 0.0, "total_ttc": 0.0, "devise": "EUR/USD/MAD"}
            },
            "formulaire": {
                "titre_formulaire": "",
                "champs_reemplis": [{"label": "Ex: Nom", "valeur": "Ex: Dupont"}],
                "cases_cochees": ["Liste des labels des cases cochées (ex: 'Sexe M')"],
                "blocs_texte_libre": [],
                "statut_signature": "Signé / Non Signé"
            },
            "generique": {
                "resume": "Résumé global",
                "entites_cles": [],
                "dates": []
            }
        }
        
        target_schema = schemas.get(doc_type, schemas["generique"])
        
        # 2. Prompt Dynamique
        prompt = f"""
        Analyse ce document MARKDOWN. Type détecté : {doc_type.upper()}.
        
        OBJECTIF : Extraire les données en JSON strict.
        
        RÈGLES SPÉCIFIQUES {doc_type.upper()} :
        """
        
        if doc_type == "cv":
            prompt += "\n- Cherche le profil complet, les compétences techniques précises et détaille les expériences."
        elif doc_type == "facture":
            prompt += "\n- Cherche les montants HT/TTC, le numéro de facture et les lignes d'articles. Convertis les nombres (ex: 10,00 -> 10.00)."
        elif doc_type == "formulaire":
            prompt += "\n- Associe chaque question à sa réponse. Identifie les cases marquées par [x] ou X. Récupère le texte manuscrit."
            
        prompt += f"""
        
        SCHEMA CIBLE :
        {json.dumps(target_schema, ensure_ascii=False)}
        
        DOCUMENT :
        {text[:25000]}
        """
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                format="json",
                options={"temperature": 0.0, "num_ctx": 8192}
            )
            clean_json = re.sub(r'```json\s*', '', response['response']).strip()
            clean_json = re.sub(r'```\s*$', '', clean_json).strip()
            return json.loads(clean_json)
        except Exception as e:
            return {"error": str(e)}

def merge_data(llm_data: Dict, raw_text: str, doc_type: str) -> Dict:
    # Boost Regex appliqué à tous les types (utile pour email/tel facture aussi)
    reg = RegexBooster.extract_contact_info(raw_text)
    
    # Injection conditionnelle selon la structure
    if doc_type == "cv" and "candidat" in llm_data:
        c = llm_data["candidat"]
        if reg["email"] and "@" not in c.get("email", ""): c["email"] = reg["email"]
        if reg["telephone"] and not c.get("telephone"): c["telephone"] = reg["telephone"]
    
    elif doc_type == "facture" and "emetteur" in llm_data:
        # Parfois l'IBAN est manqué par le LLM
        iban_match = re.search(r'[A-Z]{2}\d{2}[a-zA-Z0-9]{1,30}', raw_text.replace(" ", ""))
        if iban_match and not llm_data["emetteur"].get("iban"):
            llm_data["emetteur"]["iban"] = iban_match.group(0)

    return llm_data

def main():
    parser = argparse.ArgumentParser(description="OCR Extractor v3.3")
    parser.add_argument("input", type=Path, help="Fichier d'entrée")
    # Modification ici : 'auto' est le defaut, mais on peut forcer
    parser.add_argument("--type", choices=['auto', 'cv', 'facture', 'formulaire'], default='auto')
    parser.add_argument("--model", default="llama3.2", help="Modèle Ollama")
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    
    if not args.input.exists(): return console.print("[red]Fichier introuvable[/red]")
    args.output.mkdir(exist_ok=True, parents=True)

    # 1. Extraction
    ext = SmartExtractor()
    start = time.time()
    raw_md = ext.extract(args.input)
    
    # 2. Détection du type
    detected_type = args.type
    if args.type == 'auto':
        classifier = DocumentClassifier()
        detected_type = classifier.detect(raw_md)
        console.print(f"🤖 Type détecté : [bold cyan]{detected_type.upper()}[/bold cyan]")
    else:
        console.print(f"⚙️ Type forcé : [bold magenta]{detected_type.upper()}[/bold magenta]")

    # 3. Analyse LLM
    llm = LLMOrchestrator(model=args.model)
    with console.status(f"Parsing en tant que {detected_type}...", spinner="bouncingBar"):
        data = llm.analyze(raw_md, detected_type)
    
    # 4. Correction & Sauvegarde
    final_data = merge_data(data, raw_md, detected_type)
    out_file = args.output / f"{args.input.stem}_data.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    console.print(Panel(JSON(json.dumps(final_data, ensure_ascii=False)), title=f"Résultat ({detected_type})", border_style="green"))
    console.print(f"✅ Terminé en {time.time()-start:.2f}s")

if __name__ == "__main__":
    main()