"""Configuration models for flexible agent workflows.

This module defines Pydantic models for configuring flexible agent workflows,
including individual agent configurations and overall workflow settings.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FlexibleAgentConfig(BaseModel):
    """Configuration model for individual flexible agents.
    
    Attributes:
        name: Unique name identifier for the agent
        type: Type of agent (LlmAgent, SequentialAgent, ParallelAgent, LoopAgent)
        model: Optional model name for LLM agents
        description: Optional description of the agent's purpose
        instruction: Direct instruction text for the agent
        prompt_key: Key to load prompt from prompts configuration
        input_key: Filename of single input document to inject as context
        input_keys: List of input document filenames to inject as context
        tools: List of tool names available to the agent
        output_key: Key for storing agent output
        sub_agents: List of sub-agent names for composite agents
        max_iterations: Maximum iterations for loop agents
        parameters: Additional parameters for agent configuration
        extra: Extra configuration fields
    """
    name: str
    type: str = Field(..., pattern="^(LlmAgent|SequentialAgent|ParallelAgent|LoopAgent)$")
    model: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    prompt_key: Optional[str] = None
    input_key: Optional[str] = None
    input_keys: Optional[List[str]] = None
    tools: List[str] = Field(default_factory=list)
    output_key: Optional[str] = None
    sub_agents: List[str] = Field(default_factory=list)
    max_iterations: Optional[int] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""
        extra = "allow"


class FlexibleWorkflowConfig(BaseModel):
    """Configuration model for the entire flexible workflow.
    
    Attributes:
        name: Name of the workflow
        description: Description of the workflow's purpose
        version: Version identifier for the workflow
        main_agent: Name of the main agent to execute
        agents: List of agent configurations
    """
    name: str
    description: str
    version: str
    main_agent: str
    agents: List[FlexibleAgentConfig]

    class Config:
        """Pydantic configuration."""
        extra = "allow" 