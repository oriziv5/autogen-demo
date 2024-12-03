#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Install NPM modules for Contoso Web UI
echo "Running main.py"

python3 main.py
# npm install
# npx next telemetry disable
# popd