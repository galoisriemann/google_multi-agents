"""Agents module for flexible workflow systems.

This module provides agent-related functionality including factories,
loop checkers, and other specialized agents.
"""

from .flexible_agent_factory import FlexibleAgentFactory, FLEXIBLE_AGENT_CLASSES
from .flexible_loop_checker import FlexibleLoopChecker

__all__ = [
    "FlexibleAgentFactory",
    "FlexibleLoopChecker", 
    "FLEXIBLE_AGENT_CLASSES"
] 