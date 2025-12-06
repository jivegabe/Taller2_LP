# Diagrama UML - Implementación del Modelo de Actores en FunLang

## Diagrama de Flujo de Compilación

```mermaid
flowchart TD
    subgraph "Código Fuente FunLang"
        A[test6_actors.fun]
    end

    subgraph "Análisis Léxico - lexer.py"
        B[Tokenización]
        B1[Token ACTOR]
        B2[Token SPAWN]
        B3[Token SEND]
        B --> B1 & B2 & B3
    end

    subgraph "Análisis Sintáctico - parser.py"
        C[Parsing]
        C1[p_actor_decl]
        C2[p_spawn_expr]
        C3[p_send_expr]
        C --> C1 & C2 & C3
    end

    subgraph "AST - ast_nodes.py"
        D[Nodos AST]
        D1[ActorDecl]
        D2[SpawnExpr]
        D3[SendExpr]
        D --> D1 & D2 & D3
    end

    subgraph "Generación de Código - codegen.py"
        E[CppCodeGenerator]
        E1[visit_ActorDecl]
        E2[visit_SpawnExpr]
        E3[visit_SendExpr]
        E4[_generate_actor_runtime]
        E --> E1 & E2 & E3 & E4
    end

    subgraph "Código C++ Generado"
        F[test6_actors.cpp]
        F1[Clase Actor]
        F2[ActorSystem]
        F3[Clases xxxActor]
        F4[main con actores]
        F --> F1 & F2 & F3 & F4
    end

    A --> B
    B1 & B2 & B3 --> C
    C1 --> D1
    C2 --> D2
    C3 --> D3
    D1 --> E1
    D2 --> E2
    D3 --> E3
    E4 --> F1 & F2
    E1 --> F3
    E2 & E3 --> F4
```

## Diagrama de Clases - Nodos AST

```mermaid
classDiagram
    class Declaration {
        <<abstract>>
        +lineno: int
        +column: int
    }

    class Expression {
        <<abstract>>
        +lineno: int
        +column: int
        +inferred_type: Type
    }

    class ActorDecl {
        +name: str
        +params: List~Pattern~
        +body: Expression
    }

    class SpawnExpr {
        +actor_name: str
        +args: List~Expression~
    }

    class SendExpr {
        +target: Expression
        +message: Expression
    }

    Declaration <|-- ActorDecl
    Expression <|-- SpawnExpr
    Expression <|-- SendExpr
```

## Diagrama de Clases - Runtime C++ Generado

```mermaid
classDiagram
    class Actor {
        #queue~any~ mailbox
        #mutex mtx
        #bool running
        #thread worker
        #function~void(any)~ handler
        +send(any msg) void
        +empty() bool
        +start() void
        +stop() void
        +set_handler(function~void(any)~ h) void
    }

    class ActorSystem {
        -vector~shared_ptr~Actor~~ actors
        +spawn~T~() shared_ptr~T~
        +wait_all() void
    }

    class printerActor {
        +handle(any _msg) void
    }

    class counterActor {
        +handle(any _msg) void
    }

    Actor <|-- printerActor
    Actor <|-- counterActor
    ActorSystem --> Actor : manages
```

## Diagrama de Secuencia - Ejecución de Actores

```mermaid
sequenceDiagram
    participant Main
    participant ActorSystem
    participant PrinterActor
    participant CounterActor

    Main->>ActorSystem: spawn<printerActor>()
    ActorSystem->>PrinterActor: new + start()
    ActorSystem-->>Main: shared_ptr<printerActor>

    Main->>ActorSystem: spawn<counterActor>()
    ActorSystem->>CounterActor: new + start()
    ActorSystem-->>Main: shared_ptr<counterActor>

    Main->>PrinterActor: send("Hola desde actor!")
    Main->>PrinterActor: send("Otro mensaje")
    Main->>CounterActor: send(42)

    Main->>ActorSystem: wait_all()

    loop Procesar mailbox
        PrinterActor->>PrinterActor: handle(msg)
        PrinterActor->>PrinterActor: println(msg)
    end

    loop Procesar mailbox
        CounterActor->>CounterActor: handle(msg)
        CounterActor->>CounterActor: println(n)
    end

    ActorSystem-->>Main: todos los mensajes procesados
```

## Sintaxis Añadida

| Construcción | Sintaxis FunLang | Código C++ Generado |
|--------------|------------------|---------------------|
| Declarar actor | `actor nombre param = expr` | `class nombreActor : public Actor { ... }` |
| Crear actor | `spawn nombre` | `actorSystem.spawn<nombreActor>()` |
| Enviar mensaje | `send actor msg` | `actor->send(msg)` |
