import os
import sys
import yaml
import asyncio

# Add project root to Python path for direct execution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search  # Built-in ADK tool
from google.genai import types

from backend.tools.deep_research_tool import rag_tool


# ---- CONFIG LOADING ----

WORKFLOW_CONFIG_PATH = "backend/config/workflow_deepresearch.yml"

def load_workflow_config(path: str) -> dict:
    """Load workflow configuration from YAML file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_config_value(config: dict, key_path: str, default=None):
    """Get nested configuration value using dot notation (e.g. 'api_config.model')."""
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value

def validate_config(config: dict):
    """Validate that required configuration values are present."""
    required_keys = [
        "api_config.model",
        "app_config.app_name",
        "mcp_config.rag_mcp_endpoint",
        "gemini_config.api_key"
    ]
    
    missing_keys = []
    for key_path in required_keys:
        if get_config_value(config, key_path) is None:
            missing_keys.append(key_path)
    
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")

# Load configuration
workflow_config = load_workflow_config(WORKFLOW_CONFIG_PATH)

# Validate configuration
validate_config(workflow_config)

# Extract configuration values
MODEL_ID = get_config_value(workflow_config, "api_config.model")
APP_NAME = get_config_value(workflow_config, "app_config.app_name")
USER_ID = get_config_value(workflow_config, "app_config.user_id")
SESSION_ID = get_config_value(workflow_config, "app_config.session_id")
RAG_MCP_ENDPOINT = get_config_value(workflow_config, "mcp_config.rag_mcp_endpoint")
API_KEY = get_config_value(workflow_config, "gemini_config.api_key")

# Set Google API key as environment variable (ADK expects this)
if API_KEY:
    os.environ['GOOGLE_API_KEY'] = API_KEY

# Extract Gemini configuration
gemini_config = workflow_config.get("gemini_config", {})

# Extract agent configuration
agent_config = get_config_value(workflow_config, "mcp_config.adk_toolset.agent", {})
AGENT_NAME = agent_config.get("name", "researcher_agent")
AGENT_DESCRIPTION = agent_config.get("description", "Researcher Agent for comprehensive research")

# Load prompts configuration for agent instruction
def load_prompts_config():
    import yaml
    prompts_path = "backend/config/prompts_deepresearch.yml"
    try:
        with open(prompts_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception:
        return {}

prompts_config = load_prompts_config()
AGENT_INSTRUCTION = prompts_config.get('agent_instructions', {}).get('researcher_agent', 
                   prompts_config.get('agent_instructions', {}).get('deep_research_agent', 
                   "Use tools to perform research."))

# Tool configuration
def get_enabled_tools():
    """Get list of enabled tools based on configuration."""
    tools = []
    tool_config = agent_config.get("tools", {})
    
    # Add Google Search tool if enabled
    if tool_config.get("google_search", {}).get("enabled", True):
        tools.append(google_search)
        print(f"✅ Added Google Search tool")
    
    # Add RAG tool if enabled  
    if tool_config.get("rag_tool", {}).get("enabled", True):
        tools.append(rag_tool)
        print(f"✅ Added RAG tool")
    
    if not tools:
        print("⚠️ No tools enabled - agent will have no tools")
    
    return tools

# ---- AGENT WRAPPER ----

class DeepResearchAgent:
    """Wrapper for the ADK Agent that handles configuration and session management."""
    
    def __init__(self):
        self.config = workflow_config
        self.runner = None
        self.session = None
        
    async def _init_runner(self):
        """Initialize the ADK runner and session with configuration."""
        if self.runner is not None:
            return  # Already initialized
            
        # Create agent with tools (API key is set via environment variable)
        enabled_tools = get_enabled_tools()
        
        print(f"\n🔧 Agent Configuration:")
        print(f"   Name: {AGENT_NAME}")
        print(f"   Model: {MODEL_ID}")
        print(f"   Description: {AGENT_DESCRIPTION}")
        print(f"   Tools: {len(enabled_tools)} enabled")
        
        # Try to enable grounding by using model with search capabilities
        model_with_search = f"{MODEL_ID}"  # Base model
        
        agent = Agent(
            name=AGENT_NAME,
            model=model_with_search,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            tools=enabled_tools
        )
        
        # Setup runner 
        self.runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
        
        # Create session with initial state containing our configuration
        initial_state = {
            "workflow_config": self.config,
            "deep_research_config": self.config.get("deep_research_config", {}),
            "gemini_config": self.config.get("gemini_config", {}),
            "rag_mcp_endpoint": RAG_MCP_ENDPOINT
        }
        
        # Create session with configuration in initial state
        self.session = await self.runner.session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
            state=initial_state
        )

    async def query_async(self, query: str) -> str:
        """Query the agent asynchronously."""
        await self._init_runner()
        
        # Create very direct prompt that forces immediate action
        enhanced_prompt = f"""
{query}

Write a comprehensive markdown research report RIGHT NOW using current search data.

# Market Research Report: {query.replace('Create a brief market analysis of the ', '').replace('market in the US', 'Market in the US')}

## Executive Summary
[Write actual findings with real numbers from search results]

