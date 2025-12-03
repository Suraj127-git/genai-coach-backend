#!/bin/bash
# Quick test runner script for Railway API testing

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   GenAI Coach Backend - API Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if in correct directory
if [ ! -f "pytest.ini" ]; then
    echo -e "${RED}Error: Please run this script from the tests directory${NC}"
    exit 1
fi

# Check if dependencies are installed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    pip install -r requirements-test.txt
    echo ""
fi

# Default API URL
API_URL="${API_URL:-https://genai-coach-backend-production.up.railway.app}"

echo -e "${GREEN}API Endpoint:${NC} $API_URL"
echo ""

# Check if API is reachable
echo -e "${YELLOW}Checking API health...${NC}"
if curl -s "$API_URL/" > /dev/null; then
    echo -e "${GREEN}✓ API is reachable${NC}"
    echo ""
else
    echo -e "${RED}✗ API is not reachable${NC}"
    echo "Please check if the Railway API is running"
    exit 1
fi

# Parse command line arguments
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: ./run_tests.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --smoke        Run smoke tests only (quick)"
    echo "  --auth         Run authentication tests"
    echo "  --sessions     Run session tests"
    echo "  --upload       Run upload tests"
    echo "  --ai           Run AI chat tests"
    echo "  --all          Run all tests (default)"
    echo "  -v             Verbose output"
    echo "  -h, --help     Show this help message"
    echo ""
    exit 0
fi

# Run tests based on arguments
case "$1" in
    --smoke)
        echo -e "${BLUE}Running smoke tests...${NC}"
        pytest -m smoke -v
        ;;
    --auth)
        echo -e "${BLUE}Running authentication tests...${NC}"
        pytest -m auth -v
        ;;
    --sessions)
        echo -e "${BLUE}Running session tests...${NC}"
        pytest -m sessions -v
        ;;
    --upload)
        echo -e "${BLUE}Running upload tests...${NC}"
        pytest -m upload -v
        ;;
    --ai)
        echo -e "${BLUE}Running AI chat tests...${NC}"
        pytest -m ai -v
        ;;
    -v|--verbose)
        echo -e "${BLUE}Running all tests (verbose)...${NC}"
        pytest -vv
        ;;
    --all|"")
        echo -e "${BLUE}Running all tests...${NC}"
        pytest -v
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

EXIT_CODE=$?

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

exit $EXIT_CODE
