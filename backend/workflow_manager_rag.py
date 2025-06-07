import os
import logging
import asyncio
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import yaml
from data_model.data_models import WorkflowConfig, PromptConfig, WorkflowStatus

# Import Google ADK for tool-based approach
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import SseServerParams
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

logger = logging.getLogger(__name__)


def clean_schema_for_gemini(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean up OpenAPI schema to be compatible with Google Gemini function calling.
    
    This function fixes common issues with MCP server schemas that cause validation
    errors in Google's Gemini API, particularly 'any_of' fields with other properties.
    
    Args:
        schema: The original schema dictionary
        
    Returns:
        Cleaned schema dictionary compatible with Gemini
    """
    if not isinstance(schema, dict):
        return schema
    
    cleaned_schema = {}
    
    for key, value in schema.items():
        if key == 'properties' and isinstance(value, dict):
            # Clean up properties recursively
            cleaned_properties = {}
            for prop_name, prop_schema in value.items():
                cleaned_prop = clean_property_schema(prop_schema)
                if cleaned_prop is not None:  # Only include valid properties
                    cleaned_properties[prop_name] = cleaned_prop
            cleaned_schema[key] = cleaned_properties
        elif key in ['required', 'type', 'title', 'description', 'additionalProperties', '$schema']:
            # Keep these fields as-is
            cleaned_schema[key] = value
        elif key == 'items' and isinstance(value, dict):
            # Clean array items schema
            cleaned_schema[key] = clean_schema_for_gemini(value)
        # Skip other fields that might cause issues
    
    return cleaned_schema


def clean_property_schema(prop_schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Clean individual property schema for Gemini compatibility.
    
    Args:
        prop_schema: Property schema dictionary
        
    Returns:
        Cleaned property schema or None if it should be excluded
    """
    if not isinstance(prop_schema, dict):
        return prop_schema
    
    # Handle any_of fields - extract the most appropriate type
    if 'any_of' in prop_schema or 'anyOf' in prop_schema:
        any_of_key = 'any_of' if 'any_of' in prop_schema else 'anyOf'
        any_of_options = prop_schema[any_of_key]
        
        # Find the first non-null type option
        selected_type = None
        for option in any_of_options:
            if isinstance(option, dict):
                if option.get('type') and option.get('type') != 'null':
                    selected_type = option
                    break
        
        if selected_type:
            # Create a new schema with the selected type and preserve other fields
            cleaned_prop = {}
            
            # Copy over the selected type's properties
            for key, value in selected_type.items():
                if key != 'nullable':  # Skip nullable as it's handled by any_of
                    cleaned_prop[key] = value
            
            # Copy over other fields from the original schema (like default, title, etc.)
            for key, value in prop_schema.items():
                if key not in [any_of_key, 'nullable'] and key not in cleaned_prop:
                    cleaned_prop[key] = value
            
            return cleaned_prop
        else:
            # If no valid type found, create a basic string type
            return {
                'type': 'string',
                'title': prop_schema.get('title', 'value'),
                'description': prop_schema.get('description', 'Parameter value')
            }
    
    # Handle other problematic patterns
    cleaned_prop = {}
    for key, value in prop_schema.items():
        if key in ['type', 'title', 'description', 'default', 'minimum', 'maximum', 'items']:
            if key == 'items' and isinstance(value, dict):
                cleaned_prop[key] = clean_property_schema(value)
            else:
                cleaned_prop[key] = value
        elif key == 'enum':
            # Keep enum values
            cleaned_prop[key] = value
    
    # Ensure we have at least a type
    if 'type' not in cleaned_prop:
        cleaned_prop['type'] = 'string'
    
    return cleaned_prop


class CleanedMCPToolset(MCPToolset):
    """
    Custom MCPToolset that cleans schemas for Gemini compatibility.
    """
    
    async def get_tools(self, ctx):
        """Override to clean tool schemas before returning."""
        tools = await super().get_tools(ctx)
        
        cleaned_tools = []
        for tool in tools:
            try:
                # Instead of wrapping, directly patch the tool's _get_declaration method
                original_get_declaration = tool._get_declaration
                
                def create_cleaned_get_declaration(orig_tool, orig_method):
                    def cleaned_get_declaration():
                        try:
                            logger.debug(f"Intercepted _get_declaration call for tool: {getattr(orig_tool, 'name', 'unknown')}")
                            
                            # Get the original declaration
                            original_declaration = orig_method()
                            if not original_declaration:
                                logger.warning("No original declaration found")
                                return original_declaration
                            
                            logger.debug(f"Original declaration for {getattr(orig_tool, 'name', 'unknown')}: {original_declaration}")
                            
                            # Clone the declaration and clean its parameters
                            from copy import deepcopy
                            cleaned_declaration = deepcopy(original_declaration)
                            
                            if hasattr(cleaned_declaration, 'parameters') and cleaned_declaration.parameters:
                                logger.debug(f"Cleaning parameters for tool: {getattr(orig_tool, 'name', 'unknown')}")
                                # Clean the parameters schema - only keep query parameter
                                cleaned_params = self._clean_function_parameters(cleaned_declaration.parameters)
                                cleaned_declaration.parameters = cleaned_params
                                
                                logger.info(f"Successfully cleaned function declaration for tool: {getattr(orig_tool, 'name', 'unknown')}")
                                logger.debug(f"Cleaned declaration: {cleaned_declaration}")
                            else:
                                logger.warning(f"No parameters found in declaration for tool: {getattr(orig_tool, 'name', 'unknown')}")
                            
                            return cleaned_declaration
                            
                        except Exception as e:
                            logger.error(f"Failed to clean declaration for tool {getattr(orig_tool, 'name', 'unknown')}: {e}", exc_info=True)
                            return orig_method()
                    
                    return cleaned_get_declaration
                
                # Replace the method
                tool._get_declaration = create_cleaned_get_declaration(tool, original_get_declaration)
                
                cleaned_tools.append(tool)
                logger.debug(f"Patched _get_declaration method for tool: {getattr(tool, 'name', 'unknown')}")
                
            except Exception as e:
                logger.warning(f"Failed to patch tool {getattr(tool, 'name', 'unknown')}: {e}")
                # Include the original tool anyway
                cleaned_tools.append(tool)
        
        return cleaned_tools
    
    def _clean_function_parameters(self, parameters):
        """Clean function parameters schema for Gemini compatibility."""
        try:
            logger.debug(f"Starting parameter cleaning. Parameters object: {parameters}")
            logger.debug(f"Parameters type: {type(parameters)}")
            logger.debug(f"Parameters has properties: {hasattr(parameters, 'properties')}")
            
            # Access the parameters' properties if they exist
            if hasattr(parameters, 'properties') and parameters.properties:
                logger.debug(f"Found {len(parameters.properties)} properties: {list(parameters.properties.keys())}")
                
                # Only keep the 'query' parameter to avoid schema conflicts
                cleaned_properties = {}
                
                if 'query' in parameters.properties:
                    query_param = parameters.properties['query']
                    logger.debug(f"Found query parameter: {query_param}")
                    cleaned_query = self._clean_single_parameter(query_param)
                    if cleaned_query is not None:
                        cleaned_properties['query'] = cleaned_query
                        logger.info("Successfully cleaned and kept only 'query' parameter")
                    else:
                        logger.warning("Query parameter cleaning returned None")
                else:
                    logger.warning("No 'query' parameter found in tool schema")
                
                logger.debug(f"Cleaned properties: {cleaned_properties}")
                
                # Create new parameters object with only cleaned query parameter
                from copy import deepcopy
                cleaned_params = deepcopy(parameters)
                cleaned_params.properties = cleaned_properties
                
                # Update required fields to only include query
                if hasattr(cleaned_params, 'required'):
                    original_required = cleaned_params.required
                    cleaned_params.required = ['query'] if 'query' in cleaned_properties else []
                    logger.debug(f"Updated required fields from {original_required} to {cleaned_params.required}")
                
                logger.info(f"Parameter cleaning completed successfully. Final parameters: {cleaned_params}")
                return cleaned_params
            else:
                logger.warning(f"No properties found in parameters object: {parameters}")
            
            return parameters
            
        except Exception as e:
            logger.error(f"Error cleaning function parameters: {e}", exc_info=True)
            return parameters
    
    def _clean_single_parameter(self, param_schema):
        """Clean a single parameter schema."""
        try:
            # Convert to dict if it's an object
            if hasattr(param_schema, '__dict__'):
                schema_dict = param_schema.__dict__.copy()
            elif isinstance(param_schema, dict):
                schema_dict = param_schema.copy()
            else:
                return param_schema
            
            # For query parameter, just ensure it's a simple string type
            cleaned_schema = {
                'type': 'string',
                'title': schema_dict.get('title', 'query'),
                'description': schema_dict.get('description', 'Search query')
            }
            
            # Recreate the parameter object with cleaned schema
            if hasattr(param_schema, '__class__'):
                try:
                    return param_schema.__class__(**cleaned_schema)
                except Exception as e:
                    logger.warning(f"Failed to create new parameter instance: {e}")
                    # Fallback: modify the original object
                    for key in list(param_schema.__dict__.keys()):
                        delattr(param_schema, key)
                    for key, value in cleaned_schema.items():
                        setattr(param_schema, key, value)
                    return param_schema
            else:
                return cleaned_schema
            
        except Exception as e:
            logger.warning(f"Error cleaning parameter schema: {e}")
            # Return a safe default string parameter
            safe_schema = {
                'type': 'string',
                'title': 'query',
                'description': 'Search query'
            }
            if hasattr(param_schema, '__class__'):
                try:
                    return param_schema.__class__(**safe_schema)
                except:
                    pass
            return safe_schema


@dataclass
class WorkflowPaths:
    base_dir: Path = Path(__file__).parent
    config_dir: Path = None
    prompts_dir: Path = None
    input_dir: Path = None
    output_dir: Path = None
    workflow_config: Path = None
    prompts_config: Path = None
    gemini_config: Path = None

    def __post_init__(self):
        self.config_dir = self.base_dir / "config"
        self.prompts_dir = self.base_dir / "prompts"
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.workflow_config = self.config_dir / "workflow_rag.yml"
        self.prompts_config = self.prompts_dir / "prompts_rag.yml"
        self.gemini_config = self.config_dir / "gemini_config_rag.yml"

    def ensure_directories(self) -> None:
        for dir_path in [self.config_dir, self.prompts_dir, self.input_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directories exist: {[str(d) for d in [self.config_dir, self.prompts_dir, self.input_dir, self.output_dir]]}")


class ConfigLoader:
    def __init__(self, paths: WorkflowPaths):
        self.paths = paths

    def load_workflow_config(self) -> WorkflowConfig:
        with open(self.paths.workflow_config, 'r') as f:
            data = yaml.safe_load(f)
        config = WorkflowConfig(
            name=data['name'],
            description=data['description'],
            version=data['version'],
            api_config=data['api_config'],
            steps=data.get('steps', []),
            metadata=data.get('metadata', {})
        )
        return config

    def load_prompts_config(self) -> PromptConfig:
        with open(self.paths.prompts_config, 'r') as f:
            data = yaml.safe_load(f)
        config = PromptConfig(
            version=data['version'],
            prompts=data['prompts']
        )
        return config

    def load_llm_config(self) -> dict:
        with open(self.paths.gemini_config, 'r') as f:
            data = yaml.safe_load(f)
        api_key = data.get('api_config', {}).get('api_key')
        if not api_key:
            api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("API key not found in YAML or environment variable.")
        os.environ['GOOGLE_API_KEY'] = api_key
        data['api_config']['api_key'] = api_key
        return data


class RAGWorkflowManager:
    """
    Manages a RAG workflow using Google ADK MCPToolset.
    
    This class provides RAG functionality through Google ADK's tool-based MCP integration.
    """
    
    def __init__(
        self, 
        config_loader: ConfigLoader, 
        allowed_tools: Optional[list[str]] = None
    ):
        """
        Initialize the RAG workflow manager.
        
        Args:
            config_loader: Configuration loader instance
            allowed_tools: List of allowed MCP tools for security filtering
        """
        self.config_loader = config_loader
        self.workflow_config = self.config_loader.load_workflow_config()
        self.prompts_config = self.config_loader.load_prompts_config()
        self.llm_config = self.config_loader.load_llm_config()
        
        # Extract MCP endpoint from workflow config
        self.rag_step = next(
            (s for s in self.workflow_config.steps if s['name'] == "RAGAgent"), None
        )
        if not self.rag_step:
            raise ValueError("No RAGAgent step found in workflow config")
        
        # Get MCP endpoint configuration
        mcp_config = self.rag_step['tools'][0]['config']
        self.mcp_endpoint = mcp_config['mcp_endpoint']
        
        # Initialize the ADK agent with cleaned MCPToolset
        self._init_adk_agent(mcp_config, allowed_tools)
        
        # Initialize the runner (but not the session yet - that's async)
        self._init_runner()
        self.session = None  # Will be created in run() method
        self._cleanup_tasks = []  # Track async tasks for cleanup
        
        logger.info(f"RAGWorkflowManager initialized with cleaned MCPToolset")

    def _init_adk_agent(self, mcp_config: dict, allowed_tools: Optional[list[str]] = None) -> None:
        """Initialize Google ADK agent with cleaned MCPToolset."""
        # Use the actual MCP endpoint directly
        mcp_url = self.mcp_endpoint
        
        logger.info(f"Initializing ADK agent with MCP endpoint: {mcp_url}")
        
        # Default allowed tools for RAG operations
        default_allowed_tools = [
            'get_generative_search_response',
        ]
        
        # Use provided allowed_tools or fallback to defaults
        tool_filter = allowed_tools or default_allowed_tools
        
        # Create the ADK agent with cleaned MCPToolset
        self.adk_agent = LlmAgent(
            model='gemini-2.0-flash',
            name='rag_assistant',
            instruction="""
You are an expert research assistant specializing in Retrieval-Augmented Generation (RAG).

Your primary capabilities:
- Search and retrieve relevant documents from knowledge bases
- Analyze and synthesize information from multiple sources
- Provide accurate, well-sourced answers based on retrieved context
- Cite sources when possible and appropriate

Guidelines:
- Only provide answers based on retrieved context
- Be precise and factual in your responses
- If information is not available in the context, clearly state this
- Maintain a helpful and professional tone
            """,
            tools=[
                CleanedMCPToolset(
                    connection_params=SseServerParams(
                        url=mcp_url,
                        headers={'Accept': 'text/event-stream'},
                    ),
                    tool_filter=tool_filter,
                )
            ],
        )
        
        logger.info("ADK agent with cleaned MCPToolset initialized successfully")

    def _init_runner(self) -> None:
        """Initialize the ADK runner (without session - that's created async)."""
        self.runner = InMemoryRunner(
            agent=self.adk_agent,
            app_name="RAG_Workflow"
        )
        
        logger.info("ADK runner initialized successfully")

    async def _ensure_session(self) -> None:
        """Ensure session is created (async operation)."""
        if self.session is None:
            try:
                self.session = await self.runner.session_service.create_session(
                    app_name="RAG_Workflow",
                    user_id="workflow_user"
                )
                logger.info("ADK session created successfully")
            except Exception as e:
                logger.error(f"Failed to create ADK session: {e}")
                raise

    async def _cleanup_session(self) -> None:
        """Clean up the session and runner resources."""
        if self.session:
            try:
                logger.debug("Cleaning up ADK session...")
                # Try to gracefully close the session if there's a close method
                if hasattr(self.session, 'close'):
                    await self.session.close()
                elif hasattr(self.runner.session_service, 'close_session'):
                    await self.runner.session_service.close_session(self.session.id)
                logger.debug("ADK session cleaned up successfully")
            except Exception as e:
                logger.debug(f"Session cleanup warning (non-critical): {e}")
            finally:
                self.session = None
        
        # Clean up runner resources
        if hasattr(self.runner, 'close'):
            try:
                logger.debug("Cleaning up ADK runner...")
                await self.runner.close()
                logger.debug("ADK runner cleaned up successfully")
            except Exception as e:
                logger.debug(f"Runner cleanup warning (non-critical): {e}")

    async def _cleanup_tasks_gracefully(self) -> None:
        """Clean up any background tasks gracefully."""
        if self._cleanup_tasks:
            logger.debug(f"Cleaning up {len(self._cleanup_tasks)} background tasks...")
            for task in self._cleanup_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass  # Expected when cancelling
                    except Exception as e:
                        logger.debug(f"Task cleanup warning (non-critical): {e}")
            self._cleanup_tasks.clear()

    async def run(self, input_data: dict) -> dict:
        """
        Run the RAG workflow using Google ADK MCPToolset.
        
        Args:
            input_data: Dictionary containing query, system_prompt, and metadata
            
        Returns:
            Dictionary containing the workflow result
        """
        start_time = datetime.now().isoformat()
        import uuid
        session_id = str(uuid.uuid4())
        
        try:
            # Ensure session is created
            await self._ensure_session()
            
            query = input_data.get("query") or input_data.get("prompt")
            if not query:
                raise ValueError("Input must contain a 'query' or 'prompt' key.")

            system_prompt = input_data.get(
                "system_prompt", 
                "You are an expert research assistant. Only answer using retrieved context. Cite sources if possible."
            )

            logger.info(f"Processing query via ADK MCPToolset: {query}")
            
            # Prepare the full prompt with system instructions and user query
            full_prompt = f"""
{system_prompt}

Query: {query}

Please search for and retrieve relevant information to answer this query comprehensively.
"""
            
            # Create content for the ADK runner
            user_content = Content(
                role='user',
                parts=[Part(text=full_prompt)]
            )
            
            # Use the ADK runner to process the query with timeout and proper async handling
            response_text = ""
            try:
                # Add a reasonable timeout to prevent hanging
                async with asyncio.timeout(120):  # 2 minute timeout
                    async for event in self.runner.run_async(
                        user_id="workflow_user",
                        session_id=self.session.id,
                        new_message=user_content
                    ):
                        # Extract text from the final response
                        if event.is_final_response() and event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    response_text += part.text
            except asyncio.TimeoutError:
                logger.warning("RAG workflow timed out after 2 minutes")
                raise
            except Exception as e:
                logger.error(f"Error during RAG workflow execution: {e}")
                raise
            
            logger.debug(f"ADK agent response: {response_text}")

            result = {
                "status": WorkflowStatus.COMPLETED,
                "start_time": start_time,
                "end_time": datetime.now().isoformat(),
                "output": {
                    "response": response_text,
                    "query": query,
                    "method": "adk_toolset_cleaned",
                },
                "session_id": session_id
            }
            logger.info(f"RAG workflow completed successfully using cleaned ADK MCPToolset")
            return result
            
        except Exception as e:
            logger.error(f"RAG workflow failed: {e}", exc_info=True)
            return {
                "status": WorkflowStatus.FAILED,
                "start_time": start_time,
                "end_time": datetime.now().isoformat(),
                "error": str(e),
                "session_id": session_id
            }
        finally:
            # Always clean up resources
            await self._cleanup_gracefully()

    async def _cleanup_gracefully(self) -> None:
        """Perform graceful cleanup of all resources."""
        try:
            logger.debug("Starting graceful cleanup of RAG workflow resources...")
            
            # Clean up tasks first
            await self._cleanup_tasks_gracefully()
            
            # Clean up session and runner
            await self._cleanup_session()
            
            # Give a small delay to allow async resources to fully clean up
            await asyncio.sleep(0.1)
            
            logger.debug("Graceful cleanup completed successfully")
            
        except Exception as e:
            # Suppress specific async cleanup errors that are non-critical
            error_msg = str(e)
            if any(term in error_msg.lower() for term in [
                'generator', 'generatorexit', 'cancel', 'task', 'runtime', 
                'athrow', 'aclose', 'sse', 'event-stream'
            ]):
                logger.debug(f"Suppressed non-critical async cleanup error: {type(e).__name__}")
            else:
                logger.debug(f"Cleanup completed with warnings: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        try:
            await self._cleanup_gracefully()
        except Exception as cleanup_error:
            # Log cleanup errors but don't let them mask the original exception
            logger.debug(f"Context manager cleanup error (suppressed): {cleanup_error}")
        
        return False  # Don't suppress the original exception