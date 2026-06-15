"""
Módulo de configuración para el monitor SNMP
OIDs validados contra Eaton 93E 30 - Computer Room
"""
import os
from dotenv import load_dotenv

load_dotenv()

class SNMPConfig:
    """Configuración SNMP v3"""

    HOST = os.getenv('SNMP_HOST', '192.168.1.100')
    PORT = int(os.getenv('SNMP_PORT', '161'))
    USER = os.getenv('SNMP_USER', 'snmpuser')

    # Protocolos de autenticación
    AUTH_PROTOCOL = os.getenv('SNMP_AUTH_PROTOCOL', 'MD5')
    AUTH_PASSWORD = os.getenv('SNMP_AUTH_PASSWORD', '')

    # Protocolos de privacidad
    PRIV_PROTOCOL = os.getenv('SNMP_PRIV_PROTOCOL', 'DES')
    PRIV_PASSWORD = os.getenv('SNMP_PRIV_PASSWORD', '')

    # Nivel de seguridad
    SECURITY_LEVEL = os.getenv('SNMP_SECURITY_LEVEL', 'authPriv')

    # OIDs validados contra la UPS Eaton 93E
    # Combinación de UPS-MIB estándar y OIDs privados Eaton (1.3.6.1.4.1.534)
    OIDS = {
        # Estado general — UPS-MIB estándar
        # Valores confirmados: 3=Online, 5=On Battery
        'status': os.getenv('OID_UPS_STATUS', '1.3.6.1.2.1.33.1.4.1.0'),

        # Batería — UPS-MIB estándar
        # battery_status: 1=Unknown, 2=Normal, 3=Low, 4=Depleted
        'battery_status':   os.getenv('OID_UPS_BATTERY_STATUS',   '1.3.6.1.2.1.33.1.2.1.0'),

        # Capacidad e runtime — OIDs Eaton privados (más precisos que UPS-MIB)
        # battery_capacity: valor directo en %
        # battery_runtime:  valor en segundos
        'battery_capacity': os.getenv('OID_UPS_BATTERY_CAPACITY', '1.3.6.1.4.1.534.1.2.4.0'),
        'battery_runtime':  os.getenv('OID_UPS_BATTERY_RUNTIME',  '1.3.6.1.4.1.534.1.2.1.0'),

        # Mediciones eléctricas — UPS-MIB estándar
        'input_voltage':    os.getenv('OID_UPS_INPUT_VOLTAGE',    '1.3.6.1.2.1.33.1.3.3.1.3.1'),
        'input_frequency':  os.getenv('OID_UPS_INPUT_FREQUENCY',  '1.3.6.1.2.1.33.1.3.3.1.2.1'),
        'output_voltage':   os.getenv('OID_UPS_OUTPUT_VOLTAGE',   '1.3.6.1.2.1.33.1.4.4.1.2.1'),
        'output_frequency': os.getenv('OID_UPS_OUTPUT_FREQUENCY', '1.3.6.1.2.1.33.1.4.2.0'),
        'output_load':      os.getenv('OID_UPS_OUTPUT_LOAD',      '1.3.6.1.2.1.33.1.4.4.1.5.1'),
        'output_current':   os.getenv('OID_UPS_OUTPUT_CURRENT'),
        'output_power':     os.getenv('OID_UPS_OUTPUT_POWER',     '1.3.6.1.4.1.534.1.4.4.1.4.1'),

        # Temperatura — OID Eaton privado (sensor 1 = 19°C, coincide con interfaz web)
        # El OID estándar UPS-MIB 1.3.6.1.2.1.33.1.2.7.0 devuelve 25°C (sensor diferente)
        'temperature':      os.getenv('OID_UPS_TEMPERATURE',      '1.3.6.1.4.1.534.1.6.1.0'),

        'bypass_voltage':   os.getenv('OID_UPS_BYPASS_VOLTAGE'),

        # Alarmas — OID Eaton privado
        # Devuelve 0=sin alarmas, 1=alarma activa (más preciso que UPS-MIB estándar)
        'alarms':           os.getenv('OID_UPS_ALARMS',           '1.3.6.1.4.1.534.1.7.1.0'),
    }

    # OIDs opcionales para información del sistema
    INFO_OIDS = {
        'model':    os.getenv('OID_UPS_MODEL'),
        'firmware': os.getenv('OID_UPS_FIRMWARE'),
        'serial':   os.getenv('OID_UPS_SERIAL'),
    }

    # Factores de escala — solo frecuencias (vienen en 0.1 Hz, ej: 500 → 50.0 Hz)
    SCALE_FACTORS = {
        'input_frequency':  0.1,
        'output_frequency': 0.1,
    }


class MonitorConfig:
    """Configuración del monitor"""

    CHECK_INTERVAL    = int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))
    DAILY_REPORT_TIME = os.getenv('DAILY_REPORT_TIME', '09:00')
    DATA_DIR          = '/app/data'
    LOG_DIR           = '/app/logs'
    STATE_FILE        = os.path.join(DATA_DIR, 'ups_state.json')