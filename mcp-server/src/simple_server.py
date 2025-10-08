"""Alternative server implementation using FastMCP's built-in server.

This provides a simpler way to run the MCP server.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for absolute imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config import get_config
from utils import get_logger, setup_logging
from server import create_server

logger = get_logger(__name__)


async def run_fastmcp_server():
    """Run the server using FastMCP's built-in server capabilities."""
    try:
        # Load configuration and setup logging
        config = get_config()
        setup_logging(config.logging)
        
        logger.info("Starting MCP Crypto Server with FastMCP built-in server")
        
        # Create server instance
        mcp_server = create_server()
        app = mcp_server.get_app()
        
        # Try to run using FastMCP's built-in capabilities
        if hasattr(app, 'serve'):
            await app.serve(host=config.server.host, port=config.server.port)
        elif hasattr(app, 'run'):
            await app.run(host=config.server.host, port=config.server.port)
        else:
            # Fallback to FastAPI approach
            from fastapi import FastAPI
            import uvicorn
            
            # Create a new FastAPI app and mount the MCP app
            fastapi_app = FastAPI(title="MCP Crypto Server")
            
            # Try to get the underlying FastAPI app or create a wrapper
            if hasattr(app, 'app'):
                fastapi_app = app.app
            elif hasattr(app, '_app'):
                fastapi_app = app._app
            else:
                # Create basic FastAPI endpoints for testing
                @fastapi_app.get("/")
                async def root():
                    return {
                        "message": "MCP Crypto Server is running", 
                        "status": "ok",
                        "tools": ["encrypt", "decrypt", "add", "subtract", "multiply", "divide", "modulo"],
                        "server_type": "simple_server"
                    }
                
                @fastapi_app.get("/health")
                async def health():
                    return {"status": "healthy", "server": "MCP Crypto Server"}
            
            # Run with uvicorn
            config_uvicorn = uvicorn.Config(
                app=fastapi_app,
                host=config.server.host,
                port=config.server.port,
                log_level="info"
            )
            server = uvicorn.Server(config_uvicorn)
            await server.serve()
            
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


def main():
    """Main entry point for alternative server."""
    try:
        asyncio.run(run_fastmcp_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()