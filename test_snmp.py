#!/usr/bin/env python3
"""
Script de prueba para verificar la conectividad SNMP
Ejecutar: python test_snmp.py
"""

import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'snmp-monitor'))

from snmp_client import SNMPClient
from config import SNMPConfig

def print_separator():
    print("=" * 60)

def test_connection():
    """Prueba la conexión básica SNMP"""
    print_separator()
    print("🔍 PRUEBA 1: Conexión SNMP")
    print_separator()
    
    print(f"Host: {SNMPConfig.HOST}:{SNMPConfig.PORT}")
    print(f"Usuario: {SNMPConfig.USER}")
    print(f"Auth Protocol: {SNMPConfig.AUTH_PROTOCOL}")
    print(f"Priv Protocol: {SNMPConfig.PRIV_PROTOCOL}")
    print()
    
    client = SNMPClient()
    
    if client.test_connection():
        print("✅ Conexión SNMP exitosa")
        return True
    else:
        print("❌ Error al conectar con la UPS")
        print("\nVerifica:")
        print("  - La IP de la UPS es correcta")
        print("  - SNMP v3 está habilitado en la UPS")
        print("  - Las credenciales son correctas")
        print("  - No hay firewall bloqueando el puerto 161")
        return False

def test_oids():
    """Prueba todos los OIDs configurados"""
    print_separator()
    print("🔍 PRUEBA 2: Lectura de OIDs")
    print_separator()
    
    client = SNMPClient()
    results = client.get_all_values(SNMPConfig.OIDS)
    
    success_count = 0
    fail_count = 0
    
    for name, value in results.items():
        status = "✅" if value is not None else "❌"
        print(f"{status} {name:20} = {value}")
        
        if value is not None:
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print(f"Exitosos: {success_count}/{len(results)}")
    print(f"Fallidos: {fail_count}/{len(results)}")
    
    if fail_count > 0:
        print("\n⚠️  Algunos OIDs no retornaron valores.")
        print("Posibles causas:")
        print("  - OIDs incorrectos para tu modelo de UPS")
        print("  - Valores no soportados por tu modelo")
        print("\nConsulta OIDS.md para encontrar los OIDs correctos.")
    
    return fail_count == 0

def test_state_formatting():
    """Prueba el formateo de mensajes"""
    print_separator()
    print("🔍 PRUEBA 3: Formateo de Mensajes")
    print_separator()
    
    from ups_state import UPSState
    
    client = SNMPClient()
    data = client.get_all_values(SNMPConfig.OIDS)
    
    if all(v is None for v in data.values()):
        print("❌ No hay datos para formatear")
        return False
    
    ups_state = UPSState()
    message = ups_state.format_state_message(data)
    
    print("Mensaje generado:")
    print()
    print(message)
    
    return True

def test_environment():
    """Verifica las variables de entorno"""
    print_separator()
    print("🔍 PRUEBA 0: Variables de Entorno")
    print_separator()
    
    required_vars = [
        'SNMP_HOST',
        'SNMP_USER',
        'SNMP_AUTH_PASSWORD',
        'SNMP_PRIV_PASSWORD',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Ocultar parcialmente valores sensibles
            if 'PASSWORD' in var or 'TOKEN' in var:
                display = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
            else:
                display = value
            print(f"✅ {var:25} = {display}")
        else:
            print(f"❌ {var:25} = NO CONFIGURADA")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Faltan variables de entorno.")
        print("Edita el archivo .env con tu configuración.")
    
    return all_ok

def main():
    """Ejecuta todas las pruebas"""
    print()
    print("🔋 SISTEMA DE PRUEBAS - Monitor UPS")
    print()
    
    tests = [
        ("Variables de Entorno", test_environment),
        ("Conexión SNMP", test_connection),
        ("Lectura de OIDs", test_oids),
        ("Formateo de Mensajes", test_state_formatting),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Error en prueba: {str(e)}")
            results[test_name] = False
        print()
    
    # Resumen final
    print_separator()
    print("📊 RESUMEN DE PRUEBAS")
    print_separator()
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print_separator()
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\nTotal: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron. Revisa la configuración.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
