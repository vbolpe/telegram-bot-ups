from pysnmp.hlapi import *
from .config import UPS_IP, SNMP_USER, AUTH_PASS, PRIV_PASS, SNMP_PORT

def snmp_get(oid: str):
    iterator = getCmd(
        SnmpEngine(),
        UsmUserData(
            SNMP_USER,
            AUTH_PASS,
            PRIV_PASS,
            authProtocol=usmHMACSHAAuthProtocol,
            privProtocol=usmAesCfb128Protocol,
        ),
        udpTranportTarget((UPS_IP,SNMP_PORT), timeout=3, retries=1).
        ContextData(),
        objectType(objectIdentity(oid)),
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        raise Exception(str(errorIndication))
    if errorStatus:
        raise Exception(str(errorStatus))
    
    for varBind in varBinds:
        return varBind[1]
    
def get_ups_status():
    try:

        # OIDs estándar UPS-MIB
        status_oid = "1.3.6.1.2.1.33.1.2.1.0"
        battery_oid = "1.3.6.1.2.1.33.1.2.4.0"
        load_oid = "1.3.6.1.2.1.33.1.4.4.1.5.1"

        status = int(snmp_get(status_oid))
        battery = int(snmp_get(battery_oid))
        load = int(snmp_get(load_oid))

        return {
            "status": map_status(status),
            "battery": battery,
            "load": load,
        }
    except Exception:
        return{
            "status": "COMMUNICATION_LOST",
            "battery": None,
            "load": None,
        }
    
def map_status(code: int) -> str:
    mapping = {
        1: "UNKNOWN",
        2: "ONLINE",
        3: "ON_BATTERY",
        4: "ON_BYPASS",
        5: "SHUTDOWN",
    }
    return mapping.get(code, "UNKNOWN")