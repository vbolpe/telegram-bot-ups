.PHONY: help build up down restart logs logs-snmp logs-bot status clean test backup

help: ## Muestra esta ayuda
	@echo "🔋 Sistema de Monitoreo UPS - Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Construye los contenedores
	docker-compose build

up: ## Inicia los servicios
	docker-compose up -d

down: ## Detiene los servicios
	docker-compose down

restart: ## Reinicia los servicios
	docker-compose restart

logs: ## Muestra logs de todos los servicios
	docker-compose logs -f

logs-snmp: ## Muestra logs del monitor SNMP
	docker-compose logs -f snmp-monitor

logs-bot: ## Muestra logs del bot de Telegram
	docker-compose logs -f telegram-bot

status: ## Muestra el estado de los servicios
	docker-compose ps

clean: ## Limpia contenedores, volúmenes e imágenes
	docker-compose down -v
	docker-compose rm -f

test-snmp: ## Prueba la conexión SNMP
	docker-compose exec snmp-monitor python -c "from snmp_client import SNMPClient; client = SNMPClient(); print('Conexión OK' if client.test_connection() else 'Conexión FALLIDA')"

backup: ## Crea backup de los datos
	@mkdir -p backups
	@tar -czf backups/backup-$$(date +%Y%m%d-%H%M%S).tar.gz data/ logs/ .env
	@echo "Backup creado en backups/"

install: ## Instalación inicial completa
	@echo "📦 Instalación del sistema..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "⚠️  Edita .env con tu configuración"; exit 1; fi
	@mkdir -p data logs
	@chmod 755 data logs
	@make build
	@make up
	@echo "✅ Sistema instalado. Usa 'make logs' para ver el estado"

shell-snmp: ## Abre shell en el contenedor SNMP
	docker-compose exec snmp-monitor /bin/bash

shell-bot: ## Abre shell en el contenedor del bot
	docker-compose exec telegram-bot /bin/bash

update: ## Actualiza y reinicia los servicios
	git pull
	docker-compose down
	docker-compose build
	docker-compose up -d
	@echo "✅ Sistema actualizado"
