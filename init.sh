#!/bin/bash
# VibeFlow Studio Initialization Script

echo "🚀 Setting up VibeFlow Studio development environment..."

# Backend Setup
echo "📦 Setting up Python backend..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
else
    pip install fastapi uvicorn google-genai sqlmodel syllapy
fi

# Frontend Setup
echo "📦 Setting up Next.js frontend..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        npm install
    else
        echo "Creating Next.js app..."
        npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --use-npm --no-git
        npm install lucide-react
    fi
    cd ..
fi

echo "✅ Environment ready!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "💡 To start the app, run: ./start.sh"
