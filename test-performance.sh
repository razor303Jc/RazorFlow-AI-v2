#!/bin/bash

# Performance Test Script for RazorFlow AI

echo "🚀 Starting RazorFlow AI Performance Tests"
echo "========================================"

API_BASE="http://localhost:8000"
FRONTEND_URL="http://localhost:5173"

# Test 1: API Health Check
echo ""
echo "📊 Test 1: API Health Check"
echo "----------------------------"
start_time=$(date +%s%N)
response=$(curl -s -w "%{http_code}" "$API_BASE/health")
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))

if [[ "$response" == *"200" ]]; then
    echo "✅ API Health: PASS (${response_time}ms)"
else
    echo "❌ API Health: FAIL"
    exit 1
fi

# Test 2: API Response Times
echo ""
echo "📊 Test 2: API Endpoint Performance"
echo "-----------------------------------"

endpoints=("finance" "sales" "scheduler")
for endpoint in "${endpoints[@]}"; do
    start_time=$(date +%s%N)
    response=$(curl -s -w "%{http_code}" "$API_BASE/api/$endpoint")
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [[ "$response" == *"200" ]]; then
        echo "✅ $endpoint API: PASS (${response_time}ms)"
    else
        echo "❌ $endpoint API: FAIL"
    fi
done

# Test 3: Frontend Availability
echo ""
echo "📊 Test 3: Frontend Availability"
echo "--------------------------------"
start_time=$(date +%s%N)
response=$(curl -s -w "%{http_code}" "$FRONTEND_URL")
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))

if [[ "$response" == *"200" ]]; then
    echo "✅ Frontend: PASS (${response_time}ms)"
else
    echo "❌ Frontend: FAIL"
fi

# Test 4: Load Testing (10 concurrent requests)
echo ""
echo "📊 Test 4: Load Testing (10 concurrent requests)"
echo "-----------------------------------------------"

load_test() {
    endpoint=$1
    start_time=$(date +%s%N)
    curl -s "$API_BASE/api/$endpoint" > /dev/null
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 ))
    echo "$response_time"
}

# Run 10 concurrent requests to finance endpoint
echo "Testing finance endpoint with 10 concurrent requests..."
for i in {1..10}; do
    load_test "finance" &
done
wait

echo ""
echo "📊 Test 5: Chat API Testing"
echo "---------------------------"

# Test chat endpoints
for endpoint in "${endpoints[@]}"; do
    start_time=$(date +%s%N)
    response=$(curl -s -X POST -H "Content-Type: application/json" \
        -d '{"message":"Test message"}' \
        -w "%{http_code}" \
        "$API_BASE/api/chat/$endpoint")
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [[ "$response" == *"200" ]]; then
        echo "✅ $endpoint Chat: PASS (${response_time}ms)"
    else
        echo "❌ $endpoint Chat: FAIL"
    fi
done

echo ""
echo "🎉 Performance Tests Complete!"
echo "==============================="
echo ""
echo "Summary:"
echo "- API Health: Tested"
echo "- Endpoint Performance: Tested"
echo "- Frontend Availability: Tested"
echo "- Load Testing: Completed"
echo "- Chat API: Tested"
echo ""
echo "✨ RazorFlow AI is ready for production testing!"
