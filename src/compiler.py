"""
FunLang - Compilador Principal
Integra lexer, parser, analizador semántico y generador de código
"""

import os
import sys
import subprocess
from typing import Optional, Tuple
from dataclasses import dataclass

from .lexer import create_lexer
from .parser import create_parser
from .semantic import create_analyzer
from .codegen import create_generator
from .ast_nodes import Program, ASTPrinter


@dataclass
class CompilationResult:
    """Resultado de la compilación"""
    success: bool
    cpp_code: str = ""
    output_file: str = ""
    errors: list = None
    warnings: list = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class FunLangCompiler:
    """Compilador de FunLang a C++"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.lexer = create_lexer()
        self.parser = create_parser()
        self.analyzer = create_analyzer()
        self.generator = create_generator()
    
    def compile(self, source_code: str, output_path: Optional[str] = None) -> CompilationResult:
        """
        Compila código FunLang a C++
        
        Args:
            source_code: Código fuente en FunLang
            output_path: Ruta para el archivo C++ generado
        
        Returns:
            CompilationResult con el resultado de la compilación
        """
        result = CompilationResult(success=False)
        
        # Fase 1: Análisis Léxico
        if self.verbose:
            print("=" * 60)
            print("FASE 1: Análisis Léxico")
            print("=" * 60)
        
        tokens = self.lexer.tokenize(source_code)
        
        if self.verbose:
            print(f"Tokens encontrados: {len(tokens)}")
            for tok in tokens[:20]:  # Mostrar solo los primeros 20
                print(f"  {tok}")
            if len(tokens) > 20:
                print(f"  ... y {len(tokens) - 20} más")
        
        # Fase 2: Análisis Sintáctico
        if self.verbose:
            print("\n" + "=" * 60)
            print("FASE 2: Análisis Sintáctico")
            print("=" * 60)
        
        ast = self.parser.parse(source_code)
        
        if ast is None:
            result.errors = ["Error en el análisis sintáctico"]
            return result
        
        if self.verbose:
            print("AST generado correctamente")
            printer = ASTPrinter()
            printer.visit(ast)
        
        # Fase 3: Análisis Semántico
        if self.verbose:
            print("\n" + "=" * 60)
            print("FASE 3: Análisis Semántico")
            print("=" * 60)
        
        is_valid, semantic_errors = self.analyzer.analyze(ast)
        
        for err in semantic_errors:
            if err.severity == "error":
                result.errors.append(str(err))
            else:
                result.warnings.append(str(err))
        
        if self.verbose:
            if is_valid:
                print("Análisis semántico exitoso")
            else:
                print("Errores semánticos encontrados:")
                for err in semantic_errors:
                    print(f"  {err}")
        
        if not is_valid:
            return result
        
        # Fase 4: Generación de Código
        if self.verbose:
            print("\n" + "=" * 60)
            print("FASE 4: Generación de Código C++")
            print("=" * 60)
        
        cpp_code = self.generator.generate(ast)
        result.cpp_code = cpp_code
        
        # Guardar archivo si se especificó
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cpp_code)
            result.output_file = output_path
            
            if self.verbose:
                print(f"Código C++ guardado en: {output_path}")
        
        result.success = True
        return result
    
    def compile_file(self, input_path: str, output_path: Optional[str] = None) -> CompilationResult:
        """
        Compila un archivo FunLang
        
        Args:
            input_path: Ruta al archivo .fun
            output_path: Ruta para el archivo C++ (opcional)
        
        Returns:
            CompilationResult
        """
        if not os.path.exists(input_path):
            return CompilationResult(success=False, errors=[f"Archivo no encontrado: {input_path}"])
        
        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        if output_path is None:
            base = os.path.splitext(input_path)[0]
            output_path = base + ".cpp"
        
        return self.compile(source_code, output_path)
    
    def compile_and_run(self, source_code: str, output_dir: str = "output") -> Tuple[bool, str]:
        """
        Compila código FunLang, genera ejecutable y lo ejecuta
        
        Args:
            source_code: Código fuente en FunLang
            output_dir: Directorio para archivos generados
        
        Returns:
            Tuple (éxito, salida/error)
        """
        os.makedirs(output_dir, exist_ok=True)
        
        cpp_path = os.path.join(output_dir, "program.cpp")
        exe_path = os.path.join(output_dir, "program")
        
        if sys.platform == "win32":
            exe_path += ".exe"
        
        # Compilar a C++
        result = self.compile(source_code, cpp_path)
        
        if not result.success:
            return False, "\n".join(result.errors)
        
        # Compilar C++ a ejecutable
        compile_cmd = ["g++", "-std=c++17", "-O2", cpp_path, "-o", exe_path]
        
        try:
            proc = subprocess.run(compile_cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                return False, f"Error de compilación C++:\n{proc.stderr}"
        except FileNotFoundError:
            return False, "Error: g++ no encontrado. Instale MinGW o GCC."
        
        # Ejecutar
        try:
            proc = subprocess.run([exe_path], capture_output=True, text=True, timeout=30)
            return True, proc.stdout
        except subprocess.TimeoutExpired:
            return False, "Error: Tiempo de ejecución excedido"
        except Exception as e:
            return False, f"Error de ejecución: {e}"


def create_compiler(verbose: bool = False) -> FunLangCompiler:
    """Factory function para crear un compilador"""
    return FunLangCompiler(verbose=verbose)


# ============================================================================
# PUNTO DE ENTRADA PARA LÍNEA DE COMANDOS
# ============================================================================

def main():
    """Punto de entrada principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FunLang Compiler - Compilador de lenguaje funcional a C++"
    )
    parser.add_argument("input", nargs="?", help="Archivo fuente .fun a compilar")
    parser.add_argument("-o", "--output", help="Archivo de salida .cpp")
    parser.add_argument("-r", "--run", action="store_true", help="Compilar y ejecutar")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verbose")
    parser.add_argument("--tokens", action="store_true", help="Solo mostrar tokens")
    parser.add_argument("--ast", action="store_true", help="Solo mostrar AST")
    parser.add_argument("--version", action="version", version="FunLang Compiler 1.0.0")
    
    args = parser.parse_args()
    
    if args.input is None:
        parser.print_help()
        return
    
    compiler = create_compiler(verbose=args.verbose)
    
    if args.tokens:
        # Solo tokenizar
        with open(args.input, 'r', encoding='utf-8') as f:
            source = f.read()
        tokens = compiler.lexer.tokenize(source)
        for tok in tokens:
            print(tok)
        return
    
    if args.ast:
        # Solo mostrar AST
        with open(args.input, 'r', encoding='utf-8') as f:
            source = f.read()
        ast = compiler.parser.parse(source)
        if ast:
            printer = ASTPrinter()
            printer.visit(ast)
        return
    
    if args.run:
        # Compilar y ejecutar
        with open(args.input, 'r', encoding='utf-8') as f:
            source = f.read()
        success, output = compiler.compile_and_run(source)
        if success:
            print("=== Salida del programa ===")
            print(output)
        else:
            print("=== Error ===")
            print(output)
    else:
        # Solo compilar
        output_path = args.output
        if output_path is None:
            # Por defecto, guardar en output/
            os.makedirs("output", exist_ok=True)
            base_name = os.path.splitext(os.path.basename(args.input))[0]
            output_path = os.path.join("output", base_name + ".cpp")
        
        result = compiler.compile_file(args.input, output_path)
        
        if result.success:
            print(f"Compilación exitosa: {result.output_file}")
            if result.warnings:
                print("\nAdvertencias:")
                for w in result.warnings:
                    print(f"  {w}")
        else:
            print("Error de compilación:")
            for e in result.errors:
                print(f"  {e}")


if __name__ == "__main__":
    main()
