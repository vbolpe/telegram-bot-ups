#!/bin/bash

# Script de inicio rápido para el sistema de monitoreo UPS

set -e

echo "🔋 Sistema de Monitoreo de UPS - Instalación"
echo "============================================"
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instalar Docker primero."
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instalar Docker Compose primero."
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde plantilla..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tu configuración:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_ID"
    echo "   - SNMP_HOST y credenciales"
    echo "   - OIDs específicos de tu UPS"
    echo ""
    read -p "Presiona Enter cuando hayas configurado el archivo .env..."
else
    echo "✅ Archivo .env encontrado"
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p data logs
chmod 755 data logs

# Construir e iniciar servicios
echo ""
echo "🚀 Construyendo e iniciando servicios..."
docker-compose up -d --build

# Esperar a que los servicios se inicien
echo ""
echo "⏳ Esperando que los servicios se inicien..."
sleep 5

# Mostrar estado
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

echo ""
echo "✅ Sistema iniciado correctamente!"
echo ""
echo "📱 Comandos útiles:"
echo "   Ver logs:              docker-compose logs -f"
echo "   Ver logs SNMP:         docker-compose logs -f snmp-monitor"
echo "   Ver logs Telegram:     docker-compose logs -f telegram-bot"
echo "   Reiniciar:             docker-compose restart"
echo "   Detener:               docker-compose down"
echo "   Ver estado:            docker-compose ps"
echo ""
echo "🔍 Logs guardados en:     ./logs/"
echo "💾 Datos guardados en:    ./data/"
echo ""
echo "📖 Para más información, consulta el README.md"
