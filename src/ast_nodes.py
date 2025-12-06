"""
FunLang - Nodos del Árbol de Sintaxis Abstracta (AST)
Define todas las clases de nodos para representar el programa
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Union
from enum import Enum, auto


# ============================================================================
# ENUMERACIONES
# ============================================================================

class BinaryOp(Enum):
    """Operadores binarios"""
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    POW = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    AND = auto()
    OR = auto()
    CONS = auto()  # Lista cons (:)


class UnaryOp(Enum):
    """Operadores unarios"""
    NEG = auto()
    NOT = auto()


class TypeKind(Enum):
    """Tipos de datos básicos"""
    INT = "Int"
    FLOAT = "Float"
    DOUBLE = "Double"
    BOOL = "Bool"
    CHAR = "Char"
    STRING = "String"
    VOID = "Void"
    ARRAY = "Array"
    MATRIX = "Matrix"
    FUNCTION = "Function"
    CUSTOM = "Custom"
    INFERRED = "Inferred"


# ============================================================================
# CLASE BASE
# ============================================================================

@dataclass
class ASTNode:
    """Clase base para todos los nodos del AST"""
    lineno: int = 0
    column: int = 0
    
    def accept(self, visitor):
        """Patrón visitor para recorrer el AST"""
        method_name = f'visit_{self.__class__.__name__}'
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)


# ============================================================================
# TIPOS
# ============================================================================

@dataclass
class TypeNode(ASTNode):
    """Representa un tipo de dato"""
    kind: TypeKind = TypeKind.INFERRED
    name: str = ""
    params: List['TypeNode'] = field(default_factory=list)
    
    def __str__(self):
        if self.kind == TypeKind.FUNCTION and len(self.params) >= 2:
            return f"{self.params[0]} -> {self.params[1]}"
        elif self.kind == TypeKind.ARRAY:
            return f"[{self.params[0] if self.params else 'a'}]"
        elif self.kind == TypeKind.MATRIX:
            return f"Matrix {self.params[0] if self.params else 'a'}"
        elif self.kind == TypeKind.CUSTOM:
            return self.name
        else:
            return self.kind.value


@dataclass
class FunctionType(TypeNode):
    """Tipo función: a -> b"""
    param_type: Optional[TypeNode] = None
    return_type: Optional[TypeNode] = None
    
    def __post_init__(self):
        self.kind = TypeKind.FUNCTION


# ============================================================================
# LITERALES
# ============================================================================

@dataclass
class IntLiteral(ASTNode):
    """Literal entero"""
    value: int = 0


@dataclass
class FloatLiteral(ASTNode):
    """Literal de punto flotante"""
    value: float = 0.0


@dataclass
class BoolLiteral(ASTNode):
    """Literal booleano"""
    value: bool = False


@dataclass
class CharLiteral(ASTNode):
    """Literal de caracter"""
    value: str = ''


@dataclass
class StringLiteral(ASTNode):
    """Literal de string"""
    value: str = ""


# ============================================================================
# IDENTIFICADORES Y PATRONES
# ============================================================================

@dataclass
class Identifier(ASTNode):
    """Identificador (variable, función)"""
    name: str = ""


@dataclass
class Constructor(ASTNode):
    """Constructor de tipo de dato"""
    name: str = ""
    args: List[ASTNode] = field(default_factory=list)


@dataclass
class Pattern(ASTNode):
    """Patrón para pattern matching"""
    pass


@dataclass
class VarPattern(Pattern):
    """Patrón de variable"""
    name: str = ""


@dataclass
class LitPattern(Pattern):
    """Patrón de literal"""
    value: ASTNode = None


@dataclass
class WildcardPattern(Pattern):
    """Patrón comodín (_)"""
    pass


@dataclass
class ConsPattern(Pattern):
    """Patrón cons (x:xs)"""
    head: Pattern = None
    tail: Pattern = None


@dataclass
class ListPattern(Pattern):
    """Patrón de lista"""
    elements: List[Pattern] = field(default_factory=list)


@dataclass
class TuplePattern(Pattern):
    """Patrón de tupla"""
    elements: List[Pattern] = field(default_factory=list)


# ============================================================================
# EXPRESIONES
# ============================================================================

@dataclass
class Expression(ASTNode):
    """Clase base para expresiones"""
    inferred_type: Optional[TypeNode] = None


@dataclass
class BinaryExpr(Expression):
    """Expresión binaria"""
    op: BinaryOp = None
    left: Expression = None
    right: Expression = None


@dataclass
class UnaryExpr(Expression):
    """Expresión unaria"""
    op: UnaryOp = None
    operand: Expression = None


@dataclass
class FunctionCall(Expression):
    """Llamada a función"""
    func: Expression = None
    args: List[Expression] = field(default_factory=list)


@dataclass
class IndexExpr(Expression):
    """Acceso a índice de arreglo"""
    array: Expression = None
    index: Expression = None


@dataclass
class MatrixIndexExpr(Expression):
    """Acceso a índice de matriz"""
    matrix: Expression = None
    row: Expression = None
    col: Expression = None


@dataclass
class FieldAccess(Expression):
    """Acceso a campo de estructura"""
    obj: Expression = None
    field: str = ""


@dataclass
class IfExpr(Expression):
    """Expresión if-then-else"""
    condition: Expression = None
    then_branch: Expression = None
    else_branch: Expression = None


@dataclass
class LetExpr(Expression):
    """Expresión let-in"""
    bindings: List['LetBinding'] = field(default_factory=list)
    body: Expression = None


@dataclass
class LetBinding(ASTNode):
    """Binding de let"""
    name: str = ""
    value: Expression = None
    type_annotation: Optional[TypeNode] = None


@dataclass
class CaseExpr(Expression):
    """Expresión case-of"""
    expr: Expression = None
    alternatives: List['CaseAlt'] = field(default_factory=list)


@dataclass
class CaseAlt(ASTNode):
    """Alternativa de case"""
    pattern: Pattern = None
    body: Expression = None


@dataclass
class LambdaExpr(Expression):
    """Expresión lambda"""
    params: List[Pattern] = field(default_factory=list)
    body: Expression = None


@dataclass
class WhileExpr(Expression):
    """Expresión while"""
    condition: Expression = None
    body: Expression = None


@dataclass
class ForExpr(Expression):
    """Expresión for"""
    var: str = ""
    start: Expression = None
    end: Expression = None
    body: Expression = None
    collection: Expression = None  # Para for-in sobre colecciones


@dataclass
class DoBlock(Expression):
    """Bloque do"""
    statements: List['DoStatement'] = field(default_factory=list)


@dataclass
class DoStatement(ASTNode):
    """Sentencia dentro de bloque do"""
    pass


@dataclass
class DoExprStmt(DoStatement):
    """Expresión como sentencia"""
    expr: Expression = None


@dataclass
class DoBindStmt(DoStatement):
    """Binding en do (x <- expr)"""
    name: str = ""
    expr: Expression = None


@dataclass
class DoLetStmt(DoStatement):
    """Let en do (let x = expr)"""
    name: str = ""
    expr: Expression = None


@dataclass
class DoReturnStmt(DoStatement):
    """Return en do"""
    expr: Expression = None


# ============================================================================
# COLECCIONES
# ============================================================================

@dataclass
class ListExpr(Expression):
    """Expresión de lista"""
    elements: List[Expression] = field(default_factory=list)


@dataclass
class ArrayExpr(Expression):
    """Expresión de arreglo"""
    elements: List[Expression] = field(default_factory=list)


@dataclass
class MatrixExpr(Expression):
    """Expresión de matriz"""
    rows: List[List[Expression]] = field(default_factory=list)


@dataclass
class TupleExpr(Expression):
    """Expresión de tupla"""
    elements: List[Expression] = field(default_factory=list)


@dataclass
class RangeExpr(Expression):
    """Expresión de rango [a..b]"""
    start: Expression = None
    end: Expression = None
    step: Expression = None  # Para [a,b..c]


@dataclass
class ListComprehension(Expression):
    """Comprensión de lista [expr | qualifiers]"""
    expr: Expression = None
    qualifiers: List['Qualifier'] = field(default_factory=list)


@dataclass
class Qualifier(ASTNode):
    """Calificador en comprensión de lista"""
    pass


@dataclass
class GeneratorQual(Qualifier):
    """Generador (x <- list)"""
    var: str = ""
    expr: Expression = None


@dataclass
class FilterQual(Qualifier):
    """Filtro (condición)"""
    condition: Expression = None


# ============================================================================
# DECLARACIONES
# ============================================================================

@dataclass
class Declaration(ASTNode):
    """Clase base para declaraciones"""
    pass


@dataclass
class Program(ASTNode):
    """Nodo raíz del programa"""
    module: Optional[str] = None
    imports: List['Import'] = field(default_factory=list)
    declarations: List[Declaration] = field(default_factory=list)


@dataclass
class Import(ASTNode):
    """Declaración de importación"""
    module: str = ""
    alias: Optional[str] = None


@dataclass
class VarDecl(Declaration):
    """Declaración de variable"""
    name: str = ""
    var_type: Optional[TypeNode] = None
    value: Expression = None
    is_mutable: bool = True  # var vs let


@dataclass
class ConstDecl(Declaration):
    """Declaración de constante"""
    name: str = ""
    const_type: Optional[TypeNode] = None
    value: Expression = None


@dataclass
class FunctionDecl(Declaration):
    """Declaración de función"""
    name: str = ""
    params: List[Pattern] = field(default_factory=list)
    body: Expression = None
    type_sig: Optional[TypeNode] = None
    guards: List['GuardedExpr'] = field(default_factory=list)


@dataclass
class GuardedExpr(ASTNode):
    """Expresión con guarda (| condition = expr)"""
    guard: Expression = None
    body: Expression = None


@dataclass
class TypeDecl(Declaration):
    """Declaración de tipo (type alias)"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: TypeNode = None


