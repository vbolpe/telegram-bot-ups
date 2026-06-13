"""
Cliente SNMP v3 para consultar la UPS
Compatible con pysnmp >= 7.0 (nueva API asyncio)
"""
import asyncio
import logging
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    UsmUserData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
    usmHMACMD5AuthProtocol,
    usmHMACSHAAuthProtocol,
    usmHMAC128SHA224AuthProtocol,
    usmHMAC192SHA256AuthProtocol,
    usmHMAC256SHA384AuthProtocol,
    usmHMAC384SHA512AuthProtocol,
    usmDESPrivProtocol,
    usmAesCfb128Protocol,
    usmAesCfb192Protocol,
    usmAesCfb256Protocol,
    usm3DESEDEPrivProtocol,
)
from config import SNMPConfig

logger = logging.getLogger(__name__)


class SNMPClient:
    """Cliente para realizar consultas SNMP v3"""

    def __init__(self):
        self.host = SNMPConfig.HOST
        self.port = SNMPConfig.PORT
        self.user = SNMPConfig.USER
        self.auth_protocol = self._get_auth_protocol()
        self.auth_password = SNMPConfig.AUTH_PASSWORD
        self.priv_protocol = self._get_priv_protocol()
        self.priv_password = SNMPConfig.PRIV_PASSWORD

    def _get_auth_protocol(self):
        protocols = {
            'MD5':    usmHMACMD5AuthProtocol,
            'SHA':    usmHMACSHAAuthProtocol,
            'SHA224': usmHMAC128SHA224AuthProtocol,
            'SHA256': usmHMAC192SHA256AuthProtocol,
            'SHA384': usmHMAC256SHA384AuthProtocol,
            'SHA512': usmHMAC384SHA512AuthProtocol,
        }
        name = SNMPConfig.AUTH_PROTOCOL.upper()
        if name not in protocols:
            logger.warning(f"Protocolo de auth '{name}' no reconocido, usando MD5")
            return usmHMACMD5AuthProtocol
        return protocols[name]

    def _get_priv_protocol(self):
        protocols = {
            'DES':    usmDESPrivProtocol,
            'AES':    usmAesCfb128Protocol,
            'AES128': usmAesCfb128Protocol,
            'AES192': usmAesCfb192Protocol,
            'AES256': usmAesCfb256Protocol,
            '3DES':   usm3DESEDEPrivProtocol,
        }
        name = SNMPConfig.PRIV_PROTOCOL.upper()
        if name not in protocols:
            logger.warning(f"Protocolo de privacidad '{name}' no reconocido, usando DES")
            return usmDESPrivProtocol
        return protocols[name]

    async def _get_value_async(self, snmp_engine, oid):
        """Obtiene el valor de un OID de forma asíncrona (reutiliza el engine)"""
        try:
            transport = await UdpTransportTarget.create(
                (self.host, self.port), timeout=5.0, retries=3
            )
            error_indication, error_status, error_index, var_binds = await get_cmd(
                snmp_engine,
                UsmUserData(
                    self.user,
                    self.auth_password,
                    self.priv_password,
                    authProtocol=self.auth_protocol,
                    privProtocol=self.priv_protocol,
                ),
                transport,
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            )

            if error_indication:
                logger.error(f"Error SNMP [{oid}]: {error_indication}")
                return None
            if error_status:
                logger.error(f"Error SNMP status [{oid}]: {error_status.prettyPrint()}")
                return None

            for var_bind in var_binds:
                return var_bind[1].prettyPrint()

        except Exception as e:
            logger.error(f"Excepción al obtener OID {oid}: {str(e)}")
            return None

    def get_value(self, oid):
        """Obtiene el valor de un OID (interfaz síncrona para compatibilidad)"""
        return asyncio.run(self._get_all_async({oid: oid})).get(oid)

    async def _get_all_async(self, oids_dict):
        """Consulta todos los OIDs compartiendo un único SnmpEngine"""
        snmp_engine = SnmpEngine()
        results = {}
        try:
            for name, oid in oids_dict.items():
                if oid is None:
                    continue
                value = await self._get_value_async(snmp_engine, oid)

                # Aplicar factor de escala si corresponde
                if value is not None and name in SNMPConfig.SCALE_FACTORS:
                    try:
                        scaled = float(value) * SNMPConfig.SCALE_FACTORS[name]
                        value = str(round(scaled, 1))
                    except (ValueError, TypeError):
                        pass

                results[name] = value
                logger.debug(f"{name}: {value}")
        finally:
            snmp_engine.close_dispatcher()

        return results

    def get_all_values(self, oids_dict):
        """
        Obtiene todos los valores del diccionario de OIDs.
        Interfaz síncrona que internamente usa asyncio.
        """
        return asyncio.run(self._get_all_async(oids_dict))

    def test_connection(self):
        """Prueba la conexión SNMP obteniendo el OID de estado"""
        try:
            value = self.get_all_values({'status': SNMPConfig.OIDS['status']}).get('status')
            return value is not None
        except Exception as e:
            logger.error(f"Error al probar conexión: {str(e)}")
            return False