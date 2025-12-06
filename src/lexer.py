"""
FunLang - Analizador Léxico
Implementado con PLY (Python Lex-Yacc)
"""

import ply.lex as lex
from typing import List, Tuple

# ============================================================================
# PALABRAS RESERVADAS
# ============================================================================
reserved = {
    # Declaraciones
    'module': 'MODULE',
    'where': 'WHERE',
    'import': 'IMPORT',
    'as': 'AS',
    'let': 'LET',
    'in': 'IN',
    'var': 'VAR',
    'const': 'CONST',
    'type': 'TYPE',
    'data': 'DATA',
    
    # Control de flujo
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'case': 'CASE',
    'of': 'OF',
    'while': 'WHILE',
    'for': 'FOR',
    'do': 'DO',
    'end': 'END',
    'return': 'RETURN',
    
    # Funciones
    'fn': 'FN',
    
    # Tipos básicos
    'Int': 'TYPE_INT',
    'Float': 'TYPE_FLOAT',
    'Double': 'TYPE_DOUBLE',
    'Bool': 'TYPE_BOOL',
    'Char': 'TYPE_CHAR',
    'String': 'TYPE_STRING',
    'Void': 'TYPE_VOID',
    'array': 'ARRAY',
    'matrix': 'MATRIX',
    'Matrix': 'TYPE_MATRIX',
    
    # Literales booleanos
    'True': 'TRUE',
    'False': 'FALSE',
    
    # Operadores lógicos
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'mod': 'MOD',
    'div': 'DIV',
    
    # Modelo de Actores (básico)
    'actor': 'ACTOR',
    'spawn': 'SPAWN',
    'send': 'SEND',
}

# ============================================================================
# LISTA DE TOKENS
# ============================================================================
tokens = [
    # Identificadores y literales
    'IDENTIFIER',
    'CONSTRUCTOR',
    'INTEGER',
    'FLOAT_LIT',
    'CHAR_LIT',
    'STRING_LIT',
    
    # Operadores aritméticos
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'MODULO',
    'POWER',
    'DOUBLESTAR',
    
    # Operadores de comparación
    'EQ',
    'NEQ',
    'NEQ_HASKELL',
    'LT',
    'GT',
    'LE',
    'GE',
    
    # Operadores lógicos
    'AND_OP',
    'OR_OP',
    'NOT_OP',
    
    # Operadores de asignación
    'ASSIGN',
    'ARROW',
    'LARROW',
    'DOUBLE_COLON',
    
    # Delimitadores
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'SEMICOLON',
    'COLON',
    'DOT',
    'PIPE',
    'UNDERSCORE',
    'BACKSLASH',
    
    # Operadores especiales
    'DOTDOT',
    'DOUBLEEXCL',
    'CONS',
    'HASH_BRACKET',
    'HASH_BRACE',
    
    # Nuevas líneas (para algunas gramáticas)
    'NEWLINE',
] + list(reserved.values())

# ============================================================================
# REGLAS DE TOKENS SIMPLES
# ============================================================================

# Operadores de dos caracteres (deben ir antes de los de un caracter)
t_DOUBLESTAR    = r'\*\*'
t_EQ            = r'=='
t_NEQ           = r'!='
t_NEQ_HASKELL   = r'/='
t_LE            = r'<='
t_GE            = r'>='
t_AND_OP        = r'&&'
t_OR_OP         = r'\|\|'
t_ARROW         = r'->'
t_LARROW        = r'<-'
t_DOUBLE_COLON  = r'::'
t_DOTDOT        = r'\.\.'
t_DOUBLEEXCL    = r'!!'
t_HASH_BRACKET  = r'\#\['
t_HASH_BRACE    = r'\#\{'

# Operadores de un caracter
t_PLUS          = r'\+'
t_MINUS         = r'-'
t_TIMES         = r'\*'
t_DIVIDE        = r'/'
t_MODULO        = r'%'
t_POWER         = r'\^'
t_LT            = r'<'
t_GT            = r'>'
t_NOT_OP        = r'!'
t_ASSIGN        = r'='
t_LPAREN        = r'\('
t_RPAREN        = r'\)'
t_LBRACKET      = r'\['
t_RBRACKET      = r'\]'
t_LBRACE        = r'\{'
t_RBRACE        = r'\}'
t_COMMA         = r','
t_SEMICOLON     = r';'
t_COLON         = r':'
t_DOT           = r'\.'
t_PIPE          = r'\|'
t_UNDERSCORE    = r'_'
t_BACKSLASH     = r'\\'
t_CONS          = r':'

# ============================================================================
# REGLAS DE TOKENS COMPLEJAS
# ============================================================================

def t_FLOAT_LIT(t):
    r'\d+\.\d+([eE][+-]?\d+)?|\d+[eE][+-]?\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'0[xX][0-9a-fA-F]+|0[bB][01]+|0[oO][0-7]+|\d+'
    if t.value.startswith(('0x', '0X')):
        t.value = int(t.value, 16)
    elif t.value.startswith(('0b', '0B')):
        t.value = int(t.value, 2)
    elif t.value.startswith(('0o', '0O')):
        t.value = int(t.value, 8)
    else:
        t.value = int(t.value)
    return t

