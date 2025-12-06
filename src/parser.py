"""
FunLang - Analizador Sintáctico
Implementado con PLY (Python Lex-Yacc)
"""

import ply.yacc as yacc
from typing import List, Optional, Any
from .lexer import tokens, create_lexer
from .ast_nodes import *

# ============================================================================
# PRECEDENCIA DE OPERADORES
# ============================================================================

precedence = (
    ('left', 'OR_OP', 'OR'),
    ('left', 'AND_OP', 'AND'),
    ('left', 'NOT_OP', 'NOT'),
    ('nonassoc', 'EQ', 'NEQ', 'NEQ_HASKELL'),
    ('nonassoc', 'LT', 'GT', 'LE', 'GE'),
    ('right', 'CONS'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO', 'MOD', 'DIV'),
    ('right', 'POWER', 'DOUBLESTAR'),
    ('right', 'UMINUS'),
    ('left', 'LPAREN', 'LBRACKET'),
)

# ============================================================================
# REGLAS GRAMATICALES
# ============================================================================

def p_program(p):
    '''program : module_decl import_list decl_list
               | module_decl decl_list
               | import_list decl_list
               | decl_list'''
    if len(p) == 4:
        p[0] = Program(module=p[1], imports=p[2], declarations=p[3])
    elif len(p) == 3:
        if isinstance(p[1], str):  # module_decl
            p[0] = Program(module=p[1], imports=[], declarations=p[2])
        else:  # import_list
            p[0] = Program(module=None, imports=p[1], declarations=p[2])
    else:
        p[0] = Program(module=None, imports=[], declarations=p[1])


def p_module_decl(p):
    '''module_decl : MODULE IDENTIFIER WHERE
                   | MODULE CONSTRUCTOR WHERE'''
    p[0] = p[2]


def p_import_list(p):
    '''import_list : import_list import_decl
                   | import_decl'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_import_decl(p):
    '''import_decl : IMPORT IDENTIFIER
                   | IMPORT CONSTRUCTOR
                   | IMPORT IDENTIFIER AS IDENTIFIER
                   | IMPORT CONSTRUCTOR AS IDENTIFIER'''
    if len(p) == 3:
        p[0] = Import(module=p[2], lineno=p.lineno(1))
    else:
        p[0] = Import(module=p[2], alias=p[4], lineno=p.lineno(1))


def p_decl_list(p):
    '''decl_list : decl_list declaration
                 | declaration'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_declaration(p):
    '''declaration : function_decl
                   | type_sig
                   | var_decl
                   | const_decl
                   | type_decl
                   | data_decl
                   | actor_decl'''
    p[0] = p[1]


# ============================================================================
# DECLARACIÓN DE FUNCIONES
# ============================================================================

def p_type_sig(p):
    '''type_sig : IDENTIFIER DOUBLE_COLON type_expr'''
    p[0] = TypeSignature(name=p[1], type_expr=p[3], lineno=p.lineno(1))


def p_function_decl(p):
    '''function_decl : IDENTIFIER param_list ASSIGN expression
                     | IDENTIFIER ASSIGN expression
                     | IDENTIFIER param_list guarded_exprs
                     | IDENTIFIER guarded_exprs'''
    if len(p) == 5:
        p[0] = FunctionDecl(name=p[1], params=p[2], body=p[4], lineno=p.lineno(1))
    elif len(p) == 4:
        if p[2] == '=':
            p[0] = FunctionDecl(name=p[1], params=[], body=p[3], lineno=p.lineno(1))
        else:
            p[0] = FunctionDecl(name=p[1], params=p[2], guards=p[3], lineno=p.lineno(1))
    else:
        p[0] = FunctionDecl(name=p[1], params=[], guards=p[2], lineno=p.lineno(1))


def p_param_list(p):
    '''param_list : param_list pattern
                  | pattern'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_guarded_exprs(p):
    '''guarded_exprs : guarded_exprs guarded_expr
                     | guarded_expr'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_guarded_expr(p):
    '''guarded_expr : PIPE expression ASSIGN expression'''
    p[0] = GuardedExpr(guard=p[2], body=p[4], lineno=p.lineno(1))


# ============================================================================
# PATRONES
# ============================================================================

def p_pattern(p):
    '''pattern : IDENTIFIER
               | UNDERSCORE
               | literal
               | LPAREN pattern RPAREN
               | pattern CONS pattern
               | LBRACKET pattern_list RBRACKET
               | LBRACKET RBRACKET
               | LPAREN pattern_tuple RPAREN
               | CONSTRUCTOR'''
    if len(p) == 2:
        if p[1] == '_':
            p[0] = WildcardPattern(lineno=p.lineno(1))
        elif isinstance(p[1], str):
            if p[1][0].isupper():
                p[0] = Constructor(name=p[1], lineno=p.lineno(1))
            else:
                p[0] = VarPattern(name=p[1], lineno=p.lineno(1))
        else:
            p[0] = LitPattern(value=p[1], lineno=p.lineno(1))
    elif len(p) == 3:
        p[0] = ListPattern(elements=[], lineno=p.lineno(1))
    elif len(p) == 4:
        if p[1] == '(':
            p[0] = p[2]
        elif p[1] == '[':
            p[0] = ListPattern(elements=p[2], lineno=p.lineno(1))
        elif p[2] == ':':
            p[0] = ConsPattern(head=p[1], tail=p[3], lineno=p.lineno(1))
        else:
            p[0] = TuplePattern(elements=p[2], lineno=p.lineno(1))


def p_pattern_list(p):
    '''pattern_list : pattern_list COMMA pattern
                    | pattern'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_pattern_tuple(p):
    '''pattern_tuple : pattern COMMA pattern_list'''
    p[0] = [p[1]] + p[3]


# ============================================================================
# DECLARACIÓN DE TIPOS
# ============================================================================

def p_type_decl(p):
    '''type_decl : TYPE CONSTRUCTOR type_params ASSIGN type_expr
                 | TYPE CONSTRUCTOR ASSIGN type_expr'''
    if len(p) == 6:
        p[0] = TypeDecl(name=p[2], params=p[3], body=p[5], lineno=p.lineno(1))
    else:
        p[0] = TypeDecl(name=p[2], params=[], body=p[4], lineno=p.lineno(1))


def p_type_params(p):
    '''type_params : type_params IDENTIFIER
                   | IDENTIFIER'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_data_decl(p):
    '''data_decl : DATA CONSTRUCTOR type_params ASSIGN data_constrs
                 | DATA CONSTRUCTOR ASSIGN data_constrs'''
    if len(p) == 6:
        p[0] = DataDecl(name=p[2], params=p[3], constructors=p[5], lineno=p.lineno(1))
    else:
        p[0] = DataDecl(name=p[2], params=[], constructors=p[4], lineno=p.lineno(1))


def p_data_constrs(p):
    '''data_constrs : data_constrs PIPE data_constr
                    | data_constr'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_data_constr(p):
    '''data_constr : CONSTRUCTOR type_expr_list
                   | CONSTRUCTOR'''
    if len(p) == 3:
        p[0] = DataConstructor(name=p[1], fields=p[2], lineno=p.lineno(1))
    else:
        p[0] = DataConstructor(name=p[1], fields=[], lineno=p.lineno(1))


def p_type_expr_list(p):
    '''type_expr_list : type_expr_list base_type
                      | base_type'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


# ============================================================================
# EXPRESIONES DE TIPO
# ============================================================================

def p_type_expr(p):
    '''type_expr : type_expr ARROW type_expr
                 | base_type'''
    if len(p) == 4:
        p[0] = FunctionType(param_type=p[1], return_type=p[3], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_base_type(p):
    '''base_type : TYPE_INT
                 | TYPE_FLOAT
                 | TYPE_DOUBLE
                 | TYPE_BOOL
                 | TYPE_CHAR
                 | TYPE_STRING
                 | TYPE_VOID
                 | IDENTIFIER
                 | CONSTRUCTOR
                 | LBRACKET type_expr RBRACKET
                 | TYPE_MATRIX type_expr
                 | LPAREN type_expr RPAREN
                 | LPAREN type_tuple RPAREN'''
    if len(p) == 2:
        type_map = {
            'Int': TypeKind.INT, 'Float': TypeKind.FLOAT, 'Double': TypeKind.DOUBLE,
            'Bool': TypeKind.BOOL, 'Char': TypeKind.CHAR, 'String': TypeKind.STRING,
            'Void': TypeKind.VOID
        }
        if p[1] in type_map:
            p[0] = TypeNode(kind=type_map[p[1]], lineno=p.lineno(1))
        else:
            p[0] = TypeNode(kind=TypeKind.CUSTOM, name=p[1], lineno=p.lineno(1))
    elif len(p) == 3:  # Matrix type
        p[0] = TypeNode(kind=TypeKind.MATRIX, params=[p[2]], lineno=p.lineno(1))
    elif len(p) == 4:
        if p[1] == '[':
            p[0] = TypeNode(kind=TypeKind.ARRAY, params=[p[2]], lineno=p.lineno(1))
        else:
            if isinstance(p[2], list):
                p[0] = TypeNode(kind=TypeKind.CUSTOM, name="Tuple", params=p[2], lineno=p.lineno(1))
            else:
                p[0] = p[2]


def p_type_tuple(p):
    '''type_tuple : type_expr COMMA type_expr
                  | type_tuple COMMA type_expr'''
    if isinstance(p[1], list):
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1], p[3]]


