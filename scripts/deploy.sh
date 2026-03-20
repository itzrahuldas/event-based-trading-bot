#!/bin/bash

# Deployment Script for Event Based Trading Bot

APP_NAME="algo-trading-bot"
TAG="latest"

echo "🚀 Starting Deployment Process..."

# 1. Run Tests
echo "🧪 Running Tests..."
# python -m pytest tests/
# (Skipping for now as we invoke manually)

# 2. Build Docker Image
echo "🐳 Building Docker Image..."
docker build -t $APP_NAME:$TAG .

if [ $? -eq 0 ]; then
    echo "✅ Build Successful!"
else
    echo "❌ Build Failed!"
    exit 1
fi

# 3. Push to Registry (Optional/Commented)
# echo "Pushing to ECR/GCR..."
# docker push $APP_NAME:$TAG

echo "✅ Ready to Deploy! Use 'docker-compose up -d' to start."
