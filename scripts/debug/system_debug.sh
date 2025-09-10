#!/bin/bash

# Debug script for RazorFlow AI Backend
# Provides system and application diagnostics

echo "=== RazorFlow AI Backend Debug Information ==="
echo "Time: $(date)"
echo "Hostname: $(hostname)"
echo "User: $(whoami)"
echo ""

echo "=== System Information ==="
echo "OS: $(uname -a)"
echo "Memory:"
free -h
echo ""
echo "Disk Usage:"
df -h
echo ""
echo "Network Interfaces:"
ip addr show
echo ""

echo "=== Application Status ==="
echo "Working Directory: $(pwd)"
echo "Python Version: $(python3 --version)"
echo "Python Path: $PYTHONPATH"
echo ""

echo "=== Environment Variables ==="
env | grep -E "(RAZORFLOW|DATABASE|REDIS|CHROMA|DEBUG|LOG|PORT)" | sort
echo ""

echo "=== Log Files ==="
if [ -d "/app/logs" ]; then
    ls -la /app/logs/
    echo ""
    echo "Recent application logs:"
    tail -n 20 /app/logs/*.log 2>/dev/null || echo "No log files found"
else
    echo "Log directory not found"
fi
echo ""

echo "=== Process Information ==="
ps aux | grep -E "(python|uvicorn|razorflow)" | grep -v grep
echo ""

echo "=== Network Connections ==="
netstat -tlnp 2>/dev/null | grep ":8000" || echo "No connections on port 8000"
echo ""

echo "=== Recent System Logs ==="
dmesg | tail -n 10 2>/dev/null || echo "Cannot access system logs"
echo ""

echo "=== Debug Complete ==="
