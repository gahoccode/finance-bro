#!/bin/bash
# Complete build and deploy pipeline for Finance-Bro
# Builds locally, pushes to ghcr.io, and triggers Render deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 Finance-Bro Complete Build & Deploy Pipeline${NC}"
echo "=============================================="

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Error: Please run from project root directory${NC}"
    exit 1
fi

# Step 1: Build and push Docker image
echo -e "${BLUE}📦 Step 1: Building and pushing Docker image...${NC}"
./scripts/build-and-push.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build and push failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker image build and push completed${NC}"
echo ""

# Step 2: Deploy to Render
echo -e "${BLUE}🚀 Step 2: Deploying to Render...${NC}"

# Check if Render environment variables are set
if [ -z "$RENDER_SERVICE_ID" ] || [ -z "$RENDER_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  Render environment variables not set${NC}"
    echo "To enable automatic deployment, set:"
    echo "  export RENDER_SERVICE_ID=srv-your-service-id"
    echo "  export RENDER_API_KEY=your-api-key"
    echo ""
    echo -e "${BLUE}📋 Manual deployment options:${NC}"
    echo "1. Run: ./scripts/deploy-to-render.sh (after setting env vars)"
    echo "2. Or push will auto-deploy if Render is configured for auto-deploy"
    echo "3. Or manually deploy from Render dashboard"
    exit 0
fi

./scripts/deploy-to-render.sh

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Complete deployment pipeline successful!${NC}"
    echo -e "${BLUE}🌐 Your app should be available at:${NC}"
    echo "https://finance-bro.onrender.com"
else
    echo -e "${RED}❌ Render deployment failed${NC}"
    echo "Check your Render dashboard for details"
    exit 1
fi