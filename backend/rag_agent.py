"""A Research agent using Google's ADK with RAG and search capabilities."""
import asyncio
import json
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import time

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

try:
    from backend.core.agents.base_agent import BaseResearchAgent
    from backend.core.utils.response_formatter import format_response, format_error_response
    from backend.core.config.config_loader import ConfigLoader
    from backend.tools.deep_research_tool import rag_tool
except:
    from core.agents.base_agent import BaseResearchAgent
    from core.utils.response_formatter import format_response, format_error_response
    from core.config.config_loader import ConfigLoader
    from tools.deep_research_tool import rag_tool


class ResearchAgent(BaseResearchAgent):
    """Advanced research agent with RAG and search capabilities.
    
    Uses a simplified, proven approach that avoids ADK library bugs.
    Based on working patterns from workflow_manager_rag.py and search_agent.py.
    """

    def __init__(self):
        """Initialize the Research Agent with proven configuration patterns."""
        # Initialize with default values first
        super().__init__(
            config_path="backend/config/research/workflow_research.yml",
            prompts_path="backend/prompts/research/prompts_research.yml", 
            agent_name="research_agent",
            agent_description="Advanced research agent with RAG and search capabilities"
        )
        
        # Load secondary config for Gemini-specific settings
        self.gemini_config_loader = ConfigLoader("backend/config/research/gemini_config_research.yml")
        self.gemini_config = self.gemini_config_loader.load_config()
        
        # Load API key from gemini config
        self._load_api_key()

    def _load_api_key(self) -> None:
        """Load the API key from gemini config file."""
        try:
            api_key = self.gemini_config_loader.get_value("api_config.api_key")
            if api_key:
                os.environ['GOOGLE_API_KEY'] = api_key
                print("✅ Google API key loaded successfully")
            else:
                print("⚠️ No API key found in gemini config")
        except Exception as e:
            print(f"⚠️ Failed to load API key: {e}")

    def get_tools(self) -> list:
        """Get the tools available to this agent."""
        tools = []
        
        # Check which tools are enabled in config
        google_search_enabled = self.config_loader.get_value("mcp_config.adk_toolset.agent.tools.google_search.enabled", True)
        rag_tool_enabled = self.config_loader.get_value("mcp_config.adk_toolset.agent.tools.rag_tool.enabled", True)
        
        if google_search_enabled:
            tools.append(google_search)
            print("✅ Added Google Search tool")
        
        if rag_tool_enabled:
            tools.append(rag_tool)
            print("✅ Added RAG tool")
        
        return tools
    
    def get_agent_instruction(self) -> str:
        """Get the instruction prompt for the agent."""
        # Try to get instruction from prompts config first
        instruction = self.get_prompt("researcher_agent", "agent_instructions")
        
        if not instruction:
            # Fallback to default instruction
            instruction = self.config_loader.get_value(
                "research_config.default_instruction",
                "You are an advanced research agent. Provide comprehensive, well-researched responses."
            )
        
        return instruction

    async def process_events(self, events) -> Any:
        """Process events from the agent's execution using the proven pattern.
        
        This implements the abstract method required by BaseResearchAgent.
        Uses the same proven approach as the query_async method.
        """
        print("🔄 Processing events using proven ADK pattern...")
        
        response_text = ""
        try:
            # Use the same proven pattern as in query_async
            async for event in events:
                # Only process final responses to avoid ADK library bugs
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
                            
            return {
                "content": response_text,
                "success": bool(response_text),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Event processing failed: {e}"
            print(f"❌ {error_msg}")
            return {
                "content": f"Event processing error: {error_msg}",
                "success": False,
                "error": error_msg
            }

    async def initialize(self) -> None:
        """Initialize the agent and its dependencies using proven patterns."""
        if self.initialized:
            return
            
        self.validate_config()
        
        # Create agent with configuration from config files - simplified approach
        enabled_tools = self.get_tools()
        
        print(f"🔧 Initializing agent with {len(enabled_tools)} tools")
        
        self.agent = Agent(
            name=self.config_loader.get_value("agent_config.name"),
            model=self.config_loader.get_value("core_config.model"),
            description=self.config_loader.get_value("agent_config.description"),
            instruction=self.get_agent_instruction(),
            tools=enabled_tools
        )
        
        # Setup runner and session using config values
        app_name = self.config_loader.get_value("app_config.app_name")
        self.runner = InMemoryRunner(
            agent=self.agent, 
            app_name=app_name
        )
        await self._create_session()
        
        self.initialized = True

    async def _create_session(self) -> None:
        """Create a new session with initial state."""
        initial_state = {
            "workflow_config": self.config,
            "gemini_config": self.gemini_config,
            "deep_research_config": self.config_loader.get_value("research_config", {}),
            "mcp_config": self.config_loader.get_value("mcp_config", {}),
            "rag_mcp_endpoint": self.config_loader.get_value("mcp_config.rag_mcp_endpoint")
        }
        
        # Add any additional state from child classes
        initial_state.update(self.get_initial_state())
        
        # Use configured values with fallbacks
        app_name = self.config_loader.get_value("app_config.app_name")
        user_id = self.config_loader.get_value(
            "app_config.user_id", 
            self.config_loader.get_value("session_config.fallback_user_id", "default_user")
        )
        session_id = self.config_loader.get_value(
            "app_config.session_id",
            self.config_loader.get_value("session_config.fallback_session_id", "default_session")
        )
        
        self.session = await self.runner.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=initial_state
        )

    async def query_async(self, query: str) -> Dict[str, Any]:
        """Execute a research query using the proven working pattern."""
        start_time = time.time()
        
        try:
            print(f"🔍 RESEARCH EXECUTION")
            print(f"{'='*80}")
            
            # Initialize if not already done
            if not self.initialized:
                await self.initialize()
            
            print(f"🔧 Agent Configuration:")
            print(f"   Name: {self.agent.name}")
            print(f"   Model: {self.agent.model}")
            print(f"   Tools: {len(self.agent.tools) if self.agent.tools else 0}")
            
            # Use the proven working pattern from workflow_manager_rag.py
            content = types.Content(role='user', parts=[types.Part(text=query)])
            
            # Execute using the proven pattern with timeout
            response_text = ""
            try:
                print("🚀 Starting query execution...")
                async with asyncio.timeout(120):  # 2 minute timeout
                    async for event in self.runner.run_async(
                        user_id=self.session.user_id,
                        session_id=self.session.id,
                        new_message=content
                    ):
                        # Use the proven final response extraction pattern
                        if event.is_final_response() and event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    response_text += part.text
                                    
            except asyncio.TimeoutError:
                print("⚠️ Query timed out after 2 minutes")
                return {
                    "content": "Query timed out - please try a simpler request",
                    "metadata": {
                        "success": False,
                        "execution_time": time.time() - start_time,
                        "error": "Timeout"
                    }
                }
            except Exception as e:
                print(f"❌ Query execution error: {e}")
                return {
                    "content": f"Query failed: {str(e)}",
                    "metadata": {
                        "success": False,
                        "execution_time": time.time() - start_time,
                        "error": str(e)
                    }
                }
            
            # Format the response
            if not response_text:
                response_text = "No response generated - please try rephrasing your query"
            
            result = {
                "content": response_text,
                "metadata": {
                    "success": bool(response_text),
                    "execution_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat(),
                    "original_query": query,
                    "strategy_used": "proven_adk_pattern"
                }
            }
            
            print(f"✅ Query completed successfully")
            print(f"📊 Response length: {len(response_text)} characters")
            
            # Save results if configured
            await self.save_research_results(result, query)
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Research execution failed: {error_msg}")
            
            return {
                "content": f"Research failed: {error_msg}",
                "metadata": {
                    "success": False,
                    "execution_time": time.time() - start_time,
                    "timestamp": datetime.now().isoformat(),
                    "error": error_msg
                }
            }

    async def save_research_results(self, result: Dict[str, Any], query: str) -> None:
        """Save research results to files if configured."""
        try:
            auto_save = self.config_loader.get_value("research_config.auto_save_markdown", False)
            
            if auto_save and result.get("content"):
                # Save as markdown
                markdown_path = self.save_response_as_markdown(result["content"], query)
                print(f"💾 Research saved to: {markdown_path}")
                
                # Also save metadata
                metadata_path = markdown_path.replace(".md", "_metadata.json")
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(result["metadata"], f, indent=2, ensure_ascii=False)
                
                print(f"📊 Metadata saved to: {metadata_path}")
                
        except Exception as e:
            print(f"⚠️ Failed to save research results: {e}")

    def save_response_as_markdown(self, response: str, query: str, output_dir: str = None) -> str:
        """Save the agent response as a markdown file."""
        # Use configured output directory if not specified
        if output_dir is None:
            output_config = self.config_loader.get_value("research_config.output_config", {})
            output_dir = output_config.get("reports_directory", "output/reports")
        
        # Create absolute path for output directory
        if not Path(output_dir).is_absolute():
            script_dir = Path(__file__).parent
            output_path = script_dir / output_dir
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
        include_timestamp = self.config_loader.get_value("research_config.output_config.include_timestamp", True)
        markdown_content = f"""# Research Report: {query}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S") if include_timestamp else "N/A"}  
**Method:** ADK Research Agent (Proven Pattern)

---

{response}

---

*This report was generated automatically by the Research Agent using Google's Agent Development Kit.*
"""
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(filepath)

    def query(self, query: str) -> str:
        """Query the agent synchronously - not recommended, use query_async instead."""
        raise NotImplementedError(
            "Use query_async() instead. The synchronous query() method "
            "is not supported in this implementation."
        )


