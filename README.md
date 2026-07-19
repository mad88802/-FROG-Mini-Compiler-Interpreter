# 🐸 FROG — Mini Compiler & Interpreter

A compiler pipeline built from scratch for **FROG**, a tiny educational programming language — complete with a lexer, parser, semantic analyzer, and tree-walking interpreter, wrapped in a desktop GUI. A companion web playground is also available.

**🌐 Try it online:** [prettify-compiler.lovable.app](https://prettify-compiler.lovable.app/)

---


## Overview



1. **Lexical Analysis** (`lexer.py`) — turns raw source code into a stream of tokens, catching lexical errors (unterminated strings, invalid identifiers, unknown characters, etc.)
2. **Syntax Analysis** (`parse.py`) — a recursive-descent parser that validates the grammatical structure of the program
3. **Semantic Analysis** (`semantique.py`) — builds a symbol table and checks type consistency, variable declarations, and usage rules
4. **Interpretation** (`interpreteur.py`) — walks the token stream and actually executes the program
5. **GUI** (`gui.py`) — a Tkinter desktop app to load a `.frg` file and run each analysis stage step by step, with results displayed live

## Language Features

FROG supports:

- **Types:** `FRG_Int`, `FRG_Real`, `FRG_Strg`
- **Variables:** declaration and assignment (`:=`)
- **Control flow:** `If` / `Else`, `Repeat ... until`
- **Output:** `FRG_Print`
- **Comments:** `## comment`
- **Operators:** `+ - * /`, comparisons `< > <= >= == !=`
- **Program structure:** every program is wrapped in `FRG_Begin ... FRG_End`

### Example (`test.frg`)

```
FRG_Begin
## exemple: déclaration et boucle Repeat
FRG_Int i, x1 #
FRG_Real x3 #
FRG_Strg msg #
i:=30 #
If [ i<=20 ]
Begin
   x1:=10 #
End
Else
Begin
   x1:=30 #
   x3:=x1*4 #
   FRG_Print x1, x3 #
End
FRG_Print " Hello :) " #
Repeat
   i:=i-5 #
   FRG_Print i #
until [ i <= 15 ]
FRG_End
```

## Project Structure

```
frog_p/
├── tokens.py         # Token & TokenType definitions
├── lexer.py           # Lexical analyzer
├── parse.py           # Syntax analyzer (recursive-descent parser)
├── semantique.py       # Semantic analyzer & symbol table
├── interpreteur.py     # Interpreter / executor
├── gui.py               # Tkinter desktop GUI
└── test.frg              # Example FROG program
```

## Getting Started

### Requirements

- Python 3.11+ (uses only the standard library — `tkinter` for the GUI)

### Run the GUI

```bash
cd frog_p
python gui.py
```

Load a `.frg` file, then run the lexical, syntactic, and semantic analysis steps individually, or execute the program directly.



## Web Playground

A browser-based version of the compiler is available at:
👉 **[prettify-compiler.lovable.app](https://prettify-compiler.lovable.app/)**


