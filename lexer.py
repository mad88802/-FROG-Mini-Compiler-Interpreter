from tokens import TokenType, Token

# ==================== ÉTAPE 2: Définir les ensembles de caractères ====================
# Tous les mots-clés du langage FROG
KEYWORDS = {
    "FRG_Begin", "FRG_End", "FRG_Int", "FRG_Real", "FRG_Strg", 
    "FRG_Print", "If", "Else", "Begin", "End", "Repeat", "until"
}

OPERATORS = {
    ":=", "<=", ">=", "==", "!=",  
    "<", ">", "+", "-", "*", "/"   
}

SEPARATORS = {",", "[", "]", "(", ")", ":", ";"}


# ==================== ÉTAPE 3: Classe Lexer principale ====================
class Lexer:    
    def __init__(self, source_code):
       
        self.source = source_code
        self.pos = 0           # Position actuelle dans le source
        self.line = 1          # Numéro de ligne actuel
        self.tokens = []       # Liste des tokens générés
        self.errors = []       # Liste des erreurs lexicales
        
        # Pour suivre le début des tokens multi-caractères
        self.start = 0
    
    def tokenize(self):
        """
        Transforme tout le code source en liste de tokens
        
        Returns:
            tuple: (liste de tokens, liste d'erreurs)
        """
        print("Début de l'analyse lexicale...")
        
        # Tant qu'on n'a pas parcouru tout le source
        while self.pos < len(self.source):
            # Commencer un nouveau token
            self.start = self.pos
            self.scan_token()
        
        # Ajouter le token de fin de fichier
        self.tokens.append(Token(TokenType.EOF, "", self.line))
        
        print(f"Analyse terminée. {len(self.tokens)} tokens générés.")
        if self.errors:
            print(f"  {len(self.errors)} erreur(s) lexicale(s) trouvée(s)")
        
        return self.tokens, self.errors
    
    def scan_token(self):
        """Analyse un token à partir de la position actuelle"""
        ch = self.source[self.pos]
        
        # ==================== CAS 1: Espaces et sauts de ligne ====================
        if ch in ' \t':
            self.pos += 1
            return
        
        elif ch == '\n':
            self.line += 1
            self.pos += 1
            return
        
        # ==================== CAS 2: Commentaires (##) ====================
        elif ch == '#':
            self.handle_comment()
        
        # ==================== CAS 3: Nombres (entiers ou réels) ====================
        elif ch.isdigit():
            self.handle_number()
        
        # ==================== CAS 4: Chaînes de caractères ====================
        elif ch == '"':
            self.handle_string()
        
        # ==================== CAS 5: Identifiants et mots-clés ====================
        elif ch.isalpha() or ch == '_':
            self.handle_identifier()
        
        # ==================== CAS 6: Opérateurs et séparateurs ====================
        else:
            self.handle_operator_or_separator()
    
    def handle_comment(self):
        """Gère les commentaires (commencent par ##)"""
        # Vérifier si c'est un commentaire (##) ou juste un séparateur (#)
        if self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '#':
            # C'est un commentaire, on saute jusqu'à la fin de la ligne
            start_line = self.line
            while self.pos < len(self.source) and self.source[self.pos] != '\n':
                self.pos += 1
            
            # Extraire le texte du commentaire
            comment_text = self.source[self.start:self.pos].strip()
            self.tokens.append(Token(TokenType.COMMENT, comment_text, start_line))
        else:
            # C'est juste un end #
            self.tokens.append(Token(TokenType.END, '#', self.line))
            self.pos += 1
    

    def handle_number(self):
        """Gère les nombres entiers et réels"""
        # Lire tous les chiffres
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self.pos += 1
        
        # Vérifier si c'est un réel (avec point)
        if self.pos < len(self.source) and self.source[self.pos] == '.':
            self.pos += 1  # Manger le point
            
            # Vérifier qu'il y a des chiffres après le point
            if self.pos < len(self.source) and self.source[self.pos].isdigit():
                # Lire la partie décimale
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    self.pos += 1
                
                # C'est un nombre réel
                number_text = self.source[self.start:self.pos]
                self.tokens.append(Token(TokenType.REAL, number_text, self.line))
            else:
                # Point seul, erreur
                self.errors.append(f"Erreur lexicale ligne {self.line}: point décimal sans chiffres après")
                number_text = self.source[self.start:self.pos]
                self.tokens.append(Token(TokenType.NUMBER, number_text, self.line))
        else:
            # C'est un nombre entier
            number_text = self.source[self.start:self.pos]
            self.tokens.append(Token(TokenType.NUMBER, number_text, self.line))
    

    def handle_string(self):
        """Gère les chaînes de caractères entre guillemets"""
        self.pos += 1  # Sauter le guillemet ouvrant
        
        # Lire jusqu'au guillemet fermant
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            if self.source[self.pos] == '\n':
                self.errors.append(f"Erreur lexicale ligne {self.line}: chaîne non terminée")
                break
            self.pos += 1
        
        if self.pos >= len(self.source):
            self.errors.append(f"Erreur lexicale ligne {self.line}: chaîne non terminée à la fin du fichier")
            string_text = self.source[start:self.pos]
            self.tokens.append(Token(TokenType.STRING, string_text, self.line))
            return
        
        # Extraire le contenu de la chaîne
        string_text = self.source[start:self.pos]
        self.tokens.append(Token(TokenType.STRING, string_text, self.line))
        
        self.pos += 1  # Sauter le guillemet fermant
    

    def handle_identifier(self):
        """Gère les identifiants et mots-clés"""
        # Lire le mot complet (lettres, chiffres et underscores)
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.pos += 1
        
        identifier = self.source[self.start:self.pos]
        
        if not identifier:
            self.errors.append(f"Erreur lexicale ligne {self.line}: identifiant vide")
            return

        # Vérifier si c'est un mot-clé
        if identifier in KEYWORDS:
            self.tokens.append(Token(TokenType.KEYWORD, identifier, self.line))
        else:
            # Vérifier que l'identifiant commence bien par une lettre
            if identifier[0].isalpha():
                self.tokens.append(Token(TokenType.IDENTIFIER, identifier, self.line))
            else:
                self.errors.append(f"Erreur lexicale ligne {self.line}: identifiant doit commencer par une lettre: '{identifier}'")
    
    
    def handle_operator_or_separator(self):
        """Gère les opérateurs et séparateurs"""
        ch = self.source[self.pos]
        
        # ==================== ESSAYER LES OPÉRATEURS COMPOSÉS (2 caractères) ====================
        if self.pos + 1 < len(self.source):
            two_char = self.source[self.pos:self.pos + 2]
            if two_char in OPERATORS:
                self.tokens.append(Token(TokenType.OPERATOR, two_char, self.line))
                self.pos += 2
                return
        
        # ==================== ESSAYER LES OPÉRATEURS SIMPLES (1 caractère) ====================
        if ch in OPERATORS:
            self.tokens.append(Token(TokenType.OPERATOR, ch, self.line))
            self.pos += 1
            return
        
        # ==================== ESSAYER LES SÉPARATEURS ====================
        if ch in SEPARATORS:
            self.tokens.append(Token(TokenType.SEPARATOR, ch, self.line))
            self.pos += 1
            return
        
        # ==================== CARACTÈRE INCONNU ====================
        self.errors.append(f"Erreur lexicale ligne {self.line}: caractère inconnu '{ch}'")
        self.pos += 1  # Avancer pour éviter boucle infinie



