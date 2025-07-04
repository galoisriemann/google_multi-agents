"""Loop checker agent for flexible workflows.

This module provides a specialized agent for checking loop termination conditions
in flexible workflow systems.
"""

import logging
from typing import Optional

from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.genai import types

logger = logging.getLogger(__name__)


class FlexibleLoopChecker(BaseAgent):
    """Agent that checks loop termination conditions for flexible workflows.
    
    This agent analyzes the context and determines whether a loop should continue
    or terminate based on configurable keywords and conditions.
    """
    
    def __init__(self, name: str, stop_keyword: str = "STOP"):
        """Initialize the flexible loop checker.
        
        Args:
            name: Name of the checker agent
            stop_keyword: Keyword to stop the loop when found in the last result
        """
        super().__init__(name=name)
        self.stop_keyword = stop_keyword.lower()
        logger.debug(f"Initialized FlexibleLoopChecker '{name}' with stop keyword: '{stop_keyword}'")

    async def _run_async_impl(self, context) -> None:
        """Check if loop should stop based on last result.
        
        Args:
            context: The execution context containing session state
            
        Yields:
            Event indicating whether the loop should continue or stop
        """
        try:
            # Extract last result from context
            last_result = ""
            if hasattr(context, 'session') and context.session and hasattr(context.session, 'state'):
                last_result = context.session.state.get("last_result", "")
            
            # Check termination condition
            should_stop = self.stop_keyword in last_result.lower()
            verdict = "stop" if should_stop else "continue"
            
            logger.debug(f"Loop checker '{self.name}': {verdict} (keyword '{self.stop_keyword}' {'found' if should_stop else 'not found'})")
            
            # Create appropriate event actions
            actions = EventActions(escalate=should_stop)
            
            # Yield the decision event
            yield Event(
                author=self.name,
                content=types.Content(
                    role="assistant", 
                    parts=[types.Part(text=verdict)]
                ),
                actions=actions
            )
            
        except Exception as e:
            logger.error(f"Error in FlexibleLoopChecker '{self.name}': {e}")
            # Default to stop on error to prevent infinite loops
            yield Event(
                author=self.name,
                content=types.Content(
                    role="assistant", 
                    parts=[types.Part(text=f"stop (error: {str(e)})")]
                ),
                actions=EventActions(escalate=True)
            )

    def update_stop_keyword(self, new_keyword: str) -> None:
        """Update the stop keyword for this loop checker.
        
        Args:
            new_keyword: New keyword to use for loop termination
        """
        old_keyword = self.stop_keyword
        self.stop_keyword = new_keyword.lower()
        logger.info(f"Updated stop keyword from '{old_keyword}' to '{new_keyword}' for checker '{self.name}'") 