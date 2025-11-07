# MCP Integration - Quick Start 

## What is This?

The Xantus RAG system now has **MCP (Model Context Protocol)** support, which means an LLM can use external tools like calculators, file operations, and text processing while answering questions about your documents.

## Quick Setup

```bash
# 1. Clone with submodules (for new users)
git clone --recurse-submodules https://github.com/onamfc/rag-chat

# OR if you already cloned without submodules:
git submodule update --init --recursive

# 2. Run the MCP setup script
./setup_mcp.sh

# 3. Start Xantus
./start_api.sh
```

## What Tools Are Available?

Your TypeScript MCP server provides:

1. **Calculator** (`calculate`)
   - Perform mathematical operations
   - Example: "Calculate the sum of revenues in section 2.1"

2. **File System** (`filesystem`)
   - Read/write/list files
   - Example: "Compare this with last year's report in ../reports/2023/"

3. **Text Processing** (`text-processing`)
   - Word counting, sentiment analysis, case conversion
   - Example: "Analyze the sentiment of this customer review"

4. **Weather** (`weather`)
   - Get weather data (mock implementation - extend with real API)
   - Example: "What's the weather forecast for next week?"

## Architecture

```
┌──────────────────────────────────────────┐
│  User uploads PDF and asks question      │
└─────────────────┬────────────────────────┘
                  ↓
        ┌─────────────────┐
        │   Xantus API    │
        │    (Python)     │
        └────────┬────────┘
                 ↓
      ┌──────────────────────┐
      │   RAG Context        │
      │ + MCP Tools          │
      └────────┬─────────────┘
               ↓
    ┌───────────────────────┐
    │   Claude Sonnet 4 or  │
    │  local ollama install │
    └────────┬──────────────┘
             ↓
     Uses MCP Tools via stdio
             ↓
 ┌─────────────────────────────────────────┐
 │         TypeScript MCP Server           │
 │github.com/onamfc/mcp-starter-template-ts│
 └─────────────────────────────────────────┘
```

## Configuration

MCP is controlled in `config.yaml`:

```yaml
mcp:
  enabled: true  # Set to false to disable MCP
  servers:
    - name: "mcp-starter-template"
      command: "node"
      args: ["mcp-servers/mcp-starter-template-ts/dist/start.js"]
```

## Example Use Cases

### 1. Financial Document Analysis
```
Upload: quarterly_report.pdf containing "Q1: $500K, Q2: $750K, Costs: $300K per quarter"
Ask: "What's our H1 profit margin?"

LLM will:
1. Extract numbers from document via RAG
2. Use calculator tool: (500000 + 750000) - (300000 * 2) = 950000
3. Use calculator tool: 950000 / 1250000 * 100 = 76%
4. Answer: "Your H1 profit margin is 76%"
```

### 2. Cross-Document Comparison
```
Upload: current_report.pdf
Ask: "How does this compare to last year's report in ../reports/2023/annual.pdf?"

LLM will:
1. Read current document via RAG
2. Use filesystem tool to read ../reports/2023/annual.pdf
3. Compare both documents
4. Provide detailed comparison
```

### 3. Text Analysis
```
Upload: customer_feedback.txt
Ask: "Analyze sentiment and count positive keywords"

LLM will:
1. Retrieve feedback via RAG
2. Use text-processing tool for sentiment analysis
3. Use text-processing tool for word counting
4. Return comprehensive analysis
```

## Extending the MCP Server

Your MCP server is a git submodule in `mcp-servers/mcp-starter-template-ts/`. To add custom tools:

```bash
cd mcp-servers/mcp-starter-template-ts
# Make changes to src/tools/
npm run build
cd ../..
# Restart Xantus to use new tools
```

## Adding More MCP Servers

You can connect multiple MCP servers:

```yaml
mcp:
  enabled: true
  servers:
    # Your custom tools
    - name: "my-tools"
      command: "node"
      args: ["mcp-servers/mcp-starter-template-ts/dist/start.js"]

    # Database access
    - name: "postgres"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]

    # Web search
    - name: "brave-search"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-brave-search"]
```

## Troubleshooting

### MCP server not starting?

```bash
# Test the server standalone
node mcp-servers/mcp-starter-template-ts/dist/start.js

# If it fails, rebuild:
cd mcp-servers/mcp-starter-template-ts
npm install
npm run build
```

### Tools not available?

Check Xantus logs for:
```
Loaded X tools from 'mcp-starter-template': [tool1, tool2, ...]
```

If not present, ensure `mcp.enabled: true` in config.yaml

### Tool calls failing?

Check that Node.js is installed and in your PATH:
```bash
node --version  # Should be v18 or higher
```

## Resources

- **MCP Server Repo**: https://github.com/onamfc/mcp-starter-template-ts
- **MCP Specification**: https://modelcontextprotocol.io/
- **Community MCP Servers**: https://github.com/modelcontextprotocol/servers

## Benefits of This Architecture

✅ **Language Agnostic**: Python (Xantus) + TypeScript (MCP Server) work seamlessly\
✅ **Modular**: Add/remove tools without changing Xantus code\
✅ **Reusable**: Share MCP server across projects\
✅ **Extensible**: Easy to add new tools\
✅ **Community**: Use pre-built MCP servers from the ecosystem\
