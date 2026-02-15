"""
Servicio principal de monitoreo SNMP
"""
import logging
import time
import schedule
from datetime import datetime
from config import SNMPConfig, MonitorConfig
from snmp_client import SNMPClient
from ups_state import UPSState
import json
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(MonitorConfig.LOG_DIR, 'snmp_monitor.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class UPSMonitor:
    """Monitor principal de la UPS"""
    
    def __init__(self):
        self.snmp_client = SNMPClient()
        self.ups_state = UPSState()
        self.message_queue_file = os.path.join(MonitorConfig.DATA_DIR, 'message_queue.json')
        
    def check_ups(self):
        """Verifica el estado actual de la UPS"""
        logger.info("Verificando estado de la UPS...")
        
        try:
            # Obtener todos los valores
            data = self.snmp_client.get_all_values(SNMPConfig.OIDS)
            
            # Verificar si hay valores
            if all(v is None for v in data.values()):
                logger.error("No se pudieron obtener datos de la UPS")
                self._queue_message({
                    'type': 'error',
                    'message': '❌ Error: No se puede conectar con la UPS'
                })
                return
            
            # Actualizar estado y detectar cambios
            changes = self.ups_state.update_state(data)
            
            # Si hay cambios, encolar mensaje de alerta
            if changes:
                change_message = self.ups_state.format_change_message(changes)
                if change_message:
                    self._queue_message({
                        'type': 'alert',
                        'message': change_message
                    })
                    logger.warning(f"Cambios detectados: {changes}")
            
        except Exception as e:
            logger.error(f"Error al verificar UPS: {str(e)}")
            self._queue_message({
                'type': 'error',
                'message': f'❌ Error al verificar UPS: {str(e)}'
            })
    
    def generate_daily_report(self):
        """Genera el reporte diario"""
        logger.info("Generando reporte diario...")
        
        try:
            # Obtener estado actual
            data = self.snmp_client.get_all_values(SNMPConfig.OIDS)
            
            if all(v is None for v in data.values()):
                logger.error("No se pudieron obtener datos para el reporte diario")
                return
            
            # Generar mensaje
            message = self.ups_state.format_state_message(data)
            
            # Encolar mensaje
            self._queue_message({
                'type': 'daily_report',
                'message': f"📅 *Reporte Diario*\n\n{message}"
            })
            
            logger.info("Reporte diario generado")
            
        except Exception as e:
            logger.error(f"Error al generar reporte diario: {str(e)}")
    
    def _queue_message(self, message_data):
        """
        Agrega un mensaje a la cola para ser enviado por el bot de Telegram
        
        Args:
            message_data: Diccionario con el tipo y mensaje
        """
        try:
            os.makedirs(MonitorConfig.DATA_DIR, exist_ok=True)
            
            # Cargar cola existente
            queue = []
            if os.path.exists(self.message_queue_file):
                with open(self.message_queue_file, 'r') as f:
                    queue = json.load(f)
            
            # Agregar nuevo mensaje con timestamp
            message_data['timestamp'] = datetime.now().isoformat()
            queue.append(message_data)
            
            # Guardar cola actualizada
            with open(self.message_queue_file, 'w') as f:
                json.dump(queue, f, indent=2)
            
            logger.info(f"Mensaje encolado: {message_data['type']}")
            
        except Exception as e:
            logger.error(f"Error al encolar mensaje: {str(e)}")
    
    def start(self):
        """Inicia el monitoreo"""
        logger.info("Iniciando monitor de UPS...")
        logger.info(f"Host: {SNMPConfig.HOST}:{SNMPConfig.PORT}")
        logger.info(f"Usuario: {SNMPConfig.USER}")
        logger.info(f"Intervalo de verificación: {MonitorConfig.CHECK_INTERVAL} segundos")
        logger.info(f"Reporte diario: {MonitorConfig.DAILY_REPORT_TIME}")
        
        # Probar conexión
        if not self.snmp_client.test_connection():
            logger.error("No se pudo conectar a la UPS. Verificar configuración.")
            self._queue_message({
                'type': 'error',
                'message': '❌ Error: No se puede conectar con la UPS al iniciar'
            })
        else:
            logger.info("Conexión SNMP exitosa")
            # Enviar estado inicial
            self.generate_daily_report()
        
        # Programar tareas
        schedule.every(MonitorConfig.CHECK_INTERVAL).seconds.do(self.check_ups)
        schedule.every().day.at(MonitorConfig.DAILY_REPORT_TIME).do(self.generate_daily_report)
        
        logger.info("Monitor iniciado correctamente")
        
        # Loop principal
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Monitor detenido por el usuario")
                break
            except Exception as e:
                logger.error(f"Error en loop principal: {str(e)}")
                time.sleep(5)

if __name__ == "__main__":
    monitor = UPSMonitor()
    monitor.start()
