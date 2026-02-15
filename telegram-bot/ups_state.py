"""
Módulo para formatear el estado de la UPS (versión simplificada para bot)
"""
from datetime import datetime

class UPSState:
    """Gestión del estado de la UPS"""
    
    # Mapeo de estados comunes de UPS
    STATUS_MAP = {
        '1': 'Unknown',
        '2': 'Online (Normal)',
        '3': 'On Battery',
        '4': 'On Boost',
        '5': 'On Sleep',
        '6': 'Off',
        '7': 'Rebooting',
        '8': 'On Bypass',
        '9': 'Hardware Failure',
        '10': 'Software Failure',
        '11': 'In Test',
        '12': 'Emergency Static Bypass',
    }
    
    BATTERY_STATUS_MAP = {
        '1': 'Unknown',
        '2': 'Battery Normal',
        '3': 'Battery Low',
        '4': 'Battery Depleted',
    }
    
    def format_state_message(self, data):
        """
        Formatea los datos de estado en un mensaje legible
        
        Args:
            data: Diccionario con los datos de la UPS
            
        Returns:
            String con el mensaje formateado
        """
        status_code = data.get('status', '1')
        status_text = self.STATUS_MAP.get(status_code, f'Desconocido ({status_code})')
        
        battery_status_code = data.get('battery_status', '1')
        battery_status_text = self.BATTERY_STATUS_MAP.get(
            battery_status_code, 
            f'Desconocido ({battery_status_code})'
        )
        
        last_update = data.get('last_update', datetime.now().isoformat())
        
        try:
            last_update_dt = datetime.fromisoformat(last_update)
            last_update_str = last_update_dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            last_update_str = last_update
        
        message = f"""🔋 *Estado de la UPS*

📊 *Estado General:* {status_text}
🔋 *Batería:* {battery_status_text}
⚡ *Carga:* {data.get('battery_capacity', 'N/A')}%
⏱️ *Autonomía:* {self._format_runtime(data.get('battery_runtime'))}

📥 *Voltaje Entrada:* {data.get('input_voltage', 'N/A')} V
📤 *Voltaje Salida:* {data.get('output_voltage', 'N/A')} V
📊 *Carga de Salida:* {data.get('output_load', 'N/A')}%
🌡️ *Temperatura:* {data.get('temperature', 'N/A')}°C

🕐 *Última actualización:* {last_update_str}
"""
        return message
    
    def _format_runtime(self, runtime):
        """Formatea el tiempo de autonomía"""
        if runtime is None or runtime == 'N/A':
            return 'N/A'
        
        try:
            # El runtime suele venir en minutos
            minutes = int(runtime)
            hours = minutes // 60
            mins = minutes % 60
            
            if hours > 0:
                return f"{hours}h {mins}min"
            else:
                return f"{mins} min"
        except:
            return str(runtime)
