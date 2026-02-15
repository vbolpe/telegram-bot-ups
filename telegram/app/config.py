import os 
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID =  os.getenv("CHAT_ID")

SNMP_SERVICE_URL = os.getenv("SNMP_SERVICE_URL", "https://snmp-service:8000")

REPORT_HOUR = 9