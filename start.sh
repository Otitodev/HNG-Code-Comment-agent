#!/bin/bash
# Production startup script for Leapcell

echo "Starting Telex AI Agent..."
echo "Port: $PORT"
echo "Environment: Production"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --log-level info