"""
Bot de Telegram para notificaciones de UPS
"""
import logging
import asyncio
import json
import os
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from config import BotConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BotConfig.LOG_DIR, 'telegram_bot.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class UPSTelegramBot:
    """Bot de Telegram para notificaciones"""
    
    def __init__(self):
        self.token = BotConfig.TOKEN
        self.chat_id = BotConfig.CHAT_ID
        self.bot = None
        self.application = None
        
        if not self.token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID son requeridos")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /start"""
        await update.message.reply_text(
            '🔋 *Bot de Monitoreo UPS*\n\n'
            'Comandos disponibles:\n'
            '/start - Muestra este mensaje\n'
            '/status - Obtiene el estado actual de la UPS\n'
            '/help - Ayuda y información',
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /status"""
        try:
            # Leer el estado actual
            state_file = os.path.join(BotConfig.DATA_DIR, 'ups_state.json')
            
            if not os.path.exists(state_file):
                await update.message.reply_text(
                    '⚠️ No hay datos de estado disponibles aún.',
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # Formatear mensaje
            from ups_state import UPSState
            ups_state = UPSState()
            message = ups_state.format_state_message(state)
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error al obtener estado: {str(e)}")
            await update.message.reply_text(
                f'❌ Error al obtener estado: {str(e)}',
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /help"""
        help_text = """
🔋 *Bot de Monitoreo UPS*

Este bot monitorea el estado de una UPS mediante SNMP v3 y envía notificaciones automáticas.

*Funcionalidades:*
• Monitoreo continuo del estado de la UPS
• Alertas automáticas ante cambios de estado
• Reporte diario programado
• Consulta de estado bajo demanda

*Comandos:*
/start - Iniciar el bot
/status - Ver estado actual de la UPS
/help - Mostrar esta ayuda

*Alertas automáticas:*
Recibirás notificaciones cuando:
• La UPS cambie a batería
• El nivel de batería sea bajo
• Cambie el voltaje de entrada/salida
• Cualquier cambio crítico en el estado

*Reporte diario:*
Se envía automáticamente un reporte completo cada día.

Para soporte o configuración, consulta la documentación del proyecto.
        """
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def send_message(self, message: str):
        """
        Envía un mensaje al chat configurado
        
        Args:
            message: Texto del mensaje a enviar
        """
        try:
            if not self.bot:
                self.bot = Bot(token=self.token)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info("Mensaje enviado correctamente")
            
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {str(e)}")
            raise
    
    async def process_message_queue(self):
        """Procesa la cola de mensajes pendientes"""
        queue_file = BotConfig.MESSAGE_QUEUE_FILE
        
        if not os.path.exists(queue_file):
            return
        
        try:
            # Leer cola
            with open(queue_file, 'r') as f:
                queue = json.load(f)
            
            if not queue:
                return
            
            sent = 0
            failed = []
            # Procesar cada mensaje
            for message_data in queue:
                try:
                    await self.send_message(message_data['message'])
                    sent += 1
                    await asyncio.sleep(1)  # Evitar rate limiting
                except Exception as e:
                    logger.error(f"Error al enviar mensaje de la cola: {str(e)}")
                    failed.append(message_data)

            # Solo conservar en cola los mensajes que fallaron
            with open(queue_file, 'w') as f:
                json.dump(failed, f, indent=2)
            
            if sent:
                logger.info(f"Procesados {sent} mensajes de la cola")
            
            if failed:
                logger.warning(f"{len(failed)} mensajes quedaron en cola por error")
                
        except Exception as e:
            logger.error(f"Error al procesar cola de mensajes: {str(e)}")
    
    async def queue_checker(self, context: ContextTypes.DEFAULT_TYPE):
        """Tarea periódica para verificar la cola de mensajes"""
        await self.process_message_queue()
    
    def start_bot(self):
            """Inicia el bot"""
            logger.info("Iniciando bot de Telegram...")
            
            # Crear aplicación
            self.application = Application.builder().token(self.token).build()
            
            # Agregar manejadores de comandos
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            
            # Programar verificación periódica de la cola
            if self.application.job_queue:
                self.application.job_queue.run_repeating(
                    self.queue_checker,
                    interval=BotConfig.QUEUE_CHECK_INTERVAL,
                    first=5
                )
                logger.info("Verificador de cola de mensajes programado")
            else:
                logger.warning("JobQueue no disponible - mensajes se procesarán manualmente")
            
            logger.info("Bot configurado correctamente")
            logger.info(f"Chat ID: {self.chat_id}")
            logger.info("Iniciando polling...")
            
            # Iniciar bot en modo polling
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Función principal"""
    try:
        bot = UPSTelegramBot()
        bot.start_bot()
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        raise

if __name__ == "__main__":
    main()