# ============================================================================
# DECLARACIÓN DE VARIABLES
# ============================================================================

def p_var_decl(p):
    '''var_decl : LET IDENTIFIER COLON type_expr ASSIGN expression
                | LET IDENTIFIER ASSIGN expression
                | VAR IDENTIFIER COLON type_expr ASSIGN expression
                | VAR IDENTIFIER ASSIGN expression'''
    if len(p) == 7:
        is_mutable = p[1] == 'var'
        p[0] = VarDecl(name=p[2], var_type=p[4], value=p[6], is_mutable=is_mutable, lineno=p.lineno(1))
    else:
        is_mutable = p[1] == 'var'
        p[0] = VarDecl(name=p[2], var_type=None, value=p[4], is_mutable=is_mutable, lineno=p.lineno(1))


def p_const_decl(p):
    '''const_decl : CONST IDENTIFIER COLON type_expr ASSIGN expression
                  | CONST IDENTIFIER ASSIGN expression'''
    if len(p) == 7:
        p[0] = ConstDecl(name=p[2], const_type=p[4], value=p[6], lineno=p.lineno(1))
    else:
        p[0] = ConstDecl(name=p[2], const_type=None, value=p[4], lineno=p.lineno(1))


# ============================================================================
# EXPRESIONES
# ============================================================================

