#!/bin/bash
# One-command setup and test script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     GenAI Coach Backend - API Test Suite Setup              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
echo -e "${YELLOW}[1/5] Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $python_version${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}[2/5] Installing test dependencies...${NC}"
if [ -f "requirements-test.txt" ]; then
    pip install -q -r requirements-test.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements-test.txt not found${NC}"
    exit 1
fi
echo ""

# Check API health
API_URL="${API_URL:-https://genai-coach-backend-production.up.railway.app}"
echo -e "${YELLOW}[3/5] Checking API health...${NC}"
echo -e "    Endpoint: ${API_URL}"

if response=$(curl -s -w "\n%{http_code}" "$API_URL/" 2>&1); then
    http_code=$(echo "$response" | tail -n 1)
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ API is healthy and reachable${NC}"
    else
        echo -e "${RED}✗ API returned status code: $http_code${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Failed to reach API${NC}"
    exit 1
fi
echo ""

# Verify test files
echo -e "${YELLOW}[4/5] Verifying test files...${NC}"
test_files=(
    "test_health.py"
    "test_auth.py"
    "test_sessions.py"
    "test_upload.py"
    "test_ai.py"
    "conftest.py"
    "pytest.ini"
)

for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file not found"
        exit 1
    fi
done
echo ""

# Run smoke tests
echo -e "${YELLOW}[5/5] Running smoke tests...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
pytest -m smoke -v --tb=short

EXIT_CODE=$?
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Summary
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${BLUE}║${NC}                    ${GREEN}✅ SETUP SUCCESSFUL${NC}                        ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Your test suite is ready to use!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run all tests:       ./run_tests.sh"
    echo "  2. Run auth tests:      ./run_tests.sh --auth"
    echo "  3. Run session tests:   ./run_tests.sh --sessions"
    echo "  4. See documentation:   cat README.md"
    echo ""
    echo "You can now start frontend development with confidence!"
else
    echo -e "${BLUE}║${NC}                    ${RED}❌ TESTS FAILED${NC}                           ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Some tests failed. This might be due to:${NC}"
    echo "  - API issues on Railway"
    echo "  - Network connectivity problems"
    echo "  - Database migration needed"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check Railway logs: railway logs"
    echo "  2. Verify API: curl $API_URL/"
    echo "  3. Run verbose: pytest -vv -m smoke"
fi

exit $EXIT_CODE
