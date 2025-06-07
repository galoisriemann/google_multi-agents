"""Main entry point for the RAG workflow system using Google ADK MCPToolset."""

import logging
import sys
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

from data_model.data_models import WorkflowStatus
from workflow_manager_rag import WorkflowPaths, ConfigLoader, RAGWorkflowManager

# Configure logging with more detailed format
class AsyncCleanupFilter(logging.Filter):
    """Filter to suppress non-critical async cleanup warnings."""
    
    def filter(self, record):
        # Suppress specific async cleanup errors that don't affect functionality
        message = record.getMessage().lower()
        
        # Don't suppress if it's an actual error we care about
        if record.levelno >= logging.ERROR:
            # But suppress asyncio cleanup errors
            if any(term in message for term in [
                'async_generator', 'generatorexit', 'runtime', 'athrow',
                'cancel scope', 'task group', 'sse_client', 'aconnect_sse'
            ]):
                return False
        
        return True

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('workflow.log')
    ]
)

# Add the filter to suppress async cleanup warnings
asyncio_logger = logging.getLogger('asyncio')
asyncio_logger.addFilter(AsyncCleanupFilter())

logger = logging.getLogger(__name__)


def create_input_data() -> Dict[str, Any]:
    """Create input data for the RAG workflow."""
    logger.debug("Creating input data")
    return {
        "query": "What are the IRS regulations for Self-directed IRAs? Has it changed in the last 10 years?",
        "system_prompt": "You are an expert research assistant. Only answer using retrieved context. Cite sources if possible.",
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "source": "main_rag.py",
        }
    }


def parse_arguments():
    """Parse command line arguments for RAG workflow configuration."""
    parser = argparse.ArgumentParser(
        description="RAG Workflow System using Google ADK MCPToolset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_rag.py
  python main_rag.py --allowed-tools get_generative_search_response search_documents
  python main_rag.py --query "What are the latest AI developments?"
        """
    )
    
    parser.add_argument(
        '--allowed-tools',
        nargs='+',
        help='List of allowed MCP tools for security filtering'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='Custom query to process (overrides default query)'
    )
    
    parser.add_argument(
        '--system-prompt',
        type=str,
        help='Custom system prompt (overrides default)'
    )

    return parser.parse_args()


async def main() -> None:
    """Main entry point for the RAG workflow system."""
    logger.info("Starting RAG workflow system with Google ADK MCPToolset")
    
    # Parse command line arguments
    args = parse_arguments()
    
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

        # Create and validate input data
        logger.debug("Creating input data")
        input_data = create_input_data()
        
        # Override with command line arguments if provided
        if args.query:
            input_data["query"] = args.query
            logger.info(f"Using custom query: {args.query}")
            
        if args.system_prompt:
            input_data["system_prompt"] = args.system_prompt
            logger.info(f"Using custom system prompt: {args.system_prompt}")
            
        logger.debug(f"Input data created: {input_data}")

        # Use RAG workflow manager as async context manager for proper cleanup
        logger.info("Creating RAG workflow manager with MCPToolset")
        async with RAGWorkflowManager(
            config_loader=config_loader,
            allowed_tools=args.allowed_tools
        ) as workflow_manager:
            logger.debug("RAG workflow manager created successfully")

            # Process input through RAG workflow (asynchronous)
            logger.info("Processing input through RAG workflow")
            result = await workflow_manager.run(input_data)
            
            # Log the result
            logger.info("RAG workflow completed")
            logger.debug(f"RAG workflow result: {result}")
            
            # Print the answer/output (or handle as needed)
            if result.get('status') == WorkflowStatus.FAILED:
                logger.error(f"Workflow failed: {result.get('error')}")
                print(f"ERROR: {result.get('error')}")
                sys.exit(1)
            else:
                print("\n" + "="*50)
                print("FINAL RESPONSE")
                print("="*50)
                print(f"Query: {result['output']['query']}")
                print(f"Method Used: {result['output']['method']}")
                print("-"*50)
                print(result["output"]["response"])
                print("="*50 + "\n")

        # Context manager will handle cleanup automatically
        logger.info("RAG workflow system completed successfully")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("RAG workflow system shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Workflow interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)