import requests
from .config import SNMP_SERVICE_URL

def get_status():
    try: 
        r = requests.get(f"{SNMP_SERVICE_URL}/status", timeout=5)
        return r.json()
    except Exception:
        return None
    
def get_event():
    try:
        r = requests.get(f"{SNMP_SERVICE_URL}/event", timeout=5)
        return r.json()
    except Exception:
        return None
    