if __name__ == "__main__":
    import asyncio
    from pprint import pprint
    
    def verify_configuration():
        """Verify that all configuration parameters are being read correctly."""
        print("\n🔧 RESEARCH AGENT CONFIGURATION VERIFICATION")
        print("="*70)
        
        agent = ResearchAgent()
        
        print("📋 Workflow Configuration:")
        print(f"  • Agent Name: {agent.config_loader.get_value('agent_config.name')}")
        print(f"  • Agent Description: {agent.config_loader.get_value('agent_config.description')}")
        print(f"  • Model: {agent.config_loader.get_value('core_config.model')}")
        print(f"  • Temperature: {agent.config_loader.get_value('core_config.temperature')}")
        print(f"  • Max Tokens: {agent.config_loader.get_value('core_config.max_tokens')}")
        print(f"  • App Name: {agent.config_loader.get_value('app_config.app_name')}")
        print(f"  • Output Dir: {agent.config_loader.get_value('app_config.output_dir')}")
        print(f"  • RAG Endpoint: {agent.config_loader.get_value('mcp_config.rag_mcp_endpoint')}")
        print(f"  • Google Search Enabled: {agent.config_loader.get_value('mcp_config.adk_toolset.agent.tools.google_search.enabled')}")
        print(f"  • RAG Tool Enabled: {agent.config_loader.get_value('mcp_config.adk_toolset.agent.tools.rag_tool.enabled')}")
        
        print("\n📋 Gemini Configuration:")
        print(f"  • Provider: {agent.gemini_config_loader.get_value('api_config.provider')}")
        print(f"  • API Key Set: {'Yes' if agent.gemini_config_loader.get_value('api_config.api_key') else 'No'}")
        print(f"  • Default Model: {agent.gemini_config_loader.get_value('model_config.default_model')}")
        print(f"  • Timeout: {agent.gemini_config_loader.get_value('performance_config.timeout_seconds')}")
        
        return agent
    
    async def main():
        # First verify configuration
        agent = verify_configuration()
        
        print("\n" + "="*70)
        print("🔍 TESTING RESEARCH AGENT WITH PROVEN PATTERN")
        print("="*70)
        
        # Test query
        query = "What are the latest developments in artificial intelligence?"
        print(f"🔍 Researching: {query}")
        
        try:
            response = await agent.query_async(query)
            
            print("\n📝 Research Response:")
            if isinstance(response, dict):
                content = response.get("content", "No content in response")
                print(content)
                
                # Show metadata if available
                metadata = response.get("metadata", {})
                if metadata:
                    print(f"\n📊 Research Metadata:")
                    print(f"   Success: {metadata.get('success', 'Unknown')}")
                    print(f"   Strategy Used: {metadata.get('strategy_used', 'Unknown')}")
                    print(f"   Execution Time: {metadata.get('execution_time', 0):.2f}s")
                    print(f"   Timestamp: {metadata.get('timestamp', 'Unknown')}")
            else:
                print(response)
                
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Research Agent Error: {error_msg}")
            return {"status": "error", "content": f"Agent failed: {error_msg}"}
        
        print("\n✅ Research agent testing completed!")
        return {"status": "success", "content": "Research agent tested successfully"}
    
    asyncio.run(main()) 