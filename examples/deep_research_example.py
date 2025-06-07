#!/usr/bin/env python3
"""
Deep Research Agent Example

This example demonstrates how to use the Deep Research Agent with the Google ADK.
The agent performs multi-hop research by:
1. Breaking down complex queries into sub-questions
2. Using RAG to answer each sub-question
3. Synthesizing a comprehensive answer with citations

Requirements:
- API key configured in workflow_deepresearch.yml
- MCP server running at the configured endpoint
- Proper configuration in workflow_deepresearch.yml
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.main_rag_deepresearch import (
    call_agent, 
    call_agent_async, 
    DeepResearchAgent,
    get_workflow_config
)

def display_config_summary():
    """Display a summary of the current configuration."""
    try:
        config = get_workflow_config()
        print("\n📋 Configuration Summary:")
        print(f"   Model: {config['api_config']['model']}")
        print(f"   Agent: {config['mcp_config']['adk_toolset']['agent']['name']}")
        print(f"   RAG Endpoint: {config['mcp_config']['rag_mcp_endpoint']}")
        print(f"   Max Sub-questions: {config['deep_research_config']['process_config']['max_sub_questions']}")
        print(f"   Error Handling: {config['deep_research_config']['process_config']['enable_error_handling']}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def example_synchronous():
    """Example using synchronous API."""
    print("\n🔍 Synchronous Deep Research Example")
    print("=" * 50)
    
    query = "What are the latest developments in quantum computing and their potential impact on cybersecurity?"
    
    print(f"Query: {query}")
    print("\nProcessing...")
    
    try:
        response = call_agent(query)
        print(f"\n📖 Response:\n{response}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def example_asynchronous():
    """Example using asynchronous API."""
    print("\n🔍 Asynchronous Deep Research Example")
    print("=" * 50)
    
    query = "How are artificial intelligence and machine learning transforming the healthcare industry?"
    
    print(f"Query: {query}")
    print("\nProcessing...")
    
    try:
        response = await call_agent_async(query)
        print(f"\n📖 Response:\n{response}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def example_agent_class():
    """Example using the DeepResearchAgent class directly."""
    print("\n🔍 Agent Class Deep Research Example")
    print("=" * 50)
    
    query = "What are the environmental and economic implications of renewable energy adoption?"
    
    print(f"Query: {query}")
    print("\nCreating agent...")
    
    try:
        agent = DeepResearchAgent()
        print("Agent created successfully")
        
        print("Processing query...")
        response = await agent.call_agent_async(query)
        
        print(f"\n📖 Response:\n{response}")
        
        # Display some config info from the agent
        print(f"\n🔧 Agent Configuration:")
        print(f"   RAG Endpoint: {agent.config['mcp_config']['rag_mcp_endpoint']}")
        print(f"   Model: {agent.config['api_config']['model']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main example runner."""
    print("🚀 Deep Research Agent Examples")
    print("=" * 50)
    
    # Display configuration
    if not display_config_summary():
        return 1
    
    # Run examples
    examples = [
        ("Synchronous Example", example_synchronous),
        ("Asynchronous Example", example_asynchronous),
        ("Agent Class Example", example_agent_class),
    ]
    
    for name, example_func in examples:
        print(f"\n🎯 Running {name}")
        try:
            if asyncio.iscoroutinefunction(example_func):
                success = asyncio.run(example_func())
            else:
                success = example_func()
            
            if success:
                print(f"✅ {name} completed successfully")
            else:
                print(f"❌ {name} failed")
        except KeyboardInterrupt:
            print(f"\n⏹️  {name} interrupted by user")
            break
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
    
    print("\n🏁 Examples completed")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 