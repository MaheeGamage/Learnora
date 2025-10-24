#!/bin/bash

set -e  # Exit on error

echo "=== Learnora Frontend Setup & Run Script ==="
echo ""

# Navigate to the learner-web-app directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/learner-web-app"

cd "$FRONTEND_DIR" || exit 1

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Installing Node.js 22..."
    
    # Install Node.js 22.x using NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    # Verify installation
    if ! command -v node &> /dev/null; then
        echo "ERROR: Node.js installation failed. Please install manually."
        exit 1
    fi
    
    NODE_VERSION=$(node -v)
    NPM_VERSION=$(npm -v)
    echo "✓ Node.js $NODE_VERSION installed successfully"
    echo "✓ npm $NPM_VERSION installed successfully"
    echo ""
else
    NODE_VERSION=$(node -v)
    NPM_VERSION=$(npm -v)
    echo "✓ Node.js $NODE_VERSION is already installed"
    echo "✓ npm $NPM_VERSION is already installed"
    echo ""
fi

# Check if .env file exists (if needed)
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    echo "Creating .env from .env.example template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo "✓ Dependencies installed"
    echo ""
else
    echo "✓ node_modules found"
    echo "Checking for updates..."
    npm install
    echo "✓ Dependencies up to date"
    echo ""
fi

# Build for production
echo "Building production bundle..."
npm run build
echo "✓ Production build completed"
echo ""

# Run the production preview server
echo "Starting production server..."
echo "Access the application at: http://localhost:4173/"
echo "To expose on network, press Ctrl+C and run: npm run preview -- --host"
echo ""
npm run preview -- --host 0.0.0.0

