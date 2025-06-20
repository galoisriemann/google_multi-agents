import os
import sys
import yaml
import asyncio
from datetime import datetime
from pathlib import Path

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

# Get the directory of this script to build absolute paths
SCRIPT_DIR = Path(__file__).parent
WORKFLOW_CONFIG_PATH = SCRIPT_DIR / "config" / "deepresearch" / "workflow_deepresearch.yml"

def load_workflow_config(path: str | Path) -> dict:
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
        "core_config.model",
        "app_config.app_name",
        "mcp_config.rag_mcp_endpoint",
        "core_config.api_key"
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

# Extract configuration values - updated for new structure
MODEL_ID = get_config_value(workflow_config, "core_config.model")
API_KEY = get_config_value(workflow_config, "core_config.api_key")
TEMPERATURE = get_config_value(workflow_config, "core_config.temperature", 0.3)
MAX_TOKENS = get_config_value(workflow_config, "core_config.max_tokens", 8000)
TIMEOUT = get_config_value(workflow_config, "core_config.timeout", 60)

APP_NAME = get_config_value(workflow_config, "app_config.app_name")
USER_ID = get_config_value(workflow_config, "app_config.user_id")
SESSION_ID = get_config_value(workflow_config, "app_config.session_id")
RAG_MCP_ENDPOINT = get_config_value(workflow_config, "mcp_config.rag_mcp_endpoint")

# Set Google API key as environment variable (ADK expects this)
if API_KEY:
    os.environ['GOOGLE_API_KEY'] = API_KEY

# Extract agent configuration
agent_config = get_config_value(workflow_config, "mcp_config.adk_toolset.agent", {})
AGENT_NAME = agent_config.get("name", "researcher_agent")
AGENT_DESCRIPTION = agent_config.get("description", "Researcher Agent for comprehensive research")

