#!/bin/bash

set -e  # Exit on error

echo "=== Learnora Backend Setup & Run Script ==="
echo ""

# Navigate to the core-service directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CORE_SERVICE_DIR="$PROJECT_ROOT/core-service"

cd "$CORE_SERVICE_DIR" || exit 1

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the environment to make uv available
    export PATH="$HOME/.local/bin:$PATH"
    
    # Verify installation
    if ! command -v uv &> /dev/null; then
        echo "ERROR: UV installation failed. Please install manually."
        exit 1
    fi
    echo "✓ UV installed successfully"
    echo ""
else
    echo "✓ UV is already installed"
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    if [ -f ".env.samlpe" ]; then
        echo "Creating .env from .env.samlpe template..."
        cp .env.samlpe .env
        echo "⚠ Please edit .env file with your configuration before running the server"
        exit 1
    else
        echo "ERROR: No .env or .env.samlpe file found"
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies..."
uv sync
echo "✓ Dependencies installed"
echo ""

# Run the FastAPI development server
echo "Starting FastAPI server on 0.0.0.0:8000..."
echo "Access the server at: http://<your-ip>:8000"
echo "API Documentation at: http://<your-ip>:8000/docs"
echo ""
uv run fastapi dev app/main.py --host 0.0.0.0
