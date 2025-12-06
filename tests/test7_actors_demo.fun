-- Demo: Sistema de Logging y Notificaciones con Actores
-- Muestra procesamiento paralelo de mensajes entre múltiples actores

-- Actor logger: registra todos los eventos
actor logger msg = println(msg)

-- Actor alertas: muestra alertas importantes  
actor alertas msg = println(msg)

-- Actor stats: muestra estadísticas
actor stats msg = println(msg)

-- Actor notifier: envía notificaciones
actor notifier msg = println(msg)

-- Programa principal: simula un sistema distribuido
main = do
    -- Crear el sistema de actores (4 workers paralelos)
    let log = spawn logger
    let alert = spawn alertas
    let stat = spawn stats
    let notify = spawn notifier
    
    -- Simulación de eventos del sistema
    send log "[LOG] Sistema iniciado"
    send log "[LOG] Conexion establecida"
    send alert "[ALERTA] Usuario admin conectado"
    send stat "[STAT] CPU: 45%"
    send stat "[STAT] RAM: 2.3GB"
    send notify "[NOTIFY] Nuevo mensaje recibido"
    
    send log "[LOG] Procesando solicitud #1001"
    send log "[LOG] Procesando solicitud #1002"
    send alert "[ALERTA] Intento de acceso fallido"
    send stat "[STAT] Solicitudes/seg: 150"
    send notify "[NOTIFY] Tarea completada"
    
    send log "[LOG] Backup iniciado"
    send alert "[ALERTA] Disco al 85%"
    send stat "[STAT] Disco: 85%"
    send notify "[NOTIFY] Backup programado"
    
    send log "[LOG] Sistema estable"
    send alert "[ALERTA] Todo normal"
    send stat "[STAT] Uptime: 24h"
    send notify "[NOTIFY] Reporte generado"
    
    println("=== Main: Todos los mensajes enviados ===")
end
