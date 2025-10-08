Build a mcp server with FastMCP with http transport, 

mcp server has two tools with crypting capability encrypt and descript string base64, 
@server.tool(name="encrypt", description="Encrypt string to base64")
@server.tool(name="decrypt", description="Descrypt base64 string")

MCP server also has resources,
@server.resource("resource://mcp/version", name="status", description="Current MCP server version", mime_type="application/json")
@server.resource("resource://mcp/status", name="status", description="Current MCP server status", mime_type="application/json")
@server.resource("resource://mcp/tools/list", name="status", description="List MCP server tools", mime_type="application/json")

Use below packages
"mcp-server",
"requests",
"fastapi",
"uvicorn[standard]",
"pydantic"

Use uv for project packaging and managing dependencies

create python code under src with proper folder structure to allow modular structure.
Enable configuration to be loaded from yaml for MCP port/host (default port for server 6789), logging configuration. enable logs to be written to console as well as file under logs folder with name mcp-server.log

make sure src folder has below structure to store tools/resources/prompts
├── src/
│   ├── mcp_store/
│       └── tools/
│       ├── resources/
│       └── prompts/
│   ├── main.py
│   ├── config.py
│   ├── server.py
│   └── utils.py

