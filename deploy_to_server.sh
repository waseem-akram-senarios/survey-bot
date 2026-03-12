#!/bin/bash

# Deployment Script for Survey Bot
# Run this script on the live server (54.86.65.150)

echo "🚀 Starting Survey Bot Deployment..."

# Check if we're in the right directory
if [ ! -d "survey-bot" ]; then
    echo "❌ Error: survey-bot directory not found"
    echo "Please run this script from the parent directory of survey-bot"
    exit 1
fi

cd survey-bot

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull latest code"
    exit 1
fi

# Navigate to platform directory
cd survai-platform

# Stop existing services
echo "🛑 Stopping existing services..."
docker compose -f docker-compose.microservices.yml down

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker compose -f docker-compose.microservices.yml pull

# Build and start services
echo "🔨 Building and starting services..."
docker compose -f docker-compose.microservices.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check health
echo "🔍 Checking service health..."
docker compose -f docker-compose.microservices.yml ps

# Test API endpoints
echo "🧪 Testing API endpoints..."

# Test health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8080/pg/api/health)
if [[ $HEALTH_RESPONSE == *"OK"* ]]; then
    echo "✅ Health endpoint working"
else
    echo "⚠️  Health endpoint not responding yet"
fi

# Test translation API
echo "Testing translation API..."
TRANSLATION_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"text":"test","language":"es"}' http://localhost:8080/pg/api/brain/translate)
if [[ $TRANSLATION_RESPONSE == *"prueba"* ]]; then
    echo "✅ Translation API working"
else
    echo "⚠️  Translation API not responding"
fi

# Test surveys API
echo "Testing surveys API..."
SURVEYS_RESPONSE=$(curl -s http://localhost:8080/pg/api/surveys/list)
if [[ $SURVEYS_RESPONSE == *"["* ]]; then
    echo "✅ Surveys API working"
else
    echo "⚠️  Surveys API not responding"
fi

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📊 Service Status:"
docker compose -f docker-compose.microservices.yml ps
echo ""
echo "🌐 Access URLs:"
echo "  Dashboard: http://54.86.65.150:8080"
echo "  Recipient: http://54.86.65.150:3000"
echo "  API Gateway: http://54.86.65.150:8081"
echo ""
echo "🔧 To check logs: docker compose -f docker-compose.microservices.yml logs -f [service-name]"
echo "🛑 To stop: docker compose -f docker-compose.microservices.yml down"
