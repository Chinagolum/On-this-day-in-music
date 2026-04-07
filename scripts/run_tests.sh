#!/bin/bash
# Run the test suite
# Usage: ./scripts/run_tests.sh [test_file]
# Examples:
#   ./scripts/run_tests.sh                        — run all tests
#   ./scripts/run_tests.sh test_create_tweet       — run one test file
#   ./scripts/run_tests.sh test_db_manager -v      — verbose output
set -e

if [ -z "$1" ]; then
  echo "🧪 Running all tests..."
  pytest tests/ -v
else
  echo "🧪 Running tests/$1.py..."
  pytest tests/$1.py "${@:2}"
fi
