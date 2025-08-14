#!/bin/bash

echo "🚀 Starting VoiceAppoint Backend Development Environment"

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies with Poetry..."
poetry install

echo "🗄️ Running database migrations..."
poetry run python manage.py migrate

echo "👤 Creating superuser..."
echo "Creating development superuser (admin@voiceappoint.dev / admin123)"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@voiceappoint.dev').exists() or User.objects.create_superuser('admin@voiceappoint.dev', 'admin123', first_name='Admin', last_name='User')" | poetry run python manage.py shell

echo "🏢 Creating sample business..."
poetry run python manage.py create_superuser_with_business --email admin@voiceappoint.dev --password admin123 --business "Demo Business" || echo "Business already exists"

echo "📊 Creating sample data..."
poetry run python manage.py create_sample_data --users 5 --businesses 2 --services 10 --appointments 20

echo "🏃 Starting development server..."
echo "Access the API at: http://localhost:8000"
echo "Admin panel: http://localhost:8000/admin"
echo "API docs: http://localhost:8000/api/docs"

poetry run python manage.py runserver
