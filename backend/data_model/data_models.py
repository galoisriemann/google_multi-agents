"""
Data models for the Workflow application.
"""

import json
import enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

class WorkflowStatus(enum.Enum):
    """Workflow status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class EventType(enum.Enum):
    """Event type enum."""
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"

@dataclass
class APIConfig:
    """API configuration."""
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 60

@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 2000
    api_config: Optional[APIConfig] = None
    backend: Optional[str] = None
    step_models: Dict[int, str] = field(default_factory=dict)

@dataclass
class WorkflowConfig:
    """Workflow configuration."""
    name: str
    description: str
    version: str
    api_config: Dict[str, Any]
    steps: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PromptConfig:
    """Prompt configuration for workflow steps."""
    version: str
    prompts: Dict[str, str] = field(default_factory=dict)

@dataclass
class WorkflowInput:
    """Workflow input data."""
    prompt: str
    files: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowOutput:
    """Workflow output data."""
    status: WorkflowStatus
    steps: List[Dict[str, Any]] = field(default_factory=list)
    final_output: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class WorkflowEvent:
    """Workflow event."""
    workflow_id: str
    event_type: EventType
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON string.
        
        Returns:
            JSON string.
        """
        return json.dumps({
            "workflow_id": self.workflow_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "data": self.data
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WorkflowEvent':
        """Create from JSON string.
        
        Args:
            json_str: JSON string.
            
        Returns:
            WorkflowEvent instance.
        """
        data = json.loads(json_str)
        return cls(
            workflow_id=data["workflow_id"],
            event_type=EventType(data["event_type"]),
            timestamp=data["timestamp"],
            data=data["data"]
        )

@dataclass
class WorkflowStep:
    """Workflow step."""
    step_index: int
    prompt: str
    response: Optional[str] = None
    files: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    model: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation for serialization.
        
        Returns:
            Dictionary representation of the workflow step.
        """
        return {
            "step_index": self.step_index,
            "prompt": self.prompt,
            "response": self.response,
            "files": self.files,
            "metadata": self.metadata,
            "status": self.status.value if self.status else None,
            "model": self.model,
            "tools_used": self.tools_used
        }

