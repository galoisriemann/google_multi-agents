"""Factory for creating flexible agents from configuration.

This module provides the FlexibleAgentFactory class that creates and configures
various types of agents based on configuration specifications.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent, ParallelAgent, LoopAgent

# Try absolute imports first (for module execution), then relative imports (for direct execution)
try:
    from backend.core.config.config_loader import ConfigLoader
    from backend.core.config.flexible_config import FlexibleAgentConfig
    from backend.core.tools.tool_registry import FlexibleToolRegistry
    from backend.core.utils.document_reader import DocumentReader, DocumentReaderError
except ImportError:
    # If absolute imports fail, try relative imports for direct execution
    from ..config.config_loader import ConfigLoader
    from ..config.flexible_config import FlexibleAgentConfig
    from ..tools.tool_registry import FlexibleToolRegistry
    from ..utils.document_reader import DocumentReader, DocumentReaderError

logger = logging.getLogger(__name__)


# Map agent type strings to their corresponding classes
FLEXIBLE_AGENT_CLASSES: Dict[str, Type[BaseAgent]] = {
    "LlmAgent": LlmAgent,
    "SequentialAgent": SequentialAgent,
    "ParallelAgent": ParallelAgent,
    "LoopAgent": LoopAgent,
}


class FlexibleAgentFactory:
    """Factory for creating flexible agents from configuration.
    
    This factory handles the creation, configuration, and wiring of flexible agents
    based on configuration specifications. It supports incremental output saving
    and proper agent lifecycle management.
    """
    
    def __init__(
        self, 
        configs: List[FlexibleAgentConfig], 
        prompts_loader: ConfigLoader, 
        input_directory: Optional[Path] = None, 
        incremental_dir: Optional[Path] = None,
        progress_callback: Optional[callable] = None
    ):
        """Initialize the flexible agent factory.
        
        Args:
            configs: List of agent configurations
            prompts_loader: Configuration loader for prompts
            input_directory: Directory containing input documents
            incremental_dir: Directory for saving incremental outputs
            progress_callback: Optional callback function for progress updates (agent_name, content, execution_order)
        """
        self.configs = {c.name: c for c in configs}
        self.instances: Dict[str, BaseAgent] = {}
        self.prompts_loader = prompts_loader
        self.document_reader = DocumentReader(input_directory)
        self.incremental_dir = incremental_dir
        self.progress_callback = progress_callback
        self.agent_execution_order = {}
        self.saved_outputs = set()
        
        logger.info(f"Initialized FlexibleAgentFactory with {len(configs)} agent configurations")

    def build_all(self) -> Dict[str, BaseAgent]:
        """Build all flexible agents from configurations.
        
        Returns:
            Dictionary mapping agent names to their instances
            
        Raises:
            Exception: If agent creation or wiring fails
        """
        logger.info("Building all flexible agents...")
        
        # First pass: instantiate each agent
        for cfg in self.configs.values():
            try:
                agent = self._create_agent(cfg)
                setattr(agent, '_pending_subs', cfg.sub_agents)
                self.instances[cfg.name] = agent
                logger.info(f"Created flexible agent: {cfg.name} ({cfg.type})")
            except Exception as e:
                logger.error(f"Failed to create flexible agent {cfg.name}: {e}")
                raise

        # Second pass: wire sub_agents
        for agent in self.instances.values():
            pending = getattr(agent, '_pending_subs', [])
            if pending:
                sub_agents = []
                for sub_name in pending:
                    if sub_name in self.instances:
                        sub_agents.append(self.instances[sub_name])
                    else:
                        logger.warning(f"Sub-agent '{sub_name}' not found for agent '{agent.name}'")
                agent.sub_agents = sub_agents
            
            # Clean up temporary attribute
            if hasattr(agent, '_pending_subs'):
                delattr(agent, '_pending_subs')

        logger.info(f"Successfully built {len(self.instances)} flexible agents")
        return self.instances

    def _create_agent(self, cfg: FlexibleAgentConfig) -> BaseAgent:
        """Create a single flexible agent from configuration.
        
        Args:
            cfg: Configuration for the agent to create
            
        Returns:
            Configured agent instance
            
        Raises:
            Exception: If agent creation fails
        """
        try:
            logger.info(f"🔧 Creating agent: {cfg.name} (type: {cfg.type})")
            
            cls = FLEXIBLE_AGENT_CLASSES[cfg.type]
            kwargs: Dict[str, Any] = {"name": cfg.name}
            
            # Add common attributes
            if cfg.description:
                kwargs["description"] = cfg.description
                logger.debug(f"   Added description: {cfg.description}")
            
            # LlmAgent specific attributes
            if cfg.type == "LlmAgent":
                if cfg.model:
                    kwargs["model"] = cfg.model
                    logger.debug(f"   Added model: {cfg.model}")
                
                # Get instruction from prompt_key or direct instruction
                if cfg.prompt_key:
                    kwargs["instruction"] = self._get_prompt(cfg.prompt_key, cfg)
                    logger.debug(f"   Added instruction from prompt_key: {cfg.prompt_key}")
                elif cfg.instruction:
                    kwargs["instruction"] = cfg.instruction
                    logger.debug(f"   Added direct instruction")
                
                if cfg.output_key:
                    kwargs["output_key"] = cfg.output_key
                    logger.debug(f"   Added output_key: {cfg.output_key}")
                
                # Add after_model callback for individual file saving
                if self.incremental_dir:
                    kwargs["after_model_callback"] = self._create_after_model_callback(cfg.name)
                    logger.debug(f"   Added after_model_callback for incremental saving")
            
            # Add tools if specified
            if cfg.tools:
                try:
                    kwargs["tools"] = [FlexibleToolRegistry.get(name) for name in cfg.tools]
                    logger.debug(f"   Added tools: {cfg.tools}")
                except KeyError as e:
                    logger.warning(f"Tool not found for flexible agent {cfg.name}: {e}")
            
            # LoopAgent specific attributes
            if cfg.type == "LoopAgent" and cfg.max_iterations is not None:
                logger.debug(f"   Adding max_iterations: {cfg.max_iterations} (type: {type(cfg.max_iterations)})")
                if isinstance(cfg.max_iterations, dict):
                    logger.error(f"❌ max_iterations is a dict but should be int: {cfg.max_iterations}")
                    raise ValueError(f"max_iterations must be an integer, got dict: {cfg.max_iterations}")
                kwargs["max_iterations"] = cfg.max_iterations
            
            # Filter extra parameters to only include supported ones
            supported_params = {"name", "model", "instruction", "description", "output_key", "tools", "sub_agents", "max_iterations"}
            
            for key, value in cfg.extra.items():
                if key in supported_params:
                    logger.debug(f"   Adding extra param {key}: {value} (type: {type(value)})")
                    if key == "max_iterations" and isinstance(value, dict):
                        logger.error(f"❌ Extra param {key} is a dict but should be int: {value}")
                        raise ValueError(f"Parameter {key} must be an integer, got dict: {value}")
                    kwargs[key] = value
                else:
                    logger.debug(f"   Skipping unsupported param: {key} = {value}")
            
            logger.info(f"   Creating {cfg.type} with kwargs: {list(kwargs.keys())}")
            
            # Log the actual kwargs values for debugging
            for k, v in kwargs.items():
                logger.debug(f"     {k}: {type(v)} = {v}")
            
            agent = cls(**kwargs)
            logger.info(f"✅ Successfully created agent: {cfg.name}")
            return agent
            
        except Exception as e:
            logger.error(f"❌ Failed to create agent {cfg.name}: {e}")
            logger.error(f"   Agent config: {cfg}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            raise

    def _get_prompt(self, prompt_key: str, agent_config: FlexibleAgentConfig) -> str:
        """Get prompt from prompts configuration file and inject input file content if available.
        
        Args:
            prompt_key: Key to look up in prompts configuration
            agent_config: Configuration for the agent requesting the prompt
            
        Returns:
            The prompt text with any input documents injected
            
        Raises:
            Exception: If prompt loading fails
        """
        try:
            prompt = self.prompts_loader.get_value(f"prompts.{prompt_key}")
            if not prompt:
                raise ValueError(f"Prompt '{prompt_key}' not found in prompts configuration")
            
            # Collect input documents from both single and multiple file specifications
            input_files = []
            
            # Handle single input file (input_key)
            if hasattr(agent_config, 'input_key') and agent_config.input_key:
                input_files.append(agent_config.input_key)
            
            # Handle multiple input files (input_keys)
            if hasattr(agent_config, 'input_keys') and agent_config.input_keys:
                input_files.extend(agent_config.input_keys)
            
            # Process all input files
            if input_files:
                input_content_parts = []
                successful_files = []
                
                for i, filename in enumerate(input_files, 1):
                    try:
                        file_content = self.document_reader.read_document(filename)
                        if file_content:
                            input_content_parts.append(f"### Document {i}: {filename}\n{file_content}")
                            successful_files.append(filename)
                            logger.info(f"Loaded input document '{filename}' for agent '{agent_config.name}'")
                        else:
                            logger.warning(f"No content found in document '{filename}' for agent '{agent_config.name}'")
                    except DocumentReaderError as e:
                        logger.warning(f"Failed to read input document '{filename}': {e}")
                
                # Inject all input content into prompt if any files were successfully loaded
                if input_content_parts:
                    if len(successful_files) == 1:
                        # Single document format (backward compatibility)
                        prompt = f"{prompt}\n\n**Additional Input Document:**\n{input_content_parts[0].split('\\n', 1)[1]}"
                    else:
                        # Multiple documents format
                        combined_content = "\n\n".join(input_content_parts)
                        prompt = f"{prompt}\n\n**Additional Input Documents ({len(successful_files)} files):**\n{combined_content}"
                    
                    logger.info(f"Injected {len(successful_files)} input documents into prompt for agent '{agent_config.name}'")
                else:
                    logger.warning(f"No input documents were successfully loaded for agent '{agent_config.name}'")
            
            return prompt
        except Exception as e:
            logger.error(f"Failed to load prompt '{prompt_key}': {e}")
            raise

    def _create_after_model_callback(self, agent_name: str):
        """Create an after_model callback for saving individual agent outputs.
        
        Uses after_model_callback to get immediate access to the LLM response
        as soon as the model returns, enabling real-time saving of individual
        agent outputs during workflow execution.
        
        Args:
            agent_name: Name of the agent to create callback for
            
        Returns:
            Callback function that accepts (callback_context, llm_response) parameters
            and returns None to pass through the original response unchanged.
        """
        def after_model_callback(callback_context, llm_response):
            """Callback to save agent output immediately after model responds."""
            try:
                if not self.incremental_dir or agent_name in self.saved_outputs:
                    return None  # Don't modify response, just pass through
                
                # Get execution order
                if agent_name not in self.agent_execution_order:
                    self.agent_execution_order[agent_name] = len(self.agent_execution_order) + 1
                
                execution_order = self.agent_execution_order[agent_name]
                
                # Extract content from LLM response
                content = ""
                
                if llm_response and llm_response.content and llm_response.content.parts:
                    for part in llm_response.content.parts:
                        if hasattr(part, 'text') and part.text:
                            content += part.text
                        elif hasattr(part, 'function_call'):
                            # For function calls, we'll save a description
                            func_call = part.function_call
                            content += f"Function Call: {func_call.name}\nArguments: {func_call.args}\n"
                elif llm_response and hasattr(llm_response, 'error_message') and llm_response.error_message:
                    content = f"Error: {llm_response.error_message}"
                
                if content and len(content.strip()) > 0:
                    # Save immediately using sync method in callback
                    self._save_agent_output_sync(agent_name, content, execution_order)
                    self.saved_outputs.add(agent_name)
                    logger.info(f"🔄 Model callback saved output for agent: {agent_name} ({len(content)} chars)")
                    
                    # Call progress callback if available
                    if self.progress_callback:
                        try:
                            self.progress_callback(agent_name, content, execution_order)
                        except Exception as e:
                            logger.error(f"Error in progress callback for {agent_name}: {e}")
                else:
                    logger.warning(f"⚠️ No content found in model callback for agent: {agent_name}")
                
                # Return None to pass through original response unchanged
                return None
                
            except Exception as e:
                logger.error(f"Error in after_model_callback for {agent_name}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None  # Don't modify response on error
        
        return after_model_callback
    
    def _save_agent_output_sync(self, agent_name: str, content: str, execution_order: int):
        """Synchronous method to save agent output from callback.
        
        Args:
            agent_name: Name of the agent whose output is being saved
            content: The output content to save
            execution_order: Order in which the agent was executed
        """
        try:
            if not self.incremental_dir:
                return
                
            filename = f"{execution_order:02d}_{agent_name.lower().replace(' ', '_')}.md"
            file_path = self.incremental_dir / filename
            
            # Create markdown content
            markdown_content = f"""# {agent_name} Output
**Agent**: {agent_name}
**Execution Order**: {execution_order}
**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{content}

---
*Saved by after_agent_callback on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"💾 Saved agent output: {filename} ({len(content)} chars)")
            
        except Exception as e:
            logger.error(f"Failed to save output for {agent_name}: {e}")
    
    def get_agent_config_by_name(self, agent_name: str) -> Optional[FlexibleAgentConfig]:
        """Get agent configuration by name.
        
        Args:
            agent_name: Name of the agent to find
            
        Returns:
            Agent configuration if found, None otherwise
        """
        return self.configs.get(agent_name) 