# 🏗️ Arquitectura del Sistema

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO DE TELEGRAM                       │
│                         📱 Cliente                           │
└────────────────────────┬────────────────────────────────────┘
                         │ Comandos (/status, /help)
                         │ Recibe notificaciones
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   SERVICIO TELEGRAM BOT                      │
│                  (Container: telegram-bot)                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  bot.py                                                 │ │
│ │  - Maneja comandos de usuario                          │ │
│ │  - Lee cola de mensajes                                │ │
│ │  - Envía notificaciones                                │ │
│ │                                                         │ │
│ │  config.py                                             │ │
│ │  - Configuración del bot                               │ │
│ │  - Token y Chat ID                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
└───────────┬──────────────────────────┬──────────────────────┘
            │                          │
            │ Lee estado               │ Lee/Escribe cola
            ▼                          ▼
┌────────────────────┐      ┌───────────────────────┐
│   ups_state.json   │      │ message_queue.json    │
│   Estado actual    │      │ Mensajes pendientes   │
└────────────────────┘      └───────────────────────┘
            ▲                          ▲
            │ Escribe estado           │ Encola mensajes
            │                          │
┌───────────┴──────────────────────────┴──────────────────────┐
│               SERVICIO SNMP MONITOR                          │
│              (Container: snmp-monitor)                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  main.py                                                │ │
│ │  - Loop principal de monitoreo                         │ │
│ │  - Scheduler de tareas                                 │ │
│ │  - Genera reportes diarios                             │ │
│ │                                                         │ │
│ │  snmp_client.py                                        │ │
│ │  - Cliente SNMP v3                                     │ │
│ │  - Consulta OIDs                                       │ │
│ │  - Maneja autenticación                                │ │
│ │                                                         │ │
│ │  ups_state.py                                          │ │
│ │  - Gestión de estado                                   │ │
│ │  - Detección de cambios                                │ │
│ │  - Formateo de mensajes                                │ │
│ │                                                         │ │
│ │  config.py                                             │ │
│ │  - Configuración SNMP                                  │ │
│ │  - OIDs de la UPS                                      │ │
│ └─────────────────────────────────────────────────────────┘ │
└───────────┬─────────────────────────────────────────────────┘
            │ SNMP v3 (Puerto 161)
            │ Consultas periódicas
            ▼
┌─────────────────────────────────────────────────────────────┐
│                         UPS DEVICE                           │
│                    🔋 Hardware Físico                        │
│                      con SNMP v3                             │
└─────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

### 1. Monitoreo Continuo

```
SNMP Monitor (cada 60s)
    │
    ├─→ Consulta OIDs a UPS (SNMP v3)
    │
    ├─→ Procesa respuestas
    │
    ├─→ Compara con estado anterior
    │
    ├─→ ¿Cambios detectados?
    │   │
    │   ├─→ SÍ: Encola mensaje de alerta
    │   │
    │   └─→ NO: Continúa
    │
    └─→ Guarda nuevo estado en ups_state.json
```

### 2. Envío de Notificaciones

```
Telegram Bot (cada 5s)
    │
    ├─→ Lee message_queue.json
    │
    ├─→ ¿Hay mensajes?
    │   │
    │   ├─→ SÍ: Por cada mensaje
    │   │       │
    │   │       ├─→ Envía a Telegram API
    │   │       │
    │   │       └─→ Marca como enviado
    │   │
    │   └─→ NO: Espera
    │
    └─→ Limpia cola
```

### 3. Reporte Diario

```
Scheduler (09:00 AM)
    │
    ├─→ Obtiene estado actual de UPS
    │
    ├─→ Genera reporte completo
    │
    ├─→ Encola mensaje de reporte
    │
    └─→ Bot lo envía automáticamente
```

### 4. Comando Manual (/status)

```
Usuario en Telegram
    │
    ├─→ Envía comando /status
    │
    ├─→ Bot recibe comando
    │
    ├─→ Lee ups_state.json
    │
    ├─→ Formatea mensaje
    │
    └─→ Responde inmediatamente
```

## Componentes Detallados

### SNMP Monitor Service

**Responsabilidades:**
- Consultar periódicamente el estado de la UPS
- Detectar cambios en el estado
- Generar alertas y reportes
- Persistir el estado actual

