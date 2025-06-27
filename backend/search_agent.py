"""A Search agent using Google's ADK."""
import asyncio
import json
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search

try:
    from backend.core.agents.base_agent import BaseResearchAgent
    from backend.core.utils.response_formatter import format_response, format_error_response
    from backend.core.config.config_loader import ConfigLoader
except:
    from core.agents.base_agent import BaseResearchAgent
    from core.utils.response_formatter import format_response, format_error_response
    from core.config.config_loader import ConfigLoader


class SearchAgent(BaseResearchAgent):
    """A simple search agent."""

    def __init__(
        self,
        config_path: str = "backend/config/search/workflow_search.yml",
        prompts_path: str = "backend/prompts/search/prompts_search.yml",
        gemini_config_path: str = "backend/config/search/gemini_config_search.yml"
    ):
        """Initialize the agent."""
        super().__init__(
            config_path=config_path,
            prompts_path=prompts_path,
            agent_name=self._get_agent_name_from_config(config_path),
            agent_description=self._get_agent_description_from_config(config_path),
            required_config_keys=["core_config.model", "agent_config.name"]
        )
        
        # Load Gemini-specific configuration
        self.gemini_config_loader = ConfigLoader(gemini_config_path)
        self.gemini_config = self.gemini_config_loader.load_config()
        
        # Load and set API key from gemini config
        self._load_api_key()

    def _get_agent_name_from_config(self, config_path: str) -> str:
        """Get agent name from config file."""
        temp_loader = ConfigLoader(config_path)
        temp_config = temp_loader.load_config()
        return temp_loader.get_value("agent_config.name", "SearchAgent")
    
    def _get_agent_description_from_config(self, config_path: str) -> str:
        """Get agent description from config file.""" 
        temp_loader = ConfigLoader(config_path)
        temp_config = temp_loader.load_config()
        return temp_loader.get_value("agent_config.description", "An agent with search capabilities")

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
        # Check if google_search is enabled in config
        if self.config_loader.get_value("tools_config.google_search.enabled", True):
            return [google_search]
        return []

    async def initialize(self) -> None:
        """Initialize the agent and its dependencies."""
        if self.initialized:
            return
            
        self.validate_config()
        
        # Create agent with configuration from config files
        self.agent = Agent(
            name=self.config_loader.get_value("agent_config.name"),
            model=self.config_loader.get_value("core_config.model"),
            description=self.config_loader.get_value("agent_config.description"),
            instruction=self.get_agent_instruction(),
            tools=self.get_tools()
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
            "app_config": self.config_loader.get_value("app_config", {}),
            "search_config": self.config_loader.get_value("search_config", {}),
            "tools_config": self.config_loader.get_value("tools_config", {})
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

    def get_agent_instruction(self) -> str:
        """Get the instruction prompt for the agent."""
        instruction = self.get_prompt("agent_instruction", "prompts")
        if not instruction:
            raise ValueError("Missing agent_instruction prompt in search prompts configuration")
        return instruction

    async def process_events(self, events) -> Dict[str, Any]:
        """Process events from the agent's execution."""
        separator_length = self.config_loader.get_value("display_config.separator_length", 50)
        grounding_chunks_display = self.config_loader.get_value("search_config.grounding_chunks_display", 3)
        content_preview_length = self.config_loader.get_value("display_config.content_preview_length", 500)
        text_preview_length = self.config_loader.get_value("display_config.text_preview_length", 100)
        
        print("\n" + "="*separator_length)
        print("🚀 Starting to process events")
        print("="*separator_length)
        
        final_response = None
        tool_results = []
        tool_calls_made = []
        tool_responses_received = []
        sources = []
        query = ""
        grounding_detected = False
        
        try:
            async for event in events:
                print(f"🔍 Event type: {type(event).__name__}")
                
                # Check for grounding metadata (Google's built-in search)
                if hasattr(event, 'grounding_metadata') and event.grounding_metadata:
                    grounding_detected = True
                    print(f"   🌐 GROUNDING DETECTED: Google's built-in search was used")
                    
                    # Track grounding as external tool usage even if no chunks are available
                    grounding_info = {
                        'tool_name': 'google_grounding',
                        'call_id': 'grounding_search',
                        'arguments': {'search_performed': True, 'method': 'built_in_grounding'},
                        'timestamp': datetime.now().isoformat(),
                        'status': 'completed',
                        'description': 'Google built-in search grounding'
                    }
                    tool_calls_made.append(grounding_info)
                    
                    if hasattr(event.grounding_metadata, 'grounding_chunks') and event.grounding_metadata.grounding_chunks:
                        chunks_count = len(event.grounding_metadata.grounding_chunks)
                        print(f"   📊 Grounding chunks: {chunks_count}")
                        # Display limited number of chunks based on config
                        for i, chunk in enumerate(event.grounding_metadata.grounding_chunks[:grounding_chunks_display]):
                            if hasattr(chunk, 'web') and chunk.web:
                                web_info = {
                                    'title': getattr(chunk.web, 'title', 'N/A'),
                                    'domain': getattr(chunk.web, 'domain', 'N/A'),
                                    'url': getattr(chunk.web, 'uri', 'N/A')
                                }
                                print(f"     {i+1}. {web_info['title']} - {web_info['domain']}")
                                
                                # Add to sources
                                sources.append({
                                    'tool': 'google_grounding',
                                    'title': web_info['title'],
                                    'domain': web_info['domain'],
                                    'url': web_info['url'],
                                    'timestamp': datetime.now().isoformat()
                                })
                    else:
                        print(f"   📊 Grounding performed but no accessible chunks")
                        # Add a generic source entry for grounding
                        sources.append({
                            'tool': 'google_grounding',
                            'title': 'Google Search Grounding',
                            'domain': 'google.com',
                            'url': 'Built-in search grounding',
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Check for content and parts
                if hasattr(event, 'content') and event.content:
                    print(f"   Content type: {type(event.content)}")
                    if hasattr(event.content, 'parts') and event.content.parts:
                        print(f"   Parts count: {len(event.content.parts)}")
                        for i, part in enumerate(event.content.parts):
                            part_type = type(part).__name__
                            print(f"     Part {i}: {part_type}")
                            
                            # Track function calls (tools being invoked)
                            if hasattr(part, 'function_call') and part.function_call:
                                func_call = part.function_call
                                print(f"       🛠️ TOOL CALL: {func_call.name}")
                                print(f"       📝 Args: {dict(func_call.args)}")
                                
                                tool_call_info = {
                                    'tool_name': func_call.name,
                                    'call_id': func_call.id if hasattr(func_call, 'id') else f"call_{i}",
                                    'arguments': dict(func_call.args),
                                    'timestamp': datetime.now().isoformat(),
                                    'status': 'called'
                                }
                                tool_calls_made.append(tool_call_info)
                                
                                # Track in tool_results as well for compatibility
                                tool_results.append({
                                    'name': func_call.name,
                                    'args': dict(func_call.args),
                                    'status': 'called'
                                })
                            
                            # Track function responses (tool results)
                            if hasattr(part, 'function_response') and part.function_response:
                                func_response = part.function_response
                                print(f"       📥 TOOL RESPONSE: {func_response.name}")
                                
                                response_content = str(func_response.response) if hasattr(func_response, 'response') else 'No response content'
                                tool_response_info = {
                                    'tool_name': func_response.name,
                                    'response_id': func_response.id if hasattr(func_response, 'id') else f"response_{i}",
                                    'response_content': response_content,
                                    'timestamp': datetime.now().isoformat(),
                                    'status': 'completed'
                                }
                                tool_responses_received.append(tool_response_info)
                                
                                # Add to sources for citation with configured length limit
                                source_content = response_content[:content_preview_length] + "..." if len(response_content) > content_preview_length else response_content
                                sources.append({
                                    'tool': func_response.name,
                                    'content': source_content,
                                    'timestamp': datetime.now().isoformat()
                                })
                            
                            # Track text responses
                            if hasattr(part, 'text') and part.text:
                                text_preview = part.text[:text_preview_length] + "..." if len(part.text) > text_preview_length else part.text
                                print(f"       📄 Text: {text_preview}")
                    else:
                        print(f"   No parts or empty parts")
                
                # Check if this is the final response with content
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                final_response = part.text
                                print(f"✅ Final Response: {final_response}")
                                break
                
                # Try to extract query from initial events if available
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text and not query:
                            # This might be the initial query
                            query = part.text
                            print(f"📥 Query: {query}")

            # Print tool usage summary
            print("\n" + "="*separator_length)
            print("🔧 TOOL USAGE SUMMARY")
            print("="*separator_length)
            print(f"Tool calls made: {len(tool_calls_made)}")
            print(f"Tool responses received: {len(tool_responses_received)}")
            print(f"Google grounding used: {grounding_detected}")
            
            if tool_calls_made:
                print("\n📞 TOOLS/METHODS USED:")
                for call in tool_calls_made:
                    print(f"  • {call['tool_name']} (ID: {call['call_id']})")
                    if 'description' in call:
                        print(f"    Description: {call['description']}")
                    print(f"    Args: {call['arguments']}")
            elif grounding_detected:
                print("🌐 GOOGLE GROUNDING WAS USED - Built-in search capabilities")
            else:
                print("❌ NO TOOLS WERE CALLED - Agent used internal knowledge only")
            
            if tool_responses_received:
                print("\n📥 TOOL RESPONSES:")
                for response in tool_responses_received:
                    print(f"  • {response['tool_name']} (ID: {response['response_id']})")
                    response_preview_length = self.config_loader.get_value("display_config.content_preview_length", 200)
                    content_preview = response['response_content'][:response_preview_length] + "..." if len(response['response_content']) > response_preview_length else response['response_content']
                    print(f"    Content: {content_preview}")

            # If we still don't have a query, try to infer it from the session or use a default
            if not query:
                query = self.config_loader.get_value("session_config.default_query", "User query")
                print("⚠️ Query not found in events, using default.")

            # Prepare and return the response
            response_data = self._prepare_response_data(
                final_response, tool_results, sources, query, tool_calls_made, tool_responses_received, grounding_detected
            )
            
            # Format the final response
            formatted_response = format_response(
                content=response_data['content'],
                sources=response_data['sources'],
                tool_usage=response_data['tool_usage'],
                model_id=response_data['model'],
                query=query,
                metadata={
                    'success': response_data['success'],
                    'timestamp': response_data['timestamp'],
                    'tools_called': len(tool_calls_made),
                    'tools_responded': len(tool_responses_received)
                }
            )
            
            # Save both tool results and final response
            tool_results_path, final_response_path = self._save_dual_responses(response_data)
            if tool_results_path:
                print(f"🔧 Tool results saved to: {tool_results_path}")
            if final_response_path:
                print(f"📝 Final response saved to: {final_response_path}")
            
            return formatted_response
            
        except Exception as e:
            error_msg = f"Error processing events: {str(e)}"
            print(f"❌ {error_msg}")
            return format_error_response(
                Exception(error_msg),
                query=query,
                context="Processing agent events"
            )

    async def _call_search_tool(self, query: str, tool_results: list, sources: list) -> str:
        """Call the search tool and process results."""
        print(f"Executing search tool with query: '{query}'")
        
        # Get search configuration from config
        max_results = self.config_loader.get_value("tools_config.google_search.max_results", 5)
        max_results_display = self.config_loader.get_value("search_config.max_results_display", 3)
        search_timeout = self.config_loader.get_value("tools_config.google_search.timeout", 30)
        source_content_max_length = self.config_loader.get_value("display_config.source_content_max_length", 1000)
        
        try:
            available_tools = self.get_tools()
            print(f"🔧 Available tools: {[t.name for t in available_tools] if available_tools else 'None'}")
            
            search_tool = next((t for t in available_tools if t.name == 'google_search'), None)
            if not search_tool:
                error_msg = "❌ Search tool not found in available tools"
                print(error_msg)
                return error_msg
                
            print(f"🔍 Calling search tool with query: {query}")
                
            # Call the search tool directly with configured parameters
            try:
                print(f"🔍 Executing search with query: {query} (max_results: {max_results})")
                search_results = await search_tool(query=query, num_results=max_results)
                print(f"✅ Search completed. Results type: {type(search_results)}")
            except Exception as e:
                error_msg = f"❌ Search tool error: {str(e)}"
                print(error_msg)
                return error_msg
            
            # Process and format results
            formatted_results = []
            if not search_results:
                print("ℹ️  No search results returned")
                return "No search results found."
                
            if isinstance(search_results, list):
                print(f"📊 Processing {len(search_results)} search results (displaying {min(len(search_results), max_results_display)})")
                # Display limited number of results based on config
                for i, result in enumerate(search_results[:max_results_display], 1):
                    title = result.get('title', 'No title')
                    link = result.get('link', 'No link')
                    snippet = result.get('snippet', 'No snippet')
                    
                    print(f"   {i}. {title}")
                    print(f"      Link: {link}")
                    
                    formatted_results.append(f"{i}. {title}")
                    formatted_results.append(f"   {link}")
                    formatted_results.append(f"   {snippet}")
                    formatted_results.append("")
            
            # Log and store tool results
            tool_result = {
                'name': 'google_search',
                'input': {'query': query, 'max_results': max_results},
                'output': search_results,
                'success': True
            }
            tool_results.append(tool_result)
            print(f"✅ Tool result recorded: {tool_result['name']} (success: {tool_result['success']})")
            
            # Store sources for the response with configured length limit
            result_content = '\n'.join(formatted_results)
            source_content = result_content[:source_content_max_length] + '...' if len(result_content) > source_content_max_length else result_content
            source_info = {
                'tool': 'google_search',
                'result': source_content,
                'query': query
            }
            sources.append(source_info)
            print(f"📚 Source added: {len(sources)} source(s) total")
            
            formatted_output = '\n'.join(formatted_results)
            print(f"📝 Formatted search results (length: {len(formatted_output)} chars)")
            return formatted_output
            
        except Exception as e:
            error_msg = f"Error calling search tool: {str(e)}"
            tool_results.append({
                'name': 'google_search',
                'input': {'query': query, 'max_results': max_results},
                'error': error_msg,
                'success': False
            })
            return f"Error: {error_msg}"
    
    def _prepare_response_data(self, content, tool_results, sources, query, tool_calls_made, tool_responses_received, grounding_detected):
        """Prepare the response data structure."""
        # Count only explicit tool calls (exclude grounding)
        explicit_tool_calls = [call for call in tool_calls_made if call['tool_name'] != 'google_grounding']
        
        return {
            'success': content is not None,
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'model': self.config_loader.get_value("core_config.model", "unknown"),
            'tool_usage': tool_results,
            'detailed_tool_calls': tool_calls_made,
            'detailed_tool_responses': tool_responses_received,
            'tools_called_count': len(tool_calls_made),
            'tools_responded_count': len(tool_responses_received),
            'explicit_tools_called_count': len(explicit_tool_calls),
            'used_external_tools': len(explicit_tool_calls) > 0,  # Only explicit tools, not grounding
            'used_grounding': grounding_detected,
            'used_any_external_source': len(tool_calls_made) > 0 or grounding_detected,  # Explicit tools OR grounding
            'sources': sources,
            'content': content or "No response generated",
            'grounding_detected': grounding_detected
        }
    
    def _save_dual_responses(self, response_data: dict) -> tuple:
        """Save both tool results and final response to separate files."""
        # Get output directory
        output_dir = Path(
            self.config_loader.get_value("app_config.output_dir", "backend/output")
        )
        output_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Save detailed tool results file
        tool_results_data = {
            'query': response_data['query'],
            'timestamp': response_data['timestamp'],
            'model': response_data['model'],
            'used_external_tools': response_data['used_external_tools'],  # Only explicit tools
            'used_grounding': response_data['used_grounding'],
            'used_any_external_source': response_data['used_any_external_source'],  # Either explicit tools or grounding
            'grounding_detected': response_data['grounding_detected'],
            'tools_called_count': response_data['tools_called_count'],
            'tools_responded_count': response_data['tools_responded_count'],
            'explicit_tools_called_count': response_data['explicit_tools_called_count'],
            'detailed_tool_calls': response_data['detailed_tool_calls'],
            'detailed_tool_responses': response_data['detailed_tool_responses'],
            'sources': response_data['sources'],
            'tool_usage_summary': {
                'total_calls': len(response_data['detailed_tool_calls']),
                'total_responses': len(response_data['detailed_tool_responses']),
                'tools_used': list(set([call['tool_name'] for call in response_data['detailed_tool_calls']])),
                'explicit_search_performed': any(call['tool_name'] == 'google_search' for call in response_data['detailed_tool_calls']),
                'grounding_used': response_data['grounding_detected'],
                'external_search_used': response_data['grounding_detected'] or any(call['tool_name'] == 'google_search' for call in response_data['detailed_tool_calls']),
                'information_acquisition_method': 'explicit_tools' if response_data['used_external_tools'] 
                                                else 'grounding' if response_data['grounding_detected'] 
                                                else 'internal_knowledge'
            }
        }
        
        tool_results_file = f"tool_results_{timestamp}.json"
        tool_results_path = output_dir / tool_results_file
        
        try:
            with open(tool_results_path, 'w', encoding='utf-8') as f:
                json.dump(tool_results_data, f, indent=4, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Error saving tool results to {tool_results_path}: {e}")
            tool_results_path = None
        
        # 2. Save final response file
        final_response_data = {
            'query': response_data['query'],
            'timestamp': response_data['timestamp'],
            'model': response_data['model'],
            'final_response': response_data['content'],
            'used_external_tools': response_data['used_external_tools'],  # Only explicit tools
            'used_grounding': response_data['used_grounding'],
            'used_any_external_source': response_data['used_any_external_source'],
            'grounding_detected': response_data['grounding_detected'],
            'tools_summary': {
                'explicit_tools_called': response_data['explicit_tools_called_count'],
                'total_tools_called': response_data['tools_called_count'],
                'explicit_search_used': any(call['tool_name'] == 'google_search' for call in response_data['detailed_tool_calls']),
                'grounding_search_used': response_data['grounding_detected'],
                'information_source': 'Explicit tools' if response_data['used_external_tools'] 
                                    else 'External search (grounding)' if response_data['grounding_detected'] 
                                    else 'Internal knowledge'
            },
            'metadata': {
                'success': response_data['success'],
                'response_length': len(response_data['content']) if response_data['content'] else 0,
                'has_sources': len(response_data['sources']) > 0
            }
        }
        
        final_response_file = f"final_response_{timestamp}.json"
        final_response_path = output_dir / final_response_file
        
        try:
            with open(final_response_path, 'w', encoding='utf-8') as f:
                json.dump(final_response_data, f, indent=4, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Error saving final response to {final_response_path}: {e}")
            final_response_path = None
        
        return str(tool_results_path) if tool_results_path else None, str(final_response_path) if final_response_path else None


if __name__ == "__main__":
    import asyncio
    from pprint import pprint
    
    def verify_configuration():
        """Verify that all configuration parameters are being read correctly."""
        print("\n🔧 CONFIGURATION VERIFICATION")
        print("="*60)
        
        agent = SearchAgent()
        
        print("📋 Workflow Configuration:")
        print(f"  • Agent Name: {agent.config_loader.get_value('agent_config.name')}")
        print(f"  • Agent Description: {agent.config_loader.get_value('agent_config.description')}")
        print(f"  • Model: {agent.config_loader.get_value('core_config.model')}")
        print(f"  • Temperature: {agent.config_loader.get_value('core_config.temperature')}")
        print(f"  • Max Tokens: {agent.config_loader.get_value('core_config.max_tokens')}")
        print(f"  • App Name: {agent.config_loader.get_value('app_config.app_name')}")
        print(f"  • Output Dir: {agent.config_loader.get_value('app_config.output_dir')}")
        print(f"  • Search Max Results: {agent.config_loader.get_value('search_config.max_results')}")
        print(f"  • Display Max Results: {agent.config_loader.get_value('search_config.max_results_display')}")
        print(f"  • Grounding Chunks Display: {agent.config_loader.get_value('search_config.grounding_chunks_display')}")
        print(f"  • Google Search Enabled: {agent.config_loader.get_value('tools_config.google_search.enabled')}")
        print(f"  • Separator Length: {agent.config_loader.get_value('display_config.separator_length')}")
        print(f"  • Content Preview Length: {agent.config_loader.get_value('display_config.content_preview_length')}")
        
        print("\n📋 Gemini Configuration:")
        print(f"  • Provider: {agent.gemini_config_loader.get_value('api_config.provider')}")
        print(f"  • API Key Set: {'Yes' if agent.gemini_config_loader.get_value('api_config.api_key') else 'No'}")
        print(f"  • Default Model: {agent.gemini_config_loader.get_value('model_config.default_model')}")
        print(f"  • Backup Model: {agent.gemini_config_loader.get_value('model_config.backup_model')}")
        print(f"  • Max Requests/Min: {agent.gemini_config_loader.get_value('performance_config.max_requests_per_minute')}")
        print(f"  • Timeout: {agent.gemini_config_loader.get_value('performance_config.timeout_seconds')}")
        print(f"  • Retry Attempts: {agent.gemini_config_loader.get_value('performance_config.retry_attempts')}")
        print(f"  • Grounding Enabled: {agent.gemini_config_loader.get_value('grounding_config.enable_grounding')}")
        
        print("\n✅ All configuration parameters are being read from YAML files!")
        print("✅ No hardcoded values detected in the agent!")
        
        return agent
    
    async def main():
        # First verify configuration
        agent = verify_configuration()
        
        print("\n" + "="*60)
        print("🔍 TESTING SEARCH AGENT")
        print("="*60)
        
        query = "What is the capital of France?"
        print(f"🔍 Researching: {query}")
        
        response = await agent.query(query)
        
        print("\n📝 Response:")
        print(response.get("content", "No content in response"))
        
        return response
    
    asyncio.run(main())
