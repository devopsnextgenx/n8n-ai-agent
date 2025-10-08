"""Main entry point for MCP Crypto Server.

This module initializes the configuration, sets up logging, and starts the MCP server.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path for proper imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config import get_config, config_manager
from utils import setup_logging, get_logger
from server import create_server


def main() -> None:
    """Main entry point for the application."""
    try:
        # Parse command line arguments
        mode = "auto"  # default mode
        if "--mode" in sys.argv:
            mode_index = sys.argv.index("--mode")
            if mode_index + 1 < len(sys.argv):
                mode = sys.argv[mode_index + 1]
        
        # Load configuration
        print("Loading configuration...")
        config = config_manager.load_config()
        print(f"Configuration loaded from: {config_manager.config_path}")
        
        # Setup logging
        print("Setting up logging...")
        logger = setup_logging(config.logging)
        logger.info("=" * 60)
        logger.info("MCP Crypto Server Starting Up")
        logger.info("=" * 60)
        logger.info(f"Server will bind to: {config.server.host}:{config.server.port}")
        logger.info(f"Server mode: {mode}")
        logger.info(f"Log level: {config.logging.level}")
        logger.info(f"Log file: {config.logging.file}")
        
        # Create and start server
        logger.info("Creating MCP server instance...")
        server = create_server()
        
        logger.info(f"Starting MCP server in {mode} mode...")
        server.run_server(mode)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        logger = get_logger()
        logger.info("Server shutdown requested by user")
    except FileNotFoundError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}")
        logger = get_logger()
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


def dev_main() -> None:
    """Development entry point with additional debug information."""
    print("MCP Crypto Server - Development Mode")
    print("=" * 50)
    
    # Print environment information
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
    
    # Show available modes
    print("Available server modes:")
    print("  --mode auto      : Try builtin first, fallback to http (default)")
    print("  --mode builtin   : Use FastMCP built-in server")
    print("  --mode http      : Use http_app() with uvicorn")
    print("  --mode streamable: Use streamable_http_app() with uvicorn (for n8n)")
    print("=" * 50)
    
    main()


if __name__ == "__main__":
    # Check if running in development mode
    if "--dev" in sys.argv:
        dev_main()
    else:
        main()