**Archivos:**
- `main.py`: Orquestación principal
- `snmp_client.py`: Cliente SNMP v3
- `ups_state.py`: Lógica de estado
- `config.py`: Configuración

**Dependencias:**
- pysnmp: Cliente SNMP
- schedule: Programación de tareas
- python-dotenv: Variables de entorno

### Telegram Bot Service

**Responsabilidades:**
- Procesar comandos del usuario
- Enviar notificaciones
- Leer y responder consultas de estado

**Archivos:**
- `bot.py`: Bot principal
- `config.py`: Configuración
- `ups_state.py`: Formateador de mensajes

**Dependencias:**
- python-telegram-bot: API de Telegram
- python-dotenv: Variables de entorno

### Almacenamiento Compartido

**data/ups_state.json:**
```json
{
  "status": "2",
  "battery_status": "2",
  "battery_capacity": "100",
  "battery_runtime": "3600",
  "input_voltage": "220",
  "output_voltage": "220",
  "output_load": "45",
  "temperature": "25",
  "last_update": "2026-02-15T10:30:00"
}
```

**data/message_queue.json:**
```json
[
  {
    "type": "alert",
    "message": "⚠️ UPS cambió a batería",
    "timestamp": "2026-02-15T10:30:00"
  }
]
```

## Patrones de Diseño

### 1. Separación de Responsabilidades
- Un servicio = Una responsabilidad
- SNMP Monitor: solo monitorea
- Telegram Bot: solo comunica

### 2. Comunicación por Archivos
- Arquitectura simple y confiable
- Sin dependencias de red entre servicios
- Fácil de depurar

### 3. Estado Persistente
- Estado sobrevive reinicios
- Historia de cambios
- Recuperación ante fallos

### 4. Configuración Externa
- Variables de entorno (.env)
- Sin hardcoding
- Fácil personalización

## Escalabilidad

### Agregar Múltiples UPS

```yaml
services:
  snmp-monitor-ups1:
    build: ./snmp-monitor
    env_file: .env.ups1
    
  snmp-monitor-ups2:
    build: ./snmp-monitor
    env_file: .env.ups2
```

### Múltiples Destinos de Notificación

```yaml
services:
  telegram-bot:
    # Telegram principal
    
  slack-bot:
    # Notificaciones a Slack
    
  email-sender:
    # Emails de alerta
```

### Métricas y Monitoreo

Agregar servicios de:
- Prometheus para métricas
- Grafana para visualización
- InfluxDB para series temporales

## Seguridad

### Niveles de Seguridad

1. **SNMP v3**: Autenticación y encriptación
2. **Telegram Bot**: Token privado
3. **Docker Network**: Aislamiento de red
4. **Variables de Entorno**: Secretos fuera del código
5. **Logs**: Sin contraseñas en logs

### Recomendaciones

- Usar contraseñas fuertes (>12 caracteres)
- Cambiar credenciales por defecto
- Restringir acceso a archivos .env (chmod 600)
- Revisar logs periódicamente
- Mantener contenedores actualizados

## Mantenimiento

### Logs

```bash
# Ver todos los logs
docker-compose logs -f

# Por servicio
docker-compose logs -f snmp-monitor
docker-compose logs -f telegram-bot

# Archivos
tail -f logs/snmp_monitor.log
tail -f logs/telegram_bot.log
```

### Backup

```bash
# Backup automático
make backup

# Manual
tar -czf backup.tar.gz data/ logs/ .env
```

### Actualización

```bash
# Pull de cambios
git pull

# Reconstruir
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Problema: Servicios no se comunican

**Causa**: Red Docker
**Solución**:
```bash
docker network ls
docker network inspect ups-network
```

### Problema: Permisos en archivos

**Causa**: Usuario Docker
**Solución**:
```bash
chmod 755 data logs
chown -R 1000:1000 data logs
```

### Problema: Memoria alta

**Causa**: Logs muy grandes
**Solución**:
```bash
# Agregar límites en docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Performance

### Métricas Típicas

- CPU: <5% por servicio
- RAM: ~50MB por servicio
- Disco: <100MB total
- Red: <1KB/s promedio

### Optimizaciones

1. Ajustar CHECK_INTERVAL según necesidades
2. Limitar tamaño de logs
3. Limpiar cola de mensajes periódicamente
4. Usar volúmenes Docker para mejor I/O
