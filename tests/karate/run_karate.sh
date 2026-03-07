#!/bin/bash

# Ensure we are in the backend root directory
cd "$(dirname "$0")/../.."

echo "Current directory: $(pwd)"

# 1. Download Karate JAR if not exists
KARATE_VERSION="1.4.1"
KARATE_JAR="tests/karate/karate.jar"

if [ ! -f "$KARATE_JAR" ]; then
    echo "Downloading karate.jar v${KARATE_VERSION}..."
    curl -L -o "$KARATE_JAR" "https://github.com/karatelabs/karate/releases/download/v${KARATE_VERSION}/karate-${KARATE_VERSION}.jar"
fi

# 2. Start the mocked API in the background
echo "Starting mock API for tests..."
# IMPORTANT: use the correct python path (venv)
export PYTHONPATH="."
./venv/bin/python tests/karate/run_karate_api.py &
API_PID=$!

# Wait for the server to be ready
echo "Waiting for API to start on port 8081..."
sleep 3

# 3. Run Karate Tests
echo "Running Karate Tests..."
java -Dkarate.config.dir=tests/karate -jar "$KARATE_JAR" tests/karate/features

TEST_RESULT=$?

# 4. Stop the API
echo "Stopping Mock API (PID: $API_PID)..."
kill $API_PID

if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ Karate Tests Passed!"
else
    echo "❌ Karate Tests Failed!"
fi

exit $TEST_RESULT
