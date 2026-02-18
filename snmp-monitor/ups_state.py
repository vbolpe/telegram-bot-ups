"""
Módulo para gestionar el estado de la UPS
"""
import json
import os
from datetime import datetime
from config import MonitorConfig
import logging

logger = logging.getLogger(__name__)

class UPSState:
    """Gestión del estado de la UPS"""
    
    # Mapeo de estados comunes de UPS (ajustar según fabricante)
    STATUS_MAP = {
        '1': 'Unknown',
        #'2': 'Online (Normal)',
        '3': 'Online',
        '4': 'On Bypass',
        '5': 'On Battery',
        '6': 'Off',
        '7': 'Rebooting',
        #'8': 'On Bypass',
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
    
    def __init__(self):
        self.state_file = MonitorConfig.STATE_FILE
        self.current_state = self._load_state()
    
    def _load_state(self):
        """Carga el estado previo desde el archivo"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error al cargar estado: {str(e)}")
            return {}
    
    def _save_state(self):
        """Guarda el estado actual en el archivo"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.current_state, f, indent=2)
        except Exception as e:
            logger.error(f"Error al guardar estado: {str(e)}")
    
    def update_state(self, new_data):
        """
        Actualiza el estado con nuevos datos
        
        Args:
            new_data: Diccionario con los nuevos valores
            
        Returns:
            Diccionario con los cambios detectados
        """
        changes = {}
        timestamp = datetime.now().isoformat()
        
        # Detectar cambios
        for key, new_value in new_data.items():
            old_value = self.current_state.get(key)
            if old_value != new_value and old_value is not None:
                changes[key] = {
                    'old': old_value,
                    'new': new_value
                }
                logger.info(f"Cambio detectado en {key}: {old_value} -> {new_value}")
        
        # Actualizar estado
        self.current_state.update(new_data)
        self.current_state['last_update'] = timestamp
        
        # Guardar estado
        self._save_state()
        
        return changes
    
    def get_state(self):
        """Retorna el estado actual"""
        return self.current_state
    
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
        
        # Construir mensaje base
        message = f"""🔋 *Estado de la UPS*

📊 *Estado General:* {status_text}
🔋 *Batería:* {battery_status_text}
⚡ *Carga Batería:* {data.get('battery_capacity', 'N/A')}%
⏱️ *Autonomía:* {self._format_runtime(data.get('battery_runtime'))}

📥 *Entrada:*
   • Voltaje: {data.get('input_voltage', 'N/A')} V"""
        
        # Agregar frecuencia de entrada si está disponible
        if data.get('input_frequency'):
            message += f"\n   • Frecuencia: {data.get('input_frequency')} Hz"
        
        message += f"""

📤 *Salida:*
   • Voltaje: {data.get('output_voltage', 'N/A')} V"""
        
        # Agregar frecuencia de salida si está disponible
        if data.get('output_frequency'):
            message += f"\n   • Frecuencia: {data.get('output_frequency')} Hz"
            
        message += f"\n   • Carga: {data.get('output_load', 'N/A')}%"
        
        # Agregar corriente si está disponible
        if data.get('output_current'):
            message += f"\n   • Corriente: {data.get('output_current')} A"
        
        # Agregar potencia si está disponible
        if data.get('output_power'):
            power_kw = float(data.get('output_power', 0)) / 1000
            message += f"\n   • Potencia: {power_kw:.1f} kW"
        
        # Agregar bypass si está disponible
        if data.get('bypass_voltage'):
            message += f"\n\n🔄 *Bypass:* {data.get('bypass_voltage')} V"
        
        # Agregar temperatura
        message += f"\n\n🌡️ *Temperatura:* {data.get('temperature', 'N/A')}°C"
        
        # Agregar alarmas si existen
        if data.get('alarms') and data.get('alarms') != '0':
            message += f"\n⚠️ *Alarmas Activas:* {data.get('alarms')}"
        
        message += f"\n\n🕐 *Última actualización:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message
    
    def format_change_message(self, changes):
        """
        Formatea un mensaje de cambios detectados
        
        Args:
            changes: Diccionario con los cambios
            
        Returns:
            String con el mensaje de alerta
        """
        if not changes:
            return None
        
        message = "⚠️ *ALERTA: Cambio en el estado de la UPS*\n\n"
        
        for key, change in changes.items():
            old_val = change['old']
            new_val = change['new']
            
            # Formatear según el tipo de cambio
            if key == 'status':
                old_text = self.STATUS_MAP.get(old_val, old_val)
                new_text = self.STATUS_MAP.get(new_val, new_val)
                message += f"🔄 *Estado:* {old_text} → {new_text}\n"
            elif key == 'battery_status':
                old_text = self.BATTERY_STATUS_MAP.get(old_val, old_val)
                new_text = self.BATTERY_STATUS_MAP.get(new_val, new_val)
                message += f"🔋 *Estado Batería:* {old_text} → {new_text}\n"
            elif key == 'battery_capacity':
                message += f"⚡ *Carga Batería:* {old_val}% → {new_val}%\n"
            elif key in ['input_voltage', 'output_voltage']:
                message += f"📊 *{key.replace('_', ' ').title()}:* {old_val}V → {new_val}V\n"
            else:
                message += f"• *{key}:* {old_val} → {new_val}\n"
        
        message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
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
