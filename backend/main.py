"""Main entry point for the workflow system using Google ADK SDK.

This module implements a sequential workflow system using Google's Agent Development Kit (ADK).
It provides a flexible framework for executing multi-step workflows with LLM-powered agents.
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any

from data_model.data_models import WorkflowInput, WorkflowStatus
from workflow_manager import WorkflowPaths, ConfigLoader, WorkflowManager

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('workflow.log')
    ]
)
logger = logging.getLogger(__name__)


def create_input_data() -> Dict[str, Any]:
    """Create input data for the workflow.
    
    Returns:
        Dict containing the input data with prompt and metadata.
    """
    logger.debug("Creating input data")
    return {
        "prompt": "write me a python code to print hello world",
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "source": "main.py",
        }
    }


async def main() -> None:
    """Main entry point for the workflow system."""
    logger.info("Starting workflow system")
    
    try:
        # Initialize workflow paths and ensure directories exist
        logger.debug("Initializing workflow paths")
        paths = WorkflowPaths()
        paths.ensure_directories()
        logger.debug(f"Workflow paths initialized: {paths}")

        # Create config loader
        logger.debug("Creating config loader")
        config_loader = ConfigLoader(paths)
        logger.debug("Config loader created successfully")

        # Create workflow manager
        logger.debug("Creating workflow manager")
        workflow_manager = WorkflowManager(config_loader)
        logger.debug("Workflow manager created successfully")

        # Create and validate input data
        logger.debug("Creating input data")
        input_data = create_input_data()
        logger.debug(f"Input data created: {input_data}")

        # Process input through workflow
        logger.info("Processing input through workflow")
        result = await workflow_manager.process_input(input_data)
        
        # Log the result
        logger.info("Workflow completed")
        logger.debug(f"Workflow result: {result}")
        
        # Check for errors in the result
        if result.get('status') == WorkflowStatus.FAILED:
            logger.error(f"Workflow failed: {result.get('metadata', {}).get('error')}")
            raise Exception(f"Workflow failed: {result.get('metadata', {}).get('error')}")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Workflow system shutdown complete")


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Workflow interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1) 