# ==================== ANALYSEUR SYNTAXIQUE ====================
from tokens import TokenType, Token


class Parser:
    """Analyseur syntaxique qui vérifie la structure grammaticale"""
    
    def __init__(self, tokens):
        """
        Initialise le parser avec la liste de tokens
        
        Args:
            tokens: Liste de tokens générée par le Lexer
        """
        self.tokens = tokens
        self.pos = 0                     # Position actuelle dans les tokens
        self.errors = []                 # Liste des erreurs syntaxiques
        self.current_token = self.tokens[0] if tokens else None
    
    def parse(self):
        """
        Démarre l'analyse syntaxique
        
        Returns:
            list: Liste des erreurs syntaxiques (vide si aucune erreur)
        """
        print("\n" + "=" * 60)
        print("DEBUT DE L'ANALYSE SYNTAXIQUE")
        print("=" * 60)
        
        try:
            self.parse_program()
            
            # Vérifier qu'on a tout consommé
            if self.current_token.type != TokenType.EOF:
                self.errors.append(f"Erreur ligne {self.current_token.line}: syntaxe invalide apres '{self.current_token.value}'")
        
        except Exception as e:
            self.errors.append(f"Erreur d'analyse: {str(e)}")
        
        print(f"Analyse terminee. {len(self.errors)} erreur(s) syntaxique(s) trouvee(s).")
        return self.errors
    
    # ==================== METHODES AUXILIAIRES ====================
    
    def eat(self, expected_type=None, expected_value=None):
        """
        Consomme le token actuel s'il correspond au type/valeur attendu
        
        Args:
            expected_type: Type de token attendu (TokenType)
            expected_value: Valeur de token attendue (string)
        
        Returns:
            Token: Le token consomme
        """
        if self.current_token.type == TokenType.EOF:
            self.errors.append(f"Erreur ligne {self.current_token.line}: fin de fichier inattendue")
            return None
        
        # Verifier si le token correspond
        match = True
        if expected_type and self.current_token.type != expected_type:
            match = False
        if expected_value and self.current_token.value != expected_value:
            match = False
        
        if match:
            consumed_token = self.current_token
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = Token(TokenType.EOF, "", -1)
            return consumed_token
        else:
            # Erreur: token inattendu
            expected = expected_value if expected_value else expected_type.name
            found = f"'{self.current_token.value}' ({self.current_token.type.name})"
            self.errors.append(f"Erreur ligne {self.current_token.line}: attendu {expected}, trouve {found}")
            
            # Avancer quand meme pour eviter boucle infinie
            if self.pos < len(self.tokens):
                self.pos += 1
                if self.pos < len(self.tokens):
                    self.current_token = self.tokens[self.pos]
            return None
    
    def peek(self, lookahead=1):
        """
        Regarde les prochains tokens sans les consommer
        
        Args:
            lookahead: Nombre de tokens a regarder en avant
        
        Returns:
            Token: Le token a la position lookahead
        """
        if self.pos + lookahead < len(self.tokens):
            return self.tokens[self.pos + lookahead]
        return Token(TokenType.EOF, "", -1)
    
    # ==================== REGLES DE GRAMMAIRE ====================
    
    def parse_program(self):
        """PROGRAM → FRG_Begin STATEMENTS FRG_End"""
        print("Analyse du programme...")
        
        # FRG_Begin
        if self.current_token.value == "FRG_Begin":
            self.eat(TokenType.KEYWORD, "FRG_Begin")
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: programme doit commencer par FRG_Begin")
            return
        
        # STATEMENTS (instructions)
        while self.current_token.value != "FRG_End" and self.current_token.type != TokenType.EOF:
            self.parse_statement()
        
        # FRG_End
        if self.current_token.value == "FRG_End":
            self.eat(TokenType.KEYWORD, "FRG_End")
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: programme doit terminer par FRG_End")
    
    def parse_statement(self):
        """
        STATEMENT → DECLARATION
                   | ASSIGNMENT
                   | PRINT_STMT
                   | IF_STMT
                   | REPEAT_STMT
                   | COMMENT
        """
        token_value = self.current_token.value
        
        if token_value in {"FRG_Int", "FRG_Real", "FRG_Strg"}:
            self.parse_declaration()
        
        elif token_value == "FRG_Print":
            self.parse_print()
        
        elif token_value == "If":
            self.parse_if()
        
        elif token_value == "Repeat":
            self.parse_repeat()
        
        elif self.current_token.type == TokenType.IDENTIFIER and self.peek().value == ":=":
            self.parse_assignment()
        
        elif self.current_token.type == TokenType.COMMENT:
            self.eat(TokenType.COMMENT)  # Commentaires sont ignores syntaxiquement
        
        elif self.current_token.value == "Begin":
            self.parse_begin_end_block()
        
        elif self.current_token.value in {"Else", "until", "End"}:
            # Ces tokens sont geres dans d'autres fonctions
            return
        
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: instruction invalide '{token_value}'")
            self.eat()  # Avancer pour eviter boucle
    
    def parse_declaration(self):
        """DECLARATION → (FRG_Int | FRG_Real | FRG_Strg) IDENTIFIER ("," IDENTIFIER)* "#" """
        print(f"  Declaration ligne {self.current_token.line}")
        
        # Type (FRG_Int, FRG_Real, FRG_Strg)
        type_token = self.eat(TokenType.KEYWORD)  # Consomme le type
        
        # Premier identifiant
        if self.current_token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: identifiant attendu apres {type_token.value}")
        
        # Identifiants supplementaires separes par virgules
        while self.current_token.value == ",":
            self.eat(TokenType.SEPARATOR, ",")
            if self.current_token.type == TokenType.IDENTIFIER:
                self.eat(TokenType.IDENTIFIER)
            else:
                self.errors.append(f"Erreur ligne {self.current_token.line}: identifiant attendu apres virgule")
        
        # Fin d'instruction #
        if self.current_token.type == TokenType.END:
            self.eat(TokenType.END)
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: '#' attendu pour fin de declaration")
    
    def parse_assignment(self):
        """ASSIGNMENT → IDENTIFIER ":=" EXPRESSION "#" """
        print(f"  Affectation ligne {self.current_token.line}")
        
        # Identifiant
        self.eat(TokenType.IDENTIFIER)
        
        # Operateur :=
        if self.current_token.value == ":=":
            self.eat(TokenType.OPERATOR, ":=")
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: ':=' attendu")
        
        # Expression
        self.parse_expression()
        
        # Fin d'instruction #
        if self.current_token.type == TokenType.END:
            self.eat(TokenType.END)
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: '#' attendu pour fin d'affectation")
    
    def parse_expression(self):
        """EXPRESSION → TERM (("+" | "-") TERM)*"""
        # Premier terme
        self.parse_term()
        
        # Operateurs + ou - suivis de termes
        while self.current_token.value in {"+", "-"}:
            self.eat(TokenType.OPERATOR)  # + ou -
            self.parse_term()
    
    def parse_term(self):
        """TERM → FACTOR (("*" | "/") FACTOR)*"""
        # Premier facteur
        self.parse_factor()
        
        # Operateurs * ou / suivis de facteurs
        while self.current_token.value in {"*", "/"}:
            self.eat(TokenType.OPERATOR)  # * ou /
            self.parse_factor()
    
    def parse_factor(self):
        """
        FACTOR → NUMBER 
                | REAL 
                | STRING 
                | IDENTIFIER 
                | "(" EXPRESSION ")"
        """
        if self.current_token.type in {TokenType.NUMBER, TokenType.REAL, TokenType.STRING, TokenType.IDENTIFIER}:
            self.eat(self.current_token.type)
        
        elif self.current_token.value == "(":
            self.eat(TokenType.SEPARATOR, "(")
            self.parse_expression()
            if self.current_token.value == ")":
                self.eat(TokenType.SEPARATOR, ")")
            else:
                self.errors.append(f"Erreur ligne {self.current_token.line}: ')' attendu")
        
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: expression invalide")
    
    def parse_print(self):
        """PRINT_STMT → FRG_Print (STRING | IDENTIFIER | NUMBER) ("," (STRING | IDENTIFIER | NUMBER))* "#" """
        print(f"  Print ligne {self.current_token.line}")
        
        # Mot-cle FRG_Print
        self.eat(TokenType.KEYWORD, "FRG_Print")
        
        # Premier element a afficher
        if self.current_token.type in {TokenType.STRING, TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.REAL}:
            self.eat(self.current_token.type)
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: valeur ou variable attendue apres FRG_Print")
        
        # Elements supplementaires separes par virgules
        while self.current_token.value == ",":
            self.eat(TokenType.SEPARATOR, ",")
            if self.current_token.type in {TokenType.STRING, TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.REAL}:
                self.eat(self.current_token.type)
            else:
                self.errors.append(f"Erreur ligne {self.current_token.line}: valeur attendue apres virgule")
        
        # Fin d'instruction #
        if self.current_token.type == TokenType.END:
            self.eat(TokenType.END)
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: '#' attendu pour fin d'instruction print")
    
    def parse_if(self):
        """IF_STMT → If "[" CONDITION "]" STATEMENT (Else STATEMENT)?"""
        print(f"  If ligne {self.current_token.line}")
        
        # Mot-cle If
        self.eat(TokenType.KEYWORD, "If")
        
        # Crochet ouvrant [
        if self.current_token.value == "[":
            self.eat(TokenType.SEPARATOR, "[")
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: '[' attendu apres If")
        
        # Condition
        self.parse_condition()
        
        # Crochet fermant ]
        if self.current_token.value == "]":
            self.eat(TokenType.SEPARATOR, "]")
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: ']' attendu pour fin de condition")
        
        # Instruction du if
        self.parse_statement()
        
        # Else optionnel
        if self.current_token.value == "Else":
            self.eat(TokenType.KEYWORD, "Else")
            self.parse_statement()
    
    def parse_condition(self):
        """CONDITION → EXPRESSION COMPARATOR EXPRESSION"""
        # Expression gauche
        self.parse_expression()
        
        # Comparateur (<=, >=, ==, !=, <, >)
        if self.current_token.value in {"<=", ">=", "==", "!=", "<", ">"}:
            self.eat(TokenType.OPERATOR)
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: operateur de comparaison attendu")
        
        # Expression droite
        self.parse_expression()
    
    def parse_repeat(self):
        """REPEAT_STMT → Repeat STATEMENTS until "[" CONDITION "]" """
        print(f"  Repeat ligne {self.current_token.line}")
        
        # Mot-cle Repeat
        self.eat(TokenType.KEYWORD, "Repeat")
        
        # Instructions dans la boucle
        while self.current_token.value != "until" and self.current_token.type != TokenType.EOF:
            self.parse_statement()
        
        # Mot-cle until
        if self.current_token.value == "until":
            self.eat(TokenType.KEYWORD, "until")
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: 'until' attendu pour terminer la boucle Repeat")
            return
        
        # Crochet ouvrant [
        if self.current_token.value == "[":
            self.eat(TokenType.SEPARATOR, "[")
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: '[' attendu apres until")
        
        # Condition
        self.parse_condition()
        
        # Crochet fermant ]
        if self.current_token.value == "]":
            self.eat(TokenType.SEPARATOR, "]")
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: ']' attendu pour fin de condition")
    
    def parse_begin_end_block(self):
        """BEGIN_END → Begin STATEMENTS End"""
        print(f"  Bloc Begin/End ligne {self.current_token.line}")
        
        # Mot-cle Begin
        self.eat(TokenType.KEYWORD, "Begin")
        
        # Instructions dans le bloc
        while self.current_token.value != "End" and self.current_token.type != TokenType.EOF:
            self.parse_statement()
        
        # Mot-cle End
        if self.current_token.value == "End":
            self.eat(TokenType.KEYWORD, "End")
        else:
            self.errors.append(f"Erreur ligne {self.current_token.line}: 'End' attendu pour terminer le bloc")


