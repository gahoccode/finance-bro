#!/bin/bash
# Deploy Finance-Bro to Render.com
# This script triggers a deployment on Render after pushing a new image

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Finance-Bro Render Deployment Script${NC}"
echo "======================================"

# Configuration (can be overridden by environment variables)
SERVICE_ID=${RENDER_SERVICE_ID:-""}
API_KEY=${RENDER_API_KEY:-""}

# Check for required environment variables
if [ -z "$SERVICE_ID" ]; then
    echo -e "${RED}❌ Error: RENDER_SERVICE_ID environment variable required${NC}"
    echo "Get your service ID from Render dashboard URL:"
    echo "https://dashboard.render.com/web/srv-XXXXXXXXX (the srv-XXXXXXXXX part)"
    echo "Then export it: export RENDER_SERVICE_ID=srv-your-service-id"
    exit 1
fi

if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ Error: RENDER_API_KEY environment variable required${NC}"
    echo "Create an API key at: https://dashboard.render.com/account"
    echo "Then export it: export RENDER_API_KEY=your-api-key"
    exit 1
fi

# Get current version for logging
if [ -f "pyproject.toml" ] && command -v python3 &> /dev/null; then
    VERSION=$(python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
    print(data['project']['version'])
")
    echo -e "${YELLOW}📦 Deploying version: ${VERSION}${NC}"
fi

# Trigger deployment via Render API
echo -e "${BLUE}🔄 Triggering deployment on Render...${NC}"

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $API_KEY" \
    -H "Accept: application/json" \
    "https://api.render.com/v1/services/${SERVICE_ID}/deploys")

# Parse response
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✅ Deployment triggered successfully!${NC}"
    
    # Extract deploy ID if available
    DEPLOY_ID=$(echo "$RESPONSE_BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ ! -z "$DEPLOY_ID" ]; then
        echo -e "${BLUE}📋 Deploy ID: ${DEPLOY_ID}${NC}"
        echo -e "${BLUE}🌐 Monitor deployment at:${NC}"
        echo "https://dashboard.render.com/web/${SERVICE_ID}/deploys/${DEPLOY_ID}"
    fi
    
    echo ""
    echo -e "${YELLOW}⏳ Deployment in progress...${NC}"
    echo "This typically takes 2-3 minutes."
    echo ""
    echo -e "${GREEN}🎯 Your app will be available at:${NC}"
    echo "https://finance-bro.onrender.com (or your custom domain)"
    
elif [ "$HTTP_CODE" = "401" ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    echo "Please check your RENDER_API_KEY"
    exit 1
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "${RED}❌ Service not found${NC}"
    echo "Please check your RENDER_SERVICE_ID"
    exit 1
else
    echo -e "${RED}❌ Deployment failed (HTTP ${HTTP_CODE})${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi

# Optional: Wait for deployment status (requires jq)
if command -v jq &> /dev/null && [ ! -z "$DEPLOY_ID" ]; then
    echo -e "${YELLOW}⏳ Checking deployment status...${NC}"
    
    for i in {1..30}; do
        sleep 10
        STATUS_RESPONSE=$(curl -s \
            -H "Authorization: Bearer $API_KEY" \
            -H "Accept: application/json" \
            "https://api.render.com/v1/services/${SERVICE_ID}/deploys/${DEPLOY_ID}")
        
        STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status' 2>/dev/null || echo "unknown")
        
        case "$STATUS" in
            "live")
                echo -e "${GREEN}✅ Deployment successful! App is now live.${NC}"
                exit 0
                ;;
            "build_failed"|"update_failed"|"canceled")
                echo -e "${RED}❌ Deployment failed with status: $STATUS${NC}"
                exit 1
                ;;
            "in_progress"|"building"|"deploying")
                echo -e "${YELLOW}⏳ Still deploying... (attempt $i/30)${NC}"
                ;;
            *)
                echo -e "${YELLOW}⏳ Status: $STATUS (attempt $i/30)${NC}"
                ;;
        esac
    done
    
    echo -e "${YELLOW}⚠️  Deployment status check timed out${NC}"
    echo "Check manually at: https://dashboard.render.com/web/${SERVICE_ID}"
fi