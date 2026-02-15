# 🔋 Guía de Configuración para Eaton 93E 30kVA

## Características de la Eaton 93E

La **Eaton 93E** es una UPS trifásica de alta eficiencia (hasta 97%) diseñada para centros de datos y aplicaciones empresariales críticas. El modelo 30kVA es parte de la serie 93E que va de 20 a 200kVA.

### Especificaciones del Modelo 30kVA
- **Potencia**: 30 kVA / 30 kW
- **Entrada**: Trifásica 400V
- **Salida**: Trifásica 400V
- **Eficiencia**: Hasta 97% en modo normal, 99% en modo ECOnversion
- **Network Management Card (NMC)**: Incluida para gestión SNMP

## 📋 Configuración de SNMP en la Eaton 93E

### Paso 1: Acceder a la Interfaz Web

1. Conecta tu computadora a la misma red que la UPS
2. Abre un navegador y accede a la IP de la UPS (ejemplo: `http://192.168.1.100`)
3. Usuario por defecto: **admin**
4. Contraseña por defecto: **admin** (cámbiala inmediatamente)

### Paso 2: Habilitar SNMP v3

1. Ve a **Configuration** → **Network** → **SNMP**
2. Marca **Enable SNMPv3**
3. Desmarca **Enable SNMPv1** y **Enable SNMPv2c** (por seguridad)

### Paso 3: Crear Usuario SNMP v3

1. En la sección **SNMPv3 Users**, haz clic en **Add User**
2. Configura:
   ```
   Username: snmpmonitor
   Security Level: authPriv (Authentication + Privacy)
   Authentication Protocol: SHA
   Authentication Password: [tu_contraseña_segura_min_8_caracteres]
   Privacy Protocol: AES
   Privacy Password: [tu_contraseña_segura_min_8_caracteres]
   Access Type: Read Only
   ```
3. Haz clic en **Apply**

### Paso 4: Verificar Conexión SNMP

Desde tu servidor Linux:

```bash
# Instalar herramientas SNMP
sudo apt-get install snmp snmp-mibs-downloader

# Probar conexión
snmpwalk -v3 -l authPriv \
  -u snmpmonitor \
  -a SHA -A tu_password_auth \
  -x AES -X tu_password_priv \
  192.168.1.100

# Probar un OID específico (estado de la UPS)
snmpget -v3 -l authPriv \
  -u snmpmonitor \
  -a SHA -A tu_password_auth \
  -x AES -X tu_password_priv \
  192.168.1.100 \
  1.3.6.1.4.1.534.1.4.1.0
```

## 🔧 Configuración del Proyecto

### Usar el archivo de configuración para Eaton 93E

```bash
# Copiar la plantilla específica para Eaton
cp .env.eaton93e .env

# Editar con tus datos
nano .env
```

### Configurar las Variables Críticas

```env
# === TELEGRAM ===
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# === SNMP ===
SNMP_HOST=192.168.1.100           # IP de tu UPS Eaton 93E
SNMP_PORT=161
SNMP_USER=snmpmonitor             # Usuario creado en la UPS
SNMP_AUTH_PASSWORD=tu_password_auth
SNMP_PRIV_PASSWORD=tu_password_priv

# === LOS OIDs YA ESTÁN CONFIGURADOS PARA EATON 93E ===
```

## 📊 OIDs Específicos de Eaton 93E

Los OIDs ya están preconfigurados en `.env.eaton93e`. Aquí una referencia:

### Estados Principales
```
Estado UPS:           1.3.6.1.4.1.534.1.4.1.0
Estado Batería:       1.3.6.1.4.1.534.1.2.1.0
Carga Batería (%):    1.3.6.1.4.1.534.1.2.4.0
Tiempo Batería (s):   1.3.6.1.4.1.534.1.2.5.0
```

### Valores de Entrada (Trifásica)
```
Voltaje Entrada:      1.3.6.1.4.1.534.1.3.1.0
Frecuencia Entrada:   1.3.6.1.4.1.534.1.3.2.0
```

### Valores de Salida (Trifásica)
```
Voltaje Salida:       1.3.6.1.4.1.534.1.4.2.0
Frecuencia Salida:    1.3.6.1.4.1.534.1.4.3.0
Carga Salida (%):     1.3.6.1.4.1.534.1.4.4.1.3.1
Corriente Salida:     1.3.6.1.4.1.534.1.4.4.1.2.1
Potencia Salida (W):  1.3.6.1.4.1.534.1.4.4.1.4.1
```

### Otros Valores
```
Temperatura:          1.3.6.1.4.1.534.1.6.1.0
Bypass Voltage:       1.3.6.1.4.1.534.1.5.1.0
Alarmas Activas:      1.3.6.1.4.1.534.1.7.1.0
```

## ⚙️ Características Especiales de la 93E

### Factores de Escala
La Eaton 93E devuelve algunos valores escalados:
- **Voltajes**: Se devuelven en 0.1V (ej: 2200 = 220.0V)
- **Frecuencias**: Se devuelven en 0.1Hz (ej: 500 = 50.0Hz)
- **Corrientes**: Se devuelven en 0.1A (ej: 125 = 12.5A)

**El sistema ya aplica estos factores automáticamente**, no necesitas hacer nada.

### Modo ECOnversion
La 93E puede operar en modo ECOnversion (99% eficiencia). El sistema detectará automáticamente cuando esté en:
- **Online (Normal)**: Modo doble conversión (97%)
- **On Bypass**: Modo ECOnversion (99%)

