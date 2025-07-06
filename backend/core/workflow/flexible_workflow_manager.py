"""Flexible workflow manager for orchestrating multi-agent workflows.

This module provides the main FlexibleWorkflowManager class that handles
the orchestration, execution, and monitoring of flexible agent workflows.
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import ValidationError

# Try absolute imports first (for module execution), then relative imports (for direct execution)
try:
    from backend.data_model.data_models import WorkflowStatus
    from backend.core.config.config_loader import ConfigLoader
    from backend.core.config.flexible_config import FlexibleWorkflowConfig, FlexibleAgentConfig
    from backend.core.agents.flexible_agent_factory import FlexibleAgentFactory
    from backend.core.tools.tool_registry import FlexibleToolRegistry
except ImportError:
    # If absolute imports fail, try relative imports for direct execution
    from ...data_model.data_models import WorkflowStatus
    from ..config.config_loader import ConfigLoader
    from ..config.flexible_config import FlexibleWorkflowConfig, FlexibleAgentConfig
    from ..agents.flexible_agent_factory import FlexibleAgentFactory
    from ..tools.tool_registry import FlexibleToolRegistry

logger = logging.getLogger(__name__)


class FlexibleWorkflowManager:
    """Manages flexible workflows with multiple agent types and configurations.
    
    This class provides a complete workflow management system that can handle
    different types of agents (LLM, Sequential, Parallel, Loop) with configurable
    models, prompts, and execution strategies.
    """
    
    def __init__(self, config_dir: Optional[Path] = None, uploaded_configs: Optional[Dict[str, Dict[str, Any]]] = None):
        """Initialize the flexible workflow manager.
        
        Args:
            config_dir: Directory containing configuration files
            uploaded_configs: Optional uploaded configurations to use instead of static files
        """
        self.base_dir = Path(__file__).parent.parent.parent
        self.config_dir = config_dir or (self.base_dir / "config" / "flexible_agent")
        self.uploaded_configs = uploaded_configs or {}
        
        # Load configuration files (prioritizing uploaded configs)
        self._load_configurations()
        
        # Set up API key
        self._load_api_key()
        
        # Initialize workflow components
        self.main_agent = None
        self.all_agents = {}
        self.runner = None
        self.session = None
        
        logger.info("FlexibleWorkflowManager initialized")
        
    def update_configurations(self, uploaded_configs: Dict[str, Dict[str, Any]]) -> None:
        """Update the workflow manager with new uploaded configurations.
        
        Args:
            uploaded_configs: New uploaded configurations to use
        """
        logger.info(f"🔄 Updating configurations with: {list(uploaded_configs.keys())}")
        self.uploaded_configs = uploaded_configs
        
        # Reload configurations with new uploads
        self._load_configurations()
        
        # Reload API key with new gemini config
        self._load_api_key()
        
        # Reset agents - they will be rebuilt on next workflow run
        self.main_agent = None
        self.all_agents = {}
        self.runner = None
        self.session = None
        
        logger.info("✅ Configurations updated successfully")
        
    def _load_configurations(self) -> None:
        """Load all configuration files, prioritizing uploaded configs over static files.
        
        Raises:
            Exception: If configuration loading fails
        """
        try:
            import yaml
            
            # Main workflow configuration
            if "workflow" in self.uploaded_configs and self.uploaded_configs["workflow"].get("is_valid", True):
                logger.info("🔄 Using uploaded workflow configuration")
                config_content = self.uploaded_configs["workflow"]["content"]
                self.config = yaml.safe_load(config_content)
                # Create a dummy config loader for API compatibility
                workflow_config_path = self.config_dir / "workflow_flexible.yml"
                self.config_loader = ConfigLoader(workflow_config_path)
                self.config_loader.config = self.config  # Override with uploaded config
            else:
                logger.info("📁 Using static workflow configuration file")
                workflow_config_path = self.config_dir / "workflow_flexible.yml"
                self.config_loader = ConfigLoader(workflow_config_path)
                self.config = self.config_loader.load_config()
            
            # Gemini configuration
            if "gemini" in self.uploaded_configs and self.uploaded_configs["gemini"].get("is_valid", True):
                logger.info("🔄 Using uploaded gemini configuration")
                config_content = self.uploaded_configs["gemini"]["content"]
                self.gemini_config = yaml.safe_load(config_content)
                # Create a dummy config loader for API compatibility
                gemini_config_path = self.config_dir / "gemini_config_flexible.yml"
                self.gemini_config_loader = ConfigLoader(gemini_config_path)
                self.gemini_config_loader.config = self.gemini_config  # Override with uploaded config
            else:
                logger.info("📁 Using static gemini configuration file")
                gemini_config_path = self.config_dir / "gemini_config_flexible.yml"
                self.gemini_config_loader = ConfigLoader(gemini_config_path)
                self.gemini_config = self.gemini_config_loader.load_config()
            
            # Prompts configuration
            if "prompts" in self.uploaded_configs and self.uploaded_configs["prompts"].get("is_valid", True):
                logger.info("🔄 Using uploaded prompts configuration")
                config_content = self.uploaded_configs["prompts"]["content"]
                self.prompts_config = yaml.safe_load(config_content)
                # Create a dummy config loader for API compatibility
                prompts_config_path = self.base_dir / "prompts" / "flexible_agent" / "prompts_flexible.yml"
                self.prompts_loader = ConfigLoader(prompts_config_path)
                self.prompts_loader.config = self.prompts_config  # Override with uploaded config
            else:
                logger.info("📁 Using static prompts configuration file")
                prompts_config_path = self.base_dir / "prompts" / "flexible_agent" / "prompts_flexible.yml"
                self.prompts_loader = ConfigLoader(prompts_config_path)
                self.prompts_config = self.prompts_loader.load_config()
            
            config_sources = []
            if "workflow" in self.uploaded_configs: config_sources.append("uploaded workflow")
            if "gemini" in self.uploaded_configs: config_sources.append("uploaded gemini")
            if "prompts" in self.uploaded_configs: config_sources.append("uploaded prompts")
            
            if config_sources:
                logger.info(f"✅ Configuration loaded using: {', '.join(config_sources)}")
            else:
                logger.info("✅ All static configuration files loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load flexible agent configurations: {e}")
            raise
    
    def _load_api_key(self) -> None:
        """Load the API key from gemini config file."""
        try:
            api_key = self.gemini_config_loader.get_value("api_config.api_key")
            if api_key:
                os.environ['GOOGLE_API_KEY'] = api_key
                logger.info("✅ Google API key loaded successfully for flexible agent")
            else:
                logger.warning("⚠️ No API key found in flexible agent gemini config")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load API key for flexible agent: {e}")
    
    def _parse_workflow_config(self) -> FlexibleWorkflowConfig:
        """Parse workflow configuration into FlexibleWorkflowConfig model.
        
        Returns:
            Parsed workflow configuration
            
        Raises:
            ValidationError: If configuration is invalid
            Exception: If parsing fails
        """
        try:
            # Convert steps to agents format for compatibility
            workflow_data = {
                "name": self.config_loader.get_value("name"),
                "description": self.config_loader.get_value("description"),
                "version": self.config_loader.get_value("version"),
                "main_agent": "MainFlexibleOrchestrator",
                "agents": []
            }
            
            # Get steps from config and convert to agents
            steps = self.config_loader.get_value("steps", [])
            if steps:
                # Create individual LlmAgents from steps
                agent_configs = []
                agent_names = []
                
                for step in steps:
                    agent_config = {
                        "name": step.get("name", f"FlexibleAgent_{len(agent_configs)}"),
                        "type": "LlmAgent",
                        "model": step.get("model", self.config_loader.get_value("core_config.model")),
                        "description": step.get("description", ""),
                        "prompt_key": step.get("prompt_key"),
                        "output_key": step.get("output_key"),
                        "parameters": step.get("parameters", {})
                    }
                    agent_configs.append(agent_config)
                    agent_names.append(agent_config["name"])
                
                # Create main sequential agent that orchestrates all sub-agents
                main_agent_config = {
                    "name": "MainFlexibleOrchestrator",
                    "type": "SequentialAgent",
                    "description": "Main flexible agent that orchestrates the workflow",
                    "sub_agents": agent_names
                }
                
                workflow_data["agents"] = agent_configs + [main_agent_config]
            
            # If no steps, try to load agents directly (new format)
            elif "agents" in self.config:
                workflow_data["agents"] = self.config["agents"]
                workflow_data["main_agent"] = self.config.get("main_agent")
            
            return FlexibleWorkflowConfig(**workflow_data)
            
        except ValidationError as e:
            logger.error(f"Flexible workflow configuration validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse flexible workflow configuration: {e}")
            raise

    async def initialize(self) -> None:
        """Initialize the flexible workflow.
        
        Raises:
            Exception: If initialization fails
        """
        logger.info("🔧 Initializing Flexible Workflow")
        
        try:
            # Parse workflow configuration
            workflow_config = self._parse_workflow_config()
            logger.info(f"Flexible Workflow: {workflow_config.name} v{workflow_config.version}")
            
            # Create agent factory and build all agents
            input_directory = self.base_dir / "input"
            factory = FlexibleAgentFactory(workflow_config.agents, self.prompts_loader, input_directory)
            self.all_agents = factory.build_all()
            
            # Get the main agent
            if workflow_config.main_agent not in self.all_agents:
                raise ValueError(f"Main flexible agent '{workflow_config.main_agent}' not found in agents")
            
            self.main_agent = self.all_agents[workflow_config.main_agent]
            logger.info(f"Main flexible agent: {self.main_agent.name} ({type(self.main_agent).__name__})")
            
            # Create runner and session
            app_name = self.config_loader.get_value("app_config.app_name", "flexible_workflow")
            self.runner = InMemoryRunner(
                agent=self.main_agent,
                app_name=app_name
            )
            
            # Create session
            user_id = self.config_loader.get_value("app_config.user_id", "flexible_user")
            session_id = self.config_loader.get_value("app_config.session_id", "flexible_session")
            
            self.session = await self.runner.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            logger.info(f"✅ Flexible Workflow initialized with {len(self.all_agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize flexible workflow: {e}")
            raise

    async def run_workflow(self, user_request: str, status_callback=None) -> Dict[str, Any]:
        """Run the flexible workflow.
        
        Args:
            user_request: The user's request to process
            status_callback: Optional callback function to report progress (agent_name, progress, message)
            
        Returns:
            Dictionary containing workflow results and metadata
        """
        start_time = datetime.now()
        logger.info(f"🚀 Starting flexible workflow for request: {user_request}")
        
        # Setup incremental saving
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        output_dir = Path(self.config_loader.get_value("app_config.output_dir", "backend/output"))
        incremental_dir = output_dir / f"incremental_{timestamp}"
        incremental_dir.mkdir(parents=True, exist_ok=True)
        
        # Rebuild agents with callback support for incremental saving and status updates
        workflow_config = self._parse_workflow_config()
        input_directory = self.base_dir / "input"
        
        # Create a wrapper callback that handles both saving and status updates
        def progress_callback_wrapper(agent_name: str, content: str, execution_order: int):
            """Wrapper callback that handles both saving and status reporting."""
            logger.info(f"🔄 Agent completed: {agent_name} (#{execution_order})")
            
            # Track executed agents
            if agent_name not in executed_agents:
                executed_agents.append(agent_name)
            
            # Calculate progress based on execution order
            total_agents = len(workflow_config.agents) - 1  # Exclude MainFlexibleOrchestrator
            progress = 10.0 + (execution_order * 80.0 / max(total_agents, 1))
            
            # Report completion via status callback
            if status_callback:
                status_callback(agent_name, min(95.0, progress), f"Completed {agent_name}")
        
        factory = FlexibleAgentFactory(
            workflow_config.agents, 
            self.prompts_loader, 
            input_directory, 
            incremental_dir,
            progress_callback=progress_callback_wrapper
        )
        self.all_agents = factory.build_all()
        
        # Update main agent and runner with callback-enabled agents
        if workflow_config.main_agent not in self.all_agents:
            raise ValueError(f"Main flexible agent '{workflow_config.main_agent}' not found in agents")
        
        self.main_agent = self.all_agents[workflow_config.main_agent]
        
        # Recreate runner with callback-enabled agents
        app_name = self.config_loader.get_value("app_config.app_name", "flexible_workflow")
        self.runner = InMemoryRunner(
            agent=self.main_agent,
            app_name=app_name
        )
        
        # Create new session for the new runner
        user_id = self.config_loader.get_value("app_config.user_id", "flexible_user")
        session_id = f"flexible_session_{timestamp}"
        
        self.session = await self.runner.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Save initial workflow metadata
        await self._save_workflow_metadata(incremental_dir, user_request, start_time)
        
        # Track agent execution for better error reporting
        current_agent = None
        executed_agents = []
        agent_outputs = {}  # Store outputs for incremental saving
        
        try:
            # Initialize if not already done
            if not self.main_agent:
                await self.initialize()
            
            # Log all agent configurations for debugging
            self._log_agent_configurations()
            
            # Report initialization complete
            if status_callback:
                status_callback("Initialization", 5.0, "Workflow initialized successfully")
            
            # Create user message
            content = types.Content(role='user', parts=[types.Part(text=user_request)])
            
            # Execute the workflow
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
                
                # Extract state information for final summary
                if hasattr(event, 'state') and event.state:
                    final_state.update(event.state)
            
            # Get the final state from the session
            if not final_state and self.session:
                final_state = getattr(self.session, 'state', {})
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": WorkflowStatus.COMPLETED,
                "content": response_text or "Flexible workflow completed successfully",
                "metadata": {
                    "success": bool(response_text),
                    "execution_time": execution_time,
                    "timestamp": start_time.isoformat(),
                    "original_request": user_request,
                    "workflow_type": "flexible",
                    "workflow_name": self.config_loader.get_value("name"),
                    "workflow_version": self.config_loader.get_value("version"),
                    "agents_executed": executed_agents,
                    "main_agent": self.main_agent.name,
                    "total_agents": len(self.all_agents),
                    "model_used": self.config_loader.get_value("core_config.model"),
                    "incremental_output_dir": str(incremental_dir)
                },
                "state": final_state
            }
            
            # Save final comprehensive results
            await self._save_results(result)
            
            # Get outputs saved by callbacks
            callback_outputs = {}
            if hasattr(factory, 'saved_outputs'):
                callback_outputs = {name: "Saved via callback" for name in factory.saved_outputs}
            
            # Save final summary to incremental directory
            await self._save_final_summary(incremental_dir, result, executed_agents, callback_outputs)
            
            # Report completion via callback
            if status_callback:
                status_callback("Completed", 100.0, f"Workflow completed successfully in {execution_time:.1f}s")
            
            logger.info(f"✅ Flexible workflow completed successfully in {execution_time:.2f}s")
            logger.info(f"📁 Incremental outputs saved to: {incremental_dir}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Enhanced error reporting with agent and model details
            error_details = self._analyze_error(e, current_agent, executed_agents)
            error_msg = f"Flexible workflow failed: {str(e)}"
            
            # Log detailed error information
            logger.error(f"❌ {error_msg}")
            logger.error(f"   Failed Agent: {error_details['failed_agent']}")
            logger.error(f"   Agent Model: {error_details['agent_model']}")
            logger.error(f"   Agent Type: {error_details['agent_type']}")
            logger.error(f"   Executed Agents: {executed_agents}")
            logger.error(f"   Error Type: {error_details['error_type']}")
            
            # Get outputs saved by callbacks for error report
            callback_outputs = {}
            if 'factory' in locals() and hasattr(factory, 'saved_outputs'):
                callback_outputs = {name: "Saved via callback" for name in factory.saved_outputs}
            
            # Save error details to incremental directory
            await self._save_error_details(incremental_dir, error_details, executed_agents, callback_outputs)
            
            result = {
                "status": WorkflowStatus.FAILED,
                "content": error_msg,
                "metadata": {
                    "success": False,
                    "execution_time": execution_time,
                    "timestamp": start_time.isoformat(),
                    "error": str(e),
                    "error_details": error_details,
                    "executed_agents": executed_agents,
                    "workflow_type": "flexible",
                    "workflow_name": self.config_loader.get_value("name", "Flexible Workflow"),
                    "workflow_version": self.config_loader.get_value("version", "1.0.0"),
                    "incremental_output_dir": str(incremental_dir)
                }
            }
            
            logger.info(f"📁 Partial outputs saved to: {incremental_dir}")
            return result

    async def _save_workflow_metadata(self, incremental_dir: Path, user_request: str, start_time: datetime) -> None:
        """Save initial workflow metadata and configuration.
        
        Args:
            incremental_dir: Directory to save metadata to
            user_request: Original user request
            start_time: Workflow start time
        """
        try:
            metadata_file = incremental_dir / "00_workflow_metadata.md"
            
            metadata_content = f"""# Flexible Workflow Execution - Metadata

