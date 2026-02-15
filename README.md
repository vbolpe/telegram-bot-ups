# 🔋 Sistema de Monitoreo de UPS con Telegram

Sistema completo de monitoreo de UPS mediante SNMP v3 con notificaciones automáticas por Telegram. Arquitectura dockerizada con servicios separados para máxima modularidad y escalabilidad.

## 📋 Características

- **Monitoreo continuo** de estado de UPS vía SNMP v3
- **Notificaciones automáticas** ante cambios de estado
- **Reportes diarios** programables
- **Arquitectura modular** con servicios independientes
- **Completamente dockerizado** para fácil despliegue
- **Logging detallado** para debugging y auditoría
- **Persistencia de datos** entre reinicios

## 🏗️ Arquitectura

```
ups-monitor/
├── docker-compose.yml          # Orquestación de servicios
├── .env                        # Variables de entorno (crear desde .env.example)
├── .env.example                # Plantilla de configuración
│
├── snmp-monitor/               # Servicio de monitoreo SNMP
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # Punto de entrada
│   ├── config.py               # Configuración
│   ├── snmp_client.py          # Cliente SNMP v3
│   └── ups_state.py            # Gestión de estado
│
├── telegram-bot/               # Servicio del bot de Telegram
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── bot.py                  # Bot principal
│   ├── config.py               # Configuración
│   └── ups_state.py            # Formateador de mensajes
│
├── data/                       # Datos persistentes
│   ├── ups_state.json          # Estado actual de la UPS
│   └── message_queue.json      # Cola de mensajes pendientes
│
└── logs/                       # Logs de los servicios
    ├── snmp_monitor.log
    └── telegram_bot.log
```

## 🚀 Inicio Rápido

### 1. Prerequisitos

- Docker y Docker Compose instalados
- UPS con soporte SNMP v3
- Bot de Telegram creado (via @BotFather)
- Chat ID de Telegram

### 2. Configuración

```bash
# Clonar o copiar el proyecto
cd ups-monitor

# Crear archivo de configuración
cp .env.example .env

# Editar .env con tus datos
nano .env
```

### 3. Configurar Variables de Entorno

Edita el archivo `.env` con tu configuración:

```env
# Bot de Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# SNMP v3
SNMP_HOST=192.168.1.100
SNMP_USER=snmpuser
SNMP_AUTH_PASSWORD=tu_password_auth
SNMP_PRIV_PASSWORD=tu_password_priv

# Ajustar OIDs según tu modelo de UPS
```

### 4. Obtener Token de Telegram

