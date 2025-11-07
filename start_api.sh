#!/bin/bash
# Start the Xantus FastAPI server

cd "$(dirname "$0")"

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    set -a
    source .env
    set +a
fi

source venv/bin/activate
python -m xantus.main
