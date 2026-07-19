# ==================== ANALYSEUR SÉMANTIQUE ====================
from tokens import TokenType, Token

class SemanticAnalyzer:
    """Analyseur sémantique - vérifie la cohérence des types et déclarations"""
    
    def __init__(self, tokens):
        """
        Initialise l'analyseur sémantique
        
        Args:
            tokens: Liste de tokens déjà analysés syntaxiquement
        """
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else Token(TokenType.EOF, "", -1)
        
        # Table des symboles: {nom: {"type": str, "line": int, "initialized": bool}}
        self.symbol_table = {}
        
        # Liste des erreurs sémantiques
        self.errors = []
        
        # Types FROG
        self.frog_types = {
            "FRG_Int": "int",
            "FRG_Real": "real", 
            "FRG_Strg": "string"
        }
    
    def analyze(self):
        """
        Effectue l'analyse sémantique complète
        
        Returns:
            list: Liste des erreurs sémantiques (vide si aucune erreur)
        """
        print("\n" + "=" * 60)
        print("ANALYSE SÉMANTIQUE")
        print("=" * 60)
        
        # Premier passage: collecter toutes les déclarations
        self.collect_declarations()
        
        # Réinitialiser pour le deuxième passage
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else Token(TokenType.EOF, "", -1)
        
        # Deuxième passage: vérifier les utilisations
        self.check_usage()
        
        print(f"Analyse terminée. {len(self.errors)} erreur(s) sémantique(s) trouvée(s).")
        return self.errors
    
    # ==================== MÉTHODES AUXILIAIRES ====================
    
    def eat(self):
        """Avance d'un token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token(TokenType.EOF, "", -1)
    
    def peek(self):
        """Regarde le prochain token sans consommer"""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TokenType.EOF, "", -1)
    
    def get_token_type(self, token):
        """Retourne le type FROG d'un token"""
        if token.type == TokenType.NUMBER:
            return "int"
        elif token.type == TokenType.REAL:
            return "real"
        elif token.type == TokenType.STRING:
            return "string"
        elif token.type == TokenType.IDENTIFIER:
            if token.value in self.symbol_table:
                return self.symbol_table[token.value]["type"]
            return "unknown"
        return "unknown"
    
    def is_type_compatible(self, type1, type2, operation=":="):
        """
        Vérifie si deux types sont compatibles
        
        Règles FROG:
        - int → real : ✓ (conversion implicite)
        - real → int : ✗ (perte de précision)
        - string avec autre : ✗ (sauf string + string)
        """
        if type1 == type2:
            return True
        
        # Conversions autorisées
        if operation == ":=":  # Affectation
            if type1 == "real" and type2 == "int":
                return True  # int → real autorisé
            if type1 == "string" and type2 == "string":
                return True
        
        # Opérations arithmétiques
        if operation in {"+", "-", "*", "/"}:
            if {type1, type2} <= {"int", "real"}:  # Les deux sont int ou real
                return True
        
        # Opérations de comparaison
        if operation in {"<=", ">=", "==", "!=", "<", ">"}:
            if {type1, type2} <= {"int", "real"}:
                return True
        
        return False
    
    # ==================== COLLECTE DES DÉCLARATIONS ====================
    
    def collect_declarations(self):
        """Premier passage: collecte toutes les déclarations"""
        print("Collecte des déclarations...")
        
        while self.current_token.type != TokenType.EOF:
            if self.current_token.value in {"FRG_Int", "FRG_Real", "FRG_Strg"}:
                self.process_declaration()
            else:
                self.eat()
    
    def process_declaration(self):
        """Traite une déclaration (FRG_Int x, y #)"""
        # Type de la déclaration
        frog_type = self.current_token.value  # FRG_Int, FRG_Real, FRG_Strg
        var_type = self.frog_types[frog_type]
        line = self.current_token.line
        
        self.eat()  # Consommer le type
        
        # Premier identifiant
        if self.current_token.type == TokenType.IDENTIFIER:
            var_name = self.current_token.value
            
            # Vérifier si déjà déclaré
            if var_name in self.symbol_table:
                self.errors.append(f"Erreur sémantique ligne {line}: variable '{var_name}' déjà déclarée")
            else:
                self.symbol_table[var_name] = {
                    "type": var_type,
                    "line": line,
                    "initialized": False
                }
                print(f"  Déclaré: {var_name} ({var_type})")
            
            self.eat()
        
        # Identifiants supplémentaires
        while self.current_token.value == ",":
            self.eat()  # ,
            
            if self.current_token.type == TokenType.IDENTIFIER:
                var_name = self.current_token.value
                
                if var_name in self.symbol_table:
                    self.errors.append(f"Erreur sémantique ligne {line}: variable '{var_name}' déjà déclarée")
                else:
                    self.symbol_table[var_name] = {
                        "type": var_type,
                        "line": line,
                        "initialized": False
                    }
                    print(f"  Déclaré: {var_name} ({var_type})")
                
                self.eat()
        
        # Fin d'instruction
        if self.current_token.type== TokenType.END:
            self.eat()
    
    # ==================== VÉRIFICATION DES UTILISATIONS ====================
    
    def check_usage(self):
        """Deuxième passage: vérifie toutes les utilisations"""
        print("Vérification des utilisations...")
        
        while self.current_token.type != TokenType.EOF:
            token_val = self.current_token.value
            
            if token_val in {"FRG_Int", "FRG_Real", "FRG_Strg"}:
                self.skip_declaration()
            
            elif token_val == "FRG_Print":
                self.check_print()
            
            elif token_val == "If":
                self.check_if()
            
            elif token_val == "Repeat":
                self.check_repeat()
            
            elif token_val == "Begin":
                self.eat()  # Begin
                while self.current_token.value != "End":
                    self.check_usage()
                self.eat()  # End
            
            elif self.current_token.type == TokenType.IDENTIFIER:
                next_tok = self.peek()
                if next_tok.value == ":=":
                    self.check_assignment()
                else:
                    self.check_variable_use()
            else:
                self.eat()
    
    def skip_declaration(self):
        """Saute une déclaration (déjà traitée)"""
        self.eat()  # Type
        while self.current_token.type != TokenType.END:
            self.eat()
        self.eat()  # END
    
    def check_variable_use(self):
        """Vérifie l'utilisation d'une variable"""
        if self.current_token.type == TokenType.IDENTIFIER:
            var_name = self.current_token.value
            if var_name not in self.symbol_table:
                self.errors.append(f"Erreur sémantique ligne {self.current_token.line}: variable '{var_name}' non déclarée")
        
        self.eat()
    
    def check_assignment(self):
        """Vérifie une affectation (x := valeur #)"""
        # Variable à gauche
        var_name = self.current_token.value
        line = self.current_token.line
        
        # Vérifier si déclarée
        if var_name not in self.symbol_table:
            self.errors.append(f"Erreur sémantique ligne {line}: variable '{var_name}' non déclarée")
            # Sauter l'affectation
            while self.current_token.type != TokenType.END:
                self.eat()
            self.eat()  # END
            return
        
        # Marquer comme initialisée
        self.symbol_table[var_name]["initialized"] = True
        var_type = self.symbol_table[var_name]["type"]
        
        self.eat()  # Variable
        self.eat()  # :=
        
        # Analyser l'expression
        expr_type = self.analyze_expression()
        
        # Vérifier compatibilité
        if expr_type != "unknown" and not self.is_type_compatible(var_type, expr_type, ":="):
            self.errors.append(f"Erreur sémantique ligne {line}: type incompatible '{var_name}' ({var_type} := {expr_type})")
        
        # Fin d'instruction
        while self.current_token.value != "#":
            self.eat()
        self.eat()  # #
    
    def analyze_expression(self):
        """
        Analyse une expression FROG (infixe) et retourne son type global
        """
        expr_types = set()
        has_comparison = False

        while (self.current_token.type != TokenType.EOF and
               self.current_token.type != TokenType.END and
               self.current_token.value not in {",", "]", "until"}):
        
            token = self.current_token

            if token.type in {TokenType.NUMBER, TokenType.REAL, TokenType.STRING}:
                expr_types.add(self.get_token_type(token))

            elif token.type == TokenType.IDENTIFIER:
                if token.value not in self.symbol_table:
                    self.errors.append(
                        f"Erreur sémantique ligne {token.line}: variable '{token.value}' non déclarée"
                    )
                else:
                    expr_types.add(self.symbol_table[token.value]["type"])

            elif token.value in {"<=", ">=", "==", "!=", "<", ">"}:
                has_comparison = True

            self.eat()

        if has_comparison:
            return "bool"
        if "string" in expr_types:
            return "string"
        if "real" in expr_types:
            return "real"
        if "int" in expr_types:
            return "int"

        return "unknown"

    
    def check_print(self):
        """Vérifie FRG_Print"""
        self.eat()  # FRG_Print
        
        while self.current_token.type != TokenType.END:
            if self.current_token.type == TokenType.IDENTIFIER:
                self.check_variable_use()
            else:
                self.eat()
            
            if self.current_token.value == ",":
                self.eat()
        
        self.eat()  # #
    
    def check_if(self):
        """Vérifie If [condition] ... Else ..."""
        self.eat()  # If
        self.eat()  # [
        
        # Condition (doit être booléenne)
        cond_type = self.analyze_expression()
        if cond_type not in {"bool", "unknown"}:
            self.errors.append(f"Erreur sémantique ligne {self.current_token.line}: condition doit être booléenne")
        
        self.eat()  # ]
        
        # Bloc then
        self.parse_statement_semantic()
        
        # Else optionnel
        if self.current_token.value == "Else":
            self.eat()  # Else
            self.parse_statement_semantic()
    
    def check_repeat(self):
        """Vérifie Repeat ... until [condition]"""
        self.eat()  # Repeat
        
        # Corps de la boucle
        while self.current_token.value != "until":
            self.parse_statement_semantic()
        
        self.eat()  # until
        self.eat()  # [
        
        # Condition
        cond_type = self.analyze_expression()
        if cond_type not in {"bool", "unknown"}:
            self.errors.append(f"Erreur sémantique ligne {self.current_token.line}: condition doit être booléenne")
        
        self.eat()  # ]
    
    def parse_statement_semantic(self):
        """Version pour l'analyse sémantique"""
        token_val = self.current_token.value
        
        if token_val in {"FRG_Int", "FRG_Real", "FRG_Strg"}:
            self.skip_declaration()
        
        elif token_val == "FRG_Print":
            self.check_print()
        
        elif token_val == "If":
            self.check_if()
        
        elif token_val == "Repeat":
            self.check_repeat()
        
        elif token_val == "Begin":
            self.eat()  # Begin
            while self.current_token.value != "End":
                self.parse_statement_semantic()
            self.eat()  # End
        
        elif self.current_token.type == TokenType.IDENTIFIER:
            if self.peek().value == ":=":
                self.check_assignment()
            else:
                self.eat()
        
        else:
            self.eat()
    
    def get_symbol_table(self):
        """Retourne la table des symboles (pour affichage)"""
        return self.symbol_table