# ==================== ÉTAPE 4: Exemple de test dans le main ====================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU LEXER FROG")
    print("=" * 60)
    
    # Exemple 1: Programme simple
    print("\n1. Test avec un programme simple:")
    print("-" * 40)
    
    code_simple = """FRG_Begin
FRG_Int x, y #
x := 10 #
y := x + 5 #
FRG_Print "Resultat:", y #
FRG_End"""
    
    print("Code source:")
    print(code_simple)
    print("\nAnalyse lexicale...")
    
    lexer1 = Lexer(code_simple)
    tokens1, errors1 = lexer1.tokenize()
    
    print("\nTokens generes:")
    for i, token in enumerate(tokens1):
        print(f"  {i:2d}: Ligne {token.line:2d} - {token}")
    
    if errors1:
        print("\nErreurs:")
        for error in errors1:
            print(f"  * {error}")
    
    # Exemple 2: Avec commentaire et réel
    print("\n\n2. Test avec commentaire et nombre reel:")
    print("-" * 40)
    
    code_complexe = """FRG_Begin
## Ceci est un commentaire
FRG_Real pi #
pi := 3.14 #
FRG_Print "Valeur de pi:", pi #
FRG_End"""
    
    print("Code source:")
    print(code_complexe)
    print("\nAnalyse lexicale...")
    
    lexer2 = Lexer(code_complexe)
    tokens2, errors2 = lexer2.tokenize()
    
    print("\nTokens generes:")
    for i, token in enumerate(tokens2):
        print(f"  {i:2d}: Ligne {token.line:2d} - {token}")
    
    # Exemple 3: Test avec erreurs
    print("\n\n3. Test avec erreurs intentionnelles:")
    print("-" * 40)
    
    code_erreurs = """FRG_Begin
FRG_Int 1var #  ERREUR: commence par chiffre
x := 10$ #      ERREUR: $ inconnu
"chaine         ERREUR: guillemet non ferme
FRG_End"""
    
    print("Code source (avec erreurs):")
    print(code_erreurs)
    print("\nAnalyse lexicale...")
    
    lexer3 = Lexer(code_erreurs)
    tokens3, errors3 = lexer3.tokenize()
    
    if errors3:
        print("\nErreurs detectees:")
        for error in errors3:
            print(f"  * {error}")
    
    # Résumé
    print("\n" + "=" * 60)
    print("RESUME DES TESTS")
    print("=" * 60)
    print(f"Test 1: {len(tokens1)} tokens, {len(errors1)} erreurs")
    print(f"Test 2: {len(tokens2)} tokens, {len(errors2)} erreurs")
    print(f"Test 3: {len(tokens3)} tokens, {len(errors3)} erreurs")
    
    # Menu interactif simple
    print("\n" + "=" * 60)
    print("TEST INTERACTIF")
    print("=" * 60)
    print("Tapez votre code FROG (tapez 'QUIT' pour sortir):")
    
    while True:
        print("\n" + "-" * 40)
        code_input = ""
        print("Entrez une ligne de code FROG:")
        line = input("> ")
        
        if line.upper() == "QUIT":
            print("Au revoir!")
            break
        
        code_input = line + "\n"
        
        # Pour tester plusieurs lignes
        print("Entrez une autre ligne (ou tapez 'END' pour analyser):")
        while True:
            next_line = input("> ")
            if next_line.upper() == "END":
                break
            code_input += next_line + "\n"
        
        lexer_test = Lexer(code_input)
        tokens_test, errors_test = lexer_test.tokenize()
        
        print("\nResultats:")
        print("-" * 20)
        for i, token in enumerate(tokens_test):
            print(f"{i:3d}: {token}")
        
        if errors_test:
            print("\n* Erreurs trouvees:")
            for error in errors_test:
                print(f"  {error}")