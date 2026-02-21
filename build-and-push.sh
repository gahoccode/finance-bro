#!/bin/bash
# Build and push Docker image to GitHub Container Registry (GHCR)
# Usage: ./build-and-push.sh [version] [--no-cache]
#   version  - optional version tag (defaults to "latest")
#   --no-cache - optional flag to disable build cache

set -e

# Configuration
IMAGE_NAME="ghcr.io/gahoccode/finance-bro"
PLATFORM="linux/amd64"
VERSION="${1:-latest}"
NO_CACHE=""

# Parse arguments
for arg in "$@"; do
    if [ "$arg" == "--no-cache" ]; then
        NO_CACHE="--no-cache"
    fi
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Build and Push to GHCR${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if docker buildx is available
if ! docker buildx version &> /dev/null; then
    echo -e "${RED}Error: docker buildx not available. Please install Docker Buildx.${NC}"
    exit 1
fi

# Check if user is logged in to GHCR
echo -e "${YELLOW}Checking GHCR authentication...${NC}"
if ! docker login ghcr.io &> /dev/null; then
    echo -e "${YELLOW}Not logged in to GHCR. Please login:${NC}"
    echo "  docker login ghcr.io"
    echo "  Username: your GitHub username"
    echo "  Password: your GitHub Personal Access Token (with write:packages scope)"
    exit 1
fi
echo -e "${GREEN}Authenticated to GHCR${NC}"
echo ""

# Build for linux/amd64 platform
CACHE_MSG="${NO_CACHE:+(no-cache)} "
echo -e "${YELLOW}Building image for ${PLATFORM}${CACHE_MSG}...${NC}"
docker buildx build \
    --platform "${PLATFORM}" \
    ${NO_CACHE} \
    --load \
    -t "${IMAGE_NAME}:${VERSION}" \
    --progress=plain \
    .

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}Build completed successfully${NC}"
echo ""

# Show image size
IMAGE_SIZE=$(docker images "${IMAGE_NAME}:${VERSION}" --format "{{.Size}}")
echo -e "${GREEN}Image size: ${IMAGE_SIZE}${NC}"
echo ""

# Tag as latest if version is not "latest"
if [ "$VERSION" != "latest" ]; then
    echo -e "${YELLOW}Tagging as 'latest'...${NC}"
    docker tag "${IMAGE_NAME}:${VERSION}" "${IMAGE_NAME}:latest"
fi

# Push to GHCR
echo -e "${YELLOW}Pushing to GHCR...${NC}"
docker push "${IMAGE_NAME}:${VERSION}"

if [ $? -ne 0 ]; then
    echo -e "${RED}Push failed!${NC}"
    exit 1
fi

# Also push latest tag if version was specified
if [ "$VERSION" != "latest" ]; then
    echo -e "${YELLOW}Pushing 'latest' tag...${NC}"
    docker push "${IMAGE_NAME}:latest"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Successfully pushed: ${IMAGE_NAME}:${VERSION}${NC}"
echo -e "${GREEN}========================================${NC}"
