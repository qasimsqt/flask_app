#!/bin/bash

# Local development script for Mini Shop
set -e

echo "🏠 Starting Mini Shop locally..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Set environment variables
export FLASK_ENV=development
export SECRET_KEY=dev-secret-key
export PORT=5000
export AI_MONITOR_PORT=9000

echo "🚀 Starting all services..."
echo "📱 Flask App will be available at: http://localhost:5000"
echo "📊 AI Monitor will be available at: http://localhost:9000"
echo "🛑 Press Ctrl+C to stop all services"

# Start the application
python run_all.py
