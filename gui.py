import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
from lexer import Lexer
from parse import Parser
from semantique import SemanticAnalyzer
from interpreteur import Interpreter

class FrogCompilerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MINI COMPILATEUR FROG")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.source_file_path = ""
        self.tokens = []
        self.parser_errors = []
        self.semantic_errors = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Titre principal
        title_label = tk.Label(
            self.root, 
            text="MINI COMPILATEUR FROG",
            font=("Arial", 20, "bold"),
            bg='#4CAF50',
            fg='white',
            padx=10,
            pady=10
        )
        title_label.pack(fill=tk.X)
        
        # Frame pour charger le fichier
        file_frame = tk.Frame(self.root, bg='#f0f0f0')
        file_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # Bouton Charger Fichier
        load_btn = tk.Button(
            file_frame,
            text="Charger le fichier source",
            command=self.load_file,
            bg='#2196F3',
            fg='white',
            font=("Arial", 11),
            padx=15,
            pady=5
        )
        load_btn.pack(side=tk.LEFT)
        
        # Label pour afficher le chemin du fichier
        self.file_path_label = tk.Label(
            file_frame,
            text="Aucun fichier chargé",
            bg='#f0f0f0',
            font=("Arial", 10),
            anchor='w',
            width=60
        )
        self.file_path_label.pack(side=tk.LEFT, padx=10)
        
        # Frame pour les boutons d'analyse
        analysis_frame = tk.Frame(self.root, bg='#f0f0f0')
        analysis_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # Boutons d'analyse
        btn_lexical = tk.Button(
            analysis_frame,
            text="ANALYSE LEXICALE",
            command=self.run_lexical_analysis,
            bg='#FF9800',
            fg='white',
            font=("Arial", 12, "bold"),
            width=20,
            pady=8
        )
        btn_lexical.pack(side=tk.LEFT, padx=5)
        
        btn_syntax = tk.Button(
            analysis_frame,
            text="ANALYSE SYNTAXIQUE",
            command=self.run_syntax_analysis,
            bg='#9C27B0',
            fg='white',
            font=("Arial", 12, "bold"),
            width=20,
            pady=8
        )
        btn_syntax.pack(side=tk.LEFT, padx=5)
        
        btn_semantic = tk.Button(
            analysis_frame,
            text="ANALYSE SÉMANTIQUE",
            command=self.run_semantic_analysis,
            bg='#F44336',
            fg='white',
            font=("Arial", 12, "bold"),
            width=20,
            pady=8
        )
        btn_semantic.pack(side=tk.LEFT, padx=5)
        
        # Bouton d'exécution
        btn_execute = tk.Button(
            analysis_frame,
            text="EXÉCUTER LE PROGRAMME",
            command=self.execute_program,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 12, "bold"),
            width=20,
            pady=8
        )
        btn_execute.pack(side=tk.LEFT, padx=5)
        
        # Frame pour le code source
        code_frame = tk.Frame(self.root, bg='#f0f0f0')
        code_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        # Label pour le code source
        tk.Label(
            code_frame,
            text="CODE SOURCE:",
            font=("Arial", 11, "bold"),
            bg='#f0f0f0'
        ).pack(anchor='w')
        
        # Zone de texte pour afficher le code source
        self.source_text = scrolledtext.ScrolledText(
            code_frame,
            height=15,
            width=80,
            font=("Courier New", 10),
            bg='#FAFAFA',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.source_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame pour les résultats
        result_frame = tk.Frame(self.root, bg='#f0f0f0')
        result_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        # Notebook pour les différents résultats
        self.create_results_tabs(result_frame)
        
        # Barre de statut
        self.status_bar = tk.Label(
            self.root,
            text="Prêt",
            bg='#4CAF50',
            fg='white',
            font=("Arial", 10),
            anchor='w',
            relief=tk.SUNKEN
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_results_tabs(self, parent):
        # Frame pour les onglets
        tabs_frame = tk.Frame(parent, bg='#f0f0f0')
        tabs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Onglets
        self.results_notebook = tk.ttk.Notebook(tabs_frame)
        
        # Onglet 1: Résultats d'analyse
        tab_results = tk.Frame(self.results_notebook, bg='#f0f0f0')
        self.results_notebook.add(tab_results, text="Résultats d'analyse")
        
        self.analysis_text = scrolledtext.ScrolledText(
            tab_results,
            height=10,
            font=("Courier New", 10),
            bg='white'
        )
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 2: Sortie d'exécution
        tab_output = tk.Frame(self.results_notebook, bg='#f0f0f0')
        self.results_notebook.add(tab_output, text="Sortie d'exécution")
        
        self.output_text = scrolledtext.ScrolledText(
            tab_output,
            height=10,
            font=("Courier New", 10),
            bg='white'
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 3: Tokens
        tab_tokens = tk.Frame(self.results_notebook, bg='#f0f0f0')
        self.results_notebook.add(tab_tokens, text="Tokens")
        
        self.tokens_text = scrolledtext.ScrolledText(
            tab_tokens,
            height=10,
            font=("Courier New", 9),
            bg='white'
        )
        self.tokens_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 4: Table des symboles
        tab_symbols = tk.Frame(self.results_notebook, bg='#f0f0f0')
        self.results_notebook.add(tab_symbols, text="Table des symboles")
        
        self.symbols_text = scrolledtext.ScrolledText(
            tab_symbols,
            height=10,
            font=("Courier New", 9),
            bg='white'
        )
        self.symbols_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
    
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier source FROG",
            filetypes=[("Fichiers FROG", "*.frg"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            self.source_file_path = file_path
            self.file_path_label.config(text=file_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    source_code = file.read()
                
                # Afficher le code source
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(1.0, source_code)
                
                # Effacer les résultats précédents
                self.clear_results()
                
                self.update_status(f"Fichier chargé: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement du fichier:\n{str(e)}")
    
    def get_source_code(self):
        """Récupère le code source depuis la zone de texte"""
        return self.source_text.get(1.0, tk.END).strip()
    
    def clear_results(self):
        """Efface tous les résultats"""
        self.analysis_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.tokens_text.delete(1.0, tk.END)
        self.symbols_text.delete(1.0, tk.END)
        self.tokens = []
        self.parser_errors = []
        self.semantic_errors = []
    
    def run_lexical_analysis(self):
        """Exécute l'analyse lexicale"""
        source_code = self.get_source_code()
        if not source_code:
            messagebox.showwarning("Avertissement", "Aucun code source à analyser!")
            return
        
        self.clear_results()
        self.update_status("Analyse lexicale en cours...")
        
        try:
            # Analyse lexicale
            lexer = Lexer(source_code)
            self.tokens, errors = lexer.tokenize()
            
            # Afficher les tokens
            self.tokens_text.delete(1.0, tk.END)
            for i, token in enumerate(self.tokens):
                if token.type.name != "EOF":
                    self.tokens_text.insert(tk.END, f"{i:3d}: Ligne {token.line:2d} - {token}\n")
            
            # Afficher les résultats
            self.analysis_text.delete(1.0, tk.END)
            if errors:
                self.analysis_text.insert(tk.END, "=== ERREURS LEXICALES ===\n")
                for error in errors:
                    self.analysis_text.insert(tk.END, f"• {error}\n")
                self.analysis_text.insert(tk.END, f"\nTotal: {len(errors)} erreur(s)")
                self.update_status(f"Analyse lexicale terminée - {len(errors)} erreur(s) trouvée(s)")
            else:
                self.analysis_text.insert(tk.END, "✓ Analyse lexicale réussie !\n")
                self.analysis_text.insert(tk.END, f"✓ {len(self.tokens)} token(s) généré(s)")
                self.update_status("Analyse lexicale réussie !")
            
            # Basculer vers l'onglet des résultats
            self.results_notebook.select(0)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse lexicale:\n{str(e)}")
            self.update_status("Erreur lors de l'analyse lexicale")
    
    def run_syntax_analysis(self):
        """Exécute l'analyse syntaxique"""
        if not self.tokens:
            messagebox.showwarning("Avertissement", "Veuillez d'abord effectuer l'analyse lexicale!")
            return
        
        self.update_status("Analyse syntaxique en cours...")
        
        try:
            # Analyse syntaxique
            parser = Parser(self.tokens)
            self.parser_errors = parser.parse()
            
            # Afficher les résultats
            self.analysis_text.delete(1.0, tk.END)
            if self.parser_errors:
                self.analysis_text.insert(tk.END, "=== ERREURS SYNTAXIQUES ===\n")
                for error in self.parser_errors:
                    self.analysis_text.insert(tk.END, f"• {error}\n")
                self.analysis_text.insert(tk.END, f"\nTotal: {len(self.parser_errors)} erreur(s)")
                self.update_status(f"Analyse syntaxique terminée - {len(self.parser_errors)} erreur(s)")
            else:
                self.analysis_text.insert(tk.END, "✓ Analyse syntaxique réussie !\n")
                self.analysis_text.insert(tk.END, "✓ Programme syntaxiquement correct")
                self.update_status("Analyse syntaxique réussie !")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse syntaxique:\n{str(e)}")
            self.update_status("Erreur lors de l'analyse syntaxique")
    
    def run_semantic_analysis(self):
        """Exécute l'analyse sémantique"""
        if not self.tokens:
            messagebox.showwarning("Avertissement", "Veuillez d'abord effectuer l'analyse lexicale!")
            return
        
        self.update_status("Analyse sémantique en cours...")
        
        try:
            # Analyse sémantique
            analyzer = SemanticAnalyzer(self.tokens)
            self.semantic_errors = analyzer.analyze()
            
            # Afficher la table des symboles
            symbol_table = analyzer.get_symbol_table()
            self.symbols_text.delete(1.0, tk.END)
            if symbol_table:
                self.symbols_text.insert(tk.END, "=== TABLE DES SYMBOLES ===\n\n")
                for name, info in symbol_table.items():
                    init = "✓" if info["initialized"] else "✗"
                    self.symbols_text.insert(tk.END, f"• {name}: type={info['type']}, ligne={info['line']}, initialisée={init}\n")
            
            # Afficher les résultats
            self.analysis_text.delete(1.0, tk.END)
            if self.semantic_errors:
                self.analysis_text.insert(tk.END, "=== ERREURS SÉMANTIQUES ===\n")
                for error in self.semantic_errors:
                    self.analysis_text.insert(tk.END, f"• {error}\n")
                self.analysis_text.insert(tk.END, f"\nTotal: {len(self.semantic_errors)} erreur(s)")
                self.update_status(f"Analyse sémantique terminée - {len(self.semantic_errors)} erreur(s)")
            else:
                self.analysis_text.insert(tk.END, "✓ Analyse sémantique réussie !\n")
                self.analysis_text.insert(tk.END, "✓ Programme sémantiquement correct")
                self.update_status("Analyse sémantique réussie !")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse sémantique:\n{str(e)}")
            self.update_status("Erreur lors de l'analyse sémantique")
    
    def execute_program(self):
        """Exécute le programme FROG"""
        source_code = self.get_source_code()
        if not source_code:
            messagebox.showwarning("Avertissement", "Aucun code source à exécuter!")
            return
        
        self.update_status("Exécution du programme en cours...")
        
        try:
            # Première étape: analyse lexicale
            lexer = Lexer(source_code)
            tokens, lex_errors = lexer.tokenize()
            
            if lex_errors:
                messagebox.showwarning("Erreurs lexicales", 
                    "Des erreurs lexicales empêchent l'exécution!\nVeuillez corriger les erreurs d'abord.")
                return
            
            # Deuxième étape: analyse syntaxique
            parser = Parser(tokens)
            parser_errors = parser.parse()
            
            if parser_errors:
                messagebox.showwarning("Erreurs syntaxiques", 
                    "Des erreurs syntaxiques empêchent l'exécution!\nVeuillez corriger les erreurs d'abord.")
                return
            
            # Troisième étape: analyse sémantique
            analyzer = SemanticAnalyzer(tokens)
            semantic_errors = analyzer.analyze()
            
            if semantic_errors:
                messagebox.showwarning("Erreurs sémantiques", 
                    "Des erreurs sémantiques empêchent l'exécution!\nVeuillez corriger les erreurs d'abord.")
                return
            
            # Si toutes les analyses sont OK, exécuter
            interpreter = Interpreter(tokens)
            interpreter.run()
            
            # Afficher les résultats
            self.output_text.delete(1.0, tk.END)
            if interpreter.output:
                self.output_text.insert(tk.END, "=== RÉSULTATS D'EXÉCUTION ===\n\n")
                for line in interpreter.output:
                    self.output_text.insert(tk.END, f"{line}\n")
            else:
                self.output_text.insert(tk.END, "Programme exécuté avec succès.\n(Aucune sortie FRG_Print)")
            
            # Basculer vers l'onglet de sortie
            self.results_notebook.select(1)
            
            self.update_status("Programme exécuté avec succès !")
            
        except Exception as e:
            messagebox.showerror("Erreur d'exécution", f"Erreur lors de l'exécution:\n{str(e)}")
            self.update_status("Erreur lors de l'exécution")
    
    def update_status(self, message):
        """Met à jour la barre de statut"""
        self.status_bar.config(text=f"  {message}")
        self.root.update()
    
    def run(self):
        """Lance l'interface graphique"""
        self.root.mainloop()

# Point d'entrée principal
if __name__ == "__main__":
    # Import tkinter.ttk pour le Notebook
    import tkinter.ttk as ttk
    
    app = FrogCompilerGUI()
    app.run()