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
        'status': os.getenv('OID_UPS_STATUS', '1.3.6.1.4.1.318.1.1.1.4.1.1.0'),
        'battery_status': os.getenv('OID_UPS_BATTERY_STATUS', '1.3.6.1.4.1.318.1.1.1.2.1.1.0'),
        'battery_capacity': os.getenv('OID_UPS_BATTERY_CAPACITY', '1.3.6.1.4.1.318.1.1.1.2.2.1.0'),
        'battery_runtime': os.getenv('OID_UPS_BATTERY_RUNTIME', '1.3.6.1.4.1.318.1.1.1.2.2.3.0'),
        'input_voltage': os.getenv('OID_UPS_INPUT_VOLTAGE', '1.3.6.1.4.1.318.1.1.1.3.2.1.0'),
        'output_voltage': os.getenv('OID_UPS_OUTPUT_VOLTAGE', '1.3.6.1.4.1.318.1.1.1.4.2.1.0'),
        'output_load': os.getenv('OID_UPS_OUTPUT_LOAD', '1.3.6.1.4.1.318.1.1.1.4.2.3.0'),
        'temperature': os.getenv('OID_UPS_TEMPERATURE', '1.3.6.1.4.1.318.1.1.1.2.2.2.0'),
    }

class MonitorConfig:
    """Configuración del monitor"""
    
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))
    DAILY_REPORT_TIME = os.getenv('DAILY_REPORT_TIME', '09:00')
    DATA_DIR = '/app/data'
    LOG_DIR = '/app/logs'
    STATE_FILE = os.path.join(DATA_DIR, 'ups_state.json')
