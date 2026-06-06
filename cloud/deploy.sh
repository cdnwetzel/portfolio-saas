#!/bin/bash
set -e

echo "🚀 Starting deployment to production..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
CLOUD_USER=${CLOUD_USER:-ubuntu}
CLOUD_IP=${CLOUD_IP:-your.cloud.ip.address}
SSH_KEY=${SSH_KEY:-~/.ssh/deploy}

# 1. Build Frontend (if exists)
if [ -d "frontend" ]; then
  echo -e "${YELLOW}📦 Building React frontend...${NC}"
  cd frontend && npm run build && cd ..
fi

# 2. Sync Backend Code
echo -e "${YELLOW}📤 Syncing backend code...${NC}"
rsync -avz \
    -e "ssh -i ${SSH_KEY}" \
    src/ requirements.txt Dockerfile docker-compose.yml \
    ${CLOUD_USER}@${CLOUD_IP}:/opt/portfolio-saas/

# 3. Remote Operations
echo -e "${YELLOW}⚙️ Running remote deployment...${NC}"
ssh -i ${SSH_KEY} ${CLOUD_USER}@${CLOUD_IP} << 'REMOTE_EOF'
    set -e

    cd /opt/portfolio-saas

    # Copy environment if exists
    if [ -f .env.prod ]; then
        cp .env.prod .env
    fi

    # Build and start containers
    echo "Starting Docker containers..."
    docker-compose up -d --build

    # Wait for services
    sleep 5

    # Run migrations
    echo "Running database migrations..."
    docker-compose exec -T api alembic upgrade head || true

    # Clean up
    docker image prune -f

    echo "Deployment complete!"
REMOTE_EOF

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}Check https://app.yourdomain.com${NC}"
