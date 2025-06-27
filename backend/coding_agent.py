"""Sequential Coding Workflow using Google's ADK SDK.

This module implements a sequential workflow with three agents:
1. CodeWriterAgent - Generates initial code based on specifications
2. CodeReviewerAgent - Reviews the generated code and provides feedback  
3. CodeRefactorerAgent - Refactors code based on review comments

Based on Google's ADK Sequential Agents pattern:
https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/

How to run:
    Option 1 (Direct execution): python backend/coding_agent.py
    Option 2 (As module): python -m backend.coding_agent
    Both methods are supported and will work correctly.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path for direct execution
if __name__ == "__main__" and not __package__:
    # Get the project root (parent of backend directory)
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Try absolute imports first (for module execution), then relative imports (for direct execution)
try:
    from backend.data_model.data_models import WorkflowInput, WorkflowStatus
    from backend.core.config.config_loader import ConfigLoader
except ImportError:
    # If absolute imports fail, try relative imports for direct execution
    from data_model.data_models import WorkflowInput, WorkflowStatus
    from core.config.config_loader import ConfigLoader

# Google ADK imports
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('coding_workflow.log')
    ]
)
logger = logging.getLogger(__name__)


class CodingWorkflowManager:
    """Manages the sequential coding workflow with three agents."""
    
    def __init__(self):
        """Initialize the coding workflow manager."""
        self.base_dir = Path(__file__).parent
        
        # Load configuration files following the same pattern as other agents
        self.config_loader = ConfigLoader(self.base_dir / "config" / "coding" / "workflow_coding.yml")
        self.gemini_config_loader = ConfigLoader(self.base_dir / "config" / "coding" / "gemini_config_coding.yml")
        self.prompts_loader = ConfigLoader(self.base_dir / "prompts" / "coding" / "prompts_coding.yml")
        
        # Load configurations
        self.config = self.config_loader.load_config()
        self.gemini_config = self.gemini_config_loader.load_config()
        self.prompts_config = self.prompts_loader.load_config()
        
        # Set up API key
        self._load_api_key()
        
        # Initialize workflow components
        self.sequential_agent = None
        self.runner = None
        self.session = None
        
    def _load_api_key(self) -> None:
        """Load the API key from gemini config file."""
        try:
            api_key = self.gemini_config_loader.get_value("api_config.api_key")
            if api_key:
                os.environ['GOOGLE_API_KEY'] = api_key
                logger.info("✅ Google API key loaded successfully")
            else:
                logger.warning("⚠️ No API key found in gemini config")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load API key: {e}")
    
    def _get_prompt(self, prompt_key: str) -> str:
        """Get prompt from prompts configuration file."""
        try:
            prompt = self.prompts_loader.get_value(f"prompts.{prompt_key}")
            if not prompt:
                raise ValueError(f"Prompt '{prompt_key}' not found in prompts configuration")
            return prompt
        except Exception as e:
            logger.error(f"Failed to load prompt '{prompt_key}': {e}")
            raise
    
    def _get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get agent-specific configuration from workflow config."""
        try:
            # Look for agent configuration in the steps section
            steps = self.config_loader.get_value("steps", [])
            for step in steps:
                if step.get("name") == agent_name:
                    return step
            
            # Fallback to core config with defaults
            return {
                "model": self.config_loader.get_value("core_config.model", "gemini-1.5-flash"),
                "parameters": {
                    "temperature": self.config_loader.get_value("core_config.temperature", 0.0),
                    "max_tokens": self.config_loader.get_value("core_config.max_tokens", 4096)
                }
            }
        except Exception as e:
            logger.warning(f"Failed to load config for {agent_name}, using defaults: {e}")
            return {
                "model": "gemini-1.5-flash",
                "parameters": {"temperature": 0.0, "max_tokens": 4096}
            }
    
    def _create_code_writer_agent(self) -> LlmAgent:
        """Create the Code Writer Agent using configuration."""
        agent_config = self._get_agent_config("CodeWriterAgent")
        model = agent_config.get("model", self.config_loader.get_value("core_config.model", "gemini-1.5-flash"))
        
        # Get prompt from configuration
        instruction = self._get_prompt("code_writer")
        
        # Get output key from config or use default
        output_key = agent_config.get("output_key", "generated_code")
        
        logger.info(f"Creating CodeWriterAgent with model: {model}")
        
        return LlmAgent(
            name="CodeWriterAgent",
            model=model,
            instruction=instruction,
            description=agent_config.get("description", "Writes initial Python code based on a specification."),
            output_key=output_key
        )
    
    def _create_code_reviewer_agent(self) -> LlmAgent:
        """Create the Code Reviewer Agent using configuration."""
        agent_config = self._get_agent_config("CodeReviewerAgent")
        model = agent_config.get("model", self.config_loader.get_value("core_config.model", "gemini-1.5-flash"))
        
        # Get prompt from configuration
        instruction = self._get_prompt("code_reviewer")
        
        # Get output key from config or use default
        output_key = agent_config.get("output_key", "review_comments")
        
        logger.info(f"Creating CodeReviewerAgent with model: {model}")
        
        return LlmAgent(
            name="CodeReviewerAgent",
            model=model,
            instruction=instruction,
            description=agent_config.get("description", "Reviews code and provides feedback."),
            output_key=output_key
        )
    
    def _create_code_refactorer_agent(self) -> LlmAgent:
        """Create the Code Refactorer Agent using configuration."""
        agent_config = self._get_agent_config("CodeRefactorerAgent")
        model = agent_config.get("model", self.config_loader.get_value("core_config.model", "gemini-1.5-flash"))
        
        # Get prompt from configuration
        instruction = self._get_prompt("code_refactorer")
        
        # Get output key from config or use default
        output_key = agent_config.get("output_key", "refactored_code")
        
        logger.info(f"Creating CodeRefactorerAgent with model: {model}")
        
        return LlmAgent(
            name="CodeRefactorerAgent",
            model=model,
            instruction=instruction,
            description=agent_config.get("description", "Refactors code based on review comments."),
            output_key=output_key
        )
    
    async def initialize(self) -> None:
        """Initialize the sequential workflow."""
        logger.info("🔧 Initializing Sequential Coding Workflow")
        
        # Create the three agents using configuration
        code_writer = self._create_code_writer_agent()
        code_reviewer = self._create_code_reviewer_agent()
        code_refactorer = self._create_code_refactorer_agent()
        
        # Create the Sequential Agent using configuration
        workflow_name = self.config_loader.get_value("agent_config.name", "CodingPipelineAgent")
        workflow_description = self.config_loader.get_value("agent_config.description", 
                                                           self.config_loader.get_value("description", "Executes a sequence of code writing, reviewing, and refactoring."))
        
        self.sequential_agent = SequentialAgent(
            name=workflow_name,
            sub_agents=[code_writer, code_reviewer, code_refactorer],
            description=workflow_description
        )
        
        # Create runner and session using configuration
        app_name = self.config_loader.get_value("app_config.app_name", "coding_workflow")
        self.runner = InMemoryRunner(
            agent=self.sequential_agent,
            app_name=app_name
        )
        
        # Create session using configuration
        user_id = self.config_loader.get_value("app_config.user_id", "coding_user")
        session_id = self.config_loader.get_value("app_config.session_id", "coding_session")
        
        self.session = await self.runner.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        logger.info("✅ Sequential Coding Workflow initialized successfully")
    
    async def run_workflow(self, user_request: str) -> Dict[str, Any]:
        """Run the sequential coding workflow."""
        start_time = datetime.now()
        logger.info(f"🚀 Starting coding workflow for request: {user_request}")
        
        try:
            # Initialize if not already done
            if not self.sequential_agent:
                await self.initialize()
            
            # Create user message
            content = types.Content(role='user', parts=[types.Part(text=user_request)])
            
            # Execute the sequential workflow
            response_text = ""
            final_state = {}
            
            async for event in self.runner.run_async(
                user_id=self.session.user_id,
                session_id=self.session.id,
                new_message=content
            ):
                # Extract final response
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
                
                # Extract state information if available
                if hasattr(event, 'state') and event.state:
                    final_state.update(event.state)
            
            # Get the final state from the session
            if not final_state and self.session:
                final_state = getattr(self.session, 'state', {})
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": WorkflowStatus.COMPLETED,
                "content": response_text or "Workflow completed successfully",
                "metadata": {
                    "success": bool(response_text),
                    "execution_time": execution_time,
                    "timestamp": start_time.isoformat(),
                    "original_request": user_request,
                    "workflow_type": "sequential_coding",
                    "workflow_name": self.config_loader.get_value("name", "Coding Assistant Workflow"),
                    "workflow_version": self.config_loader.get_value("version", "1.0.0"),
                    "agents_executed": ["CodeWriterAgent", "CodeReviewerAgent", "CodeRefactorerAgent"],
                    "model_used": self.config_loader.get_value("core_config.model", "gemini-1.5-flash")
                },
                "state": final_state
            }
            
            # Save results
            await self._save_results(result)
            
            logger.info(f"✅ Coding workflow completed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Coding workflow failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                "status": WorkflowStatus.FAILED,
                "content": error_msg,
                "metadata": {
                    "success": False,
                    "execution_time": execution_time,
                    "timestamp": start_time.isoformat(),
                    "error": str(e),
                    "workflow_type": "sequential_coding",
                    "workflow_name": self.config_loader.get_value("name", "Coding Assistant Workflow"),
                    "workflow_version": self.config_loader.get_value("version", "1.0.0")
                }
            }
    
    async def _save_results(self, result: Dict[str, Any]) -> None:
        """Save workflow results to output directory using configuration."""
        try:
            # Use output directory from configuration
            output_dir = Path(self.config_loader.get_value("app_config.output_dir", "backend/output"))
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save main result
            result_file = output_dir / f"coding_workflow_result_{timestamp}.json"
            import json
            
            # Handle WorkflowStatus enum serialization
            result_copy = result.copy()
            if 'status' in result_copy:
                result_copy['status'] = str(result_copy['status'])
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_copy, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Results saved to: {result_file}")
            
            # Extract and save individual agent outputs if available
            state = result.get("state", {})
            if state:
                # Save generated code
                if "generated_code" in state:
                    code_file = output_dir / f"generated_code_{timestamp}.py"
                    with open(code_file, 'w', encoding='utf-8') as f:
                        f.write(state["generated_code"])
                    logger.info(f"📝 Generated code saved to: {code_file}")
                
                # Save review comments
                if "review_comments" in state:
                    review_file = output_dir / f"review_comments_{timestamp}.md"
                    with open(review_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Code Review Comments\n\n{state['review_comments']}")
                    logger.info(f"📋 Review comments saved to: {review_file}")
                
                # Save refactored code
                if "refactored_code" in state:
                    refactored_file = output_dir / f"refactored_code_{timestamp}.py"
                    with open(refactored_file, 'w', encoding='utf-8') as f:
                        f.write(state["refactored_code"])
                    logger.info(f"🔄 Refactored code saved to: {refactored_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save results: {e}")

    def print_configuration_summary(self) -> None:
        """Print a summary of the loaded configuration for debugging."""
        logger.info("📋 Configuration Summary:")
        logger.info(f"   Workflow Name: {self.config_loader.get_value('name', 'N/A')}")
        logger.info(f"   Workflow Version: {self.config_loader.get_value('version', 'N/A')}")
        logger.info(f"   Model: {self.config_loader.get_value('core_config.model', 'N/A')}")
        logger.info(f"   Temperature: {self.config_loader.get_value('core_config.temperature', 'N/A')}")
        logger.info(f"   Max Tokens: {self.config_loader.get_value('core_config.max_tokens', 'N/A')}")
        logger.info(f"   App Name: {self.config_loader.get_value('app_config.app_name', 'N/A')}")
        logger.info(f"   Output Dir: {self.config_loader.get_value('app_config.output_dir', 'N/A')}")
        logger.info(f"   API Provider: {self.gemini_config_loader.get_value('api_config.provider', 'N/A')}")
        logger.info(f"   API Key Present: {'Yes' if self.gemini_config_loader.get_value('api_config.api_key') else 'No'}")
        logger.info(f"   Timeout: {self.gemini_config_loader.get_value('performance_config.timeout_seconds', 'N/A')}")


async def main() -> None:
    """Main entry point for the sequential coding workflow."""
    logger.info("🎯 Starting Sequential Coding Workflow System")
    
    try:
        # Create workflow manager
        workflow_manager = CodingWorkflowManager()
        
        # Print configuration summary for debugging
        workflow_manager.print_configuration_summary()
        
        # Get example coding request from configuration or use default
        user_request = "Write a Python function for binary tree traversal"
        
        # Run the workflow
        result = await workflow_manager.run_workflow(user_request)
        
        # Display results
        print("\n" + "="*80)
        print("🎉 CODING WORKFLOW RESULTS")
        print("="*80)
        print(f"Status: {result['status']}")
        print(f"Success: {result['metadata']['success']}")
        print(f"Execution Time: {result['metadata']['execution_time']:.2f}s")
        print(f"Workflow: {result['metadata'].get('workflow_name', 'N/A')} v{result['metadata'].get('workflow_version', 'N/A')}")
        print(f"Model: {result['metadata'].get('model_used', 'N/A')}")
        print(f"Agents Executed: {result['metadata'].get('agents_executed', [])}")
        
        if result['metadata']['success']:
            print(f"\n📝 Final Response:")
            print(result['content'])
            
            # Show individual agent outputs if available
            state = result.get('state', {})
            if 'generated_code' in state:
                print(f"\n🤖 Generated Code:")
                print(state['generated_code'])
            
            if 'review_comments' in state:
                print(f"\n📋 Review Comments:")
                print(state['review_comments'])
            
            if 'refactored_code' in state:
                print(f"\n🔄 Refactored Code:")
                print(state['refactored_code'])
        else:
            print(f"\n❌ Error: {result['metadata'].get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)
        return {
            "status": WorkflowStatus.FAILED,
            "metadata": {"error": str(e), "success": False}
        }


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result["metadata"]["success"]:
            print("\n✅ Sequential Coding Workflow completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Sequential Coding Workflow failed: {result['metadata'].get('error')}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Workflow interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1) 