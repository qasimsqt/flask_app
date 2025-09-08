#!/bin/bash

# Build script for Mini Shop Flask Application
set -e

echo "🏗️  Building Mini Shop Docker Image..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Build Docker image
docker build -t mini-shop:latest .

echo "✅ Docker image built successfully!"
echo "📦 Image: mini-shop:latest"

# Optional: Tag with version
if [ ! -z "$1" ]; then
    docker tag mini-shop:latest mini-shop:$1
    echo "🏷️  Tagged as: mini-shop:$1"
fi

echo "🚀 Ready for deployment!"