def p_expression(p):
    '''expression : let_expr
                  | if_expr
                  | case_expr
                  | lambda_expr
                  | while_expr
                  | for_expr
                  | do_block
                  | spawn_expr
                  | send_expr
                  | logical_or_expr'''
    p[0] = p[1]


def p_let_expr(p):
    '''let_expr : LET let_bindings IN expression'''
    p[0] = LetExpr(bindings=p[2], body=p[4], lineno=p.lineno(1))


def p_let_bindings(p):
    '''let_bindings : let_bindings SEMICOLON let_binding
                    | let_bindings COMMA let_binding
                    | let_binding'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_let_binding(p):
    '''let_binding : IDENTIFIER ASSIGN expression'''
    p[0] = LetBinding(name=p[1], value=p[3], lineno=p.lineno(1))


def p_if_expr(p):
    '''if_expr : IF expression THEN expression ELSE expression'''
    p[0] = IfExpr(condition=p[2], then_branch=p[4], else_branch=p[6], lineno=p.lineno(1))


def p_case_expr(p):
    '''case_expr : CASE expression OF case_alts'''
    p[0] = CaseExpr(expr=p[2], alternatives=p[4], lineno=p.lineno(1))


def p_case_alts(p):
    '''case_alts : case_alts case_alt
                 | case_alt'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_case_alt(p):
    '''case_alt : pattern ARROW expression'''
    p[0] = CaseAlt(pattern=p[1], body=p[3], lineno=p.lineno(1))


def p_lambda_expr(p):
    '''lambda_expr : BACKSLASH param_list ARROW expression
                   | FN param_list ARROW expression'''
    p[0] = LambdaExpr(params=p[2], body=p[4], lineno=p.lineno(1))


def p_while_expr(p):
    '''while_expr : WHILE expression DO expression END'''
    p[0] = WhileExpr(condition=p[2], body=p[4], lineno=p.lineno(1))


def p_for_expr(p):
    '''for_expr : FOR IDENTIFIER IN expression DOTDOT expression DO expression END
                | FOR IDENTIFIER IN expression DO expression END'''
    if len(p) == 10:
        p[0] = ForExpr(var=p[2], start=p[4], end=p[6], body=p[8], lineno=p.lineno(1))
    else:
        p[0] = ForExpr(var=p[2], collection=p[4], body=p[6], lineno=p.lineno(1))


