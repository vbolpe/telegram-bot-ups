# 🚀 Guía de Configuración Rápida

## Paso 1: Crear Bot de Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía el comando: `/newbot`
3. Elige un nombre para tu bot (ej: "Monitor UPS")
4. Elige un username (debe terminar en "bot", ej: "mi_ups_monitor_bot")
5. Copia el **token** que te proporciona (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Paso 2: Obtener tu Chat ID

### Opción A: Usando un bot auxiliar
1. Busca **@userinfobot** en Telegram
2. Envía `/start`
3. Copia tu **ID** (es un número como `123456789`)

### Opción B: Manualmente
1. Envía cualquier mensaje a tu bot recién creado
2. Abre en tu navegador: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   (reemplaza `<TU_TOKEN>` con el token del paso 1)
3. Busca `"chat":{"id":` y copia el número que aparece

## Paso 3: Configurar SNMP en tu UPS

### Para UPS APC
1. Accede a la interfaz web de tu UPS (usualmente `http://IP_DE_TU_UPS`)
2. Ve a **Configuration** → **Network** → **SNMP**
3. Habilita **SNMPv3**
4. Crea un usuario con:
   - Username: `snmpuser` (o el que prefieras)
   - Authentication Protocol: **SHA**
   - Authentication Password: (elige una contraseña segura)
   - Privacy Protocol: **AES**
   - Privacy Password: (elige una contraseña segura)
   - Access Type: **Read Only**

### Para otras marcas
Consulta el manual de tu UPS para habilitar SNMP v3.

## Paso 4: Identificar los OIDs de tu UPS

### Opción A: Usar los OIDs por defecto (APC)
Los OIDs en `.env.example` son para UPS APC y funcionan en la mayoría de los casos.

### Opción B: Descubrir los OIDs de tu UPS

Instala herramientas SNMP en tu sistema:

```bash
# En Ubuntu/Debian
sudo apt-get install snmp snmp-mibs-downloader

# En macOS
brew install net-snmp
```

Explora tu UPS:

```bash
snmpwalk -v3 -l authPriv \
  -u snmpuser \
  -a SHA -A tu_password_auth \
  -x AES -X tu_password_priv \
  192.168.1.100
```

Busca valores como:
- Estado de la UPS
- Porcentaje de batería
- Voltajes de entrada/salida
- Temperatura

## Paso 5: Configurar el archivo .env

Edita `.env` con tus valores:

```env
# === TELEGRAM ===
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# === SNMP ===
SNMP_HOST=192.168.1.100          # IP de tu UPS
SNMP_PORT=161                     # Puerto (generalmente 161)
SNMP_USER=snmpuser                # Usuario que creaste
SNMP_AUTH_PASSWORD=tu_password_auth
SNMP_PRIV_PASSWORD=tu_password_priv

# === MONITOREO ===
CHECK_INTERVAL_SECONDS=60         # Verificar cada 60 segundos
DAILY_REPORT_TIME=09:00           # Reporte diario a las 9 AM
```

## Paso 6: Iniciar el Sistema

### Opción A: Script automático
```bash
./start.sh
```

### Opción B: Manual
```bash
# Construir e iniciar
docker-compose up -d --build

# Ver logs
docker-compose logs -f
```

## Paso 7: Verificar Funcionamiento

1. Deberías recibir un mensaje en Telegram: "✅ Bot de monitoreo UPS iniciado"
2. Envía `/status` a tu bot para ver el estado actual
3. Revisa los logs: `docker-compose logs -f`

## 🔍 Solución de Problemas Comunes

### No recibo mensajes del bot
- Verifica que el TELEGRAM_BOT_TOKEN sea correcto
- Verifica que el TELEGRAM_CHAT_ID sea tu ID personal
- Revisa logs: `docker-compose logs telegram-bot`

### Error de conexión SNMP
- Verifica que la IP de la UPS sea correcta
- Verifica que SNMP v3 esté habilitado en la UPS
- Verifica las credenciales SNMP
- Prueba conexión manualmente con `snmpwalk`

### OIDs devuelven valores nulos
- Los OIDs varían por fabricante
- Usa `snmpwalk` para encontrar los OIDs correctos
- Actualiza los valores en `.env`

## 📱 Prueba del Sistema

1. **Prueba de estado**: Envía `/status` al bot
2. **Prueba de alerta**: Desconecta la UPS (pasará a batería)
   - Deberías recibir una alerta automática
3. **Prueba de reporte**: Espera al horario configurado para el reporte diario

## ✅ Checklist de Configuración

- [ ] Bot creado en @BotFather
- [ ] Token del bot copiado
- [ ] Chat ID obtenido
- [ ] SNMP v3 habilitado en la UPS
- [ ] Usuario SNMP creado
- [ ] IP de la UPS identificada
- [ ] Archivo `.env` configurado
- [ ] Servicios Docker iniciados
- [ ] Mensaje de inicio recibido en Telegram
- [ ] Comando `/status` funciona

## 🎉 ¡Listo!

Tu sistema de monitoreo ya está funcionando. Recibirás:
- Alertas automáticas ante cambios
- Reporte diario del estado
- Posibilidad de consultar en cualquier momento con `/status`