## Market Size and Growth
[Include specific dollar amounts and growth percentages]

## Key Companies
[List real company names with their market positions]

## Current Trends
[Detail current market trends with supporting data]

## Regulatory Landscape
[Describe actual regulations and policies]

## Future Outlook
[Provide forecasts with specific timeframes]

## Sources
[Cite the search sources used]

Fill each section with REAL DATA from search results. Do not write placeholders or plans.
"""
        
        content = types.Content(role='user', parts=[types.Part(text=enhanced_prompt)])
        
        # Run the agent and collect events
        events = self.runner.run_async(
            user_id=self.session.user_id,
            session_id=self.session.id,
            new_message=content
        )
        
        # Process events and capture tool usage information
        final_response = None
        tool_usage_info = []
        search_sources = []
        deep_research_data = None
        
        print("\n" + "="*80)
        print("🔍 DEEP RESEARCH TOOL USAGE TRACKING")
        print("="*80)
        
        async for event in events:
            print(f"🔄 Processing event: {type(event).__name__}")
            
            # Check for function calls (deep research tool)
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            tool_name = part.function_call.name
                            tool_info = f"🛠️  Tool Called: {tool_name}"
                            if hasattr(part.function_call, 'args'):
                                args = part.function_call.args
                                tool_info += f"\n   Arguments: {args}"
                                print(f"✅ {tool_info}")
                            tool_usage_info.append(tool_info)
                            
                        elif hasattr(part, 'function_response') and part.function_response:
                            response_name = part.function_response.name
                            response_info = f"📝 Tool Response: {response_name}"
                            tool_usage_info.append(response_info)
                            print(f"✅ {response_info}")
                            
                            # If this is the RAG tool response, capture the data
                            if response_name in ["rag_tool", "deep_research_tool"]:
                                try:
                                    response_content = part.function_response.response
                                    if hasattr(response_content, 'output'):
                                        deep_research_data = response_content.output
                                    elif isinstance(response_content, dict):
                                        deep_research_data = response_content
                                    print(f"📊 Deep research data captured")
                                except Exception as e:
                                    print(f"⚠️ Could not parse deep research data: {e}")
                            
                        elif hasattr(part, 'text') and part.text:
                            print(f"📝 Text part found: {len(part.text)} characters")
                            print(f"    First 200 chars: {part.text[:200]}")
                            final_response = part.text  # Always update with latest text

            # Extract grounding metadata (Google Search results) - backup method
            if hasattr(event, 'grounding_metadata') and event.grounding_metadata:
                if hasattr(event.grounding_metadata, 'grounding_chunks') and event.grounding_metadata.grounding_chunks:
                    print(f"🌐 Found {len(event.grounding_metadata.grounding_chunks)} grounding chunks (Google Search results)")
                    for chunk in event.grounding_metadata.grounding_chunks:
                        if hasattr(chunk, 'web') and chunk.web:
                            web_info = {
                                'title': getattr(chunk.web, 'title', 'N/A'),
                                'domain': getattr(chunk.web, 'domain', 'N/A'),
                                'url': getattr(chunk.web, 'uri', 'N/A')
                            }
                            search_sources.append(web_info)
                            print(f"   📄 {web_info['title']} - {web_info['domain']}")
                    
                    if event.grounding_metadata.grounding_chunks:
                        tool_usage_info.append(f"🔍 Google Search: Found {len(event.grounding_metadata.grounding_chunks)} web sources")
            
            # Check for different types of responses
            if hasattr(event, 'role') and event.role == 'model':
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                print(f"🤖 Model response: {len(part.text)} characters")
                                final_response = part.text
            
            # Check for final response
            if hasattr(event, 'is_final_response') and event.is_final_response():
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts') and event.content.parts:
                    final_response = event.content.parts[0].text
                print("🏁 Final response detected")
                break
        
        print("="*80)
        print(f"🛠️  Tool Usage Detected: {len(tool_usage_info)} instances")
        print(f"🌐 Web Sources Found: {len(search_sources)} sources")
        
        # Create comprehensive response with all information
        if deep_research_data:
            # Extract detailed information from deep research
            sub_questions = deep_research_data.get('sub_questions', [])
            rag_results = deep_research_data.get('rag_results', [])
            search_results = deep_research_data.get('search_results', [])
            config_used = deep_research_data.get('config_used', {})
            
            # Count successful results
            successful_rag = len([r for r in rag_results if r.get('method') != 'rag_error'])
            successful_search = len([r for r in search_results if r.get('method') != 'search_error'])
            
            # Create detailed citations
            citations_section = f"""
🔬 **DEEP RESEARCH METHODOLOGY**
Research Method: {config_used.get('method', 'hybrid_rag_and_search')}
Query Decomposition: {len(sub_questions)} sub-questions generated
RAG System Queries: {successful_rag}/{len(rag_results)} successful
Current Research Queries: {successful_search}/{len(search_results)} successful
Total Sources Consulted: {sum(len(r.get('sources', [])) for r in rag_results + search_results)}

