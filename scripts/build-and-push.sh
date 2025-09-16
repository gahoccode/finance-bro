#!/bin/bash
# Local Docker build and push script for Finance-Bro
# Builds image locally and pushes to GitHub Container Registry (ghcr.io)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="ghcr.io/gahoccode"
IMAGE_NAME="finance-bro"

echo -e "${BLUE}🏗️  Finance-Bro Docker Build & Push Script${NC}"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Error: pyproject.toml not found. Please run from project root.${NC}"
    exit 1
fi

# Get version from pyproject.toml
if command -v python3 &> /dev/null; then
    VERSION=$(python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
    print(data['project']['version'])
")
else
    echo -e "${RED}❌ Error: Python 3 not found. Required for version extraction.${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Version detected: ${VERSION}${NC}"

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ Error: GITHUB_TOKEN environment variable required${NC}"
    echo "Create a Personal Access Token with 'write:packages' scope at:"
    echo "https://github.com/settings/personal-access-tokens/new"
    echo "Then export it: export GITHUB_TOKEN=ghp_your_token_here"
    exit 1
fi

# Build Docker image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
DOCKER_BUILDKIT=1 docker build \
    --tag "${REGISTRY}/${IMAGE_NAME}:${VERSION}" \
    --tag "${REGISTRY}/${IMAGE_NAME}:latest" \
    --cache-from "${REGISTRY}/${IMAGE_NAME}:latest" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build completed successfully${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

# Authenticate with GitHub Container Registry
echo -e "${BLUE}🔐 Authenticating with GitHub Container Registry...${NC}"
echo $GITHUB_TOKEN | docker login ghcr.io -u $(git config user.name) --password-stdin

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi

# Push images
echo -e "${BLUE}🚀 Pushing images to registry...${NC}"
docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
docker push "${REGISTRY}/${IMAGE_NAME}:latest"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Push completed successfully!${NC}"
    echo ""
    echo "📍 Images available at:"
    echo "   • ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    echo "   • ${REGISTRY}/${IMAGE_NAME}:latest"
    echo ""
    echo "🎯 Next steps:"
    echo "   1. Deploy to Render: ./scripts/deploy-to-render.sh"
    echo "   2. Or trigger auto-deploy if configured"
else
    echo -e "${RED}❌ Push failed${NC}"
    exit 1
fi

# Show image size
echo -e "${YELLOW}📊 Image information:${NC}"
docker images "${REGISTRY}/${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"