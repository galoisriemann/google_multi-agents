"""Main FastAPI application for flexible agent workflows.

This module creates the FastAPI application and defines all the REST API endpoints
for interacting with the flexible agent workflow system.
"""

import asyncio
import json
import logging
import tempfile
import time
import uuid
import yaml
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, AsyncGenerator, Tuple
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from ..core.workflow.flexible_workflow_manager import FlexibleWorkflowManager
from ..core.tools.tool_registry import FlexibleToolRegistry
from ..core.config.flexible_config import FlexibleAgentConfig, FlexibleWorkflowConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global workflow manager instance
workflow_manager: Optional[FlexibleWorkflowManager] = None

# Global dictionary to track background tasks for cancellation
background_tasks_tracker = {}


# Pydantic Models for API
class WorkflowRequest(BaseModel):
    """Request model for workflow execution."""
    user_request: str = Field(..., description="The user's request to process")
    prompt: Optional[str] = Field(None, description="Optional custom prompt")
    model: Optional[str] = Field(None, description="Optional model override")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional configuration")


class WorkflowResponse(BaseModel):
    """Response model for workflow execution."""
    id: str = Field(..., description="Workflow execution ID")
    status: str = Field(..., description="Execution status")
    content: Optional[str] = Field(None, description="Workflow output content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    state: Dict[str, Any] = Field(default_factory=dict, description="Workflow state")


class WorkflowStatus(BaseModel):
    """Status model for workflow execution tracking."""
    id: str = Field(..., description="Workflow execution ID")
    status: str = Field(..., description="Current status")
    progress: float = Field(default=0.0, description="Execution progress (0-100)")
    current_agent: Optional[str] = Field(None, description="Currently executing agent")
    executed_agents: List[str] = Field(default_factory=list, description="List of executed agents")
    start_time: Optional[str] = Field(None, description="Workflow start time")
    execution_time: Optional[float] = Field(None, description="Total execution time in seconds")


class AgentConfigResponse(BaseModel):
    """Response model for agent configuration."""
    name: str
    type: str
    model: Optional[str] = None
    description: Optional[str] = None
    tools: List[str] = Field(default_factory=list)


class ToolInfo(BaseModel):
    """Information about available tools."""
    name: str
    description: str


class WorkflowConfigResponse(BaseModel):
    """Response model for workflow configuration."""
    name: str
    description: str
    version: str
    main_agent: str
    agents: List[AgentConfigResponse]
    available_tools: List[ToolInfo]


# In-memory storage for tracking workflows (in production, use Redis or database)
active_workflows: Dict[str, Dict[str, Any]] = {}

# YAML Configuration models
class YamlConfigResponse(BaseModel):
    name: str
    content: str
    is_valid: bool
    error: Optional[str] = None
    last_modified: Optional[str] = None

class ConfigurationSummary(BaseModel):
    workflow: Optional[YamlConfigResponse] = None
    gemini: Optional[YamlConfigResponse] = None
    prompts: Optional[YamlConfigResponse] = None
    total_configs: int = 0
    all_valid: bool = False

# Live streaming models  
class StreamMessage(BaseModel):
    id: str
    timestamp: str
    type: str
    agent_name: Optional[str] = None
    content: str
    metadata: Optional[Dict] = None

# Input file models
class InputFileInfo(BaseModel):
    """Information about an input file."""
    name: str
    size: int
    type: str
    last_modified: str
    path: str

class InputFilesResponse(BaseModel):
    """Response model for listing input files."""
    files: List[InputFileInfo]
    total_count: int
    total_size: int

# Storage for uploaded configurations
uploaded_configs: Dict[str, Dict[str, str]] = {}

def validate_yaml_content(content: str) -> tuple[bool, Optional[str]]:
    """Validate YAML content and return (is_valid, error_message)"""
    try:
        yaml.safe_load(content)
        return True, None
    except yaml.YAMLError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global workflow_manager
    
    try:
        # Initialize workflow manager (will be updated with uploaded configs later)
        logger.info("🔧 Initializing Flexible Workflow Manager...")
        workflow_manager = FlexibleWorkflowManager()
        await workflow_manager.initialize()
        logger.info("✅ Flexible Workflow Manager initialized successfully")
        logger.info("📝 Note: Workflow manager will use uploaded configs when available")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize Flexible Workflow Manager: {e}")
        raise
    finally:
        # Cleanup if needed
        workflow_manager = None
        logger.info("🔄 Flexible Workflow Manager cleaned up")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Flexible Agent Workflow API",
        description="REST API for executing and managing flexible agent workflows",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080", "http://localhost:8081"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Flexible Agent Workflow API",
            "version": "1.0.0",
            "status": "active",
            "endpoints": {
                "execute": "/api/v1/workflow/execute",
                "status": "/api/v1/workflow/status/{workflow_id}",
                "config": "/api/v1/workflow/config",
                "tools": "/api/v1/tools",
                "health": "/api/v1/health"
            }
        }
    
    @app.get("/api/v1/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "workflow_manager_initialized": workflow_manager is not None,
            "active_workflows": len(active_workflows)
        }
    
    @app.get("/api/v1/workflow/config", response_model=WorkflowConfigResponse)
    async def get_workflow_config():
        """Get the current workflow configuration, prioritizing uploaded configs over static files."""
        if not workflow_manager:
            raise HTTPException(status_code=503, detail="Workflow manager not initialized")
        
        try:
            # PRIORITY 1: Use uploaded workflow configuration if available
            if "workflow" in uploaded_configs and uploaded_configs["workflow"].get("is_valid", True):
                logger.info("🔄 Using uploaded workflow configuration")
                config_content = uploaded_configs["workflow"]["content"]
                config_data = yaml.safe_load(config_content)
            else:
                # PRIORITY 2: Fall back to static file configuration
                logger.info("📁 Using static file workflow configuration")
                config_data = workflow_manager.config_loader.load_config()
            
            # Parse agent configurations
            agents = []
            for agent_config in config_data.get("agents", []):
                agents.append(AgentConfigResponse(
                    name=agent_config.get("name", "Unknown"),
                    type=agent_config.get("type", "Unknown"),
                    model=agent_config.get("model"),
                    description=agent_config.get("description"),
                    tools=agent_config.get("tools", [])
                ))
            
            # Get available tools
            tool_names = FlexibleToolRegistry.list_tools()
            tools = [
                ToolInfo(name=name, description=f"Tool: {name}")
                for name in tool_names
            ]
            
            # Log configuration source for debugging
            config_source = "uploaded" if "workflow" in uploaded_configs else "static"
            logger.info(f"📋 Returning {config_source} workflow config with {len(agents)} agents")
            
            return WorkflowConfigResponse(
                name=config_data.get("name", "Flexible Agent Workflow"),
                description=config_data.get("description", ""),
                version=config_data.get("version", "1.0.0"),
                main_agent=config_data.get("main_agent", "MainFlexibleOrchestrator"),
                agents=agents,
                available_tools=tools
            )
            
        except Exception as e:
            logger.error(f"Failed to get workflow config: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get workflow config: {str(e)}")
    
    @app.get("/api/v1/tools", response_model=List[ToolInfo])
    async def get_available_tools():
        """Get list of available tools."""
        tool_names = FlexibleToolRegistry.list_tools()
        return [
            ToolInfo(name=name, description=f"Tool: {name}")
            for name in tool_names
        ]
    
    @app.post("/api/v1/workflow/execute", response_model=WorkflowResponse)
    async def execute_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
        """Execute a workflow with optional custom configurations"""
        return await execute_workflow_with_custom_config(request, background_tasks)
    
    @app.get("/api/v1/workflow/status/{workflow_id}")
    async def get_workflow_status(workflow_id: str):
        """Get the status of a specific workflow execution."""
        if workflow_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow_data = active_workflows[workflow_id]
        
        # Calculate execution time if workflow has started
        execution_time = workflow_data.get("execution_time")
        if not execution_time and workflow_data.get("start_time"):
            try:
                start_time = time.strptime(workflow_data["start_time"], '%Y-%m-%d %H:%M:%S')
                start_timestamp = time.mktime(start_time)
                execution_time = time.time() - start_timestamp
            except:
                execution_time = None
        
        return {
            "id": workflow_id,
            "status": workflow_data.get("status", "unknown"),
            "progress": workflow_data.get("progress", 0.0),
            "current_agent": workflow_data.get("current_agent"),
            "executed_agents": workflow_data.get("executed_agents", []),
            "start_time": workflow_data.get("start_time"),
            "execution_time": execution_time,
            "error": workflow_data.get("error")
        }
    
    @app.get("/api/v1/workflow/result/{workflow_id}")
    async def get_workflow_result(workflow_id: str):
        """Get the result of a completed workflow execution."""
        if workflow_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow_data = active_workflows[workflow_id]
        
        if workflow_data["status"] == "running" or workflow_data["status"] == "initializing":
            raise HTTPException(status_code=202, detail="Workflow still running")
        
        if workflow_data["status"] == "failed":
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": workflow_data.get("error", "Unknown error"),
                "content": None,
                "metadata": {
                    "success": False,
                    "execution_time": workflow_data.get("execution_time")
                }
            }
        
        result = workflow_data.get("result", {})
        
        return {
            "workflow_id": workflow_id,
            "status": workflow_data["status"],
            "content": result.get("content", "No content available"),
            "metadata": result.get("metadata", {}),
            "state": result.get("state", {})
        }
    
    @app.delete("/api/v1/workflow/{workflow_id}")
    async def cancel_workflow(workflow_id: str):
        """Cancel a running workflow."""
        if workflow_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow_data = active_workflows[workflow_id]
        
        if workflow_data["status"] not in ["running", "initializing"]:
            raise HTTPException(status_code=400, detail="Workflow is not running")
        
        # Set cancellation flag - this will be picked up by the status callback
        workflow_data["cancelled"] = True
        logger.info(f"🛑 Cancellation requested for workflow {workflow_id}")
        
        return {"message": "Workflow cancellation requested"}
    
    @app.get("/api/v1/workflows")
    async def list_workflows():
        """List all workflows and their statuses."""
        return {
            "workflows": [
                {
                    "id": wf_id,
                    "status": wf_data["status"],
                    "progress": wf_data["progress"],
                    "start_time": wf_data["start_time"],
                    "execution_time": wf_data["execution_time"]
                }
                for wf_id, wf_data in active_workflows.items()
            ],
            "total": len(active_workflows)
        }
    
    @app.post("/api/v1/config/upload")
    async def upload_config(
        config_type: str = Form(...),
        file: UploadFile = File(...)
    ) -> Dict[str, Any]:
        """Upload and validate a YAML configuration file."""
        try:
            # Validate config type
            valid_types = ["workflow", "gemini", "prompts"]
            if config_type not in valid_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid config type. Must be one of: {valid_types}"
                )
            
            # Read file content
            content = await file.read()
            content_str = content.decode('utf-8')
            
            # Validate YAML syntax
            try:
                yaml.safe_load(content_str)
            except yaml.YAMLError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid YAML syntax: {str(e)}"
                )
            
            # Store configuration
            if config_type not in uploaded_configs:
                uploaded_configs[config_type] = {}
            
            uploaded_configs[config_type] = {
                "content": content_str,
                "filename": file.filename,
                "uploaded_at": datetime.now().isoformat(),
                "is_valid": True
            }
            
            return {
                "message": f"Configuration '{config_type}' uploaded successfully",
                "config_type": config_type,
                "filename": file.filename,
                "is_valid": True
            }
            
        except Exception as e:
            logger.error(f"Error uploading config: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/v1/config/validate")
    async def validate_all_configs() -> Dict[str, Any]:
        """Validate all uploaded configurations and return detailed validation results."""
        try:
            validation_results = {}
            required_configs = ["workflow", "gemini", "prompts"]
            
            for config_type in required_configs:
                if config_type not in uploaded_configs:
                    validation_results[config_type] = {
                        "is_valid": False,
                        "error": f"Missing required configuration: {config_type}",
                        "warnings": []
                    }
                    continue
                
                config_content = uploaded_configs[config_type]["content"]
                
                try:
                    data = yaml.safe_load(config_content)
                    
                    # Type-specific validation
                    if config_type == "workflow":
                        errors, warnings = validate_workflow_config(data)
                    elif config_type == "gemini":
                        errors, warnings = validate_gemini_config(data)
                    elif config_type == "prompts":
                        errors, warnings = validate_prompts_config(data)
                    else:
                        errors, warnings = [], []
                    
                    validation_results[config_type] = {
                        "is_valid": len(errors) == 0,
                        "error": "; ".join(errors) if errors else None,
                        "warnings": warnings
                    }
                    
                except yaml.YAMLError as e:
                    validation_results[config_type] = {
                        "is_valid": False,
                        "error": f"YAML parsing error: {str(e)}",
                        "warnings": []
                    }
            
            all_valid = all(result["is_valid"] for result in validation_results.values())
            
            return {
                "all_valid": all_valid,
                "validation_results": validation_results,
                "total_configs": len(validation_results),
                "valid_configs": sum(1 for r in validation_results.values() if r["is_valid"])
            }
            
        except Exception as e:
            logger.error(f"Error validating configs: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def validate_workflow_config(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate workflow configuration."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ["name", "description", "version", "main_agent", "agents"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate agents
        if "agents" in data and isinstance(data["agents"], list):
            agent_names = []
            valid_agent_types = ["LlmAgent", "SequentialAgent", "ParallelAgent", "LoopAgent"]
            
            for i, agent in enumerate(data["agents"]):
                if not isinstance(agent, dict):
                    errors.append(f"Agent at index {i} must be an object")
                    continue
                    
                # Required agent fields
                for field in ["name", "type", "description"]:
                    if field not in agent:
                        errors.append(f"Agent at index {i} missing required field: {field}")
                
                # Validate agent type
                if "type" in agent and agent["type"] not in valid_agent_types:
                    errors.append(f"Agent at index {i} has invalid type: {agent['type']}")
                
                # Check for duplicate names
                if "name" in agent:
                    if agent["name"] in agent_names:
                        warnings.append(f"Duplicate agent name: {agent['name']}")
                    agent_names.append(agent["name"])
            
            # Validate main_agent exists
            if "main_agent" in data and data["main_agent"] not in agent_names:
                errors.append(f"Main agent '{data['main_agent']}' not found in agents list")
        
        return errors, warnings

    def validate_gemini_config(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate Gemini configuration."""
        errors = []
        warnings = []
        
        if "api_config" not in data:
            errors.append("Missing required field: api_config")
            return errors, warnings
        
        api_config = data["api_config"]
        
        # Required API config fields
        for field in ["provider", "model"]:
            if field not in api_config:
                errors.append(f"Missing required field in api_config: {field}")
        
        # Validate provider
        if "provider" in api_config and api_config["provider"] != "gemini":
            warnings.append(f"Provider is '{api_config['provider']}', expected 'gemini'")
        
        # Validate model
        if "model" in api_config:
            valid_models = ["gemini-1.0-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-2.5-flash"]
            if not any(model in api_config["model"] for model in valid_models):
                warnings.append(f"Model '{api_config['model']}' may not be a valid Gemini model")
        
        return errors, warnings

    def validate_prompts_config(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate prompts configuration."""
        errors = []
        warnings = []
        
        if not isinstance(data, dict):
            errors.append("Prompts configuration must be an object")
            return errors, warnings
        
        # Check for common prompt patterns
        common_agents = ["requirement_analyzer", "architectural_designer", "code_generator"]
        has_prompts = False
        
        for key, value in data.items():
            if isinstance(value, dict):
                has_prompts = True
                
                if "system" not in value and "template" not in value:
                    warnings.append(f"Prompt '{key}' should have either 'system' or 'template' field")
                
                if "template" in value and not isinstance(value["template"], str):
                    errors.append(f"Prompt '{key}' template must be a string")
                
                if "system" in value and not isinstance(value["system"], str):
                    errors.append(f"Prompt '{key}' system message must be a string")
        
        if not has_prompts:
            warnings.append("No prompt configurations found. Consider adding prompts for your agents.")
        
        # Check for missing common agent prompts
        for agent in common_agents:
            if agent not in data:
                warnings.append(f"Missing prompt for common agent: {agent}")
        
        return errors, warnings

    @app.get("/api/v1/config/summary", response_model=ConfigurationSummary)
    async def get_configuration_summary():
        """Get summary of all uploaded configurations"""
        try:
            summary = ConfigurationSummary()
            
            for config_type in ['workflow', 'gemini', 'prompts']:
                if config_type in uploaded_configs:
                    config_data = uploaded_configs[config_type]
                    
                    # Extract name from YAML content if not stored separately
                    config_name = config_data.get('filename', f'{config_type}.yml')
                    try:
                        parsed_yaml = yaml.safe_load(config_data['content'])
                        config_name = parsed_yaml.get('name', config_name)
                    except:
                        pass  # Use filename as fallback
                    
                    setattr(summary, config_type, YamlConfigResponse(
                        name=config_name,
                        content=config_data['content'],
                        is_valid=config_data.get('is_valid', True),
                        error=config_data.get('error'),
                        last_modified=config_data.get('uploaded_at')  # Fix field name mismatch
                    ))
            
            summary.total_configs = len(uploaded_configs)
            summary.all_valid = all(
                config.get('is_valid', True) for config in uploaded_configs.values()
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting configuration summary: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get configuration summary: {str(e)}")

    @app.get("/api/v1/config/{config_type}")
    async def get_yaml_config(config_type: str):
        """Get a specific YAML configuration"""
        try:
            valid_types = ['workflow', 'gemini', 'prompts']
            if config_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid config type. Must be one of: {valid_types}"
                )
            
            if config_type not in uploaded_configs:
                raise HTTPException(
                    status_code=404,
                    detail=f"Configuration {config_type} not found"
                )
            
            config_data = uploaded_configs[config_type]
            return YamlConfigResponse(
                name=config_data['name'],
                content=config_data['content'],
                is_valid=config_data['is_valid'],
                error=config_data.get('error'),
                last_modified=config_data['last_modified']
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting config: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

    @app.get("/api/v1/input-files", response_model=InputFilesResponse)
    async def list_input_files():
        """List all files in the backend input directory."""
        try:
            # Get the absolute path to the backend input directory
            current_file = Path(__file__)
            backend_dir = current_file.parent.parent  # Go up from api/ to backend/
            input_dir = backend_dir / "input"
            
            # Create input directory if it doesn't exist
            input_dir.mkdir(parents=True, exist_ok=True)
            
            files_info = []
            total_size = 0
            
            # List all files in the input directory
            for file_path in input_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    try:
                        stat = file_path.stat()
                        
                        # Determine file type based on extension
                        extension = file_path.suffix.lower()
                        file_type_map = {
                            '.txt': 'text/plain',
                            '.md': 'text/markdown',
                            '.csv': 'text/csv',
                            '.json': 'application/json',
                            '.yml': 'text/yaml',
                            '.yaml': 'text/yaml',
                            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                            '.pdf': 'application/pdf'
                        }
                        file_type = file_type_map.get(extension, 'application/octet-stream')
                        
                        file_info = InputFileInfo(
                            name=file_path.name,
                            size=stat.st_size,
                            type=file_type,
                            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            path=str(file_path.relative_to(backend_dir.parent))  # Relative to project root
                        )
                        
                        files_info.append(file_info)
                        total_size += stat.st_size
                        
                    except OSError as e:
                        logger.warning(f"Could not read file info for {file_path}: {e}")
                        continue
            
            # Sort files by name
            files_info.sort(key=lambda x: x.name.lower())
            
            return InputFilesResponse(
                files=files_info,
                total_count=len(files_info),
                total_size=total_size
            )
            
        except Exception as e:
            logger.error(f"Error listing input files: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to list input files: {str(e)}")

    @app.get("/api/v1/workflow/{workflow_id}/interim-outputs")
    async def get_workflow_interim_outputs(workflow_id: str):
        """Get interim outputs for a workflow."""
        if workflow_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        try:
            workflow_data = active_workflows[workflow_id]
            
            # Try to get incremental output directory from result metadata
            incremental_dir = None
            if "result" in workflow_data and workflow_data["result"]:
                metadata = workflow_data["result"].get("metadata", {})
                incremental_dir_str = metadata.get("incremental_output_dir")
                if incremental_dir_str:
                    incremental_dir = Path(incremental_dir_str)
            
            # If not found in result, try to find by pattern
            if not incremental_dir or not incremental_dir.exists():
                backend_dir = Path(__file__).parent.parent
                output_dir = backend_dir / "output"
                
                # Look for incremental directories matching workflow start time
                start_time = workflow_data.get("start_time", "")
                if start_time:
                    # Convert start time to directory pattern
                    try:
                        dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                        pattern = f"incremental_{dt.strftime('%Y%m%d_%H%M%S')}"
                        potential_dir = output_dir / pattern
                        if potential_dir.exists():
                            incremental_dir = potential_dir
                    except:
                        pass
                
                # Last resort: find the most recent incremental directory
                if not incremental_dir or not incremental_dir.exists():
                    if output_dir.exists():
                        incremental_dirs = [d for d in output_dir.iterdir() 
                                          if d.is_dir() and d.name.startswith("incremental_")]
                        if incremental_dirs:
                            incremental_dir = max(incremental_dirs, key=lambda x: x.stat().st_mtime)
            
            outputs = []
            if incremental_dir and incremental_dir.exists():
                # Read all markdown files in the incremental directory
                for file_path in sorted(incremental_dir.glob("*.md")):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract agent name from filename
                        filename = file_path.name
                        if filename.startswith("00_"):
                            agent_name = "Workflow Metadata"
                        elif filename.startswith("99_"):
                            agent_name = "Final Summary"
                        else:
                            # Extract agent name from pattern like "01_requirementanalyzer.md"
                            parts = filename.split('_', 1)
                            if len(parts) > 1:
                                agent_name = parts[1].replace('.md', '').replace('_', ' ').title()
                            else:
                                agent_name = filename.replace('.md', '')
                        
                        outputs.append({
                            "filename": filename,
                            "agent_name": agent_name,
                            "content": content,
                            "timestamp": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"Could not read interim output file {file_path}: {e}")
            
            return {
                "workflow_id": workflow_id,
                "incremental_dir": str(incremental_dir) if incremental_dir else None,
                "outputs": outputs,
                "total_outputs": len(outputs)
            }
            
        except Exception as e:
            logger.error(f"Error getting interim outputs for workflow {workflow_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get interim outputs: {str(e)}")

    @app.get("/api/v1/workflow/stream/{workflow_id}")
    async def stream_workflow_progress(workflow_id: str):
        """Stream live workflow progress using Server-Sent Events"""
        try:
            if workflow_id not in active_workflows:
                raise HTTPException(status_code=404, detail="Workflow not found")
            
            async def generate_stream():
                """Generate Server-Sent Event stream"""
                last_update_time = None
                message_count = 0
                
                while workflow_id in active_workflows:
                    workflow = active_workflows[workflow_id]
                    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Check if there's a new update
                    workflow_update_time = workflow.get('last_update')
                    
                    if workflow_update_time != last_update_time or workflow['status'] in ['completed', 'failed']:
                        last_update_time = workflow_update_time
                        
                        # Create message based on current workflow state
                        current_agent = workflow.get('current_agent', 'Unknown')
                        progress = workflow.get('progress', 0.0)
                        last_message = workflow.get('last_message', '')
                        status = workflow.get('status', 'unknown')
                        
                        if status == 'running' and current_agent:
                            message = StreamMessage(
                                id=f"msg_{message_count}",
                                timestamp=current_time,
                                type="agent_progress",
                                agent_name=current_agent,
                                content=last_message or f"Processing with {current_agent}...",
                                metadata={
                                    "progress": progress,
                                    "status": "processing"
                                }
                            )
                            
                            yield f"data: {message.model_dump_json()}\n\n"
                            message_count += 1
                        
                        elif status == 'completed':
                            completion_message = StreamMessage(
                                id=f"msg_complete",
                                timestamp=current_time,
                                type="workflow_status",
                                content="Workflow completed successfully!",
                                metadata={
                                    "progress": 100,
                                    "status": "completed"
                                }
                            )
                            yield f"data: {completion_message.model_dump_json()}\n\n"
                            break
                        
                        elif status == 'failed':
                            error_message = StreamMessage(
                                id=f"msg_error",
                                timestamp=current_time,
                                type="workflow_status", 
                                content=f"Workflow failed: {workflow.get('error', 'Unknown error')}",
                                metadata={
                                    "progress": 0,
                                    "status": "failed"
                                }
                            )
                            yield f"data: {error_message.model_dump_json()}\n\n"
                            break
                        
                        elif status == 'cancelled':
                            cancel_message = StreamMessage(
                                id=f"msg_cancelled",
                                timestamp=current_time,
                                type="workflow_status",
                                content="Workflow was cancelled by user",
                                metadata={
                                    "progress": 0,
                                    "status": "cancelled"
                                }
                            )
                            yield f"data: {cancel_message.model_dump_json()}\n\n"
                            break
                    
                    await asyncio.sleep(1)  # Check for updates every second
                
                yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
            
        except Exception as e:
            logger.error(f"Error streaming workflow progress: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to stream workflow progress: {str(e)}")
    
    return app


async def execute_workflow_background(workflow_id: str, user_request: str):
    """Execute workflow in the background and update status."""
    global workflow_manager
    
    try:
        if not workflow_manager:
            raise Exception("Workflow manager not initialized")
        
        # Update status to running (don't set current_agent until actually running)
        active_workflows[workflow_id]["status"] = "running"
        active_workflows[workflow_id]["progress"] = 0.0
        active_workflows[workflow_id]["current_agent"] = None
        active_workflows[workflow_id]["cancelled"] = False
        
        logger.info(f"🚀 Starting workflow execution for ID: {workflow_id}")
        
        # Create status callback to update workflow status in real-time
        def status_callback(agent_name: str, progress: float, message: str = ""):
            """Callback to update workflow status during execution."""
            # Check for cancellation
            if workflow_id in active_workflows and active_workflows[workflow_id].get("cancelled", False):
                raise asyncio.CancelledError("Workflow was cancelled by user")
            
            if workflow_id in active_workflows:
                active_workflows[workflow_id]["current_agent"] = agent_name
                active_workflows[workflow_id]["progress"] = min(100.0, max(0.0, progress))
                active_workflows[workflow_id]["last_message"] = message
                active_workflows[workflow_id]["last_update"] = time.time()
                logger.info(f"📊 Workflow {workflow_id}: {agent_name} - {progress:.1f}% - {message}")
        
        # Execute the workflow with status callback
        result = await workflow_manager.run_workflow(user_request, status_callback=status_callback)
        
        # Check if execution was successful
        if result and result.get("content"):
            # Update to completed status
            active_workflows[workflow_id]["status"] = "completed"
            active_workflows[workflow_id]["progress"] = 100.0
            active_workflows[workflow_id]["current_agent"] = "Completed"
            active_workflows[workflow_id]["result"] = result
            active_workflows[workflow_id]["execution_time"] = result.get("metadata", {}).get("execution_time", 0)
            active_workflows[workflow_id]["executed_agents"] = result.get("metadata", {}).get("agents_executed", ["MainAgent"])
            
            logger.info(f"✅ Workflow {workflow_id} completed successfully")
        else:
            # Handle case where result is empty or invalid
            active_workflows[workflow_id]["status"] = "failed" 
            active_workflows[workflow_id]["error"] = "Workflow execution returned empty result"
            active_workflows[workflow_id]["progress"] = 0.0
            
            logger.error(f"❌ Workflow {workflow_id} failed: Empty result")
        
    except asyncio.CancelledError:
        logger.info(f"🛑 Workflow {workflow_id} was cancelled by user")
        if workflow_id in active_workflows:
            active_workflows[workflow_id]["status"] = "cancelled"
            active_workflows[workflow_id]["progress"] = 0.0
            active_workflows[workflow_id]["current_agent"] = "Cancelled"
    except Exception as e:
        logger.error(f"❌ Workflow {workflow_id} failed: {e}")
        if workflow_id in active_workflows:
            active_workflows[workflow_id]["status"] = "failed"
            active_workflows[workflow_id]["error"] = str(e)
            active_workflows[workflow_id]["progress"] = 0.0


# Modified execute workflow to use uploaded configurations
async def execute_workflow_with_custom_config(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Execute workflow using uploaded configurations if available"""
    try:
        workflow_id = f"workflow_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        # Create workflow entry with proper initialization
        active_workflows[workflow_id] = {
            "id": workflow_id,
            "status": "initializing",
            "request": request.user_request,
            "start_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "progress": 0.0,
            "current_agent": None,
            "executed_agents": [],
            "execution_time": None,
            "result": None,
            "error": None,
            "last_message": "Workflow queued for execution",
            "last_update": time.time(),  # Use timestamp for better comparison
            "metadata": {
                "success": False,
                "message": "Workflow execution started",
                "has_custom_configs": len(uploaded_configs) > 0,
                "config_types": list(uploaded_configs.keys())
            }
        }
        
        # Update global workflow manager with uploaded configurations if available
        global workflow_manager
        if uploaded_configs:
            logger.info(f"✅ Using uploaded configurations: {list(uploaded_configs.keys())}")
            if workflow_manager:
                workflow_manager.update_configurations(uploaded_configs)
            else:
                # Create new workflow manager with uploaded configs
                workflow_manager = FlexibleWorkflowManager(uploaded_configs=uploaded_configs)
        
        # Execute the workflow in background
        background_tasks.add_task(execute_workflow_background, workflow_id, request.user_request)
        
        logger.info(f"Started workflow {workflow_id} for request: {request.user_request[:50]}...")
        
        return WorkflowResponse(
            id=workflow_id,
            status="started",
            content=None,
            metadata={
                "message": f"Workflow execution started with {'custom' if uploaded_configs else 'default'} configurations",
                "has_custom_configs": len(uploaded_configs) > 0,
                "config_types": list(uploaded_configs.keys())
            },
            state={}
        )
        
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute workflow: {str(e)}")


# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 