### Sistema Trifásico
La 93E es trifásica. Los OIDs configurados obtienen valores de fase 1. Si necesitas monitorear las 3 fases:

```env
# Fase 2
OID_UPS_OUTPUT_LOAD_PHASE2=1.3.6.1.4.1.534.1.4.4.1.3.2
OID_UPS_OUTPUT_CURRENT_PHASE2=1.3.6.1.4.1.534.1.4.4.1.2.2

# Fase 3
OID_UPS_OUTPUT_LOAD_PHASE3=1.3.6.1.4.1.534.1.4.4.1.3.3
OID_UPS_OUTPUT_CURRENT_PHASE3=1.3.6.1.4.1.534.1.4.4.1.2.3
```

## 🚀 Iniciar el Sistema

```bash
# Usar el script de inicio
./start.sh

# O manualmente
docker-compose up -d --build

# Ver logs
docker-compose logs -f
```

## 🔍 Verificación

### 1. Probar SNMP
```bash
python test_snmp.py
```

Deberías ver algo como:
```
✅ Conexión SNMP exitosa
✅ status                 = 2
✅ battery_status         = 2
✅ battery_capacity       = 100
✅ input_voltage          = 220.0
✅ output_voltage         = 220.0
✅ output_load            = 45
✅ temperature            = 28
```

### 2. Verificar Mensaje de Telegram

Deberías recibir un mensaje como:
```
🔋 Estado de la UPS

📊 Estado General: Online (Normal)
🔋 Batería: Battery Normal
⚡ Carga Batería: 100%
⏱️ Autonomía: 45 min

📥 Entrada:
   • Voltaje: 220.0 V
   • Frecuencia: 50.0 Hz

📤 Salida:
   • Voltaje: 220.0 V
   • Frecuencia: 50.0 Hz
   • Carga: 45%
   • Corriente: 12.5 A
   • Potencia: 13.5 kW

🌡️ Temperatura: 28°C

🕐 Última actualización: 2026-02-15 10:30:00
```

## 🎯 Escenarios de Prueba

### Prueba 1: Fallo de Alimentación
1. Simula un corte de energía (apaga el interruptor de entrada)
2. La UPS pasará a batería
3. Deberías recibir: **⚠️ ALERTA: UPS cambió a batería**

### Prueba 2: Vuelta de Alimentación
1. Reactiva la alimentación
2. La UPS volverá a modo Online
3. Deberías recibir: **✅ UPS volvió a modo Online**

### Prueba 3: Alto Consumo
1. Incrementa la carga en la UPS
2. Si supera ciertos umbrales, recibirás alertas

## 📈 Valores Típicos de la 93E 30kVA

### En Condiciones Normales
- **Estado**: Online (Normal) o On Bypass (ECOnversion)
- **Voltaje Entrada**: 380-420V (trifásica)
- **Voltaje Salida**: 400V ±1%
- **Frecuencia**: 50Hz ±0.1Hz
- **Carga**: Variable según uso
- **Temperatura**: 20-35°C (ambiente controlado)
- **Batería**: 100% cuando está en línea

### Autonomía Típica (depende de baterías instaladas)
- **A 30kW (100%)**: 5-10 minutos
- **A 15kW (50%)**: 15-25 minutos
- **A 7.5kW (25%)**: 40-60 minutos

## ⚠️ Alertas Importantes

El sistema te notificará automáticamente ante:
- ✅ **Cambio a batería** (corte de energía)
- ✅ **Batería baja** (menos de 20%)
- ✅ **Sobrecarga** (más de 90%)
- ✅ **Cambio de bypass** (modo ECOnversion)
- ✅ **Variaciones de voltaje** significativas
- ✅ **Temperatura alta** (>40°C)
- ✅ **Alarmas activas** en la UPS

## 🔧 Troubleshooting Específico

### Problema: OIDs devuelven valores muy altos
**Causa**: Factores de escala no aplicados
**Solución**: Verifica que `SCALE_FACTORS` esté configurado en `config.py`

### Problema: No se detecta el bypass
**Causa**: La 93E puede estar en modo ECOnversion
**Solución**: Revisa el estado. "8 = On Bypass" es normal en modo ECO

### Problema: Valores de potencia incorrectos
**Causa**: La 93E es trifásica, necesitas sumar las 3 fases
**Solución**: El OID configurado da la potencia total, no por fase

## 📞 Soporte Adicional

- **Manual Eaton 93E**: Busca "Eaton 93E User Manual"
- **MIB Eaton**: Descarga el MIB oficial de Eaton para referencia
- **Soporte Eaton**: https://www.eaton.com/support

## ✅ Checklist Final

- [ ] SNMP v3 habilitado en la UPS
- [ ] Usuario SNMP creado con authPriv
- [ ] Contraseñas seguras (>8 caracteres)
- [ ] IP de la UPS accesible desde el servidor
- [ ] Archivo `.env` configurado con `.env.eaton93e`
- [ ] Telegram bot creado y token obtenido
- [ ] Chat ID configurado
- [ ] `test_snmp.py` ejecutado exitosamente
- [ ] Servicios Docker iniciados
- [ ] Mensaje de inicio recibido en Telegram

¡Tu sistema está listo para monitorear la Eaton 93E 30kVA! 🎉