def t_CHAR_LIT(t):
    r"'(\\[ntr\\\'\"0]|[^'\\])'"
    # Procesar secuencias de escape
    value = t.value[1:-1]  # Quitar comillas
    if value.startswith('\\'):
        escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', "'": "'", '"': '"', '0': '\0'}
        t.value = escape_map.get(value[1], value[1])
    else:
        t.value = value
    return t

def t_STRING_LIT(t):
    r'"([^"\\]|\\[ntr\\\'\"0])*"'
    # Procesar secuencias de escape
    value = t.value[1:-1]  # Quitar comillas
    escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', "'": "'", '"': '"', '0': '\0'}
    result = []
    i = 0
    while i < len(value):
        if value[i] == '\\' and i + 1 < len(value):
            result.append(escape_map.get(value[i+1], value[i+1]))
            i += 2
        else:
            result.append(value[i])
            i += 1
    t.value = ''.join(result)
    return t

def t_CONSTRUCTOR(t):
    r'[A-Z][a-zA-Z0-9_]*'
    # Los constructores empiezan con mayúscula
    t.type = reserved.get(t.value, 'CONSTRUCTOR')
    return t

def t_IDENTIFIER(t):
    r'[a-z_][a-zA-Z0-9_\']*'
    # Verificar si es palabra reservada
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

# ============================================================================
# MANEJO DE COMENTARIOS Y ESPACIOS
# ============================================================================

def t_COMMENT_SINGLE(t):
    r'--[^\n]*'
    pass  # Ignorar comentarios de una línea

def t_COMMENT_MULTI(t):
    r'\{-[\s\S]*?-\}'
    # Contar nuevas líneas en comentarios multilínea
    t.lexer.lineno += t.value.count('\n')
    pass  # Ignorar comentarios multilínea

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    # Podemos opcionalmente retornar el token si la gramática lo necesita
    # return t
    pass

# Ignorar espacios y tabs
t_ignore = ' \t\r'

# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

def t_error(t):
    print(f"Error léxico: Caracter ilegal '{t.value[0]}' en línea {t.lineno}, columna {find_column(t)}")
    t.lexer.skip(1)

def find_column(token):
    """Encuentra la columna del token"""
    line_start = token.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

# ============================================================================
# CONSTRUCCIÓN DEL LEXER
# ============================================================================

class FunLangLexer:
    """Clase wrapper para el lexer de FunLang"""
    
    def __init__(self):
        self.lexer = lex.lex()
        self.errors: List[str] = []
        self._data: str = ""
    
    def input(self, data: str):
        """Establece el input del lexer"""
        self._data = data
        self.lexer.input(data)
        self.errors = []
    
    def token(self):
        """Obtiene el siguiente token"""
        return self.lexer.token()
    
    def _find_column(self, token) -> int:
        """Encuentra la columna del token"""
        line_start = self._data.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1
    
    def tokenize(self, data: str) -> List[Tuple]:
        """Tokeniza todo el input y retorna lista de tokens"""
        self.input(data)
        tokens = []
        while True:
            tok = self.token()
            if not tok:
                break
            tokens.append((tok.type, tok.value, tok.lineno, self._find_column(tok)))
        return tokens
    
    def reset_lineno(self):
        """Resetea el número de línea"""
        self.lexer.lineno = 1


def create_lexer():
    """Factory function para crear un lexer"""
    return FunLangLexer()


# ============================================================================
# PRUEBA DEL LEXER
# ============================================================================

if __name__ == '__main__':
    test_code = '''
    -- Este es un comentario
    module Main where
    
    {- Comentario
       multilínea -}
    
    -- Declaración de tipos
    gcd :: Int -> Int -> Int
    gcd a 0 = a
    gcd a b = gcd b (a mod b)
    
    -- Función principal
    main = do
        let x = 10
        let y = 25.5
        let result = gcd 48 18
        return result
    end
    
    -- Variables y arreglos
    let arr = [1, 2, 3, 4, 5]
    let mat = matrix [[1, 2], [3, 4]]
    
    -- Control de flujo
    factorial n = if n <= 1 then 1 else n * factorial (n - 1)
    
    -- Lambda
    let double = \\x -> x * 2
    '''
    
    lexer = create_lexer()
    tokens = lexer.tokenize(test_code)
    
    print("=" * 60)
    print("ANÁLISIS LÉXICO - FunLang")
    print("=" * 60)
    
    for tok_type, tok_value, lineno, column in tokens:
        print(f"Línea {lineno:3d}, Col {column:3d}: {tok_type:20s} -> {repr(tok_value)}")
    
    print("=" * 60)
    print(f"Total de tokens: {len(tokens)}")
