"""
Constants used throughout the application.
"""

# Default values
DEFAULT_MODEL = "qwq:latest"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 300  # seconds
DEFAULT_RESEARCH_TOPIC = "quantum computing"

# Tool call markers
TOOL_CALL_START = "<<TOOL_CALL>>"
TOOL_CALL_END = "<<TOOL_CALL_END>>"
TOOL_CALL_RESULT = "<<TOOL_RESULT>>"

# Tool parameter markers
TOOL_NAME_PREFIX = "tool_name:"
TOOL_PARAM_PREFIX = "parameters:"
