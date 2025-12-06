-- Test 6: Actores básicos en FunLang

-- Definir un actor simple que imprime mensajes
actor printer msg = println(msg)

-- Definir un actor contador
actor counter n = println(n)

-- Programa principal
main = do
    let p = spawn printer
    let c = spawn counter
    send p "Hola desde actor!"
    send p "Otro mensaje"
    send c 42
    println("Mensajes enviados")
  end
