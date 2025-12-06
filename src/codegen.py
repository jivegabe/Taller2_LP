"""
FunLang - Generador de Código C++
Genera código C++ ejecutable desde el AST
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from .ast_nodes import *


# ============================================================================
# GENERADOR DE CÓDIGO C++
# ============================================================================

class CppCodeGenerator(ASTVisitor):
    """Genera código C++ desde el AST de FunLang"""
    
    def __init__(self):
        self.indent_level = 0
        self.output: List[str] = []
        self.includes: Set[str] = set()
        self.function_defs: List[str] = []
        self.global_vars: List[str] = []
        self.main_code: List[str] = []
        self.current_context = "global"  # "global", "function", "main"
        self.temp_counter = 0
        self.functions_declared: Set[str] = set()
        self.actors_declared: Set[str] = set()
        self.uses_actors = False
    
    def generate(self, ast: Program) -> str:
        """Genera código C++ desde el AST"""
        self.output = []
        self.includes = {"iostream", "vector", "string", "cmath", "functional", "algorithm"}
        self.function_defs = []
        self.global_vars = []
        self.main_code = []
        
        # Visitar el AST
        self.visit(ast)
        
        # Construir el código final
        return self._build_output()
    
    def _build_output(self) -> str:
        """Construye el código C++ final"""
        lines = []
        
        # Includes
        lines.append("// Código generado por FunLang Compiler")
        lines.append("// Lenguaje funcional -> C++")
        lines.append("")
        
        # Añadir includes para actores si es necesario
        if self.uses_actors:
            self.includes.add("thread")
            self.includes.add("queue")
            self.includes.add("mutex")
            self.includes.add("memory")
            self.includes.add("any")
        
        for inc in sorted(self.includes):
            lines.append(f"#include <{inc}>")
        lines.append("")
        
        # Using namespace
        lines.append("using namespace std;")
        lines.append("")
        
        # Tipos y utilidades
        lines.extend(self._generate_runtime())
        lines.append("")
        
        # Runtime de actores si se usan
        if self.uses_actors:
            lines.extend(self._generate_actor_runtime())
            lines.append("")
        
        # Variables globales
        if self.global_vars:
            lines.append("// Variables globales")
            lines.extend(self.global_vars)
            lines.append("")
        
        # Declaraciones forward de funciones
        if self.functions_declared:
            lines.append("// Declaraciones forward")
            for func in self.functions_declared:
                lines.append(f"auto {func}();")
            lines.append("")
        
        # Definiciones de funciones
        if self.function_defs:
            lines.append("// Funciones")
            lines.extend(self.function_defs)
            lines.append("")
        
        # Main
        lines.append("int main() {")
        if self.main_code:
            for line in self.main_code:
                lines.append("    " + line)
        else:
            lines.append("    // No hay código principal")
        if self.uses_actors:
            lines.append("    // Esperar a que los actores procesen todos los mensajes")
            lines.append("    actorSystem.wait_all();")
        lines.append("    return 0;")
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_runtime(self) -> List[str]:
        """Genera el runtime de FunLang"""
        return [
            "// ============= Runtime de FunLang =============",
            "",
            "// Tipo para listas/arreglos dinámicos",
            "template<typename T>",
            "using List = vector<T>;",
            "",
            "// Tipo para matrices",
            "template<typename T>",
            "using Matrix = vector<vector<T>>;",
            "",
            "// Funciones de lista",
            "template<typename T>",
            "int length(const List<T>& xs) { return xs.size(); }",
            "",
            "template<typename T>",
            "T head(const List<T>& xs) { return xs.front(); }",
            "",
            "template<typename T>",
            "List<T> tail(const List<T>& xs) { return List<T>(xs.begin()+1, xs.end()); }",
            "",
            "template<typename T>",
            "T last(const List<T>& xs) { return xs.back(); }",
            "",
            "template<typename T>",
            "List<T> init(const List<T>& xs) { return List<T>(xs.begin(), xs.end()-1); }",
            "",
            "template<typename T>",
            "List<T> take(int n, const List<T>& xs) {",
            "    return List<T>(xs.begin(), xs.begin() + min((size_t)n, xs.size()));",
            "}",
            "",
            "template<typename T>",
            "List<T> drop(int n, const List<T>& xs) {",
            "    return List<T>(xs.begin() + min((size_t)n, xs.size()), xs.end());",
            "}",
            "",
            "template<typename T>",
            "List<T> reverse_list(const List<T>& xs) {",
            "    List<T> result(xs.rbegin(), xs.rend());",
            "    return result;",
            "}",
            "",
            "template<typename T>",
            "List<T> concat(const List<T>& xs, const List<T>& ys) {",
            "    List<T> result = xs;",
            "    result.insert(result.end(), ys.begin(), ys.end());",
            "    return result;",
            "}",
            "",
            "template<typename T>",
            "T sum(const List<T>& xs) {",
            "    T result = 0;",
            "    for (const auto& x : xs) result += x;",
            "    return result;",
            "}",
            "",
            "template<typename T>",
            "T product(const List<T>& xs) {",
            "    T result = 1;",
            "    for (const auto& x : xs) result *= x;",
            "    return result;",
            "}",
            "",
            "template<typename T>",
            "bool elem(const T& x, const List<T>& xs) {",
            "    return find(xs.begin(), xs.end(), x) != xs.end();",
            "}",
            "",
            "// Función range [a..b]",
            "List<int> range(int start, int end) {",
            "    List<int> result;",
            "    for (int i = start; i <= end; i++) result.push_back(i);",
            "    return result;",
            "}",
            "",
            "// Función range con paso [a,b..c]",
            "List<int> range_step(int start, int next, int end) {",
            "    List<int> result;",
            "    int step = next - start;",
            "    if (step > 0) {",
            "        for (int i = start; i <= end; i += step) result.push_back(i);",
            "    } else if (step < 0) {",
            "        for (int i = start; i >= end; i += step) result.push_back(i);",
            "    }",
            "    return result;",
            "}",
            "",
            "// Map",
            "template<typename T, typename F>",
            "auto map_list(F f, const List<T>& xs) {",
            "    List<decltype(f(xs[0]))> result;",
            "    for (const auto& x : xs) result.push_back(f(x));",
            "    return result;",
            "}",
            "",
            "// Filter",
            "template<typename T, typename F>",
            "List<T> filter_list(F f, const List<T>& xs) {",
            "    List<T> result;",
            "    for (const auto& x : xs) if (f(x)) result.push_back(x);",
            "    return result;",
            "}",
            "",
            "// Foldl",
            "template<typename T, typename R, typename F>",
            "R foldl(F f, R acc, const List<T>& xs) {",
            "    for (const auto& x : xs) acc = f(acc, x);",
            "    return acc;",
            "}",
            "",
            "// Funciones de I/O",
            "template<typename T>",
            "void print(const T& x) { cout << x; }",
            "",
            "template<typename T>",
            "void println(const T& x) { cout << x << endl; }",
            "",
            "string readLine() { string s; getline(cin, s); return s; }",
            "int readInt() { int x; cin >> x; return x; }",
            "double readFloat() { double x; cin >> x; return x; }",
            "",
            "// Conversiones",
            "int toInt(double x) { return (int)x; }",
            "int toInt(const string& s) { return stoi(s); }",
            "double toFloat(int x) { return (double)x; }",
            "double toFloat(const string& s) { return stod(s); }",
            "string toString(int x) { return to_string(x); }",
            "string toString(double x) { return to_string(x); }",
            "",
            "// Funciones matemáticas adicionales",
            "template<typename T>",
            "T min_val(T a, T b) { return a < b ? a : b; }",
            "",
            "template<typename T>",
            "T max_val(T a, T b) { return a > b ? a : b; }",
            "",
            "// ============= Fin Runtime =============",
        ]
    
    def _generate_actor_runtime(self) -> List[str]:
        """Genera runtime básico para actores"""
        return [
            "// ============= Runtime de Actores (Básico) =============",
            "",
            "// Helper para imprimir any",
            "void print_any(const any& a) {",
            "    if (a.type() == typeid(int)) cout << any_cast<int>(a);",
            "    else if (a.type() == typeid(double)) cout << any_cast<double>(a);",
            "    else if (a.type() == typeid(string)) cout << any_cast<string>(a);",
            "    else if (a.type() == typeid(const char*)) cout << any_cast<const char*>(a);",
            "    else cout << \"[any]\";",
            "}",
            "",
            "void println(const any& x) { print_any(x); cout << endl; }",
            "",
            "// Actor simple con cola de mensajes",
            "class Actor {",
            "protected:",
            "    queue<any> mailbox;",
            "    mutex mtx;",
            "    bool running = true;",
            "    thread worker;",
            "    function<void(any)> handler;",
            "",
            "public:",
            "    virtual ~Actor() { stop(); }",
            "",
            "    void send(any msg) {",
            "        lock_guard<mutex> lock(mtx);",
            "        mailbox.push(msg);",
            "    }",
            "",
            "    bool empty() {",
            "        lock_guard<mutex> lock(mtx);",
            "        return mailbox.empty();",
            "    }",
            "",
            "    void start() {",
            "        worker = thread([this]() {",
            "            while (running) {",
            "                any msg;",
            "                {",
            "                    lock_guard<mutex> lock(mtx);",
            "                    if (!mailbox.empty()) {",
            "                        msg = mailbox.front();",
            "                        mailbox.pop();",
            "                    } else {",
            "                        this_thread::sleep_for(chrono::milliseconds(10));",
            "                        continue;",
            "                    }",
            "                }",
            "                if (handler) handler(msg);",
            "            }",
            "        });",
            "    }",
            "",
            "    void stop() {",
            "        running = false;",
            "        if (worker.joinable()) worker.join();",
            "    }",
            "",
            "    void set_handler(function<void(any)> h) { handler = h; }",
            "};",
            "",
            "// Sistema de actores simple",
            "class ActorSystem {",
            "    vector<shared_ptr<Actor>> actors;",
            "public:",
            "    template<typename T>",
            "    shared_ptr<T> spawn() {",
            "        auto actor = make_shared<T>();",
            "        actor->start();",
            "        actors.push_back(actor);",
            "        return actor;",
            "    }",
            "    ",
            "    void wait_all() {",
            "        // Esperar a que todos los mailboxes estén vacíos",
            "        bool all_empty = false;",
            "        while (!all_empty) {",
            "            all_empty = true;",
            "            for (auto& a : actors) {",
            "                if (!a->empty()) {",
            "                    all_empty = false;",
            "                    break;",
            "                }",
            "            }",
            "            if (!all_empty) this_thread::sleep_for(chrono::milliseconds(10));",
            "        }",
            "        // Pequeña espera para el último mensaje en proceso",
            "        this_thread::sleep_for(chrono::milliseconds(50));",
            "    }",
            "};",
            "",
            "ActorSystem actorSystem;",
            "",
            "// ============= Fin Runtime de Actores =============",
        ]
    
    def indent(self) -> str:
        """Retorna la indentación actual"""
        return "    " * self.indent_level
    
    def emit(self, code: str):
        """Emite código según el contexto actual"""
        if self.current_context == "function":
            self.function_defs.append(self.indent() + code)
        elif self.current_context == "main":
            self.main_code.append(code)
        else:
            self.global_vars.append(code)
    
    def new_temp(self) -> str:
        """Genera un nombre de variable temporal"""
        self.temp_counter += 1
        return f"_temp{self.temp_counter}"
    
    # ========================================================================
    # VISITORS
    # ========================================================================
    
    def visit_Program(self, node: Program):
        """Visita el programa principal"""
        # Procesar declaraciones
        for decl in node.declarations:
            if isinstance(decl, FunctionDecl) and decl.name == "main":
                self.current_context = "main"
                self._generate_main_function(decl)
            elif isinstance(decl, (VarDecl, ConstDecl)):
                self.current_context = "global"
                self.visit(decl)
            elif isinstance(decl, FunctionDecl):
                self.current_context = "function"
                self.visit(decl)
            elif isinstance(decl, ActorDecl):
                self.uses_actors = True
                self.visit(decl)
            elif isinstance(decl, TypeSignature):
                pass  # Las firmas se manejan junto con las funciones
    
    def _generate_main_function(self, node: FunctionDecl):
        """Genera el código de la función main"""
        if node.body:
            code = self.visit(node.body)
            if code:
                self.main_code.append(code + ";")
    
    def visit_FunctionDecl(self, node: FunctionDecl):
        """Visita una declaración de función"""
        if node.name == "main":
            return  # main se maneja aparte
        
        # Para compatibilidad con C++14/17, usamos templates y tipos explícitos
        num_params = len(node.params)
        
        # Analizar si la función es recursiva
        is_recursive = self._is_recursive_function(node)
        
        if num_params > 0:
            # Generar parámetros de template
            template_params = ", ".join([f"typename T{i}" for i in range(num_params)])
            self.function_defs.append(f"template<{template_params}>")
            
            # Declarar la función con tipos de template
            params = []
            for i, param in enumerate(node.params):
                param_name = self._pattern_to_name(param)
                params.append(f"T{i} {param_name}")
            params_str = ", ".join(params)
            
            # Para funciones recursivas, usar T0 como tipo de retorno
            if is_recursive:
                return_type = "T0"
            else:
                return_type = "auto"
        else:
            params_str = ""
            return_type = "int"  # Default para funciones sin parámetros
        
        self.function_defs.append(f"{return_type} {node.name}({params_str}) {{")
        self.indent_level += 1
        
        if node.body:
            body_code = self.visit(node.body)
            self.function_defs.append(f"{self.indent()}return {body_code};")
        elif node.guards:
            for guard in node.guards:
                guard_code = self.visit(guard.guard)
                body_code = self.visit(guard.body)
                self.function_defs.append(f"{self.indent()}if ({guard_code}) return {body_code};")
            self.function_defs.append(f'{self.indent()}throw runtime_error("No matching guard");')
        
        self.indent_level -= 1
        self.function_defs.append("}")
        self.function_defs.append("")
    
    def _is_recursive_function(self, node: FunctionDecl) -> bool:
        """Detecta si una función es recursiva"""
        func_name = node.name
        
        def check_recursive(expr):
            if expr is None:
                return False
            if isinstance(expr, FunctionCall):
                if isinstance(expr.func, Identifier) and expr.func.name == func_name:
                    return True
                for arg in expr.args:
                    if check_recursive(arg):
                        return True
            elif isinstance(expr, BinaryExpr):
                return check_recursive(expr.left) or check_recursive(expr.right)
            elif isinstance(expr, UnaryExpr):
                return check_recursive(expr.operand)
            elif isinstance(expr, IfExpr):
                return (check_recursive(expr.condition) or 
                        check_recursive(expr.then_branch) or 
                        check_recursive(expr.else_branch))
            elif isinstance(expr, LetExpr):
                for binding in expr.bindings:
                    if check_recursive(binding.value):
                        return True
                return check_recursive(expr.body)
            elif isinstance(expr, DoBlock):
                for stmt in expr.statements:
                    if hasattr(stmt, 'expr') and check_recursive(stmt.expr):
                        return True
            elif isinstance(expr, LambdaExpr):
                return check_recursive(expr.body)
            return False
        
        if node.body:
            return check_recursive(node.body)
        elif node.guards:
            for guard in node.guards:
                if check_recursive(guard.body):
                    return True
        return False
    
    def _pattern_to_name(self, pattern: Pattern) -> str:
        """Convierte un patrón a un nombre de parámetro"""
        if isinstance(pattern, VarPattern):
            return pattern.name
        elif isinstance(pattern, LitPattern):
            return self.new_temp()
        elif isinstance(pattern, WildcardPattern):
            return "_"
        else:
            return self.new_temp()
    
    def visit_VarDecl(self, node: VarDecl) -> str:
        """Visita una declaración de variable"""
        value_code = self.visit(node.value)
        cpp_type = self._type_to_cpp(node.var_type) if node.var_type else "auto"
        
        if self.current_context == "global":
            self.global_vars.append(f"{cpp_type} {node.name} = {value_code};")
            return ""
        else:
            return f"{cpp_type} {node.name} = {value_code}"
    
    def visit_ConstDecl(self, node: ConstDecl) -> str:
        """Visita una declaración de constante"""
        value_code = self.visit(node.value)
        cpp_type = self._type_to_cpp(node.const_type) if node.const_type else "auto"
        
        if self.current_context == "global":
            self.global_vars.append(f"const {cpp_type} {node.name} = {value_code};")
            return ""
        else:
            return f"const {cpp_type} {node.name} = {value_code}"
    
    def _type_to_cpp(self, type_node: TypeNode) -> str:
        """Convierte un tipo de FunLang a C++"""
        if type_node is None:
            return "auto"
        
        type_map = {
            TypeKind.INT: "int",
            TypeKind.FLOAT: "double",
            TypeKind.DOUBLE: "double",
            TypeKind.BOOL: "bool",
            TypeKind.CHAR: "char",
            TypeKind.STRING: "string",
            TypeKind.VOID: "void",
            TypeKind.INFERRED: "auto",
        }
        
        if type_node.kind in type_map:
            return type_map[type_node.kind]
        elif type_node.kind == TypeKind.ARRAY:
            elem_type = self._type_to_cpp(type_node.params[0]) if type_node.params else "auto"
            return f"List<{elem_type}>"
        elif type_node.kind == TypeKind.MATRIX:
            elem_type = self._type_to_cpp(type_node.params[0]) if type_node.params else "double"
            return f"Matrix<{elem_type}>"
        elif type_node.kind == TypeKind.FUNCTION:
            return "auto"
        else:
            return "auto"
    
    def visit_IfExpr(self, node: IfExpr) -> str:
        """Visita una expresión if"""
        cond = self.visit(node.condition)
        then_code = self.visit(node.then_branch)
        else_code = self.visit(node.else_branch)
        return f"({cond} ? {then_code} : {else_code})"
    
    def visit_LetExpr(self, node: LetExpr) -> str:
        """Visita una expresión let"""
        # Usar una lambda inmediatamente invocada para let-in
        bindings = []
        for binding in node.bindings:
            value_code = self.visit(binding.value)
            bindings.append(f"auto {binding.name} = {value_code};")
        
        body_code = self.visit(node.body)
        
        bindings_str = " ".join(bindings)
        return f"[&]() {{ {bindings_str} return {body_code}; }}()"
    
    def visit_CaseExpr(self, node: CaseExpr) -> str:
        """Visita una expresión case (simplificado)"""
        expr_code = self.visit(node.expr)
        temp = self.new_temp()
        
        # Generar código para cada alternativa
        conditions = []
        for alt in node.alternatives:
            if isinstance(alt.pattern, LitPattern):
                pattern_code = self.visit(alt.pattern.value)
                body_code = self.visit(alt.body)
                conditions.append(f"({temp} == {pattern_code} ? {body_code}")
            elif isinstance(alt.pattern, WildcardPattern):
                body_code = self.visit(alt.body)
                conditions.append(body_code)
            elif isinstance(alt.pattern, VarPattern):
                body_code = self.visit(alt.body)
                conditions.append(body_code)
        
        if len(conditions) == 1:
            return f"[&]() {{ auto {temp} = {expr_code}; return {conditions[0]}; }}()"
        else:
            result = conditions[-1]
            for cond in reversed(conditions[:-1]):
                result = f"{cond} : {result})"
            return f"[&]() {{ auto {temp} = {expr_code}; return {result}; }}()"
    
    def visit_LambdaExpr(self, node: LambdaExpr) -> str:
        """Visita una expresión lambda"""
        params = []
        for param in node.params:
            param_name = self._pattern_to_name(param)
            params.append(f"auto {param_name}")
        
        params_str = ", ".join(params)
        body_code = self.visit(node.body)
        return f"[&]({params_str}) {{ return {body_code}; }}"
    
    def visit_WhileExpr(self, node: WhileExpr) -> str:
        """Visita una expresión while"""
        cond = self.visit(node.condition)
        body = self.visit(node.body)
        return f"[&]() {{ while ({cond}) {{ {body}; }} }}()"
    
    def visit_ForExpr(self, node: ForExpr) -> str:
        """Visita una expresión for"""
        var = node.var
        
        if node.start and node.end:
            start = self.visit(node.start)
            end = self.visit(node.end)
            body = self.visit(node.body)
            return f"[&]() {{ for (int {var} = {start}; {var} <= {end}; {var}++) {{ {body}; }} }}()"
        elif node.collection:
            coll = self.visit(node.collection)
            body = self.visit(node.body)
            return f"[&]() {{ for (auto& {var} : {coll}) {{ {body}; }} }}()"
        
        return ""
    
    def visit_DoBlock(self, node: DoBlock) -> str:
        """Visita un bloque do"""
        statements = []
        last_value = "0"
        last_is_void = False
        
        for stmt in node.statements:
            if isinstance(stmt, DoExprStmt):
                code = self.visit(stmt.expr)
                statements.append(f"{code};")
                last_value = code
                # Detectar si es println/print (void)
                last_is_void = "println" in code or "print(" in code or "->send(" in code
            elif isinstance(stmt, DoBindStmt):
                code = self.visit(stmt.expr)
                statements.append(f"auto {stmt.name} = {code};")
                last_is_void = False
            elif isinstance(stmt, DoLetStmt):
                code = self.visit(stmt.expr)
                statements.append(f"auto {stmt.name} = {code};")
                last_is_void = False
            elif isinstance(stmt, DoReturnStmt):
                code = self.visit(stmt.expr)
                last_value = code
                last_is_void = False
        
        stmts_str = " ".join(statements)
        if last_is_void:
            return f"[&]() {{ {stmts_str} return 0; }}()"
        else:
            return f"[&]() {{ {stmts_str} return {last_value}; }}()"
    
    def visit_BinaryExpr(self, node: BinaryExpr) -> str:
        """Visita una expresión binaria"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        op_map = {
            BinaryOp.ADD: "+",
            BinaryOp.SUB: "-",
            BinaryOp.MUL: "*",
            BinaryOp.DIV: "/",
            BinaryOp.MOD: "%",
            BinaryOp.POW: None,  # Especial
            BinaryOp.EQ: "==",
            BinaryOp.NEQ: "!=",
            BinaryOp.LT: "<",
            BinaryOp.GT: ">",
            BinaryOp.LE: "<=",
            BinaryOp.GE: ">=",
            BinaryOp.AND: "&&",
            BinaryOp.OR: "||",
        }
        
        if node.op == BinaryOp.POW:
            self.includes.add("cmath")
            return f"pow({left}, {right})"
        
        op = op_map.get(node.op, "?")
        return f"({left} {op} {right})"
    
    def visit_UnaryExpr(self, node: UnaryExpr) -> str:
        """Visita una expresión unaria"""
        operand = self.visit(node.operand)
        
        if node.op == UnaryOp.NEG:
            return f"(-{operand})"
        elif node.op == UnaryOp.NOT:
            return f"(!{operand})"
        
        return operand
    
    def visit_FunctionCall(self, node: FunctionCall) -> str:
        """Visita una llamada a función"""
        if isinstance(node.func, Identifier):
            func_name = node.func.name
        else:
            func_name = self.visit(node.func)
        
        args = [self.visit(arg) for arg in node.args]
        args_str = ", ".join(args)
        
        # Mapear funciones built-in
        builtin_map = {
            "print": "print",
            "println": "println",
            "readLine": "readLine",
            "readInt": "readInt",
            "readFloat": "readFloat",
            "length": "length",
            "head": "head",
            "tail": "tail",
            "last": "last",
            "init": "init",
            "take": "take",
            "drop": "drop",
            "reverse": "reverse_list",
            "concat": "concat",
            "sum": "sum",
            "product": "product",
            "elem": "elem",
            "map": "map_list",
            "filter": "filter_list",
            "foldl": "foldl",
            "abs": "abs",
            "sqrt": "sqrt",
            "sin": "sin",
            "cos": "cos",
            "tan": "tan",
            "log": "log",
            "exp": "exp",
            "floor": "floor",
            "ceil": "ceil",
            "round": "round",
            "pow": "pow",
            "min": "min_val",
            "max": "max_val",
            "toInt": "toInt",
            "toFloat": "toFloat",
            "toString": "toString",
        }
        
        if func_name in builtin_map:
            func_name = builtin_map[func_name]
        
        return f"{func_name}({args_str})"
    
    def visit_IndexExpr(self, node: IndexExpr) -> str:
        """Visita un acceso por índice"""
        array = self.visit(node.array)
        index = self.visit(node.index)
        return f"{array}[{index}]"
    
    def visit_MatrixIndexExpr(self, node: MatrixIndexExpr) -> str:
        """Visita un acceso a matriz"""
        matrix = self.visit(node.matrix)
        row = self.visit(node.row)
        col = self.visit(node.col)
        return f"{matrix}[{row}][{col}]"
    
    def visit_Identifier(self, node: Identifier) -> str:
        """Visita un identificador"""
        return node.name
    
    def visit_Constructor(self, node: Constructor) -> str:
        """Visita un constructor"""
        return node.name
    
    def visit_IntLiteral(self, node: IntLiteral) -> str:
        return str(node.value)
    
    def visit_FloatLiteral(self, node: FloatLiteral) -> str:
        return str(node.value)
    
    def visit_BoolLiteral(self, node: BoolLiteral) -> str:
        return "true" if node.value else "false"
    
    def visit_CharLiteral(self, node: CharLiteral) -> str:
        escaped = node.value.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
    
    def visit_StringLiteral(self, node: StringLiteral) -> str:
        escaped = node.value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")
        return f'"{escaped}"'
    
    def visit_ListExpr(self, node: ListExpr) -> str:
        """Visita una expresión de lista"""
        elements = [self.visit(elem) for elem in node.elements]
        elements_str = ", ".join(elements)
        return f"List<decltype({elements[0] if elements else '0'})>{{{elements_str}}}"
    
    def visit_ArrayExpr(self, node: ArrayExpr) -> str:
        """Visita una expresión de arreglo"""
        elements = [self.visit(elem) for elem in node.elements]
        elements_str = ", ".join(elements)
        return f"List<decltype({elements[0] if elements else '0'})>{{{elements_str}}}"
    
    def visit_MatrixExpr(self, node: MatrixExpr) -> str:
        """Visita una expresión de matriz"""
        rows = []
        for row in node.rows:
            elems = [self.visit(elem) for elem in row]
            rows.append("{" + ", ".join(elems) + "}")
        rows_str = ", ".join(rows)
        return f"Matrix<double>{{{rows_str}}}"
    
    def visit_TupleExpr(self, node: TupleExpr) -> str:
        """Visita una expresión de tupla"""
        self.includes.add("tuple")
        elements = [self.visit(elem) for elem in node.elements]
        elements_str = ", ".join(elements)
        return f"make_tuple({elements_str})"
    
    def visit_RangeExpr(self, node: RangeExpr) -> str:
        """Visita una expresión de rango"""
        start = self.visit(node.start)
        end = self.visit(node.end)
        
        if node.step:
            step = self.visit(node.step)
            return f"range_step({start}, {step}, {end})"
        else:
            return f"range({start}, {end})"
    
    def visit_ListComprehension(self, node: ListComprehension) -> str:
        """Visita una comprensión de lista"""
        # [expr | var <- list, cond]
        # se convierte a filter_list + map_list
        
        generators = []
        filters = []
        
        for qual in node.qualifiers:
            if isinstance(qual, GeneratorQual):
                generators.append((qual.var, self.visit(qual.expr)))
            elif isinstance(qual, FilterQual):
                filters.append(self.visit(qual.condition))
        
        if not generators:
            return "List<int>{}"
        
        var, coll = generators[0]
        expr = self.visit(node.expr)
        
        # Construir la expresión
        result = coll
        
        # Aplicar filtros
        for filt in filters:
            result = f"filter_list([&](auto {var}) {{ return {filt}; }}, {result})"
        
        # Aplicar transformación
        result = f"map_list([&](auto {var}) {{ return {expr}; }}, {result})"
        
        return result
    
    # ========================================================================
    # VISITORS PARA ACTORES
    # ========================================================================
    
    def visit_ActorDecl(self, node: ActorDecl) -> str:
        """Genera código para una declaración de actor"""
        self.actors_declared.add(node.name)
        
        params = [self._pattern_to_name(p) for p in node.params]
        params_str = ", ".join([f"any {p}" for p in params])
        
        # Generar clase actor
        lines = [
            f"// Actor: {node.name}",
            f"class {node.name}Actor : public Actor {{",
            "public:",
            f"    {node.name}Actor() {{",
            "        set_handler([this](any _msg) { this->handle(_msg); });",
            "    }",
            "",
            "    void handle(any _msg) {",
        ]
        
        # Generar cuerpo del handler
        if node.body:
            body_code = self.visit(node.body)
            if params:
                lines.append(f"        auto {params[0]} = _msg;")
            lines.append(f"        {body_code};")
        
        lines.extend([
            "    }",
            "};",
            "",
        ])
        
        self.function_defs.extend(lines)
        return ""
    
    def visit_SpawnExpr(self, node: SpawnExpr) -> str:
        """Genera código para spawn de actor"""
        self.uses_actors = True
        actor_name = node.actor_name
        return f"actorSystem.spawn<{actor_name}Actor>()"
    
    def visit_SendExpr(self, node: SendExpr) -> str:
        """Genera código para envío de mensaje"""
        target = self.visit(node.target)
        message = self.visit(node.message)
        return f"{target}->send({message})"
    
    def generic_visit(self, node: ASTNode) -> str:
        """Visita genérica"""
        return ""


def create_generator():
    """Factory function para crear un generador de código"""
    return CppCodeGenerator()