def p_do_block(p):
    '''do_block : DO do_statements END'''
    p[0] = DoBlock(statements=p[2], lineno=p.lineno(1))


def p_do_statements(p):
    '''do_statements : do_statements do_statement
                     | do_statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_do_statement(p):
    '''do_statement : expression SEMICOLON
                    | expression
                    | IDENTIFIER LARROW expression SEMICOLON
                    | IDENTIFIER LARROW expression
                    | LET IDENTIFIER ASSIGN expression SEMICOLON
                    | LET IDENTIFIER ASSIGN expression
                    | RETURN expression SEMICOLON
                    | RETURN expression'''
    if len(p) == 2:
        p[0] = DoExprStmt(expr=p[1], lineno=p.lineno(1))
    elif len(p) == 3:
        if p[1] == 'return':
            p[0] = DoReturnStmt(expr=p[2], lineno=p.lineno(1))
        else:
            p[0] = DoExprStmt(expr=p[1], lineno=p.lineno(1))
    elif len(p) == 4:
        if p[1] == 'return':
            p[0] = DoReturnStmt(expr=p[2], lineno=p.lineno(1))
        else:
            p[0] = DoBindStmt(name=p[1], expr=p[3], lineno=p.lineno(1))
    elif len(p) == 5:
        if p[1] == 'let':
            p[0] = DoLetStmt(name=p[2], expr=p[4], lineno=p.lineno(1))
        else:
            p[0] = DoBindStmt(name=p[1], expr=p[3], lineno=p.lineno(1))
    else:
        p[0] = DoLetStmt(name=p[2], expr=p[4], lineno=p.lineno(1))


# ============================================================================
# EXPRESIONES LÓGICAS Y ARITMÉTICAS
# ============================================================================

def p_logical_or_expr(p):
    '''logical_or_expr : logical_or_expr OR_OP logical_and_expr
                       | logical_or_expr OR logical_and_expr
                       | logical_and_expr'''
    if len(p) == 4:
        p[0] = BinaryExpr(op=BinaryOp.OR, left=p[1], right=p[3], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_logical_and_expr(p):
    '''logical_and_expr : logical_and_expr AND_OP equality_expr
                        | logical_and_expr AND equality_expr
                        | equality_expr'''
    if len(p) == 4:
        p[0] = BinaryExpr(op=BinaryOp.AND, left=p[1], right=p[3], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_equality_expr(p):
    '''equality_expr : equality_expr EQ relational_expr
                     | equality_expr NEQ relational_expr
                     | equality_expr NEQ_HASKELL relational_expr
                     | relational_expr'''
    if len(p) == 4:
        op = BinaryOp.EQ if p[2] == '==' else BinaryOp.NEQ
        p[0] = BinaryExpr(op=op, left=p[1], right=p[3], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_relational_expr(p):
    '''relational_expr : relational_expr LT additive_expr
                       | relational_expr GT additive_expr
                       | relational_expr LE additive_expr
                       | relational_expr GE additive_expr
                       | additive_expr'''
    if len(p) == 4:
        op_map = {'<': BinaryOp.LT, '>': BinaryOp.GT, '<=': BinaryOp.LE, '>=': BinaryOp.GE}
        p[0] = BinaryExpr(op=op_map[p[2]], left=p[1], right=p[3], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_additive_expr(p):
    '''additive_expr : additive_expr PLUS multiplicative_expr
                     | additive_expr MINUS multiplicative_expr
                     | multiplicative_expr'''
    if len(p) == 4:
        op = BinaryOp.ADD if p[2] == '+' else BinaryOp.SUB
        p[0] = BinaryExpr(op=op, left=p[1], right=p[3], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_multiplicative_expr(p):
    '''multiplicative_expr : multiplicative_expr TIMES power_expr
                           | multiplicative_expr DIVIDE power_expr
                           | multiplicative_expr MODULO power_expr
                           | multiplicative_expr MOD power_expr
                           | multiplicative_expr DIV power_expr
                           | power_expr'''
    if len(p) == 4:
        op_map = {'*': BinaryOp.MUL, '/': BinaryOp.DIV, '%': BinaryOp.MOD, 'mod': BinaryOp.MOD, 'div': BinaryOp.DIV}
        p[0] = BinaryExpr(op=op_map[p[2]], left=p[1], right=p[3], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_power_expr(p):
    '''power_expr : unary_expr POWER power_expr
                  | unary_expr DOUBLESTAR power_expr
                  | unary_expr'''
    if len(p) == 4:
        p[0] = BinaryExpr(op=BinaryOp.POW, left=p[1], right=p[3], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_unary_expr(p):
    '''unary_expr : MINUS unary_expr %prec UMINUS
                  | NOT unary_expr
                  | NOT_OP unary_expr
                  | postfix_expr'''
    if len(p) == 3:
        if p[1] == '-':
            p[0] = UnaryExpr(op=UnaryOp.NEG, operand=p[2], lineno=p.lineno(1))
        else:
            p[0] = UnaryExpr(op=UnaryOp.NOT, operand=p[2], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_postfix_expr(p):
    '''postfix_expr : postfix_expr LPAREN arg_list RPAREN
                    | postfix_expr LPAREN RPAREN
                    | postfix_expr LBRACKET expression RBRACKET
                    | postfix_expr LBRACKET expression COMMA expression RBRACKET
                    | postfix_expr DOT IDENTIFIER
                    | postfix_expr DOUBLEEXCL expression
                    | primary_expr'''
    if len(p) == 5:
        if p[2] == '(':
            p[0] = FunctionCall(func=p[1], args=p[3], lineno=p.lineno(1))
        else:
            p[0] = IndexExpr(array=p[1], index=p[3], lineno=p.lineno(1))
    elif len(p) == 4:
        if p[2] == '(':
            p[0] = FunctionCall(func=p[1], args=[], lineno=p.lineno(1))
        elif p[2] == '.':
            p[0] = FieldAccess(obj=p[1], field=p[3], lineno=p.lineno(1))
        else:  # !!
            p[0] = IndexExpr(array=p[1], index=p[3], lineno=p.lineno(1))
    elif len(p) == 7:
        p[0] = MatrixIndexExpr(matrix=p[1], row=p[3], col=p[5], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_arg_list(p):
    '''arg_list : arg_list COMMA expression
                | expression'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


