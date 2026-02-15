# OIDs Comunes para Diferentes Fabricantes de UPS

## APC (American Power Conversion)

### Estado y Batería
```
OID_UPS_STATUS=1.3.6.1.4.1.318.1.1.1.4.1.1.0
OID_UPS_BATTERY_STATUS=1.3.6.1.4.1.318.1.1.1.2.1.1.0
OID_UPS_BATTERY_CAPACITY=1.3.6.1.4.1.318.1.1.1.2.2.1.0
OID_UPS_BATTERY_RUNTIME=1.3.6.1.4.1.318.1.1.1.2.2.3.0
OID_UPS_TEMPERATURE=1.3.6.1.4.1.318.1.1.1.2.2.2.0
```

### Voltajes
```
OID_UPS_INPUT_VOLTAGE=1.3.6.1.4.1.318.1.1.1.3.2.1.0
OID_UPS_OUTPUT_VOLTAGE=1.3.6.1.4.1.318.1.1.1.4.2.1.0
OID_UPS_OUTPUT_LOAD=1.3.6.1.4.1.318.1.1.1.4.2.3.0
```

### Información del Sistema
```
OID_UPS_MODEL=1.3.6.1.4.1.318.1.1.1.1.1.1.0
OID_UPS_SERIAL=1.3.6.1.4.1.318.1.1.1.1.2.3.0
OID_UPS_FIRMWARE=1.3.6.1.4.1.318.1.1.1.1.2.1.0
```

## Eaton

### Estado y Batería
```
OID_UPS_STATUS=1.3.6.1.4.1.534.1.4.1.0
OID_UPS_BATTERY_STATUS=1.3.6.1.4.1.534.1.2.1.0
OID_UPS_BATTERY_CAPACITY=1.3.6.1.4.1.534.1.2.4.0
OID_UPS_BATTERY_RUNTIME=1.3.6.1.4.1.534.1.2.5.0
```

### Voltajes
```
OID_UPS_INPUT_VOLTAGE=1.3.6.1.4.1.534.1.3.1.0
OID_UPS_OUTPUT_VOLTAGE=1.3.6.1.4.1.534.1.4.2.0
OID_UPS_OUTPUT_LOAD=1.3.6.1.4.1.534.1.4.4.1.3.1
```

## Tripp Lite

### Estado y Batería
```
OID_UPS_STATUS=1.3.6.1.4.1.850.1.1.3.1.4.1.0
OID_UPS_BATTERY_STATUS=1.3.6.1.4.1.850.1.1.3.2.1.0
OID_UPS_BATTERY_CAPACITY=1.3.6.1.4.1.850.1.1.3.2.2.0
OID_UPS_BATTERY_RUNTIME=1.3.6.1.4.1.850.1.1.3.2.3.0
```

### Voltajes
```
OID_UPS_INPUT_VOLTAGE=1.3.6.1.4.1.850.1.1.3.3.3.1.0
OID_UPS_OUTPUT_VOLTAGE=1.3.6.1.4.1.850.1.1.3.4.2.1.0
OID_UPS_OUTPUT_LOAD=1.3.6.1.4.1.850.1.1.3.4.3.1.0
```

## CyberPower

### Estado y Batería
```
OID_UPS_STATUS=1.3.6.1.4.1.3808.1.1.1.4.1.1.0
OID_UPS_BATTERY_STATUS=1.3.6.1.4.1.3808.1.1.1.2.1.1.0
OID_UPS_BATTERY_CAPACITY=1.3.6.1.4.1.3808.1.1.1.2.2.1.0
OID_UPS_BATTERY_RUNTIME=1.3.6.1.4.1.3808.1.1.1.2.2.3.0
```

### Voltajes
```
OID_UPS_INPUT_VOLTAGE=1.3.6.1.4.1.3808.1.1.1.3.2.1.0
OID_UPS_OUTPUT_VOLTAGE=1.3.6.1.4.1.3808.1.1.1.4.2.1.0
OID_UPS_OUTPUT_LOAD=1.3.6.1.4.1.3808.1.1.1.4.2.3.0
```

## OIDs Estándar UPS-MIB (RFC 1628)

Algunos fabricantes siguen el estándar RFC 1628:

```
# Base OID: 1.3.6.1.2.1.33

OID_UPS_STATUS=1.3.6.1.2.1.33.1.4.1.0
OID_UPS_BATTERY_STATUS=1.3.6.1.2.1.33.1.2.1.0
OID_UPS_BATTERY_CAPACITY=1.3.6.1.2.1.33.1.2.4.0
OID_UPS_BATTERY_RUNTIME=1.3.6.1.2.1.33.1.2.3.0
OID_UPS_INPUT_VOLTAGE=1.3.6.1.2.1.33.1.3.3.1.3.1
OID_UPS_OUTPUT_VOLTAGE=1.3.6.1.2.1.33.1.4.4.1.2.1
OID_UPS_OUTPUT_LOAD=1.3.6.1.2.1.33.1.4.4.1.5.1
OID_UPS_TEMPERATURE=1.3.6.1.2.1.33.1.2.7.0
```

## Cómo Descubrir los OIDs de tu UPS

### 1. Usando snmpwalk

```bash
# Instalar herramientas
sudo apt-get install snmp snmp-mibs-downloader

# Explorar todos los OIDs
snmpwalk -v3 -l authPriv \
  -u USUARIO \
  -a SHA -A PASSWORD_AUTH \
  -x AES -X PASSWORD_PRIV \
  IP_UPS

# Buscar OIDs específicos (ejemplo: batería)
snmpwalk -v3 -l authPriv \
  -u USUARIO \
  -a SHA -A PASSWORD_AUTH \
  -x AES -X PASSWORD_PRIV \
  IP_UPS | grep -i battery
```

### 2. Usando la herramienta MIB Browser

Muchos fabricantes proporcionan herramientas gráficas como:
- iReasoning MIB Browser
- ManageEngine MibBrowser

### 3. Consultar Documentación del Fabricante

Busca en la documentación:
- "SNMP MIB Reference"
- "SNMP OID List"
- Manual del administrador

## Valores de Estado Comunes

### Status (OID_UPS_STATUS)
```
1 = Unknown
2 = Online (Normal)
3 = On Battery
4 = On Boost
5 = On Sleep
6 = Off
7 = Rebooting
8 = On Bypass
```

### Battery Status (OID_UPS_BATTERY_STATUS)
```
1 = Unknown
2 = Battery Normal
3 = Battery Low
4 = Battery Depleted
```

## Tips para Configurar

1. **Identifica el fabricante**: Busca primero en la sección de tu fabricante
2. **Prueba los OIDs**: Usa `snmpwalk` para verificar que funcionan
3. **Documenta los valores**: Anota qué valor devuelve cada OID
4. **Ajusta el código**: Modifica los mapeos en `ups_state.py` si es necesario
5. **Prueba las alertas**: Desconecta la UPS para verificar que las alertas funcionan

## Ejemplo de Prueba Rápida

```bash
# Probar OID de estado
snmpget -v3 -l authPriv \
  -u snmpuser \
  -a SHA -A tu_password \
  -x AES -X tu_password \
  192.168.1.100 \
  1.3.6.1.4.1.318.1.1.1.4.1.1.0

# Si devuelve un valor numérico (ej: 2), ¡funciona!
```
