#!/bin/bash
#
# Deployment script for Kush Image Analyzer API
# Usage: ./scripts/deploy.sh [dev|staging|prod]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default environment
ENV=${1:-dev}

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Kush Image Analyzer - Serverless Deployment${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Validate environment
if [[ ! "$ENV" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}❌ Error: Invalid environment '$ENV'${NC}"
    echo -e "Usage: $0 [dev|staging|prod]"
    exit 1
fi

echo -e "${YELLOW}📦 Environment: ${ENV}${NC}"
echo ""

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo -e "${RED}❌ Error: Serverless Framework not found${NC}"
    echo -e "Install it with: npm install -g serverless"
    exit 1
fi

# Check if required environment variables are set for production
if [ "$ENV" = "prod" ]; then
    echo -e "${YELLOW}⚠️  Production deployment - checking prerequisites...${NC}"

    required_vars=("AWS_REGION" "JWT_SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}❌ Error: ${var} environment variable not set${NC}"
            exit 1
        fi
    done

    echo -e "${GREEN}✓ All required variables are set${NC}"

    # Confirm production deployment
    echo ""
    echo -e "${YELLOW}⚠️  WARNING: You are about to deploy to PRODUCTION${NC}"
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Deployment cancelled${NC}"
        exit 0
    fi
fi

echo ""
echo -e "${YELLOW}🧪 Running tests...${NC}"
if ! poetry run pytest tests/ -v --tb=short; then
    echo -e "${RED}❌ Tests failed. Fix them before deploying.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ All tests passed${NC}"

echo ""
echo -e "${YELLOW}🔍 Running linter...${NC}"
if ! poetry run ruff check .; then
    echo -e "${YELLOW}⚠️  Linting warnings found (non-blocking)${NC}"
else
    echo -e "${GREEN}✓ Code quality checks passed${NC}"
fi

echo ""
echo -e "${YELLOW}🚀 Deploying to ${ENV}...${NC}"

# Export environment variable
export ENV=$ENV

# Deploy with serverless
serverless deploy --stage "$ENV" --verbose

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deployment to ${ENV} completed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Show deployment info
echo ""
echo -e "${YELLOW}📊 Deployment Information:${NC}"
serverless info --stage "$ENV"

echo ""
echo -e "${YELLOW}💡 Useful commands:${NC}"
echo "  - View logs: npm run logs:auth (or logs:analyze)"
echo "  - Test endpoint: curl https://<api-url>/api/v1/health"
echo "  - Remove stack: serverless remove --stage $ENV"