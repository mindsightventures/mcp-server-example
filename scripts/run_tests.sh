#!/bin/bash
set -e

# Default values
COVERAGE=false
INTEGRATION=false

# Parse command line arguments
for arg in "$@"; do
  case $arg in
    --coverage)
      COVERAGE=true
      shift
      ;;
    --integration)
      INTEGRATION=true
      shift
      ;;
    *)
      # Unknown option
      ;;
  esac
done

# Prepare command
if [ "$INTEGRATION" = true ]; then
  TEST_CMD="pytest tests -v -m integration"
else
  TEST_CMD="pytest tests -v -k \"not integration\""
fi

# Add coverage if requested
if [ "$COVERAGE" = true ]; then
  TEST_CMD="$TEST_CMD --cov=src/weather --cov-report=term --cov-report=html"
fi

# Run the tests
echo "Running: $TEST_CMD"
eval "uv run $TEST_CMD"

# If coverage was generated, show where to find the report
if [ "$COVERAGE" = true ]; then
  echo ""
  echo "Coverage report generated in htmlcov/ directory"
  echo "Open htmlcov/index.html in your browser to view the detailed report"
fi
