"""
Cliente SNMP v3 para consultar la UPS
"""
from pysnmp.hlapi import *
from config import SNMPConfig
import logging

logger = logging.getLogger(__name__)

class SNMPClient:
    """Cliente para realizar consultas SNMP v3"""
    
    def __init__(self):
        self.host = SNMPConfig.HOST
        self.port = SNMPConfig.PORT
        self.user = SNMPConfig.USER
        
        # Configurar autenticación
        self.auth_protocol = self._get_auth_protocol()
        self.auth_password = SNMPConfig.AUTH_PASSWORD
        
        # Configurar privacidad
        self.priv_protocol = self._get_priv_protocol()
        self.priv_password = SNMPConfig.PRIV_PASSWORD
        
    def _get_auth_protocol(self):
        """Obtiene el protocolo de autenticación"""
        protocols = {
            'MD5': usmHMACMD5AuthProtocol,
            'SHA': usmHMACSHAAuthProtocol,
            'SHA224': usmHMAC128SHA224AuthProtocol,
            'SHA256': usmHMAC192SHA256AuthProtocol,
            'SHA384': usmHMAC256SHA384AuthProtocol,
            'SHA512': usmHMAC384SHA512AuthProtocol,
        }
        return protocols.get(SNMPConfig.AUTH_PROTOCOL.upper(), usmHMACSHAAuthProtocol)
    
    def _get_priv_protocol(self):
        """Obtiene el protocolo de privacidad"""
        protocols = {
            'DES': usmDESPrivProtocol,
            'AES': usmAesCfb128Protocol,
            'AES128': usmAesCfb128Protocol,
            'AES192': usmAesCfb192Protocol,
            'AES256': usmAesCfb256Protocol,
        }
        return protocols.get(SNMPConfig.PRIV_PROTOCOL.upper(), usmAesCfb128Protocol)
    
    def get_value(self, oid):
        """
        Obtiene el valor de un OID específico
        
        Args:
            oid: OID a consultar
            
        Returns:
            Valor del OID o None si hay error
        """
        try:
            iterator = getCmd(
                SnmpEngine(),
                UsmUserData(
                    self.user,
                    self.auth_password,
                    self.priv_password,
                    authProtocol=self.auth_protocol,
                    privProtocol=self.priv_protocol
                ),
                UdpTransportTarget((self.host, self.port), timeout=5.0, retries=3),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if errorIndication:
                logger.error(f"Error de indicación SNMP: {errorIndication}")
                return None
            elif errorStatus:
                logger.error(f"Error de estado SNMP: {errorStatus.prettyPrint()}")
                return None
            else:
                for varBind in varBinds:
                    return varBind[1].prettyPrint()
                    
        except Exception as e:
            logger.error(f"Error al obtener OID {oid}: {str(e)}")
            return None
    
    def get_all_values(self, oids_dict):
        """
        Obtiene todos los valores de un diccionario de OIDs
        
        Args:
            oids_dict: Diccionario con nombres y OIDs
            
        Returns:
            Diccionario con los valores obtenidos
        """
        results = {}
        for name, oid in oids_dict.items():
            if oid is None:  # Skip si el OID no está configurado
                continue
                
            value = self.get_value(oid)
            
            # Aplicar factor de escala si existe
            if value is not None and name in SNMPConfig.SCALE_FACTORS:
                try:
                    numeric_value = float(value)
                    scaled_value = numeric_value * SNMPConfig.SCALE_FACTORS[name]
                    # Redondear a 1 decimal para voltajes/frecuencias
                    value = str(round(scaled_value, 1))
                except (ValueError, TypeError):
                    pass  # Mantener el valor original si no se puede convertir
            
            results[name] = value
            logger.debug(f"{name}: {value}")
        
        return results
    
    def test_connection(self):
        """
        Prueba la conexión SNMP
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Intentar obtener el OID de estado
            value = self.get_value(SNMPConfig.OIDS['status'])
            return value is not None
        except Exception as e:
            logger.error(f"Error al probar conexión: {str(e)}")
            return False
