#!/usr/bin/env python3
"""
Data Source Checker for RAG Agent

This script helps you understand what data sources are being used by the RAG agent:
1. MCP Server status and connectivity
2. Google Search availability 
3. Configuration verification
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import yaml
from backend.core.config.config_loader import ConfigLoader


def check_mcp_server_status(endpoint: str) -> Dict[str, Any]:
    """Check if the MCP server is running and responsive."""
    try:
        # Try to ping the MCP server
        response = requests.get(endpoint, timeout=5)
        
        if response.status_code == 200:
            return {
                "status": "✅ Online",
                "endpoint": endpoint,
                "response_code": response.status_code,
                "details": "MCP server is responding"
            }
        else:
            return {
                "status": "⚠️ Issues",
                "endpoint": endpoint,
                "response_code": response.status_code,
                "details": f"Server responded but with code {response.status_code}"
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "status": "❌ Offline",
            "endpoint": endpoint,
            "response_code": None,
            "details": "Cannot connect to MCP server - is it running?"
        }
    except requests.exceptions.Timeout:
        return {
            "status": "⚠️ Timeout",
            "endpoint": endpoint,
            "response_code": None,
            "details": "MCP server is not responding (timeout)"
        }
    except Exception as e:
        return {
            "status": "❌ Error",
            "endpoint": endpoint,
            "response_code": None,
            "details": f"Error checking MCP server: {e}"
        }


def check_google_api_key() -> Dict[str, Any]:
    """Check if Google API key is configured."""
    # Check environment variable
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    if api_key:
        return {
            "status": "✅ Configured",
            "source": "Environment variable",
            "details": f"API key found (length: {len(api_key)} chars)"
        }
    
    # Check in config files
    try:
        config_loader = ConfigLoader("backend/config/research/gemini_config_research.yml")
        config_loader.load_config()  # Must call this to load the YAML file
        config_api_key = config_loader.get_value("api_config.api_key")
        
        if config_api_key:
            return {
                "status": "✅ Configured",
                "source": "Configuration file",
                "details": f"API key found in config (length: {len(config_api_key)} chars)"
            }
    except Exception as e:
        pass
    
    return {
        "status": "❌ Missing",
        "source": "Not found",
        "details": "Google API key not found in environment or config files"
    }


def load_research_config() -> Dict[str, Any]:
    """Load and verify research configuration."""
    try:
        config_loader = ConfigLoader("backend/config/research/workflow_research.yml")
        config_loader.load_config()  # Must call this to load the YAML file
        
        # Get values with proper defaults
        mcp_endpoint = config_loader.get_value("mcp_config.rag_mcp_endpoint", "Not configured")
        google_search_enabled = config_loader.get_value("mcp_config.adk_toolset.agent.tools.google_search.enabled", False)
        rag_tool_enabled = config_loader.get_value("mcp_config.adk_toolset.agent.tools.rag_tool.enabled", False)
        max_sub_questions = config_loader.get_value("research_config.max_sub_questions", 2)
        model = config_loader.get_value("core_config.model", "Not configured")
        
        return {
            "status": "✅ Loaded",
            "details": {
                "mcp_endpoint": mcp_endpoint,
                "google_search_enabled": google_search_enabled,
                "rag_tool_enabled": rag_tool_enabled,
                "max_sub_questions": max_sub_questions,
                "model": model
            }
        }
    except Exception as e:
        return {
            "status": "❌ Error",
            "details": f"Failed to load config: {e}"
        }


def check_recent_research_logs() -> Dict[str, Any]:
    """Check for recent research logs to see what sources were used."""
    logs_dir = Path("data/logs")
    
    if not logs_dir.exists():
        return {
            "status": "⚠️ No logs",
            "details": "No logs directory found"
        }
    
    # Find most recent research data file
    research_files = list(logs_dir.glob("deep_research_data_*.json"))
    
    if not research_files:
        return {
            "status": "⚠️ No research logs",
            "details": "No recent research data files found"
        }
    
    # Get the most recent file
    latest_file = max(research_files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        # Analyze what sources were used
        findings = data.get('findings', [])
        rag_successes = sum(1 for f in findings if f.get('rag_success', False))
        total_questions = len(findings)
        
        return {
            "status": "✅ Found",
            "details": {
                "latest_file": latest_file.name,
                "query": data.get('query', 'Unknown'),
                "timestamp": data.get('timestamp', 'Unknown'),
                "total_sub_questions": total_questions,
                "rag_successes": rag_successes,
                "mcp_endpoint_used": data.get('config_used', {}).get('mcp_endpoint', 'Unknown')
            }
        }
    except Exception as e:
        return {
            "status": "❌ Error",
            "details": f"Failed to read latest log: {e}"
        }


def main():
    """Run comprehensive data source check."""
    print("🔍 DATA SOURCE CHECKER FOR RAG AGENT")
    print("=" * 60)
    
    # Load configuration first
    print("\n1. 📋 Configuration Check")
    config_result = load_research_config()
    print(f"   Status: {config_result['status']}")
    
    if config_result['status'] == "✅ Loaded":
        config_details = config_result['details']
        mcp_endpoint = config_details['mcp_endpoint']
        print(f"   MCP Endpoint: {mcp_endpoint}")
        print(f"   Google Search Enabled: {config_details['google_search_enabled']}")
        print(f"   RAG Tool Enabled: {config_details['rag_tool_enabled']}")
        print(f"   Model: {config_details['model']}")
    else:
        print(f"   Error: {config_result['details']}")
        return
    
    # Check MCP server status
    print("\n2. 🌐 MCP Server Status")
    if mcp_endpoint and mcp_endpoint != "Not configured":
        mcp_result = check_mcp_server_status(mcp_endpoint)
        print(f"   Status: {mcp_result['status']}")
        print(f"   Endpoint: {mcp_result['endpoint']}")
        print(f"   Details: {mcp_result['details']}")
    else:
        mcp_result = {
            "status": "❌ Not Configured",
            "endpoint": mcp_endpoint,
            "details": "MCP endpoint not found in configuration"
        }
        print(f"   Status: {mcp_result['status']}")
        print(f"   Details: {mcp_result['details']}")
    
    # Check Google API key
    print("\n3. 🔑 Google API Key")
    api_result = check_google_api_key()
    print(f"   Status: {api_result['status']}")
    print(f"   Source: {api_result['source']}")
    print(f"   Details: {api_result['details']}")
    
    # Check recent research logs
    print("\n4. 📝 Recent Research Activity")
    logs_result = check_recent_research_logs()
    print(f"   Status: {logs_result['status']}")
    
    if logs_result['status'] == "✅ Found":
        details = logs_result['details']
        print(f"   Latest Query: {details['query']}")
        print(f"   Timestamp: {details['timestamp']}")
        print(f"   Sub-questions: {details['total_sub_questions']}")
        print(f"   RAG Successes: {details['rag_successes']}/{details['total_sub_questions']}")
        print(f"   MCP Endpoint Used: {details['mcp_endpoint_used']}")
    else:
        print(f"   Details: {logs_result['details']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    
    all_systems_ok = (
        config_result['status'] == "✅ Loaded" and
        mcp_result['status'] in ["✅ Online", "✅ Active"] and
        api_result['status'] == "✅ Configured"
    )
    
    if all_systems_ok:
        print("✅ All systems operational - RAG agent ready for production!")
        print("\n🔍 Data Sources Available:")
        print("   • MCP Server (RAG) - Online and responsive")
        print("   • Google Search (via API) - Configured and ready")
        print("   • Internal Knowledge - Always available")
    else:
        print("⚠️  Some issues detected:")
        if config_result['status'] != "✅ Loaded":
            print("   • Configuration issues")
        if mcp_result['status'] not in ["✅ Online", "✅ Active"]:
            print(f"   • MCP server issues: {mcp_result['status']}")
        if api_result['status'] != "✅ Configured":
            print("   • Google API key not configured")
        
        print("\n💡 Note: The RAG agent can still work with available sources:")
        if mcp_result['status'] in ["✅ Online", "✅ Active"]:
            print("   ✅ MCP Server (RAG) - Available")
        if api_result['status'] == "✅ Configured":
            print("   ✅ Google Search - Available")
        print("   ✅ Internal Knowledge - Always available")
    
    print("\n💡 To see detailed source usage in real-time, run:")
    print("   python -m backend.rag_agent")


if __name__ == "__main__":
    main() 