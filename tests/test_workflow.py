"""Tests for the workflow system."""
import os
import pytest
from pathlib import Path
from typing import Dict, Any

from backend.data_model.data_models import (
    WorkflowConfig,
    WorkflowStep,
    WorkflowInput,
    WorkflowOutput,
    WorkflowStatus,
    PromptConfig,
)
from backend.main import setup_workflow, process_input


@pytest.fixture
def workflow_config() -> WorkflowConfig:
    """Create a test workflow configuration."""
    return WorkflowConfig(
        name="Test Workflow",
        description="Test workflow for unit tests",
        version="1.0.0",
        steps=[
            WorkflowStep(
                name="TestStep",
                description="Test step",
                agent_type="TestAgent",
                config={},
            )
        ],
        metadata={"test": True},
    )


@pytest.fixture
def prompt_config() -> PromptConfig:
    """Create a test prompt configuration."""
    return PromptConfig(
        initial_prompt="Test initial prompt",
        chain_prompt_templates=["Test template"],
        version="1.0.0",
        prompts={"test": "Test prompt"},
        metadata={"test": True},
    )


@pytest.fixture
def workflow_input() -> WorkflowInput:
    """Create a test workflow input."""
    return WorkflowInput(
        prompt="Test input prompt",
        files={"test.py": "print('Hello, World!')"},
        metadata={"test": True},
    )


@pytest.mark.asyncio
async def test_workflow_setup(workflow_config: WorkflowConfig) -> None:
    """Test workflow setup."""
    workflow = await setup_workflow(workflow_config)
    assert workflow is not None
    assert workflow.name == workflow_config.name
    assert len(workflow.steps) == len(workflow_config.steps)


@pytest.mark.asyncio
async def test_workflow_execution(
    workflow_config: WorkflowConfig,
    prompt_config: PromptConfig,
    workflow_input: WorkflowInput,
) -> None:
    """Test workflow execution."""
    workflow = await setup_workflow(workflow_config)
    output = await process_input(workflow, workflow_input, prompt_config)
    
    assert output is not None
    assert isinstance(output, WorkflowOutput)
    assert output.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]
    assert len(output.steps) == len(workflow_config.steps)


@pytest.mark.asyncio
async def test_workflow_error_handling(
    workflow_config: WorkflowConfig,
    prompt_config: PromptConfig,
) -> None:
    """Test workflow error handling."""
    workflow = await setup_workflow(workflow_config)
    invalid_input = WorkflowInput(
        prompt="",  # Empty prompt should trigger an error
        files={},
        metadata={},
    )
    
    output = await process_input(workflow, invalid_input, prompt_config)
    assert output is not None
    assert output.status == WorkflowStatus.FAILED
    assert output.error is not None


if __name__ == "__main__":
    pytest.main([__file__]) 