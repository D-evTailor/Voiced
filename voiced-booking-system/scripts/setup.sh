#!/bin/bash

# VoiceAppoint Initial Setup Script
# This script sets up the development environment

set -e

echo "🚀 VoiceAppoint Initial Setup"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✓"
}

# Check if .env file exists
setup_env() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before proceeding"
    else
        print_status ".env file already exists ✓"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p nginx/ssl
    mkdir -p backups
    mkdir -p logs
    print_status "Directories created ✓"
}

# Generate SSL certificates for development
generate_ssl() {
    if [ ! -f nginx/ssl/cert.crt ] || [ ! -f nginx/ssl/cert.key ]; then
        print_status "Generating self-signed SSL certificates for development..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/cert.key \
            -out nginx/ssl/cert.crt \
            -subj "/C=ES/ST=Madrid/L=Madrid/O=VoiceAppoint/CN=localhost" 2>/dev/null
        print_status "SSL certificates generated ✓"
    else
        print_status "SSL certificates already exist ✓"
    fi
}

# Start Docker services
start_services() {
    print_status "Starting Docker services..."
    docker-compose up -d db redis
    
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Check if database is ready
    until docker-compose exec -T db pg_isready -U postgres; do
        print_status "Waiting for database..."
        sleep 2
    done
    
    print_status "Database is ready ✓"
}

# Run database migrations
run_migrations() {
    print_status "Building backend container..."
    docker-compose build backend
    
    print_status "Running database migrations..."
    docker-compose run --rm backend poetry run python manage.py migrate
    
    print_status "Database migrations completed ✓"
}

# Create superuser
create_superuser() {
    read -p "Do you want to create a Django superuser? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Creating Django superuser..."
        docker-compose run --rm backend poetry run python manage.py createsuperuser
    fi
}

# Start all services
start_all_services() {
    print_status "Starting all services..."
    docker-compose up -d
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    print_status "Checking service health..."
    docker-compose ps
}

# Display final information
show_info() {
    echo
    echo "🎉 VoiceAppoint setup completed successfully!"
    echo "=========================================="
    echo
    echo "Access your application:"
    echo "📱 Frontend:    http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "👤 Admin:       http://localhost:8000/admin"
    echo "📖 API Docs:    http://localhost:8000/api/docs"
    echo "🐘 PgAdmin:     http://localhost:8080 (admin@voiceappoint.com / admin)"
    echo "🔴 Redis UI:    http://localhost:8081"
    echo
    echo "Useful commands:"
    echo "make logs          - View all logs"
    echo "make logs-backend  - View backend logs"
    echo "make logs-frontend - View frontend logs"
    echo "make test          - Run all tests"
    echo "make help          - Show all available commands"
    echo
    echo "🚀 Happy coding!"
}

# Main execution
main() {
    print_status "Starting VoiceAppoint setup..."
    
    check_docker
    setup_env
    create_directories
    generate_ssl
    start_services
    run_migrations
    create_superuser
    start_all_services
    show_info
}

# Run main function
main "$@"
