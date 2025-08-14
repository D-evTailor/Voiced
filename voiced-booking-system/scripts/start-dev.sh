#!/bin/bash

# VoiceAppoint - Quick Start Script
# Este script configura y ejecuta el entorno completo de desarrollo

set -e

echo "🚀 VoiceAppoint - Iniciando entorno de desarrollo..."

# Verificar que Docker está ejecutándose
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está ejecutándose. Por favor, inicia Docker Desktop."
    exit 1
fi

# Verificar que Docker Compose está disponible
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ Docker Compose no está instalado."
    exit 1
fi

# Crear archivos .env si no existen
echo "📝 Configurando variables de entorno..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Creado .env principal"
fi

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Creado .env del backend"
fi

# Construir y ejecutar servicios
echo "🔨 Construyendo imágenes Docker..."
docker-compose build --parallel

echo "🗄️ Iniciando servicios de base de datos..."
docker-compose up -d db redis

echo "⏳ Esperando que los servicios estén listos..."
sleep 10

echo "🚀 Ejecutando migraciones..."
docker-compose run --rm backend poetry run python manage.py migrate

echo "👤 Creando superusuario y datos de prueba..."
docker-compose run --rm backend poetry run python manage.py create_sample_data

echo "🌐 Iniciando todos los servicios..."
docker-compose up -d

echo ""
echo "✅ ¡Entorno listo!"
echo ""
echo "📱 Aplicación Frontend: http://localhost:3000"
echo "🔧 API Backend: http://localhost:8000"
echo "🗄️ PgAdmin: http://localhost:8080 (admin@voiceappoint.com / admin)"
echo "📊 Redis Commander: http://localhost:8081"
echo "🌍 Nginx Proxy: http://localhost"
echo ""
echo "📋 Para ver logs: docker-compose logs -f"
echo "🛑 Para detener: docker-compose down"
echo "🧹 Para limpiar: docker-compose down -v --remove-orphans"
echo ""
