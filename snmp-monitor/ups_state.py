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

    # Mapeo validado contra Eaton 93E real
    # OID: 1.3.6.1.2.1.33.1.4.1.0
    # Valor confirmado: 3=Online (UPS en red normal)
    STATUS_MAP = {
        '1':  'Unknown',
        '2':  'Online (Normal)',
        '3':  'Online',                # Confirmado: valor normal en Eaton 93E
        '4':  'On Boost',
        '5':  'On Battery',            # CRÍTICO: UPS en batería
        '6':  'Off',
        '7':  'Rebooting',
        '8':  'On Bypass',
        '9':  'Hardware Failure',
        '10': 'Software Failure',
        '11': 'In Test',
        '12': 'Emergency Static Bypass',
        '14': 'Power Saving (ECOnversion)',
    }

    # OID: 1.3.6.1.2.1.33.1.2.1.0
    BATTERY_STATUS_MAP = {
        '1': 'Unknown',
        '2': 'Battery Normal',
        '3': 'Battery Low',       # CRÍTICO
        '4': 'Battery Depleted',  # CRÍTICO
        '8': 'Charging',
    }

    # Estados que requieren alerta inmediata
    CRITICAL_STATUSES = {'5', '9', '10', '12'}         # On Battery, failures
    CRITICAL_BATTERY_STATUSES = {'3', '4'}              # Low, Depleted

    # Umbrales mínimos de cambio para generar alerta (evitar ruido)
    CHANGE_THRESHOLDS = {
        'input_voltage':    5.0,   # V  — no alertar por ±1V de ruido
        'output_voltage':   5.0,   # V
        'bypass_voltage':   5.0,   # V
        'battery_capacity': 5.0,   # %  — alertar cada 5%
        'output_load':      5.0,   # %
        'output_current':   1.0,   # A
        'temperature':      3.0,   # °C
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

    def _exceeds_threshold(self, key, old_val, new_val):
        """
        Determina si un cambio numérico supera el umbral mínimo para alertar.
        Para claves sin umbral definido, siempre retorna True (alertar).
        """
        if key not in self.CHANGE_THRESHOLDS:
            return True
        try:
            return abs(float(new_val) - float(old_val)) >= self.CHANGE_THRESHOLDS[key]
        except (TypeError, ValueError):
            return old_val != new_val

    def update_state(self, new_data):
        """
        Actualiza el estado con nuevos datos.

        Returns:
            Diccionario con los cambios que superan el umbral.
        """
        changes = {}
        timestamp = datetime.now().isoformat()

        for key, new_value in new_data.items():
            old_value = self.current_state.get(key)

            if old_value is None or old_value == new_value:
                continue

            if self._exceeds_threshold(key, old_value, new_value):
                changes[key] = {'old': old_value, 'new': new_value}
                logger.info(f"Cambio detectado en {key}: {old_value} -> {new_value}")

        self.current_state.update(new_data)
        self.current_state['last_update'] = timestamp
        self._save_state()

        return changes

    def get_state(self):
        """Retorna el estado actual"""
        return self.current_state

    def format_state_message(self, data):
        """Formatea los datos de estado en un mensaje legible"""
        status_code = data.get('status', '1')
        status_text = self.STATUS_MAP.get(status_code, f'Desconocido ({status_code})')

        battery_status_code = data.get('battery_status', '1')
        battery_status_text = self.BATTERY_STATUS_MAP.get(
            battery_status_code,
            f'Desconocido ({battery_status_code})'
        )

        # Icono de estado
        status_icon = '🔴' if status_code in self.CRITICAL_STATUSES else '🟢'
        battery_icon = '🔴' if battery_status_code in self.CRITICAL_BATTERY_STATUSES else '🔋'

        message = (
            f"🔋 *Estado de la UPS*\n\n"
            f"{status_icon} *Estado General:* {status_text}\n"
            f"{battery_icon} *Batería:* {battery_status_text}\n"
            f"⚡ *Carga Batería:* {data.get('battery_capacity', 'N/A')}%\n"
            f"⏱️ *Autonomía:* {self._format_runtime(data.get('battery_runtime'))}\n\n"
            f"📥 *Entrada:*\n"
            f"   • Voltaje: {data.get('input_voltage', 'N/A')} V"
        )

        if data.get('input_frequency'):
            message += f"\n   • Frecuencia: {data.get('input_frequency')} Hz"

        message += f"\n\n📤 *Salida:*\n   • Voltaje: {data.get('output_voltage', 'N/A')} V"

        if data.get('output_frequency'):
            message += f"\n   • Frecuencia: {data.get('output_frequency')} Hz"

        message += f"\n   • Carga: {data.get('output_load', 'N/A')}%"

        if data.get('output_current'):
            message += f"\n   • Corriente: {data.get('output_current')} A"

        if data.get('output_power'):
            try:
                power_kw = float(data.get('output_power', 0)) / 1000
                message += f"\n   • Potencia: {power_kw:.1f} kW"
            except (ValueError, TypeError):
                message += f"\n   • Potencia: {data.get('output_power')} W"

        if data.get('bypass_voltage'):
            message += f"\n\n🔄 *Bypass:* {data.get('bypass_voltage')} V"

        message += f"\n\n🌡️ *Temperatura:* {data.get('temperature', 'N/A')}°C"

        if data.get('alarms') and data.get('alarms') != '0':
            message += f"\n⚠️ *Alarmas Activas:* {data.get('alarms')}"

        message += f"\n\n🕐 *Última actualización:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return message

    def format_change_message(self, changes):
        """Formatea un mensaje de alerta por cambios detectados"""
        if not changes:
            return None

        # Determinar si algún cambio es crítico
        is_critical = (
            ('status' in changes and changes['status']['new'] in self.CRITICAL_STATUSES) or
            ('battery_status' in changes and changes['battery_status']['new'] in self.CRITICAL_BATTERY_STATUSES)
        )

        header = "🚨 *ALERTA CRÍTICA UPS*\n\n" if is_critical else "⚠️ *Cambio en el estado de la UPS*\n\n"
        message = header

        for key, change in changes.items():
            old_val = change['old']
            new_val = change['new']

            if key == 'status':
                old_text = self.STATUS_MAP.get(old_val, old_val)
                new_text = self.STATUS_MAP.get(new_val, new_val)
                icon = '🚨' if new_val in self.CRITICAL_STATUSES else '🔄'
                message += f"{icon} *Estado:* {old_text} → {new_text}\n"
            elif key == 'battery_status':
                old_text = self.BATTERY_STATUS_MAP.get(old_val, old_val)
                new_text = self.BATTERY_STATUS_MAP.get(new_val, new_val)
                icon = '🚨' if new_val in self.CRITICAL_BATTERY_STATUSES else '🔋'
                message += f"{icon} *Estado Batería:* {old_text} → {new_text}\n"
            elif key == 'battery_capacity':
                message += f"⚡ *Carga Batería:* {old_val}% → {new_val}%\n"
            elif key in ('input_voltage', 'output_voltage', 'bypass_voltage'):
                label = key.replace('_', ' ').title()
                message += f"📊 *{label}:* {old_val}V → {new_val}V\n"
            elif key == 'temperature':
                message += f"🌡️ *Temperatura:* {old_val}°C → {new_val}°C\n"
            else:
                message += f"• *{key}:* {old_val} → {new_val}\n"

        message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return message

    def _format_runtime(self, runtime):
        """
        Formatea el tiempo de autonomía.
        OID Eaton privado 1.3.6.1.4.1.534.1.2.1.0 devuelve SEGUNDOS.
        Validado: 7747s = 2h 9min (coincide con interfaz web Eaton).
        """
        if runtime is None or runtime == 'N/A':
            return 'N/A'
        try:
            total_seconds = int(runtime)
            hours = total_seconds // 3600
            mins = (total_seconds % 3600) // 60
            if hours > 0:
                return f"{hours}h {mins}min"
            else:
                return f"{mins} min"
        except (ValueError, TypeError):
            return str(runtime)