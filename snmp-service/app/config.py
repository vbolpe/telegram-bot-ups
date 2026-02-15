import os
from dotenv import load_dotenv

load_dotenv()

UPS_IP = os.getenv("UPS_IP")
SNMP_USER = os.getenv("SNMP_USER")
AUTH_PASS = os.getenv("AUtH_PASS")
PRIV_PASS = os.getenv("PRIV_PASS")

SNMP_PORT = 161
CHECK_INTERVAL = 30
STATE_FILE = "/app/state.json"