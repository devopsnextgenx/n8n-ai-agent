"""Development server script."""

import uvicorn
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from n8n_mcp_server.cli import create_dev_app
from n8n_mcp_server.config import get_settings


def main():
    """Run development server."""
    settings = get_settings()
    
    print("🚀 Starting N8N MCP Server Development Mode")
    print(f"📍 Server will run on http://{settings.host}:{settings.port + 1000}")
    print("🔄 Auto-reload enabled - changes will restart the server")
    print("📊 Visit /tools to see available MCP tools")
    print("🏥 Visit /health for health check")
    print()
    
    try:
        uvicorn.run(
            "n8n_mcp_server.cli:create_dev_app",
            factory=True,
            host=settings.host,
            port=settings.port + 1000,
            reload=settings.auto_reload,
            log_level=settings.log_level.lower(),
        )
    except KeyboardInterrupt:
        print("\n👋 Development server stopped by user")
    except Exception as e:
        print(f"❌ Development server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()