# ============================================================================
# EXPRESIONES PRIMARIAS
# ============================================================================

def p_primary_expr(p):
    '''primary_expr : literal
                    | IDENTIFIER
                    | CONSTRUCTOR
                    | LPAREN expression RPAREN
                    | tuple_expr
                    | list_expr
                    | array_expr
                    | matrix_expr
                    | range_expr
                    | list_comprehension'''
    if len(p) == 2:
        if isinstance(p[1], str):
            if p[1][0].isupper():
                p[0] = Constructor(name=p[1], lineno=p.lineno(1))
            else:
                p[0] = Identifier(name=p[1], lineno=p.lineno(1))
        else:
            p[0] = p[1]
    else:
        p[0] = p[2]


def p_tuple_expr(p):
    '''tuple_expr : LPAREN expression COMMA expression_list RPAREN'''
    p[0] = TupleExpr(elements=[p[2]] + p[4], lineno=p.lineno(1))


def p_expression_list(p):
    '''expression_list : expression_list COMMA expression
                       | expression'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_literal(p):
    '''literal : INTEGER
               | FLOAT_LIT
               | CHAR_LIT
               | STRING_LIT
               | TRUE
               | FALSE'''
    if isinstance(p[1], int):
        p[0] = IntLiteral(value=p[1], lineno=p.lineno(1))
    elif isinstance(p[1], float):
        p[0] = FloatLiteral(value=p[1], lineno=p.lineno(1))
    elif p[1] == 'True':
        p[0] = BoolLiteral(value=True, lineno=p.lineno(1))
    elif p[1] == 'False':
        p[0] = BoolLiteral(value=False, lineno=p.lineno(1))
    elif len(p[1]) == 1:
        p[0] = CharLiteral(value=p[1], lineno=p.lineno(1))
    else:
        p[0] = StringLiteral(value=p[1], lineno=p.lineno(1))


# ============================================================================
# LISTAS Y ARREGLOS
# ============================================================================

def p_list_expr(p):
    '''list_expr : LBRACKET expression_list RBRACKET
                 | LBRACKET RBRACKET'''
    if len(p) == 4:
        p[0] = ListExpr(elements=p[2], lineno=p.lineno(1))
    else:
        p[0] = ListExpr(elements=[], lineno=p.lineno(1))


def p_array_expr(p):
    '''array_expr : ARRAY LBRACKET expression_list RBRACKET
                  | ARRAY LBRACKET RBRACKET
                  | HASH_BRACKET expression_list RBRACKET
                  | HASH_BRACKET RBRACKET'''
    if len(p) == 5:
        p[0] = ArrayExpr(elements=p[3], lineno=p.lineno(1))
    elif len(p) == 4:
        if p[1] == '#[':
            p[0] = ArrayExpr(elements=p[2], lineno=p.lineno(1))
        else:
            p[0] = ArrayExpr(elements=[], lineno=p.lineno(1))
    else:
        p[0] = ArrayExpr(elements=[], lineno=p.lineno(1))


def p_matrix_expr(p):
    '''matrix_expr : MATRIX LBRACKET matrix_rows RBRACKET
                   | HASH_BRACE matrix_rows RBRACE'''
    p[0] = MatrixExpr(rows=p[3], lineno=p.lineno(1))


def p_matrix_rows(p):
    '''matrix_rows : matrix_rows SEMICOLON matrix_row
                   | matrix_row'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_matrix_row(p):
    '''matrix_row : expression_list'''
    p[0] = p[1]


