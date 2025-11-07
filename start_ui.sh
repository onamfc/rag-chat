#!/bin/bash
# Start the Xantus Streamlit UI

cd "$(dirname "$0")"

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

source venv/bin/activate
streamlit run ui/streamlit_app.py
