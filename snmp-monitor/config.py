"""
Módulo de configuración para el monitor SNMP
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
    AUTH_PROTOCOL = os.getenv('SNMP_AUTH_PROTOCOL', 'SHA')
    AUTH_PASSWORD = os.getenv('SNMP_AUTH_PASSWORD', '')
    
    # Protocolos de privacidad
    PRIV_PROTOCOL = os.getenv('SNMP_PRIV_PROTOCOL', 'AES')
    PRIV_PASSWORD = os.getenv('SNMP_PRIV_PASSWORD', '')
    
    # Nivel de seguridad
    SECURITY_LEVEL = os.getenv('SNMP_SECURITY_LEVEL', 'authPriv')
    
    # OIDs de la UPS
    OIDS = {
        'status': os.getenv('OID_UPS_STATUS', '1.3.6.1.4.1.534.1.4.1.0'),
        'battery_status': os.getenv('OID_UPS_BATTERY_STATUS', '1.3.6.1.4.1.318.1.1.1.2.1.1.0'),
        'battery_capacity': os.getenv('OID_UPS_BATTERY_CAPACITY', '1.3.6.1.4.1.318.1.1.1.2.2.1.0'),
        'battery_runtime': os.getenv('OID_UPS_BATTERY_RUNTIME', '1.3.6.1.4.1.318.1.1.1.2.2.3.0'),
        'input_voltage': os.getenv('OID_UPS_INPUT_VOLTAGE', '1.3.6.1.4.1.534.1.3.4.1.2.1'),
        'input_frequency': os.getenv('OID_UPS_INPUT_FREQUENCY', '1.3.6.1.4.1.534.1.3.1.0'),
        'output_voltage': os.getenv('OID_UPS_OUTPUT_VOLTAGE', '1.3.6.1.4.1.534.1.4.4.1.2.1'),
        'output_frequency': os.getenv('OID_UPS_OUTPUT_FREQUENCY', '1.3.6.1.4.1.534.1.4.2.0'),
        'output_load': os.getenv('OID_UPS_OUTPUT_LOAD', '1.3.6.1.4.1.534.1.4.3.0'),
        'output_current': os.getenv('OID_UPS_OUTPUT_CURRENT'),
        'output_power': os.getenv('OID_UPS_OUTPUT_POWER', '1.3.6.1.4.1.534.1.4.4.1.4.1'),
        'temperature': os.getenv('OID_UPS_TEMPERATURE', '1.3.6.1.4.1.318.1.1.1.2.2.2.0'),
        'bypass_voltage': os.getenv('OID_UPS_BYPASS_VOLTAGE'),
        'alarms': os.getenv('OID_UPS_ALARMS', '1.3.6.1.4.1.534.1.4.8.0'),
    }
    
    # OIDs opcionales para información del sistema
    INFO_OIDS = {
        'model': os.getenv('OID_UPS_MODEL'),
        'firmware': os.getenv('OID_UPS_FIRMWARE'),
        'serial': os.getenv('OID_UPS_SERIAL'),
    }
    
    # Factores de escala para valores de Eaton 93E
    # Solo la frecuencia necesita escalado (viene en 0.1 Hz)
    SCALE_FACTORS = {
        'input_frequency': 0.1,   # 500 → 50.0 Hz
        'output_frequency': 0.1,  # 500 → 50.0 Hz
    }

class MonitorConfig:
    """Configuración del monitor"""
    
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))
    DAILY_REPORT_TIME = os.getenv('DAILY_REPORT_TIME', '09:00')
    DATA_DIR = '/app/data'
    LOG_DIR = '/app/logs'
    STATE_FILE = os.path.join(DATA_DIR, 'ups_state.json')