## 🚀 Workflow Information
- **Workflow Name**: {self.config_loader.get_value('name', 'Flexible Workflow')}
- **Version**: {self.config_loader.get_value('version', '1.0.0')}
- **Started**: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Type**: Flexible Multi-Agent Workflow

## 📝 Original Request
```
{user_request}
```

## 🤖 Agent Configuration
- **Main Agent**: {self.config_loader.get_value('main_agent', 'MainFlexibleOrchestrator')}
- **Model**: {self.config_loader.get_value('core_config.model', 'gemini-1.5-flash')}
- **Total Agents**: {len(self.all_agents) if self.all_agents else 0}

### Available Agents:
"""
            
            if self.all_agents:
                for i, (name, agent) in enumerate(self.all_agents.items(), 1):
                    agent_type = type(agent).__name__
                    metadata_content += f"{i}. **{name}** ({agent_type})\n"
            
            metadata_content += f"""
## 📁 Output Organization
- This directory contains incremental outputs from each agent
- Files are numbered in execution order
- Each agent's output is saved immediately upon completion
- If the workflow fails, you'll have outputs up to the failure point

---
*Generated by FlexibleWorkflowManager on {start_time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                f.write(metadata_content)
                
            logger.info(f"📋 Workflow metadata saved: {metadata_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save workflow metadata: {e}")

    async def _save_final_summary(
        self, 
        incremental_dir: Path, 
        result: Dict[str, Any], 
        executed_agents: List[str],
        agent_outputs: Dict[str, str]
    ) -> None:
        """Save final workflow summary to incremental directory.
        
        Args:
            incremental_dir: Directory to save summary to
            result: Workflow execution result
            executed_agents: List of executed agent names
            agent_outputs: Dictionary of agent outputs
        """
        try:
            summary_file = incremental_dir / "99_final_summary.md"
            metadata = result.get("metadata", {})
            
            summary_content = f"""# Workflow Execution Summary

## ✅ Final Status: {result.get('status', 'Unknown')}

## 📊 Execution Metrics
- **Success**: {metadata.get('success', False)}
- **Execution Time**: {metadata.get('execution_time', 0):.2f} seconds
- **Total Agents**: {metadata.get('total_agents', 0)}
- **Agents Executed**: {len(executed_agents)}
- **Agents with Outputs**: {len(agent_outputs)}

## 🤖 Agent Execution Order
"""
            
            for i, agent in enumerate(executed_agents, 1):
                status = "✅ Completed" if agent in agent_outputs else "⏸️ No Output"
                summary_content += f"{i}. **{agent}** - {status}\n"
            
            summary_content += f"""
## 📝 Final Response
{result.get('content', 'No final response available')}

## 📁 Generated Files
"""
            
            # List all generated files
            try:
                for file_path in sorted(incremental_dir.glob("*.md")):
                    if file_path.name != "99_final_summary.md":
                        summary_content += f"- `{file_path.name}`\n"
            except:
                summary_content += "- Error listing generated files\n"
            
            summary_content += f"""
## 🎯 Workflow Performance
- **Average time per agent**: {metadata.get('execution_time', 0) / max(len(executed_agents), 1):.2f}s
- **Success rate**: {len(agent_outputs) / max(len(executed_agents), 1) * 100:.1f}%

---
*Workflow completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            logger.info(f"📋 Final summary saved: {summary_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save final summary: {e}")

    async def _save_error_details(
        self, 
        incremental_dir: Path, 
        error_details: Dict[str, Any],
        executed_agents: List[str],
        agent_outputs: Dict[str, str]
    ) -> None:
        """Save error details and partial results when workflow fails.
        
        Args:
            incremental_dir: Directory to save error details to
            error_details: Dictionary containing error information
            executed_agents: List of executed agent names
            agent_outputs: Dictionary of agent outputs
        """
        try:
            error_file = incremental_dir / "99_error_report.md"
            
            error_content = f"""# ❌ Workflow Execution Failed

## 🚨 Error Details
- **Failed Agent**: {error_details.get('failed_agent', 'Unknown')}
- **Agent Type**: {error_details.get('agent_type', 'Unknown')}
- **Agent Model**: {error_details.get('agent_model', 'Unknown')}
- **Error Type**: {error_details.get('error_type', 'Unknown')}
- **Error Category**: {error_details.get('error_category', 'Unknown')}
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📝 Error Message
```
{error_details.get('error_message', 'No error message available')}
```

## ✅ Successfully Completed Agents
"""
            
            for i, agent in enumerate(executed_agents, 1):
                status = "✅ Completed with Output" if agent in agent_outputs else "⏸️ Executed (No Output)"
                error_content += f"{i}. **{agent}** - {status}\n"
            
            error_content += f"""
## 📊 Partial Execution Statistics
- **Total Agents in Workflow**: {error_details.get('total_agents_in_workflow', 0)}
- **Agents Executed**: {len(executed_agents)}
- **Agents with Outputs**: {len(agent_outputs)}
- **Success Rate**: {len(agent_outputs) / max(len(executed_agents), 1) * 100:.1f}%

## 💾 Available Outputs
You have the following partial results available:
"""
            
            # List available outputs
            for agent in executed_agents:
                if agent in agent_outputs:
                    safe_name = agent.lower().replace(' ', '_').replace('-', '_')
                    file_pattern = f"*_{safe_name}.md"
                    error_content += f"- **{agent}**: See `{file_pattern}`\n"
            
            error_content += f"""
## 🔧 Troubleshooting
- Check the failed agent configuration
- Verify API quotas and connectivity
- Review agent-specific logs above
- Consider running from the last successful checkpoint

## 🔄 Recovery Options
1. **Partial Results**: Use the outputs from successful agents
2. **Restart from Checkpoint**: Modify workflow to start from last successful agent
3. **Debug Mode**: Run individual agents to isolate the issue

---
*Error report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(error_content)
            
            logger.info(f"🚨 Error report saved: {error_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save error details: {e}")

    async def _save_results(self, result: Dict[str, Any]) -> None:
        """Save flexible workflow results to output directory in multiple formats.
        
        Args:
            result: Workflow execution result to save
        """
        try:
            output_dir = Path(self.config_loader.get_value("app_config.output_dir", "backend/output"))
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save JSON result
            result_file = output_dir / f"flexible_workflow_result_{timestamp}.json"
            import json
            result_copy = result.copy()
            if 'status' in result_copy:
                result_copy['status'] = str(result_copy['status'])
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_copy, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Flexible workflow results saved to: {result_file}")
            
            # Save comprehensive markdown report
            await self._save_markdown_report(result, output_dir, timestamp)
            
            # Save individual agent outputs if available in state (legacy support)
            await self._save_individual_outputs(result, output_dir, timestamp)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save flexible workflow results: {e}")

    async def _save_markdown_report(self, result: Dict[str, Any], output_dir: Path, timestamp: str) -> None:
        """Save a comprehensive markdown report of the workflow execution.
        
        Args:
            result: Workflow execution result
            output_dir: Directory to save report to
            timestamp: Timestamp for file naming
        """
        try:
            markdown_file = output_dir / f"flexible_workflow_report_{timestamp}.md"
            metadata = result.get("metadata", {})
            state = result.get("state", {})
            
            markdown_content = f"""# Flexible Workflow Execution Report

## 📋 Summary
- **Workflow**: {metadata.get('workflow_name', 'N/A')} v{metadata.get('workflow_version', 'N/A')}
- **Status**: {result.get('status', 'N/A')}
- **Success**: {metadata.get('success', False)}
- **Execution Time**: {metadata.get('execution_time', 0):.2f} seconds
- **Timestamp**: {metadata.get('timestamp', 'N/A')}
- **Workflow Type**: {metadata.get('workflow_type', 'N/A')}
- **Incremental Outputs**: {metadata.get('incremental_output_dir', 'N/A')}

## 🎯 Original Request
```
{metadata.get('original_request', 'N/A')}
```

## 🤖 Agent Configuration
- **Main Agent**: {metadata.get('main_agent', 'N/A')}
- **Total Agents**: {metadata.get('total_agents', 0)}
- **Model Used**: {metadata.get('model_used', 'N/A')}

### Agents Executed:
"""
            
            # Add list of agents
            agents_executed = metadata.get('agents_executed', [])
            for i, agent in enumerate(agents_executed, 1):
                markdown_content += f"{i}. **{agent}**\n"
            
            markdown_content += f"""
## 📝 Final Response
{result.get('content', 'No response content available')}
"""
            
            # Add incremental outputs information
            incremental_dir = metadata.get('incremental_output_dir')
            if incremental_dir:
                markdown_content += f"""
## 📁 Incremental Outputs
Individual agent outputs have been saved to: `{incremental_dir}`

Each agent's output is saved as a separate markdown file with execution order:
- `00_workflow_metadata.md` - Initial workflow configuration
- `01_[agent_name].md` - First agent output
- `02_[agent_name].md` - Second agent output
- `...` - Additional agent outputs in execution order
- `99_final_summary.md` - Execution summary

Note: Actual filenames will match the executed agents in your workflow.
"""
            
            # Add individual agent outputs if available
            if state:
                markdown_content += "\n## 🔍 Individual Agent Outputs\n"
                
                for key, value in state.items():
                    if value and isinstance(value, str):
                        # Format the key to be more readable
                        formatted_key = key.replace('_', ' ').title()
                        markdown_content += f"""
### {formatted_key}
```
{value}
```
"""
            
            # Add performance and metadata section
            markdown_content += f"""
## 📊 Performance Metrics
- **Execution Time**: {metadata.get('execution_time', 0):.2f} seconds
- **Success Rate**: {'100%' if metadata.get('success') else '0%'}
- **Memory Usage**: Available in full JSON report
- **API Calls**: Tracked in session state

## 🔧 Technical Details
- **Workflow Manager**: FlexibleWorkflowManager
- **Runner Type**: InMemoryRunner
- **Session ID**: {self.config_loader.get_value('app_config.session_id', 'N/A')}
- **User ID**: {self.config_loader.get_value('app_config.user_id', 'N/A')}
- **App Name**: {self.config_loader.get_value('app_config.app_name', 'N/A')}
"""
            
            # Add error information if failed
            if not metadata.get('success', True):
                error_msg = metadata.get('error', 'Unknown error')
                markdown_content += f"""
## ❌ Error Information
```
{error_msg}
```
"""
            
            # Add footer
            markdown_content += f"""
---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Flexible Workflow System*
"""
            
            # Write the markdown file
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"📄 Markdown report saved to: {markdown_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save markdown report: {e}")

    async def _save_individual_outputs(self, result: Dict[str, Any], output_dir: Path, timestamp: str) -> None:
        """Save individual agent outputs as separate files if available (legacy support).
        
        Args:
            result: Workflow execution result
            output_dir: Directory to save outputs to
            timestamp: Timestamp for file naming
        """
        try:
            state = result.get("state", {})
            if not state:
                return
            
            # Save each output in state as a separate file
            for key, value in state.items():
                if value and isinstance(value, str) and len(value.strip()) > 0:
                    # Determine file extension based on content
                    if any(keyword in key.lower() for keyword in ['code', 'script', 'program']):
                        if 'python' in value.lower() or 'def ' in value or 'import ' in value:
                            ext = 'py'
                        elif 'javascript' in value.lower() or 'function ' in value or 'const ' in value:
                            ext = 'js'
                        elif 'typescript' in value.lower() or 'interface ' in value:
                            ext = 'ts'
                        else:
                            ext = 'txt'
                    elif any(keyword in key.lower() for keyword in ['review', 'comment', 'analysis', 'report']):
                        ext = 'md'
                    elif any(keyword in key.lower() for keyword in ['config', 'setting']):
                        ext = 'yml'
                    else:
                        ext = 'txt'
                    
                    # Create filename
                    safe_key = key.lower().replace(' ', '_').replace('-', '_')
                    output_file = output_dir / f"{safe_key}_{timestamp}.{ext}"
                    
                    # Write the file
                    with open(output_file, 'w', encoding='utf-8') as f:
                        if ext == 'md' and not value.startswith('#'):
                            # Add markdown header if it's a markdown file without one
                            f.write(f"# {key.replace('_', ' ').title()}\n\n{value}")
                        else:
                            f.write(value)
                    
                    logger.info(f"📁 Individual output saved: {output_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save individual outputs: {e}")

    def _log_agent_configurations(self) -> None:
        """Log detailed agent configurations for debugging."""
        logger.info("🔍 Agent Configuration Details:")
        
        if not self.all_agents:
            logger.warning("   No agents initialized yet")
            return
            
        for agent_name, agent in self.all_agents.items():
            agent_type = type(agent).__name__
            
            # Try to get model from agent or config
            model = "unknown"
            if hasattr(agent, 'model'):
                model = agent.model
            else:
                # Look up in workflow config
                agents_config = self.config_loader.get_value('agents', [])
                for agent_config in agents_config:
                    if agent_config.get('name') == agent_name:
                        model = agent_config.get('model', 'not specified')
                        break
            
            logger.info(f"   📱 {agent_name}: {agent_type} (model: {model})")
    
    def _analyze_error(self, error: Exception, current_agent: str, executed_agents: list) -> Dict[str, Any]:
        """Analyze error and provide detailed information about the failure.
        
        Args:
            error: The exception that occurred
            current_agent: Name of the currently executing agent
            executed_agents: List of agents that were executed
            
        Returns:
            Dictionary containing detailed error analysis
        """
        error_str = str(error)
        error_type = type(error).__name__
        
        # Determine which agent likely failed
        failed_agent = current_agent or (executed_agents[-1] if executed_agents else "unknown")
        
        # Try to determine the model for the failed agent
        agent_model = "unknown"
        agent_type = "unknown"
        
        if failed_agent and failed_agent in self.all_agents:
            agent = self.all_agents[failed_agent]
            agent_type = type(agent).__name__
            
            # Try to get model from agent
            if hasattr(agent, 'model'):
                agent_model = agent.model
            else:
                # Look up in workflow config
                agents_config = self.config_loader.get_value('agents', [])
                for agent_config in agents_config:
                    if agent_config.get('name') == failed_agent:
                        agent_model = agent_config.get('model', 'not specified')
                        break
        
        # Classify error type
        error_category = "unknown"
        if "503" in error_str and ("overloaded" in error_str.lower() or "unavailable" in error_str.lower()):
            error_category = "api_overloaded"
        elif "429" in error_str:
            error_category = "rate_limit"
        elif "401" in error_str or "unauthorized" in error_str.lower():
            error_category = "authentication"
        elif "400" in error_str:
            error_category = "bad_request"
        elif "timeout" in error_str.lower():
            error_category = "timeout"
        elif "network" in error_str.lower() or "connection" in error_str.lower():
            error_category = "network"
        
        return {
            "failed_agent": failed_agent,
            "agent_model": agent_model,
            "agent_type": agent_type,
            "error_type": error_type,
            "error_category": error_category,
            "error_message": error_str,
            "all_executed_agents": executed_agents,
            "total_agents_in_workflow": len(self.all_agents) if self.all_agents else 0
        }

    def print_configuration_summary(self) -> None:
        """Print a summary of the loaded flexible workflow configuration."""
        logger.info("📋 Flexible Workflow Configuration Summary:")
        logger.info(f"   Workflow Name: {self.config_loader.get_value('name', 'N/A')}")
        logger.info(f"   Workflow Version: {self.config_loader.get_value('version', 'N/A')}")
        logger.info(f"   Model: {self.config_loader.get_value('core_config.model', 'N/A')}")
        logger.info(f"   Available Tools: {FlexibleToolRegistry.list_tools()}")
        if self.all_agents:
            logger.info(f"   Total Agents: {len(self.all_agents)}")
            for name, agent in self.all_agents.items():
                logger.info(f"     - {name}: {type(agent).__name__}") 