# Test ULTRA simple du parser
if __name__ == "__main__":
    print("TEST ULTRA SIMPLE")
    
    # Programme minimal correct
    tokens = [
        Token(TokenType.KEYWORD, "FRG_Begin", 1),
        Token(TokenType.KEYWORD, "FRG_Int", 2),
        Token(TokenType.IDENTIFIER, "x", 2),
        Token(TokenType.SEPARATOR, "#", 2),
        Token(TokenType.KEYWORD, "FRG_End", 3),
        Token(TokenType.EOF, "", 3)
    ]
    
    print("\nTest 1: Programme minimal (doit être correct)")
    parser = Parser(tokens)
    errors = parser.parse()
    
    if not errors:
        print(" SUCCÈS: Parser accepte programme correct")
    else:
        print(" ÉCHEC: Parser rejette programme correct")
        for e in errors:
            print(f"  {e}")
    
    # Programme avec erreur
    tokens_err = [
        Token(TokenType.KEYWORD, "FRG_Begin", 1),
        Token(TokenType.KEYWORD, "FRG_Int", 2),
        # OUBLIÉ: identifiant et #
        Token(TokenType.KEYWORD, "FRG_End", 3),
        Token(TokenType.EOF, "", 3)
    ]
    
    print("\nTest 2: Programme avec erreur (doit détecter)")
    parser2 = Parser(tokens_err)
    errors2 = parser2.parse()
    
    if errors2:
        print(" SUCCÈS: Parser détecte l'erreur")
    else:
        print(" ÉCHEC: Parser ne détecte pas l'erreur")