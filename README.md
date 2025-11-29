# FunLang - Lenguaje Funcional SPL

## Descripción del Proyecto
Sistema de Procesamiento del Lenguaje (SPL) que implementa un lenguaje funcional inspirado en Haskell.
El compilador genera código C++ ejecutable.

## Estructura del Proyecto
```
Taller2_LP/
├── src/
│   ├── lexer.py          # Analizador Léxico (PLY Lex)
│   ├── parser.py         # Analizador Sintáctico (PLY Yacc)
│   ├── ast_nodes.py      # Nodos del AST
│   ├── semantic.py       # Analizador Semántico
│   ├── codegen.py        # Generador de Código C++
│   └── compiler.py       # Compilador Principal
├── grammar/
│   └── funlang.ebnf      # Gramática E-BNF
├── tests/
│   ├── test1_euclides.fun    # Algoritmo de Euclides
│   ├── test2_factorial.fun   # Factorial recursivo
│   ├── test3_fibonacci.fun   # Serie Fibonacci
│   ├── test4_arrays.fun      # Manejo de arreglos
│   └── test5_matrices.fun    # Operaciones con matrices
├── output/                   # Código C++ generado
├── docs/
│   └── manual_tecnico.md     # Documentación técnica
└── main.py                   # Punto de entrada
```

## Características del Lenguaje FunLang
- Paradigma funcional con soporte imperativo
- Tipos de datos: Int, Float, Bool, Char, String, Array, Matrix
- Estructuras: secuencia, selección (if-then-else), iteración (for, while)
- Funciones de primera clase
- Pattern matching básico
- Aritmética de punto flotante
- TDA (Tipos de Datos Abstractos)

## Requisitos
- Python 3.8+
- PLY (Python Lex-Yacc)
- G++ (para compilar el código generado)

## Uso
Para usar la CLI
```bash
python main.py tests/test1_euclides.fun
```

Para usar la GUI
```bash
python src/view/visualizer.py
```

## Autores
Taller #2 - Lenguajes de Programación
