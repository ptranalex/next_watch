***REMOVED***!/bin/bash

***REMOVED*** BFF Development Environment Setup Script

set -e

echo "🚀 Setting up BFF development environment..."

***REMOVED*** Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

***REMOVED*** Install dependencies
echo "📦 Installing dependencies..."
poetry install

***REMOVED*** Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp env.example .env
    echo "✏️  Please edit .env file with your configuration"
fi

***REMOVED*** Check if Redis is running (optional)
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running. Start it with: redis-server"
    fi
else
    echo "⚠️  Redis CLI not found. Install Redis for caching support"
fi

echo ""
echo "🎉 BFF development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your configuration"
echo "  2. Start the backend-api service (if not running)"
echo "  3. Start Redis (if not running): redis-server"
echo "  4. Run the BFF service:"
echo "     poetry run bff serve --reload --verbose"
echo ""
echo "Available commands:"
echo "  poetry run bff serve          ***REMOVED*** Start the server"
echo "  poetry run bff config         ***REMOVED*** Show configuration"
echo "  poetry run bff health-check   ***REMOVED*** Check service health"
echo "  poetry run pytest             ***REMOVED*** Run tests"
echo "" 