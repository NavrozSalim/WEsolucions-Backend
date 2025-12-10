#!/bin/bash

# Deployment script for Contabo VPS
# This script helps deploy the application to your Contabo VPS

set -e

echo "🚀 Starting deployment to Contabo VPS..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found. Creating default .env...${NC}"
    cat > .env << 'EOF'
PORT=3000
NODE_ENV=production
DATABASE_URL=postgresql://postgres:NSP0122%40150@db.hihygeuawvzzrundvzev.supabase.co:5432/postgres
SUPABASE_DB_HOST=db.hihygeuawvzzrundvzev.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=NSP0122@150
SUPABASE_DB_SSL=true
SUPABASE_DB_POOL_MIN=2
SUPABASE_DB_POOL_MAX=10
EOF
    echo -e "${GREEN}✅ Default .env created. Please review and update if needed.${NC}"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please run setup-vps.sh first${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please run setup-vps.sh first${NC}"
    exit 1
fi

# Build Docker image
echo -e "${BLUE}📦 Building Docker image...${NC}"
docker build -t wesolucions-backend:latest . || {
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
}

# Stop existing container if running
echo -e "${BLUE}🛑 Stopping existing container...${NC}"
docker-compose down 2>/dev/null || true

# Start new container
echo -e "${BLUE}▶️  Starting new container...${NC}"
docker-compose up -d || {
    echo -e "${RED}❌ Failed to start containers${NC}"
    exit 1
}

# Wait for health check
echo -e "${BLUE}⏳ Waiting for application to start...${NC}"
sleep 15

# Check if container is running
if docker ps | grep -q wesolucions-backend; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    echo "📊 Container status:"
    docker-compose ps
    echo ""
    echo "🌐 Application URLs:"
    echo "   http://localhost:3000"
    echo "   http://localhost:3000/health"
    echo ""
    echo "📝 View logs with: docker-compose logs -f"
    echo "📝 Restart with: docker-compose restart"
    echo "📝 Stop with: docker-compose down"
else
    echo -e "${YELLOW}⚠️  Container may not be running. Check logs with: docker-compose logs${NC}"
    exit 1
fi