# Load prompts configuration for agent instruction
def load_prompts_config():
    """Load prompts configuration from YAML file.
    
    Returns:
        dict: Loaded prompts configuration
        
    Raises:
        FileNotFoundError: If prompts file is not found
        yaml.YAMLError: If YAML parsing fails
    """
    import yaml
    # Use absolute path based on script directory
    prompts_path = SCRIPT_DIR / "prompts" / "deepresearch" / "prompts_deepresearch.yml"
    try:
        with open(prompts_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"⚠️ Prompts file not found at {prompts_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"⚠️ Error parsing prompts YAML: {e}")
        return {}

prompts_config = load_prompts_config()
AGENT_INSTRUCTION = prompts_config.get('agent_instructions', {}).get('researcher_agent', 
                   prompts_config.get('agent_instructions', {}).get('deep_research_agent', 
                   "Use tools to perform research."))

def get_prompt_template(template_name: str, category: str = None) -> str:
    """Get a specific prompt template from the loaded configuration.
    
    Args:
        template_name: Name of the template to retrieve
        category: Category under which the template is organized
        
    Returns:
        str: The prompt template, or empty string if not found
    """
    if category:
        return prompts_config.get(category, {}).get(template_name, "")
    
    # Search across all categories if no category specified
    for cat_name, cat_data in prompts_config.items():
        if isinstance(cat_data, dict) and template_name in cat_data:
            return cat_data[template_name]
    
    return ""

def build_enhanced_prompt(query: str, template_type: str = "market_research") -> str:
    """Build an enhanced prompt using templates from configuration.
    
    Args:
        query: The original research query
        template_type: Type of template to use ("market_research" or "general_research")
        
    Returns:
        str: Enhanced prompt ready for the agent
    """
    template_key = f"{template_type}_template"
    template = get_prompt_template(template_key, "query_enhancement")
    
    if not template:
        # Fallback to general template if specific one not found
        template = get_prompt_template("general_research_template", "query_enhancement")
    
    if not template:
        # Final fallback to basic enhancement
        return f"{query}\n\nProvide a comprehensive research response with supporting data and sources."
    
    # Generate report title for market research
    if template_type == "market_research":
        report_title = query.replace('Create a brief market analysis of the ', '').replace('market in the US', 'Market in the US')
        return template.format(query=query, report_title=report_title)
    else:
        return template.format(query=query)

def build_response_with_citations(final_response: str, deep_research_data: dict = None, 
                                tool_usage_info: list = None, search_sources: list = None,
                                query: str = "", model_id: str = "") -> str:
    """Build a comprehensive response with citations using templates from configuration.
    
    Args:
        final_response: The main response content
        deep_research_data: Data from deep research tool if available
        tool_usage_info: List of tool usage information
        search_sources: List of search sources found
        query: Original query
        model_id: Model identifier used
        
    Returns:
        str: Formatted response with citations and methodology
    """
    if deep_research_data:
        # Use deep research response template
        template = get_prompt_template("deep_research_response_template", "response_formatting")
        
        # Build citations section using deep research methodology template
        methodology_template = get_prompt_template("deep_research_methodology_template", "response_formatting")
        
        sub_questions = deep_research_data.get('sub_questions', [])
        rag_results = deep_research_data.get('rag_results', [])
        search_results = deep_research_data.get('search_results', [])
        config_used = deep_research_data.get('config_used', {})
        
        successful_rag = len([r for r in rag_results if r.get('method') != 'rag_error'])
        successful_search = len([r for r in search_results if r.get('method') != 'search_error'])
        total_sources = sum(len(r.get('sources', [])) for r in rag_results + search_results)
        
        sub_questions_list = "\n".join(f"{i}. {sq}" for i, sq in enumerate(sub_questions, 1))
        
        if methodology_template:
            citations_section = methodology_template.format(
                research_method=config_used.get('method', 'hybrid_rag_and_search'),
                sub_questions_count=len(sub_questions),
                successful_rag=successful_rag,
                total_rag=len(rag_results),
                successful_search=successful_search,
                total_search=len(search_results),
                total_sources=total_sources,
                sub_questions_list=sub_questions_list
            )
        else:
            citations_section = f"Deep research completed with {len(sub_questions)} sub-questions"
        
        # Add RAG and search sources
        if rag_results:
            citations_section += f"\n\n📚 **SPECIALIZED KNOWLEDGE SOURCES (RAG System):**\n"
            for i, result in enumerate(rag_results, 1):
                if result.get('method') != 'rag_error':
                    citations_section += f"{i}. Query: {result['sub_query'][:60]}...\n"
                    if result.get('sources'):
                        for source in result['sources'][:2]:
                            citations_section += f"   Source: {source}\n"
                    citations_section += f"   Method: {result.get('method', 'unknown')}\n\n"
        
        if search_results:
            citations_section += f"\n🌐 **CURRENT INFORMATION SOURCES:**\n"
            for i, result in enumerate(search_results, 1):
                if result.get('method') != 'search_error':
                    citations_section += f"{i}. Query: {result['sub_query'][:60]}...\n"
                    if result.get('sources'):
                        for source in result['sources']:
                            citations_section += f"   Source: {source}\n"
                    citations_section += f"   Method: {result.get('method', 'unknown')}\n\n"
        
        if template:
            return template.format(
                citations_section=citations_section,
                final_response=final_response or deep_research_data.get('synthesized_answer', 'No response received')
            )
    
    elif tool_usage_info or search_sources:
        # Use tool usage response template
        template = get_prompt_template("tool_usage_response_template", "response_formatting")
        methodology_template = get_prompt_template("methodology_section_template", "response_formatting")
        
        # Build methodology section
        if methodology_template:
            methodology_section = methodology_template.format(
                tool_usage_count=len(tool_usage_info),
                sources_count=len(search_sources),
                model_id=model_id,
                query=query
            )
        else:
            methodology_section = f"Research conducted using {len(tool_usage_info)} tools and {len(search_sources)} sources"
        
        # Build citations section
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
        
        if template:
            return template.format(
                methodology_section=methodology_section,
                citations_section=citations_section,
                final_response=final_response or "No response received from agent"
            )
    
    else:
        # Use no tools response template
        template = get_prompt_template("no_tools_response_template", "response_formatting")
        if template:
            return template.format(final_response=final_response or "No response received from agent")
    
    # Fallback if no templates found
    return f"""
📊 **RESEARCH REPORT**
{final_response or "No response received from agent"}

💡 **Note:** Response generated using available research capabilities.
"""

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
        
        # Create enhanced prompt using template from configuration
        # Auto-detect if this is a market research query
        is_market_research = any(keyword in query.lower() for keyword in 
                               ['market analysis', 'market research', 'market report', 'market study'])
        
        template_type = "market_research" if is_market_research else "general_research"
        enhanced_prompt = build_enhanced_prompt(query, template_type)
        
        print(f"🔧 Using prompt template: {template_type}")
        print(f"📝 Enhanced prompt length: {len(enhanced_prompt)} characters")
        
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
        
        # Create comprehensive response with citations using template-based formatting
        response_with_citations = build_response_with_citations(
            final_response=final_response,
            deep_research_data=deep_research_data,
            tool_usage_info=tool_usage_info,
            search_sources=search_sources,
            query=query,
            model_id=MODEL_ID
        )
        
        # Save response as markdown file if configured
        output_config = get_config_value(workflow_config, "deep_research_config.output_config", {})
        if output_config.get("auto_save_markdown", True):
            try:
                markdown_file_path = save_response_as_markdown(response_with_citations, query)
                print(f"📄 Research report saved to: {markdown_file_path}")
                # Add file path info to response
                response_with_citations += f"\n\n📁 **Report saved to:** `{markdown_file_path}`"
            except Exception as e:
                print(f"⚠️ Could not save markdown file: {e}")
        else:
            print("📄 Auto-save disabled in configuration")
        
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

def save_response_as_markdown(response: str, query: str, output_dir: str = None) -> str:
    """Save the agent response as a markdown file.
    
    Args:
        response: The formatted response text to save
        query: The original query for filename generation
        output_dir: Directory to save the markdown file (uses config if None)
        
    Returns:
        Path to the saved markdown file
    """
    # Use configured output directory if not specified
    if output_dir is None:
        output_config = get_config_value(workflow_config, "deep_research_config.output_config", {})
        output_dir = output_config.get("reports_directory", "output/reports")
    
    # Create absolute path for output directory based on script location
    if not Path(output_dir).is_absolute():
        output_path = SCRIPT_DIR / output_dir
    else:
        output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from query and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clean query for filename (remove special characters)
    clean_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()
    clean_query = clean_query.replace(' ', '_')[:50]  # Limit length
    
    filename = f"research_report_{clean_query}_{timestamp}.md"
    filepath = output_path / filename
    
    # Add header to markdown
    markdown_content = f"""# Research Report: {query}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Method:** Deep Research Agent with Dynamic Tool Configuration

---

{response}

---

*This report was generated automatically by the Researcher Agent using configured tools including Google Search and RAG systems.*
"""
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return str(filepath)

if __name__ == "__main__":
    # Example usage
    query = "a detailed report on AI for private equity"
    
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