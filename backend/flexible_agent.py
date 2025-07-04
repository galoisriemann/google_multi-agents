"""Configurable Flexible Workflow using Google's ADK SDK.

This module implements a flexible workflow system that can handle any number of agents
with configurable types, models, and prompts. Supports:
- LlmAgent: Language model agents with custom instructions
- SequentialAgent: Agents that run sub-agents in sequence
- ParallelAgent: Agents that run sub-agents in parallel
- LoopAgent: Agents that repeat operations until a condition is met
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path for direct execution
if __name__ == "__main__" and not __package__:
    # Get the project root (parent of backend directory)
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Try absolute imports first (for module execution), then relative imports (for direct execution)
try:
    from backend.data_model.data_models import WorkflowStatus
    from backend.core.workflow.flexible_workflow_manager import FlexibleWorkflowManager
    from backend.core.tools.tool_registry import FlexibleToolRegistry
    from backend.core.config.flexible_config import FlexibleAgentConfig, FlexibleWorkflowConfig
    from backend.core.agents.flexible_loop_checker import FlexibleLoopChecker
    from backend.core.agents.flexible_agent_factory import FlexibleAgentFactory
except ImportError:
    # If absolute imports fail, try relative imports for direct execution
    from data_model.data_models import WorkflowStatus
    from core.workflow.flexible_workflow_manager import FlexibleWorkflowManager
    from core.tools.tool_registry import FlexibleToolRegistry
    from core.config.flexible_config import FlexibleAgentConfig, FlexibleWorkflowConfig
    from core.agents.flexible_loop_checker import FlexibleLoopChecker
    from core.agents.flexible_agent_factory import FlexibleAgentFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('flexible_workflow.log')
    ]
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the flexible workflow system."""
    logger.info("🎯 Starting Flexible Workflow System")
    
    try:
        # Create workflow manager
        workflow_manager = FlexibleWorkflowManager()
        
        # Print configuration summary for debugging
        workflow_manager.print_configuration_summary()
        
        # Get example request
        user_request = "Create a comprehensive LLM guided Gartner style market research report generating framework"
        
        # Run the workflow
        result = await workflow_manager.run_workflow(user_request)
        
        # Display results
        print("\n" + "="*80)
        print("🎉 FLEXIBLE WORKFLOW RESULTS")
        print("="*80)
        print(f"Status: {result['status']}")
        print(f"Success: {result['metadata']['success']}")
        print(f"Execution Time: {result['metadata']['execution_time']:.2f}s")
        print(f"Workflow: {result['metadata'].get('workflow_name', 'N/A')} v{result['metadata'].get('workflow_version', 'N/A')}")
        
        if result['metadata']['success']:
            print(f"\n📝 Final Response:")
            print(result['content'])
        else:
            print(f"\n❌ Error: {result['metadata'].get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Fatal error in flexible workflow main: {str(e)}", exc_info=True)
        return {
            "status": WorkflowStatus.FAILED,
            "metadata": {"error": str(e), "success": False}
        }


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result["metadata"]["success"]:
            print("\n✅ Flexible Workflow completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Flexible Workflow failed: {result['metadata'].get('error')}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Flexible workflow interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in flexible workflow: {str(e)}", exc_info=True)
        sys.exit(1) 