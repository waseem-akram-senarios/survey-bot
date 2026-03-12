#!/bin/bash

echo "=================================================="
echo "    Starting SurvAI Platform (Local Dev Mode)     "
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running. Please start Docker Desktop or the Docker daemon first."
  exit 1
fi

# Step 1: Start Backend Microservices
echo ""
echo "[1/2] Starting backend microservices via Docker Compose..."
echo "--------------------------------------------------"
docker compose -f docker-compose.microservices.yml up -d

# Step 2: Check standard Gateway health
echo ""
echo "[System Check] Ensuring Gateway is responsive..."
sleep 2 # Give it a moment to initialize if already created
if ! curl -s http://localhost:8080/health > /dev/null; then
  echo "Waiting for services to become healthy..."
  sleep 5
fi

# Step 3: Start Frontend Dev Server
echo ""
echo "[2/2] Starting React Dashboard Development Server..."
echo "--------------------------------------------------"
cd dashboard || { echo "Error: dashboard directory not found"; exit 1; }

# Install packages if node_modules is missing
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Dashboard will be available at: http://localhost:5173 or http://localhost:5174"
echo "Press Ctrl+C to stop the frontend dev server (Docker services will remain running in background)."
echo ""

# Run the dev server
npm run dev