📋 **SUB-QUESTIONS RESEARCHED:**
"""
            for i, sq in enumerate(sub_questions, 1):
                citations_section += f"{i}. {sq}\n"
            
            # Add RAG sources
            if rag_results:
                citations_section += f"\n📚 **SPECIALIZED KNOWLEDGE SOURCES (RAG System):**\n"
                for i, result in enumerate(rag_results, 1):
                    if result.get('method') != 'rag_error':
                        citations_section += f"{i}. Query: {result['sub_query'][:60]}...\n"
                        if result.get('sources'):
                            for source in result['sources'][:2]:  # Show first 2 sources
                                citations_section += f"   Source: {source}\n"
                        citations_section += f"   Method: {result.get('method', 'unknown')}\n\n"
            
            # Add search sources  
            if search_results:
                citations_section += f"\n🌐 **CURRENT INFORMATION SOURCES:**\n"
                for i, result in enumerate(search_results, 1):
                    if result.get('method') != 'search_error':
                        citations_section += f"{i}. Query: {result['sub_query'][:60]}...\n"
                        if result.get('sources'):
                            for source in result['sources']:
                                citations_section += f"   Source: {source}\n"
                        citations_section += f"   Method: {result.get('method', 'unknown')}\n\n"
            
            response_with_citations = f"""
📊 **COMPREHENSIVE RESEARCH REPORT**
{citations_section}
📄 **SYNTHESIZED RESEARCH RESULTS:**
{final_response or deep_research_data.get('synthesized_answer', 'No response received')}

💡 **Note:** This research combines specialized knowledge from a curated RAG system with current information research. All sub-questions and their sources are logged in `data/logs/deep_research_[timestamp].log` for authenticity verification.

🗂️ **Research Data Available:** Sub-questions, RAG responses, search responses, and synthesis process are all logged for transparency and verification.
"""
        
        elif tool_usage_info or search_sources:
            # If we have a good final response with search results, return it directly
            if final_response and len(final_response) > 1000 and search_sources:
                print(f"✅ Returning agent response directly (length: {len(final_response)} chars)")
                return final_response
            
            # Fallback for other tool usage
            citations_section = ""
            
            if tool_usage_info:
                citations_section += f"\n🔍 **TOOL USAGE DETAILS:**\n"
                for info in tool_usage_info:
                    citations_section += f"• {info}\n"
            
            if search_sources:
                citations_section += f"\n📚 **WEB SOURCES CONSULTED:**\n"
                for i, source in enumerate(search_sources, 1):
                    citations_section += f"{i}. **{source['title']}**\n"
                    citations_section += f"   Domain: {source['domain']}\n"
                    if source['url'] != 'N/A':
                        citations_section += f"   URL: {source['url']}\n"
                    citations_section += "\n"
                    
            response_with_citations = f"""
📊 **RESEARCH SUMMARY**  
Research Method: Tool-based research
Tool Invocations: {len(tool_usage_info)} detected
Web Sources: {len(search_sources)} consulted
{citations_section}
📄 **RESEARCH RESULTS:**
{final_response or "No response received from agent"}

💡 **Note:** This research was conducted using available tools. Check logs for detailed information.
"""
        else:
            response_with_citations = f"""
⚠️  **NO TOOL USAGE DETECTED**
This response may not include specialized research data.

📄 **AGENT RESPONSE:**
{final_response or "No response received from agent"}

💡 **Note:** No tool usage or specialized research detected. Response may be based on general knowledge only.
"""
        
        return response_with_citations

    def query(self, query: str) -> str:
        """Query the agent synchronously."""
        return asyncio.run(self.query_async(query))

# ---- AGENT INTERACTION FUNCTIONS ----

def call_agent(query: str) -> str:
    """Synchronous wrapper for agent interaction."""
    research_agent = DeepResearchAgent()
    return research_agent.query(query)

async def call_agent_async(query: str) -> str:
    """Asynchronous agent interaction."""
    research_agent = DeepResearchAgent()
    return await research_agent.query_async(query)

def get_workflow_config() -> dict:
    """Get the loaded workflow configuration."""
    return workflow_config

if __name__ == "__main__":
    # Example usage
    query = "Can you create me a market research report on the market for SD-IRAs in the US?"
    
    # Print configuration summary
    print(f"Configuration loaded from: {WORKFLOW_CONFIG_PATH}")
    print(f"Model: {MODEL_ID}")
    print(f"RAG MCP Endpoint: {RAG_MCP_ENDPOINT}")
    print(f"Agent: {AGENT_NAME}")
    print(f"API Key configured: {'Yes' if API_KEY else 'No'}")
    print(f"GOOGLE_API_KEY env var set: {'Yes' if os.environ.get('GOOGLE_API_KEY') else 'No'}")
    
    # Print tool configuration
    tool_config = agent_config.get("tools", {})
    print(f"Tool Configuration:")
    print(f"  Google Search: {'Enabled' if tool_config.get('google_search', {}).get('enabled', True) else 'Disabled'}")
    print(f"  RAG Tool: {'Enabled' if tool_config.get('rag_tool', {}).get('enabled', True) else 'Disabled'}")
    print("-" * 50)
    
    try:
        response = call_agent(query)
        print("Agent Response:", response)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()