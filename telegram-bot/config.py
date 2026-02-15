"""
Configuración del bot de Telegram
"""
import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig:
    """Configuración del bot de Telegram"""
    
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    DATA_DIR = '/app/data'
    LOG_DIR = '/app/logs'
    MESSAGE_QUEUE_FILE = os.path.join(DATA_DIR, 'message_queue.json')
    
    # Intervalo para verificar mensajes en cola (segundos)
    QUEUE_CHECK_INTERVAL = 5