1. Hablar con [@BotFather](https://t.me/botfather) en Telegram
2. Enviar `/newbot` y seguir instrucciones
3. Copiar el token proporcionado
4. Para obtener tu Chat ID:
   - Enviar un mensaje a tu bot
   - Visitar: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Buscar el campo `"chat":{"id":`

### 5. Identificar OIDs de tu UPS

Los OIDs varían según el fabricante. Para identificarlos:

```bash
# Instalar herramientas SNMP
apt-get install snmp snmp-mibs-downloader

# Explorar tu UPS
snmpwalk -v3 -l authPriv -u USUARIO -a SHA -A PASSWORD_AUTH \
         -x AES -X PASSWORD_PRIV 192.168.1.100
```

**OIDs comunes por fabricante:**

**APC:**
```
Status: 1.3.6.1.4.1.318.1.1.1.4.1.1.0
Battery Status: 1.3.6.1.4.1.318.1.1.1.2.1.1.0
Battery Capacity: 1.3.6.1.4.1.318.1.1.1.2.2.1.0
```

**Eaton:**
```
Status: 1.3.6.1.4.1.534.1.4.1.0
Battery Status: 1.3.6.1.4.1.534.1.2.1.0
```

### 6. Levantar el Sistema

```bash
# Construir e iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar estado
docker-compose ps
```

## 📱 Uso del Bot

### Comandos Disponibles

- `/start` - Iniciar el bot y ver comandos
- `/status` - Obtener estado actual de la UPS
- `/help` - Ver ayuda completa

### Notificaciones Automáticas

El bot enviará mensajes automáticamente cuando:

- **Cambio de estado**: UPS pasa a batería o vuelve a línea
- **Batería baja**: Nivel crítico de batería
- **Cambios de voltaje**: Variaciones significativas
- **Reporte diario**: Resumen completo del estado (configurable)

## ⚙️ Configuración Avanzada

### Ajustar Intervalo de Monitoreo

```env
# Verificar cada 30 segundos
CHECK_INTERVAL_SECONDS=30
```

### Cambiar Hora del Reporte Diario

```env
# Reporte a las 8:00 AM
DAILY_REPORT_TIME=08:00
```

### Personalizar Zona Horaria

```env
TZ=America/Argentina/Buenos_Aires
```

## 🔧 Mantenimiento

### Ver Logs

```bash
# Logs en tiempo real
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f snmp-monitor
docker-compose logs -f telegram-bot

# Logs en archivos
tail -f logs/snmp_monitor.log
tail -f logs/telegram_bot.log
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar un servicio
docker-compose restart snmp-monitor
```

### Actualizar Configuración

```bash
# Editar .env
nano .env

# Aplicar cambios
docker-compose down
docker-compose up -d
```

### Backup de Datos

```bash
# Backup del estado
cp data/ups_state.json backups/ups_state_$(date +%Y%m%d).json
```

## 🛠️ Desarrollo y Personalización

### Estructura Modular

El código está diseñado para facilitar mejoras:

- `snmp_client.py`: Cliente SNMP reutilizable
- `ups_state.py`: Lógica de estado y formateado
- `config.py`: Configuración centralizada
- `main.py` / `bot.py`: Puntos de entrada

### Agregar Nuevos OIDs

1. Agregar OID en `.env`:
```env
OID_UPS_CUSTOM=1.3.6.1.4.1.x.x.x.x
```

2. Actualizar `config.py`:
```python
OIDS = {
    # ... otros OIDs
    'custom': os.getenv('OID_UPS_CUSTOM'),
}
```

3. Actualizar formateador en `ups_state.py`

### Agregar Nuevos Comandos al Bot

Editar `telegram-bot/bot.py`:

```python
async def custom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Tu lógica aquí
    await update.message.reply_text("Respuesta")

# En start_bot()
self.application.add_handler(CommandHandler("comando", self.custom_command))
```

## 🐛 Troubleshooting

### Bot no responde

```bash
# Verificar que el servicio esté corriendo
docker-compose ps

# Ver logs del bot
docker-compose logs telegram-bot

# Verificar token
docker-compose exec telegram-bot env | grep TELEGRAM
```

### No hay datos de la UPS

```bash
# Ver logs del monitor
docker-compose logs snmp-monitor

# Probar conexión SNMP manualmente
docker-compose exec snmp-monitor python -c "
from snmp_client import SNMPClient
client = SNMPClient()
print(client.test_connection())
"
```

### Permisos de archivos

```bash
# Dar permisos a directorios
chmod -R 755 data logs
```

## 📊 Monitoreo del Sistema

### Healthcheck

```bash
# Estado de contenedores
docker-compose ps

# Uso de recursos
docker stats ups-snmp-monitor ups-telegram-bot
```

### Métricas

- Estado guardado en `data/ups_state.json`
- Logs detallados en `logs/`
- Cola de mensajes en `data/message_queue.json`

## 🔒 Seguridad

- Usar SNMP v3 con autenticación y privacidad
- No compartir el archivo `.env`
- Mantener actualizados los contenedores
- Revisar logs periódicamente

## 📝 Licencia

Este proyecto es de código abierto. Úsalo y modifícalo según tus necesidades.

## 🤝 Contribuciones

Las mejoras y sugerencias son bienvenidas. El código está modularizado específicamente para facilitar contribuciones.

## 📧 Soporte

Para problemas o preguntas:
1. Revisar logs en `logs/`
2. Verificar configuración en `.env`
3. Probar conexión SNMP manualmente
4. Consultar documentación de tu modelo de UPS

---

**Nota**: Ajusta los OIDs según tu modelo específico de UPS. Los valores proporcionados son ejemplos comunes para UPS APC.
