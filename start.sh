#!/bin/bash

# Function to kill child processes on exit
cleanup() {
    echo "🛑 Shutting down VibeFlow Studio..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

echo "🚀 Starting VibeFlow Studio..."

# Check for .env
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating one..."
    if [ -z "$GEMINI_API_KEY" ]; then
        echo "❌ GEMINI_API_KEY environment variable not set."
        read -p "🔑 Enter your Gemini API Key: " api_key
        echo "GEMINI_API_KEY=$api_key" > .env
    else
        echo "GEMINI_API_KEY=$GEMINI_API_KEY" > .env
    fi
fi

# Start Backend
echo "📦 Starting Backend (Port 8000)..."
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "✨ Starting Frontend (Port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ VibeFlow Studio is running!"
echo "👉 Open http://localhost:3000 in your browser"
echo "Press Ctrl+C to stop."

wait
