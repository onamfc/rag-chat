"""MCP (Model Context Protocol) Service for integrating external tools."""

import asyncio
import json
import subprocess
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPServer:
    """Manages a single MCP server process and communication."""

    def __init__(self, name: str, command: str, args: List[str] = None):
        """
        Initialize an MCP server.

        Args:
            name: Human-readable name for the server
            command: Command to start the server (e.g., 'node', 'npx')
            args: Arguments to pass to the command
        """
        self.name = name
        self.command = command
        self.args = args or []
        self.process: Optional[subprocess.Popen] = None
        self.tools: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []

    async def start(self) -> bool:
        """Start the MCP server process."""
        try:
            cmd = [self.command] + self.args
            logger.info(f"Starting MCP server '{self.name}': {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Initialize the connection
            await self._send_request({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "clientInfo": {
                        "name": "xantus",
                        "version": "0.1.0"
                    }
                }
            })

            # Get available tools
            await self._list_tools()

            logger.info(f"MCP server '{self.name}' started successfully with {len(self.tools)} tools")
            return True

        except Exception as e:
            logger.error(f"Failed to start MCP server '{self.name}': {e}")
            return False

    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
        if not self.process or not self.process.stdin:
            raise RuntimeError(f"MCP server '{self.name}' is not running")

        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError(f"No response from MCP server '{self.name}'")

        return json.loads(response_line)

    async def _list_tools(self):
        """Get the list of available tools from the server."""
        try:
            response = await self._send_request({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            })

            if "result" in response and "tools" in response["result"]:
                self.tools = response["result"]["tools"]
                logger.info(f"Loaded {len(self.tools)} tools from '{self.name}': {[t['name'] for t in self.tools]}")

        except Exception as e:
            logger.error(f"Failed to list tools from '{self.name}': {e}")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool execution result
        """
        try:
            response = await self._send_request({
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            })

            if "result" in response:
                return response["result"]
            elif "error" in response:
                raise RuntimeError(f"Tool error: {response['error']}")

        except Exception as e:
            logger.error(f"Failed to call tool '{tool_name}' on '{self.name}': {e}")
            raise

    def get_tools_for_claude(self) -> List[Dict[str, Any]]:
        """
        Convert MCP tools to Claude-compatible tool format.

        Returns:
            List of tools in Anthropic's tool calling format
        """
        claude_tools = []
        for tool in self.tools:
            claude_tools.append({
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get("inputSchema", {
                    "type": "object",
                    "properties": {},
                    "required": []
                })
            })
        return claude_tools

    def stop(self):
        """Stop the MCP server process."""
        if self.process:
            logger.info(f"Stopping MCP server '{self.name}'")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None


class MCPService:
    """Service for managing multiple MCP servers and coordinating tool calls."""

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self._initialized = False

    async def initialize(self, mcp_servers_config: List[Dict[str, Any]]):
        """
        Initialize and start all configured MCP servers.

        Args:
            mcp_servers_config: List of server configurations
                Example: [
                    {
                        "name": "my-mcp-server",
                        "command": "node",
                        "args": ["/path/to/your/mcp-server/build/index.js"]
                    }
                ]
        """
        for config in mcp_servers_config:
            server = MCPServer(
                name=config["name"],
                command=config["command"],
                args=config.get("args", [])
            )

            if await server.start():
                self.servers[config["name"]] = server

        self._initialized = True
        logger.info(f"MCP Service initialized with {len(self.servers)} servers")

    def get_all_tools_for_claude(self) -> List[Dict[str, Any]]:
        """Get all tools from all MCP servers in Claude format."""
        all_tools = []
        for server in self.servers.values():
            all_tools.extend(server.get_tools_for_claude())
        return all_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the appropriate MCP server.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        # Find which server has this tool
        for server in self.servers.values():
            if any(t["name"] == tool_name for t in server.tools):
                return await server.call_tool(tool_name, arguments)

        raise ValueError(f"Tool '{tool_name}' not found in any MCP server")

    def shutdown(self):
        """Shutdown all MCP servers."""
        for server in self.servers.values():
            server.stop()
        self.servers.clear()
        self._initialized = False
        logger.info("MCP Service shutdown complete")
