#!/bin/bash

echo "🔥 Starting RazorFlow AI Backend"
echo "================================"

# Load environment variables
if [ -f ".env" ]; then
    # Source the .env file instead of using export with xargs to handle complex values
    set -a  # automatically export all variables
    source .env
    set +a  # disable automatic export
else
    echo "⚠️  .env file not found. Using defaults."
    export DATABASE_URL="sqlite:///./razorflow_local.db"
    export API_PORT="8000"
fi

# Change to backend directory
cd backend || exit

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run ./setup-local.sh first"
    exit 1
fi

# Start the server
echo "🚀 Starting FastAPI server on http://localhost:${API_PORT:-8000}"
echo "📖 API docs available at http://localhost:${API_PORT:-8000}/docs"
echo "🔄 Press Ctrl+C to stop"
echo ""

uvicorn main:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload
