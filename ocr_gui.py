#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Graphique pour Ultimate OCR & LLM Parser
"""

import os
import sys
import json
import threading
import re
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

# Import de notre extracteur
from ocr_extractor import (
    SmartExtractor, 
    DocumentClassifier, 
    LLMOrchestrator,
    RegexBooster,
    merge_data
)

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class StdoutRedirector:
    """Redirige stdout/stderr vers un widget Tkinter"""
    def __init__(self, widget):
        self.widget = widget
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def write(self, message):
        if not message: return
        # Nettoyer codes ANSI (couleurs Rich)
        clean_msg = self.ansi_escape.sub('', message)
        
        def append():
            self.widget.configure(state="normal")
            self.widget.insert("end", clean_msg)
            self.widget.see("end")
            self.widget.configure(state="disabled")
        
        # Thread-safe update
        self.widget.after(0, append)

    def flush(self):
        pass

class OCRApp(ctk.CTk, TkinterDnD.DnDWrapper):

    """Application GUI pour OCR avec drag & drop"""
    
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre principale
        self.title("🔍 Ultimate OCR & LLM Parser")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Variables
        self.selected_file = None
        self.processing = False
        self.result_data = None
        
        # Configuration Drag & Drop
        self.TkdndVersion = TkinterDnD._require(self)
        
        # Création de l'interface
        self._create_widgets()
        
    def _create_widgets(self):
        """Création de tous les widgets de l'interface"""
        
        # === PANNEAU GAUCHE : Configuration ===
        self.left_frame = ctk.CTkFrame(self, corner_radius=10)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Titre
        title = ctk.CTkLabel(
            self.left_frame, 
            text="⚙️ Configuration",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(20, 10), padx=20)
        
        # Zone de drop
        self.drop_frame = ctk.CTkFrame(self.left_frame, corner_radius=10, fg_color="#2b2b2b")
        self.drop_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text="📁 Glissez un fichier ici\nou cliquez pour parcourir\n\n(PDF, PNG, JPG)",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        self.drop_label.pack(expand=True, pady=40)
        
        # Configuration Drag & Drop
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self._on_drop)
        self.drop_frame.bind('<Button-1>', lambda e: self._browse_file())
        self.drop_label.bind('<Button-1>', lambda e: self._browse_file())
        
        # Nom du fichier sélectionné
        self.file_label = ctk.CTkLabel(
            self.left_frame,
            text="Aucun fichier sélectionné",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        )
        self.file_label.pack(pady=5, padx=20)
        
        # Type de document
        ctk.CTkLabel(
            self.left_frame, 
            text="Type de document :",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(20, 5), padx=20, anchor="w")
        
        self.doc_type_var = ctk.StringVar(value="auto")
        doc_types = ["auto", "cv", "facture", "formulaire"]
        self.doc_type_menu = ctk.CTkOptionMenu(
            self.left_frame,
            values=doc_types,
            variable=self.doc_type_var,
            width=200
        )
        self.doc_type_menu.pack(pady=5, padx=20)
        
        # Modèle LLM
        ctk.CTkLabel(
            self.left_frame,
            text="Modèle LLM :",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(15, 5), padx=20, anchor="w")
        
        self.model_var = ctk.StringVar(value="llama3.2")
        models = ["llama3.2", "mistral"]
        self.model_menu = ctk.CTkOptionMenu(
            self.left_frame,
            values=models,
            variable=self.model_var,
            width=200
        )
        self.model_menu.pack(pady=5, padx=20)
        
        # Dossier de sortie
        ctk.CTkLabel(
            self.left_frame,
            text="Dossier de sortie :",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(15, 5), padx=20, anchor="w")
        
        self.output_var = ctk.StringVar(value="output")
        output_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        output_frame.pack(pady=5, padx=20)
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_var,
            width=140
        )
        self.output_entry.pack(side="left", padx=(0, 5))
        
        browse_output_btn = ctk.CTkButton(
            output_frame,
            text="📂",
            width=40,
            command=self._browse_output
        )
        browse_output_btn.pack(side="left")
        
        # Bouton de traitement
        self.process_btn = ctk.CTkButton(
            self.left_frame,
            text="🚀 Traiter le document",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            command=self._process_document,
            state="disabled"
        )
        self.process_btn.pack(pady=20, padx=20, fill="x")
        
        # Barre de progression
        self.progress = ctk.CTkProgressBar(self.left_frame, width=200)
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.set(0)
        
        # Status
        self.status_label = ctk.CTkLabel(
            self.left_frame,
            text="En attente...",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        self.status_label.pack(pady=5, padx=20)
        
        # === PANNEAU DROIT : Résultats ===
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        # Titre
        result_title = ctk.CTkLabel(
            self.right_frame,
            text="📊 Résultats",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        result_title.pack(pady=(20, 10), padx=20)
        
        # Zone de texte pour JSON
        self.result_text = ctk.CTkTextbox(
            self.right_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word"
        )
        self.result_text.pack(pady=10, padx=20, fill="both", expand=True)
        self.result_text.insert("1.0", "Les résultats apparaîtront ici...")
        self.result_text.configure(state="disabled")
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        action_frame.pack(pady=10, padx=20, fill="x")
        
        self.save_btn = ctk.CTkButton(
            action_frame,
            text="💾 Sauvegarder",
            command=self._save_result,
            state="disabled",
            width=140
        )
        self.save_btn.pack(side="left", padx=(0, 10))
        
        self.copy_btn = ctk.CTkButton(
            action_frame,
            text="📋 Copier",
            command=self._copy_result,
            state="disabled",
            width=140
        )
        self.copy_btn.pack(side="left", padx=(0, 10))
        
        self.clear_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Effacer",
            command=self._clear_result,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            width=140
        )
        self.clear_btn.pack(side="left")
        
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
    def _on_drop(self, event):
        """Gestion du drag & drop"""
        file_path = event.data
        # Nettoyer le chemin (enlever les accolades si présentes)
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self._load_file(file_path)
        
    def _browse_file(self):
        """Parcourir les fichiers"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un document",
            filetypes=[
                ("Tous les fichiers supportés", "*.pdf *.png *.jpg *.jpeg"),
                ("PDF", "*.pdf"),
                ("Images", "*.png *.jpg *.jpeg")
            ]
        )
        if file_path:
            self._load_file(file_path)
            
    def _load_file(self, file_path):
        """Charger un fichier"""
        path = Path(file_path)
        if not path.exists():
            messagebox.showerror("Erreur", "Le fichier n'existe pas !")
            return
            
        if path.suffix.lower() not in ['.pdf', '.png', '.jpg', '.jpeg']:
            messagebox.showerror("Erreur", "Format non supporté !")
            return
            
        self.selected_file = path
        self.file_label.configure(text=f"✓ {path.name}", text_color="#4caf50")
        self.process_btn.configure(state="normal")
        self.drop_label.configure(text=f"📄 {path.name}\n\nFichier chargé !", text_color="#4caf50")
        
    def _browse_output(self):
        """Parcourir les dossiers pour la sortie"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier de sortie")
        if folder:
            self.output_var.set(folder)
            
    def _process_document(self):
        """Traiter le document dans un thread séparé"""
        if self.processing:
            return
            
        if not self.selected_file:
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier !")
            return
            
        self.processing = True
        self.process_btn.configure(state="disabled")
        self.progress.set(0)
        self.status_label.configure(text="Traitement en cours...", text_color="#2196f3")
        
        # Reset text box for logs
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "Les résultats apparaîtront ici...\n") # Remettre le placeholder pour que le check fonctionne
        self.result_text.configure(state="disabled")
        
        # Lancer dans un thread pour ne pas bloquer l'interface
        thread = threading.Thread(target=self._run_ocr)
        thread.daemon = True
        thread.start()
        
        # Reset progress
        self.progress.set(0)
        
    def update_progress(self, current, message):
        """Callback pour mettre à jour la progression depuis le thread"""
        self.after(0, lambda: self.progress.set(current))
        self.after(0, lambda: self.status_label.configure(text=message))
        
        # Afficher aussi dans la zone de logs (panneau droit)
        def log_to_text():
            self.result_text.configure(state="normal")
            # Effacer le placeholder si c'est le premier message
            if self.result_text.get("1.0", "end-1c").strip() == "Les résultats apparaîtront ici...":
                self.result_text.delete("1.0", "end")
            
            # Ajouter le log avec timestamp simule ou pourcentage
            self.result_text.insert("end", f"➤ [{int(current*100)}%] {message}\n")
            self.result_text.see("end") # Auto-scroll
            self.result_text.configure(state="disabled")
            
        self.after(0, log_to_text)
            
    def _run_ocr(self):
        """Exécution du traitement OCR"""
        # Redirection des LOGS vers l'interface
        import sys
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        sys.stdout = StdoutRedirector(self.result_text)
        sys.stderr = StdoutRedirector(self.result_text)
        
        try:
            print("-" * 50)
            print(f"🚀 DOSSIER : {self.output_var.get()}")
            print(f"📄 FICHIER : {self.selected_file.name}")
            print("-" * 50)
            
            # 1. Extraction
            self._update_status("Extraction du texte...")
            extractor = SmartExtractor()
            # On passe notre fonction de callback
            raw_text = extractor.extract(self.selected_file, progress_callback=self.update_progress)
            
            # Fin extraction -> 80%
            self.update_progress(0.8, "Analyse sémantique...")
            
            # 2. Détection du type
            self._update_status("Détection du type de document...")
            doc_type = self.doc_type_var.get()
            if doc_type == "auto":
                classifier = DocumentClassifier()
                doc_type = classifier.detect(raw_text)
            
            # 3. Analyse LLM
            self._update_status(f"Analyse LLM ({doc_type})...")
            llm = LLMOrchestrator(model=self.model_var.get())
            data = llm.analyze(raw_text, doc_type)
            
            # 4. Enrichissement
            self._update_status("Enrichissement des données...")
            final_data = merge_data(data, raw_text, doc_type)
            
            # 5. Sauvegarde
            output_dir = Path(self.output_var.get())
            output_dir.mkdir(exist_ok=True, parents=True)
            
            out_file = output_dir / f"{self.selected_file.stem}_data.json"
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False)
            
            # Afficher le résultat
            self.result_data = final_data
            self._display_result(final_data, doc_type)
            
            self._update_status(f"✓ Terminé ! ({out_file.name})", "#4caf50")
            self.progress.set(1.0)
            
        except Exception as e:
            self._update_status(f"Erreur : {str(e)}", "#f44336")
            messagebox.showerror("Erreur", f"Erreur lors du traitement :\n{str(e)}")
            self.progress.set(0)
            
            self.progress.set(0)
            
        finally:
            # Restaurer stdout
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            self.processing = False
            self.process_btn.configure(state="normal")
            
    def _update_status(self, message, color="#2196f3"):
        """Mettre à jour le status (thread-safe)"""
        self.after(0, lambda: self.status_label.configure(text=message, text_color=color))
        
    def _display_result(self, data, doc_type):
        """Afficher le résultat JSON"""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        def update_ui():
            self.result_text.configure(state="normal")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"Type détecté : {doc_type.upper()}\n\n{json_str}")
            self.result_text.configure(state="disabled")
            self.save_btn.configure(state="normal")
            self.copy_btn.configure(state="normal")
            
        self.after(0, update_ui)
        
    def _save_result(self):
        """Sauvegarder le résultat"""
        if not self.result_data:
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Sauvegarder le résultat",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.result_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Succès", "Résultat sauvegardé !")
            
    def _copy_result(self):
        """Copier le résultat dans le presse-papier"""
        if not self.result_data:
            return
            
        json_str = json.dumps(self.result_data, indent=2, ensure_ascii=False)
        self.clipboard_clear()
        self.clipboard_append(json_str)
        messagebox.showinfo("Succès", "Résultat copié dans le presse-papier !")
        
    def _clear_result(self):
        """Effacer les résultats"""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "Les résultats apparaîtront ici...")
        self.result_text.configure(state="disabled")
        self.result_data = None
        self.save_btn.configure(state="disabled")
        self.copy_btn.configure(state="disabled")
        self.selected_file = None
        self.file_label.configure(text="Aucun fichier sélectionné", text_color="#666666")
        self.drop_label.configure(
            text="📁 Glissez un fichier ici\nou cliquez pour parcourir\n\n(PDF, PNG, JPG)",
            text_color="#888888"
        )
        self.process_btn.configure(state="disabled")
        self.progress.set(0)
        self.status_label.configure(text="En attente...", text_color="#888888")


def main():
    """Point d'entrée de l'application"""
    app = OCRApp()
    app.mainloop()


if __name__ == "__main__":
    main()