def p_range_expr(p):
    '''range_expr : LBRACKET expression DOTDOT expression RBRACKET
                  | LBRACKET expression COMMA expression DOTDOT expression RBRACKET'''
    if len(p) == 6:
        p[0] = RangeExpr(start=p[2], end=p[4], lineno=p.lineno(1))
    else:
        p[0] = RangeExpr(start=p[2], end=p[6], step=p[4], lineno=p.lineno(1))


def p_list_comprehension(p):
    '''list_comprehension : LBRACKET expression PIPE qualifiers RBRACKET'''
    p[0] = ListComprehension(expr=p[2], qualifiers=p[4], lineno=p.lineno(1))


def p_qualifiers(p):
    '''qualifiers : qualifiers COMMA qualifier
                  | qualifier'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_qualifier(p):
    '''qualifier : IDENTIFIER LARROW expression
                 | expression'''
    if len(p) == 4:
        p[0] = GeneratorQual(var=p[1], expr=p[3], lineno=p.lineno(1))
    else:
        p[0] = FilterQual(condition=p[1], lineno=p.lineno(1))


# ============================================================================
# MODELO DE ACTORES (Prototipo Básico)
# ============================================================================

def p_actor_decl(p):
    '''actor_decl : ACTOR IDENTIFIER param_list ASSIGN expression'''
    p[0] = ActorDecl(name=p[2], params=p[3], body=p[5], lineno=p.lineno(1))


def p_spawn_expr(p):
    '''spawn_expr : SPAWN IDENTIFIER'''
    p[0] = SpawnExpr(actor_name=p[2], lineno=p.lineno(1))


def p_send_expr(p):
    '''send_expr : SEND postfix_expr postfix_expr'''
    p[0] = SendExpr(target=p[2], message=p[3], lineno=p.lineno(1))


# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

def p_error(p):
    if p:
        print(f"Error sintáctico en línea {p.lineno}: Token inesperado '{p.value}' (tipo: {p.type})")
    else:
        print("Error sintáctico: Fin de archivo inesperado")


# ============================================================================
# CONSTRUCCIÓN DEL PARSER
# ============================================================================

class FunLangParser:
    """Clase wrapper para el parser de FunLang"""
    
    def __init__(self):
        self.lexer = create_lexer()
        self.parser = yacc.yacc(debug=False, write_tables=False)
        self.errors = []
    
    def parse(self, data: str) -> Optional[Program]:
        """Parsea el código fuente y retorna el AST"""
        self.errors = []
        try:
            result = self.parser.parse(data, lexer=self.lexer.lexer)
            return result
        except Exception as e:
            self.errors.append(str(e))
            return None


def create_parser():
    """Factory function para crear un parser"""
    return FunLangParser()


# ============================================================================
# PRUEBA DEL PARSER
# ============================================================================

if __name__ == '__main__':
    test_code = '''
    -- Algoritmo de Euclides
    gcd :: Int -> Int -> Int
    gcd a 0 = a
    gcd a b = gcd b (a mod b)
    
    -- Función principal
    main = do
        let x = 48
        let y = 18
        let result = gcd(x, y)
        return result
    end
    '''
    
    parser = create_parser()
    ast = parser.parse(test_code)
    
    if ast:
        print("=" * 60)
        print("ANÁLISIS SINTÁCTICO - FunLang")
        print("=" * 60)
        printer = ASTPrinter()
        printer.visit(ast)
    else:
        print("Error en el análisis sintáctico")