@dataclass
class DataDecl(Declaration):
    """Declaración de tipo de dato algebraico"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    constructors: List['DataConstructor'] = field(default_factory=list)


@dataclass
class DataConstructor(ASTNode):
    """Constructor de tipo de dato"""
    name: str = ""
    fields: List[TypeNode] = field(default_factory=list)


@dataclass
class TypeSignature(Declaration):
    """Firma de tipo de función"""
    name: str = ""
    type_expr: TypeNode = None


# ============================================================================
# MODELO DE ACTORES (Prototipo Básico)
# ============================================================================

@dataclass
class ActorDecl(Declaration):
    """Declaración de un actor: actor name param = body"""
    name: str = ""
    params: List[Pattern] = field(default_factory=list)
    body: Expression = None


@dataclass
class SpawnExpr(Expression):
    """Crear un actor: spawn ActorName"""
    actor_name: str = ""


@dataclass
class SendExpr(Expression):
    """Enviar mensaje: send actor mensaje"""
    target: Expression = None
    message: Expression = None


@dataclass
class ReceiveExpr(Expression):
    """Recibir mensajes: receive pattern -> expr end"""
    handlers: List['ReceiveHandler'] = field(default_factory=list)


@dataclass
class ReceiveHandler(ASTNode):
    """Handler de mensaje en receive"""
    pattern: Pattern = None
    body: Expression = None


# ============================================================================
# VISITOR PARA RECORRER EL AST
# ============================================================================

class ASTVisitor:
    """Clase base para visitantes del AST"""
    
    def visit(self, node: ASTNode):
        """Visita un nodo"""
        if node is None:
            return None
        return node.accept(self)
    
    def generic_visit(self, node: ASTNode):
        """Visita genérica para nodos no manejados"""
        raise NotImplementedError(f"No hay visitor para {node.__class__.__name__}")
    
    def visit_children(self, node: ASTNode):
        """Visita todos los hijos de un nodo"""
        for field_name in node.__dataclass_fields__:
            value = getattr(node, field_name)
            if isinstance(value, ASTNode):
                self.visit(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ASTNode):
                        self.visit(item)


class ASTPrinter(ASTVisitor):
    """Imprime el AST de forma legible"""
    
    def __init__(self):
        self.indent = 0
    
    def print_node(self, name: str, **fields):
        """Imprime un nodo con indentación"""
        indent_str = "  " * self.indent
        print(f"{indent_str}{name}")
        self.indent += 1
        for key, value in fields.items():
            if isinstance(value, ASTNode):
                print(f"{indent_str}  {key}:")
                self.indent += 1
                self.visit(value)
                self.indent -= 1
            elif isinstance(value, list):
                print(f"{indent_str}  {key}:")
                self.indent += 1
                for item in value:
                    if isinstance(item, ASTNode):
                        self.visit(item)
                    else:
                        print(f"{'  ' * self.indent}{item}")
                self.indent -= 1
            else:
                print(f"{indent_str}  {key}: {value}")
        self.indent -= 1
    
    def visit_Program(self, node: Program):
        self.print_node("Program", module=node.module, imports=node.imports, declarations=node.declarations)
    
    def visit_IntLiteral(self, node: IntLiteral):
        self.print_node("IntLiteral", value=node.value)
    
    def visit_FloatLiteral(self, node: FloatLiteral):
        self.print_node("FloatLiteral", value=node.value)
    
    def visit_BoolLiteral(self, node: BoolLiteral):
        self.print_node("BoolLiteral", value=node.value)
    
    def visit_StringLiteral(self, node: StringLiteral):
        self.print_node("StringLiteral", value=node.value)
    
    def visit_Identifier(self, node: Identifier):
        self.print_node("Identifier", id_name=node.name)
    
    def visit_BinaryExpr(self, node: BinaryExpr):
        self.print_node("BinaryExpr", op=node.op, left=node.left, right=node.right)
    
    def visit_UnaryExpr(self, node: UnaryExpr):
        self.print_node("UnaryExpr", op=node.op, operand=node.operand)
    
    def visit_IfExpr(self, node: IfExpr):
        self.print_node("IfExpr", condition=node.condition, then_branch=node.then_branch, else_branch=node.else_branch)
    
    def visit_FunctionDecl(self, node: FunctionDecl):
        self.print_node("FunctionDecl", func_name=node.name, params=node.params, body=node.body)
    
    def visit_VarDecl(self, node: VarDecl):
        self.print_node("VarDecl", var_name=node.name, value=node.value)
    
    def visit_FunctionCall(self, node: FunctionCall):
        self.print_node("FunctionCall", func=node.func, args=node.args)
    
    def visit_ListExpr(self, node: ListExpr):
        self.print_node("ListExpr", elements=node.elements)
    
    def visit_DoBlock(self, node: DoBlock):
        self.print_node("DoBlock", statements=node.statements)
    
    def generic_visit(self, node: ASTNode):
        self.print_node(node.__class__.__name__)
