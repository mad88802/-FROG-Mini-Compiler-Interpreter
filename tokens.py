# tokens.py
from enum import Enum

class TokenType(Enum):
    KEYWORD = 1
    IDENTIFIER = 2
    NUMBER = 3
    REAL = 4
    STRING = 5
    OPERATOR = 6
    SEPARATOR = 7
    COMMENT = 8
    EOF = 9
    END = 10

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"{self.value}: {self.type.name.lower()}"