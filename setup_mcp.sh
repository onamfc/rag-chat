#!/bin/bash
# Setup script for MCP integration

set -e  # Exit on error

echo "🚀 Setting up MCP Integration for Xantus..."
echo

# Check if git submodule is initialized
if [ ! -f "mcp-servers/mcp-starter-template-ts/package.json" ]; then
    echo "📦 Initializing MCP server submodule..."
    git submodule update --init --recursive
else
    echo "✅ MCP server submodule already initialized"
fi

# Navigate to MCP server directory
cd mcp-servers/mcp-starter-template-ts

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📥 Installing MCP server dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Build the MCP server
echo "🔨 Building MCP server..."
npm run build

# Return to xantus directory
cd ../..

echo
echo "✨ MCP setup complete!"
echo
echo "The MCP server provides the following tools:"
echo "  • Calculator - Perform mathematical calculations"
echo "  • File System - Read/write files"
echo "  • Text Processing - Word counting, sentiment analysis"
echo "  • Weather - Get weather information"
echo
echo "To enable MCP, set 'mcp.enabled: true' in config.yaml"
echo "(It's already enabled by default!)"
echo
echo "Next steps:"
echo "  1. ./start_api.sh  # Start the Xantus server"
echo "  2. Check logs for: 'Loaded 4 tools from mcp-starter-template'"
echo "  3. Ask Claude to use the tools!"
echo
