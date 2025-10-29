#!/bin/bash

# Event Sales Application Deployment Script
# For AWS Lightsail with Cloudflare Integration

echo "Starting Event Sales Application Deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop any running containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.cloudflare.yml down

# Build and start the application (builds custom image from Dockerfile)
echo "Building custom image and starting the application..."
docker-compose -f docker-compose.cloudflare.yml up -d --build

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check if containers are running
echo "Checking container status..."
docker-compose -f docker-compose.cloudflare.yml ps

# Check application health
echo "Checking application health..."
if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access your application at: https://thehoweranchpayment.com"
else
    echo "❌ Application health check failed. Please check logs:"
    echo "docker-compose -f docker-compose.cloudflare.yml logs"
fi

echo "Deployment completed!"