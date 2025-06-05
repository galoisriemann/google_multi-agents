"""Tests for the Gemini LLM provider."""
import os
import pytest
from typing import Dict, Any

from backend.data_model.data_models import LLMConfig
from backend.llm_providers.gemini_provider import GeminiProvider


@pytest.fixture
def llm_config() -> LLMConfig:
    """Create a test LLM configuration."""
    return LLMConfig(
        model_name="gemini-pro",
        temperature=0.7,
        max_tokens=1000,
        top_p=0.95,
        top_k=40,
        stop_sequences=[],
        metadata={"test": True},
    )


@pytest.fixture
def gemini_provider(llm_config: LLMConfig) -> GeminiProvider:
    """Create a test Gemini provider instance."""
    return GeminiProvider(llm_config)


@pytest.mark.asyncio
async def test_gemini_provider_initialization(llm_config: LLMConfig) -> None:
    """Test Gemini provider initialization."""
    provider = GeminiProvider(llm_config)
    assert provider is not None
    assert provider.config == llm_config


@pytest.mark.asyncio
async def test_gemini_provider_generate(gemini_provider: GeminiProvider) -> None:
    """Test text generation with Gemini provider."""
    prompt = "Write a simple Python function that adds two numbers."
    response = await gemini_provider.generate(prompt)
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_gemini_provider_error_handling(gemini_provider: GeminiProvider) -> None:
    """Test error handling in Gemini provider."""
    with pytest.raises(Exception):
        await gemini_provider.generate("")  # Empty prompt should raise an error


@pytest.mark.asyncio
async def test_gemini_provider_config_validation() -> None:
    """Test configuration validation in Gemini provider."""
    invalid_config = LLMConfig(
        model_name="invalid-model",
        temperature=2.0,  # Invalid temperature
        max_tokens=-1,  # Invalid max tokens
        top_p=1.5,  # Invalid top_p
        top_k=-1,  # Invalid top_k
        stop_sequences=[],
        metadata={},
    )
    
    with pytest.raises(ValueError):
        GeminiProvider(invalid_config)


if __name__ == "__main__":
    pytest.main([__file__]) 