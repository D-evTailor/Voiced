#!/bin/bash

# Quick Build Script for VoiceAppoint
# This script builds the Docker images for development

set -e

echo "🔨 Building VoiceAppoint Docker Images"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Build backend image
print_status "Building backend image..."
docker build -t voiceappoint-backend:dev --target development ./backend

# Build frontend image  
print_status "Building frontend image..."
docker build -t voiceappoint-frontend:dev --target development ./frontend

print_status "Docker images built successfully! ✅"

echo
echo "Next steps:"
echo "1. Copy environment variables: cp .env.example .env"
echo "2. Start services: docker-compose up"
echo "3. Open browser: http://localhost:3000"
echo
echo "🎉 Ready to develop!"
