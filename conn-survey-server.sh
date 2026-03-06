#!/bin/bash

# Survey Bot Service Verification Script
# This script checks the health of all microservices and provides E2E test shortcuts.

GATEWAY_URL="http://localhost:8080"
E2E_DIR="./survai-platform/e2e-tests"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "   Survey Bot: Service Health Check   "
echo "=========================================="

# 1. Check Docker Containers
echo -e "\n[1/3] Checking Docker Containers..."
CONTAINERS=("gateway" "brain-service" "voice-service" "survey-service" "question-service" "template-service" "analytics-service" "scheduler-service" "dashboard" "recipient" "postgres" "smtp" "livekit-agent")
ALL_UP=true

for container in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
        echo -e "  ✓ $container is ${GREEN}RUNNING${NC}"
    else
        echo -e "  ✗ $container is ${RED}DOWN${NC}"
        ALL_UP=false
    fi
done

# 2. Check API Health Endpoints via Gateway
echo -e "\n[2/3] Checking API Health Endpoints..."
SERVICES=("brain" "voice" "surveys" "questions" "templates" "analytics" "scheduler")

for service in "${SERVICES[@]}"; do
    ENDPOINT="$GATEWAY_URL/pg/api/$service/health"
    RESPONSE=$(curl -s "$ENDPOINT")
    if [[ $RESPONSE == *"status"*"OK"* ]]; then
        echo -e "  ✓ $service service: ${GREEN}HEALTHY${NC}"
    else
        echo -e "  ✗ $service service: ${RED}UNHEALTHY${NC} (or gateway unreachable)"
    fi
done

# 3. Playwright E2E Tests
echo -e "\n[3/3] Playwright E2E Test Shortcuts"
echo "To run E2E tests, use the following commands:"
echo "  - All tests:       cd $E2E_DIR && npm test"
echo "  - API Health:      cd $E2E_DIR && npm run test:api"
echo "  - Dashboard UI:    cd $E2E_DIR && npm run test:dashboard"

echo -e "\nSummary:"
if [ "$ALL_UP" = true ]; then
    echo -e "${GREEN}All systems operational.${NC}"
else
    echo -e "${RED}Some services are DOWN. Check 'docker ps' or 'docker logs'.${NC}"
fi
echo "=========================================="
