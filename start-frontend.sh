#!/bin/bash

echo "⚛️  Starting RazorFlow AI Frontend"
echo "================================="

# Change to frontend directory
cd frontend || exit

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not installed. Run ./setup-local.sh first"
    exit 1
fi

# Start the development server
echo "🚀 Starting Vite development server..."
echo "🌐 Frontend will be available at http://localhost:5173"
echo "🔄 Press Ctrl+C to stop"
echo ""

npm run dev
