"""FastAPI module for flexible agent workflows.

This module provides REST API endpoints for interacting with the flexible agent
workflow system through a web interface.
"""

from .main import create_app

__all__ = ["create_app"] 