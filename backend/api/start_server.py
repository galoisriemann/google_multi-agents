#!/usr/bin/env python3
"""Startup script for the Flexible Agent API server.

This script starts the FastAPI server for the flexible agent workflow system.
It handles proper initialization and error handling for the API.
"""

import asyncio
import logging
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import is now handled by uvicorn using the import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to start the API server."""
    try:
        logger.info("🚀 Starting Flexible Agent API Server...")
        
        # Configuration
        host = "0.0.0.0"
        port = 8000
        
        logger.info(f"🌐 Server will be available at: http://localhost:{port}")
        logger.info(f"📖 API Documentation will be available at: http://localhost:{port}/docs")
        logger.info(f"🔍 API Health Check: http://localhost:{port}/api/v1/health")
        
        # Start the server with import string for reload to work
        uvicorn.run(
            "backend.api.main:app",  # Use import string instead of app object
            host=host,
            port=port,
            reload=True,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 