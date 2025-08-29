#!/bin/bash

# ReadRecall FastAPI Service Setup Script

set -e

echo "🚀 Setting up ReadRecall FastAPI Service..."

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [[ $(echo "$python_version >= 3.9" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory structure
echo "📁 Creating upload directories..."
mkdir -p uploads/{books,covers,temp}

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your configuration:"
    echo "   - DATABASE_URL (Neon PostgreSQL connection string)"
    echo "   - OPENSEARCH_HOST (OpenSearch cluster URL)"
    echo "   - OPENSEARCH_USER and OPENSEARCH_PASSWORD"
    echo "   - GEMINI_API_KEY (Google Gemini API key)"
    echo "   - SECRET_KEY and JWT_SECRET_KEY (generate secure keys)"
    echo ""
fi

# Check if database migrations exist
if [ ! -d "alembic/versions" ]; then
    echo "🗄️  Creating initial database migration..."
    mkdir -p alembic/versions
    alembic revision --autogenerate -m "Initial migration"
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run database migrations: alembic upgrade head"
echo "3. Start the development server: python run_dev.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "To run with Docker:"
echo "docker-compose up --build"
echo ""

# Make the script executable
chmod +x setup.sh