# ==================== TEST DE L'ANALYSE SÉMANTIQUE ====================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE L'ANALYSEUR SeMANTIQUE")
    print("=" * 60)
    
    # Test 1: Programme correct
    code1 = """FRG_Begin
FRG_Int a, b #
FRG_Real c #
a := 10 #
b := a + 5 #
c := 3.14 #
c := a + c # int + real → real
FRG_Print "Valeurs:", a, b, c #
FRG_End"""
    
    print("\nTest 1: Programme semantiquement correct")
    print("-" * 40)
    
    # Simuler les tokens (en vrai, viendrait du lexer)
    from lexer import Lexer
    lexer = Lexer(code1)
    tokens, _ = lexer.tokenize()
    
    analyzer = SemanticAnalyzer(tokens)
    errors = analyzer.analyze()
    
    if not errors:
        print(" Programme semantiquement correct")
        print("\nTable des symboles:")
        for name, info in analyzer.symbol_table.items():
            init = "✓" if info["initialized"] else "✗"
            print(f"  {name}: {info['type']} (ligne {info['line']}, init: {init})")
    else:
        print(" Erreurs:")
        for error in errors:
            print(f"  {error}")
    
    # Test 2: Avec erreurs
    code2 = """FRG_Begin
x := 10 # ERREUR: x non déclaré
FRG_Int y #
y := "hello" # ERREUR: int := string
FRG_End"""
    
    print("\n\nTest 2: Programme avec erreurs")
    print("-" * 40)
    
    lexer2 = Lexer(code2)
    tokens2, _ = lexer2.tokenize()
    
    analyzer2 = SemanticAnalyzer(tokens2)
    errors2 = analyzer2.analyze()
    
    if errors2:
        print(" Erreurs detectees:")
        for error in errors2:
            print(f"  {error}")