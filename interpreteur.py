# interpreter.py
from tokens import TokenType, Token
from lexer import Lexer
from parse import Parser
from semantique import SemanticAnalyzer

class Interpreter:
    """Interpréteur pour exécuter un programme FROG"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
        self.vars = {}  # Table des variables: {'x': 10, 'y': 3.14}
        self.output = []  # Stocke les sorties FRG_Print

    def run(self):
        """Exécute tout le programme"""
        while self.current_token.type != TokenType.EOF:
            try:
                self.execute_statement()
            except Exception as e:
                self.output.append(f"Erreur: {e}")
                self.eat()            

    def execute_statement(self):
        tok_val = self.current_token.value
        
        if tok_val in {"FRG_Int", "FRG_Real", "FRG_Strg"}:
            self.handle_declaration()
        elif tok_val == "FRG_Print":
            self.handle_print()
        elif tok_val == "If":
            self.handle_if()
        elif tok_val == "Repeat":
            self.handle_repeat()
        elif tok_val == "Begin":
            self.eat()
        elif tok_val == "End":
            self.eat()
        elif self.current_token.type == TokenType.IDENTIFIER and self.peek().value == ":=":
            self.handle_assignment()
        else:
            # Ignorer commentaires ou tokens inutiles
            self.eat()

    # ==================== Méthodes auxiliaires ====================
    
    def eat(self):
        """Consomme le token actuel et passe au suivant"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token(TokenType.EOF, "", -1)
    
    def peek(self, lookahead=1):
        """Regarde les prochains tokens sans consommer"""
        if self.pos + lookahead < len(self.tokens):
            return self.tokens[self.pos + lookahead]
        return Token(TokenType.EOF, "", -1)
    
    def evaluate_expression(self):
        """Évalue une expression simple (supporte +, -, *, /)"""
        # Expression très simple : on lit jusqu'à '#' ou séparateur
        result = self.get_value(self.current_token)
        self.eat()
        
        while self.current_token.value in {"+", "-", "*", "/"}:
            op = self.current_token.value
            self.eat()
            rhs = self.get_value(self.current_token)
            self.eat()
            try: 
                if op == "+":
                    result += rhs
                elif op == "-":
                    result -= rhs
                elif op == "*":
                    result *= rhs
                elif op == "/":
                    if rhs == 0:
                        raise Exception("Erreur : division par zéro")
                    result /= rhs
            except Exception as e:
                raise e
            
        return result

    def get_value(self, token):
        """Retourne la valeur numérique ou string d’un token/variable"""
        if token.type == TokenType.NUMBER:
            return int(token.value)
        elif token.type == TokenType.REAL:
            return float(token.value)
        elif token.type == TokenType.STRING:
            return token.value
        elif token.type == TokenType.IDENTIFIER:
            if token.value in self.vars:
                return self.vars[token.value]
            else:
                raise Exception(f"Variable '{token.value}' non initialisée")
        else:
            raise Exception(f"Expression invalide: {token.value}")

    # ==================== Gestion des instructions ====================
    
    def handle_declaration(self):
        """Gère les déclarations de variables (FRG_Int x, y #)"""
        self.eat()  # Consomme le type
        
        while self.current_token.type == TokenType.IDENTIFIER:
            var_name = self.current_token.value
            if var_name not in self.vars:
                self.vars[var_name] = None  # Initialisation par défaut
            self.eat()
            if self.current_token.value == ",":
                self.eat()
        
        if self.current_token.type == TokenType.END:
            self.eat()
    
    def handle_assignment(self):
        """Gère x := expression #"""
        var_name = self.current_token.value
        self.eat()  # Consommer identifiant
        self.eat()  # Consommer ':='

        try:
            value = self.evaluate_expression()
            if var_name in self.vars:
                self.vars[var_name] = value
            else:
                raise Exception(f"Variable '{var_name}' non déclarée")
        except Exception as e:
            self.output.append(f"Erreur lors de l'exécution de '{var_name}': {e}")

        if self.current_token.type == TokenType.END:
            self.eat()
    
    def handle_print(self):
        """Gère FRG_Print ... #"""
        self.eat()  # FRG_Print
        values = []
        
        while self.current_token.type != TokenType.END:
            if self.current_token.type == TokenType.IDENTIFIER:
                values.append(str(self.vars.get(self.current_token.value, "undefined")))
            else:
                values.append(str(self.current_token.value))
            self.eat()
            if self.current_token.value == ",":
                self.eat()
        
        self.output.append(" ".join(values))
        if self.current_token.type == TokenType.END:
            self.eat()
    

    def handle_if(self):
        """Gère If [condition] statement (Else statement)?"""
        self.eat()  # If
        self.eat()  # [
        cond = self.evaluate_expression()
        self.eat()  # ]
        
        if cond:
            self.execute_statement()
            if self.current_token.value == "Else":
                self.skip_statement()
        else:
            self.skip_statement()
            if self.current_token.value == "Else":
                self.eat()
                self.execute_statement()
    

    def handle_repeat(self):
        """Gère Repeat ... until [condition]"""
        self.eat()  # Repeat
        start_pos = self.pos
        while True:
            while self.current_token.value != "until":
                self.execute_statement()
            self.eat()  # until
            self.eat()  # [
            cond = self.evaluate_expression()
            self.eat()  # ]
            if cond:
                break
            else:
                self.pos = start_pos
                self.current_token = self.tokens[self.pos]
    
    
    def skip_statement(self):
        """Ignore un statement (pour Else ou condition fausse)"""
        depth = 0
        while True:
            if self.current_token.value in {"FRG_Int", "FRG_Real", "FRG_Strg", "FRG_Print", "If", "Repeat"}:
                depth += 1
            elif self.current_token.value in {"End", "until", "Else"}:
                if depth == 0:
                    break
                depth -= 1
            self.eat()

# ==================== TEST RAPIDE ====================
if __name__ == "__main__":
    code = """FRG_Begin
FRG_Int i, x1, x2 #
FRG_Real x3 #
i := 30 #
If [i <= 20]
x1 := 10 #
Else
Begin
x1 := 30 #
x3 := x1 * 4 #
FRG_Print x1, x3 #
End
FRG_Print "Hell" #
Repeat
i := i - 5 #
FRG_Print i #
until [i <= 15]
FRG_End"""

    lexer = Lexer(code)
    tokens, _ = lexer.tokenize()
    
    # Vérifier syntaxe et sémantique avant exécution
    parser = Parser(tokens)
    parser_errors = parser.parse()
    analyzer = SemanticAnalyzer(tokens)
    semantic_errors = analyzer.analyze()
    
    if not parser_errors and not semantic_errors:
        interp = Interpreter(tokens)
        interp.run()
        print("\n=== Résultat de l'exécution ===")
        for line in interp.output:
            print(line)
    else:
        print("Erreurs détectées. Execution annulée.")
