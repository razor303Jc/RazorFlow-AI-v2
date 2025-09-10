#!/bin/bash

echo "🧪 RazorFlow AI - Manual Testing Guide"
echo "===================================="

echo ""
echo "🔗 Your local deployment is running on:"
echo "  • Backend API: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Frontend: http://localhost:5173 or http://localhost:5174"

echo ""
echo "🧪 Manual Tests to Perform:"
echo "1. Open http://localhost:8000/docs in your browser"
echo "   - You should see the FastAPI interactive documentation"
echo "   - Try the '/health' endpoint"
echo "   - Try the '/api/finance', '/api/sales', '/api/scheduler' endpoints"

echo ""
echo "2. Test API endpoints with curl:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/api/finance"
echo "   curl http://localhost:8000/api/sales" 
echo "   curl http://localhost:8000/api/scheduler"

echo ""
echo "3. Open your frontend:"
echo "   - Try http://localhost:5173"
echo "   - Try http://localhost:5174" 
echo "   - Try http://localhost:5173/RazorFlow-AI-v2/"
echo "   - Try http://localhost:5174/RazorFlow-AI-v2/"

echo ""
echo "🎭 Run Playwright Tests:"
echo "   ./run-playwright.sh"

echo ""
echo "🛑 To stop servers:"
echo "   Press Ctrl+C in the terminal windows running the servers"

echo ""
echo "📊 Server Status:"
curl -s http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Backend: Running on port 8000"
else
    echo "   ❌ Backend: Not responding on port 8000"
fi

curl -s http://localhost:5173 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Frontend: Running on port 5173"
else
    curl -s http://localhost:5174 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "   ✅ Frontend: Running on port 5174"
    else
        echo "   ❌ Frontend: Not responding on ports 5173 or 5174"
    fi
fi
