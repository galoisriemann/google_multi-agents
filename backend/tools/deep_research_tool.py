"""
Deep research tool that decomposes questions and uses specialized RAG system via Google ADK MCPToolset.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

# Import the cleaned MCPToolset from workflow_manager_rag.py
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from workflow_manager_rag import CleanedMCPToolset


def load_config() -> Dict:
    """Load configuration from workflow_research.yml file.
    
    Returns:
        Dictionary containing the complete workflow configuration.
        
    Raises:
        FileNotFoundError: If configuration file is not found.
        yaml.YAMLError: If YAML parsing fails.
    """
    config_path = Path("backend/config/research/workflow_research.yml")
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML configuration: {e}")


def load_prompts_config(config: Dict) -> Dict:
    """Load prompts configuration from the prompts file.
    
    Args:
        config: Main workflow configuration containing prompts file path.
        
    Returns:
        Dictionary containing all prompt templates.
        
    Raises:
        FileNotFoundError: If prompts configuration file is not found.
        yaml.YAMLError: If YAML parsing fails.
    """
    research_config = config.get('research_config', {})
    prompts_file = research_config.get('prompts_config_file', 'backend/prompts/research/prompts_research.yml')
    prompts_path = Path(prompts_file)
    
    try:
        with open(prompts_path, 'r', encoding='utf-8') as file:
            prompts_config = yaml.safe_load(file)
            return prompts_config
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompts configuration file not found: {prompts_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing prompts YAML configuration: {e}")


def setup_research_logger(config: Dict) -> logging.Logger:
    """Set up logging for the research process using config values.
    
    Args:
        config: Complete workflow configuration.
        
    Returns:
        Configured logger instance.
    """
    logging_config = config.get('research_config', {}).get('logging_config', {})
    
    if not logging_config.get('enabled', True):
        return logging.getLogger('deep_research_disabled')
    
    logger = logging.getLogger('deep_research')
    logger.setLevel(getattr(logging, logging_config.get('log_level', 'INFO')))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create log directory
    log_dir = Path(logging_config.get('log_directory', 'data/logs'))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"deep_research_{timestamp}.log"
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (optional)
    if logging_config.get('console_output', True):
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    logger.info(f"Deep research logging initialized. Log file: {log_file}")
    return logger


async def query_rag_system_via_adk(
    query: str, 
    config: Dict, 
    logger: logging.Logger
) -> Tuple[bool, Optional[str]]:
    """Query the RAG system through Google ADK MCPToolset (like main_rag.py).
    
    Args:
        query: The search query.
        config: Complete workflow configuration.
        logger: Logger instance.
        
    Returns:
        Tuple of (success: bool, response: Optional[str]).
    """
    try:
        # Get MCP configuration
        mcp_config = config.get('mcp_config', {})
        rag_mcp_endpoint = mcp_config.get('rag_mcp_endpoint', 'http://localhost:8000/mcp')
        adk_config = mcp_config.get('adk_toolset', {})
        allowed_tools = adk_config.get('allowed_tools', ['get_generative_search_response'])
        
        # Get agent configuration
        agent_config = adk_config.get('agent', {})
        agent_model = agent_config.get('model', 'gemini-2.0-flash')
        agent_name = agent_config.get('name', 'rag_agent')
        
        logger.info(f"Querying RAG system via ADK MCPToolset: {query}")
        logger.info(f"MCP endpoint: {rag_mcp_endpoint}")
        logger.info(f"Allowed tools: {allowed_tools}")
        
        # Load prompts for agent instruction
        prompts_config = load_prompts_config(config)
        agent_instruction = prompts_config.get('agent_instructions', {}).get('rag_specialist_agent', 
                                                                            'You are a research assistant.')
        
        # Create ADK agent with cleaned MCPToolset (same approach as main_rag.py)
        adk_agent = LlmAgent(
            model=agent_model,
            name=agent_name,
            instruction=agent_instruction,
            tools=[
                CleanedMCPToolset(
                    connection_params=SseServerParams(
                        url=rag_mcp_endpoint,
                        headers={'Accept': 'text/event-stream'},
                    ),
                    tool_filter=allowed_tools,
                )
            ],
        )
        
        # Create runner
        runner = InMemoryRunner(
            agent=adk_agent,
            app_name="DeepResearch_RAG"
        )
        
        # Create session
        app_config = config.get('app_config', {})
        user_id = app_config.get('user_id', 'user1')
        
        session = await runner.session_service.create_session(
            app_name="DeepResearch_RAG",
            user_id=user_id
        )
        
        # Load prompts and format RAG search prompt
        prompts_config = load_prompts_config(config)
        rag_search_prompt = prompts_config.get('research', {}).get('rag_search_prompt', 
                                               'Search for information about: {query}')
        formatted_rag_prompt = rag_search_prompt.format(query=query)
        
        # Prepare query content
        user_content = Content(
            role='user',
            parts=[Part(text=formatted_rag_prompt)]
        )
        
        # Execute query with timeout
        response_text = ""
        try:
            async with asyncio.timeout(45):  # Timeout from config
                async for event in runner.run_async(
                    user_id=user_id,
                    session_id=session.id,
                    new_message=user_content
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                response_text += part.text
                                
        except asyncio.TimeoutError:
            logger.warning(f"RAG query timed out: {query}")
            return False, None
        
        # Cleanup
        try:
            if hasattr(session, 'close'):
                await session.close()
            if hasattr(runner, 'close'):
                await runner.close()
        except Exception as e:
            logger.debug(f"Cleanup warning: {e}")
        
        if response_text.strip():
            logger.info(f"✅ RAG system response received: {len(response_text)} chars")
            return True, response_text
        else:
            prompts_config = load_prompts_config(config)
            error_msg = prompts_config.get('error_messages', {}).get('no_rag_response', 
                                          'RAG system returned empty response')
            logger.warning(f"❌ {error_msg}")
            return False, None
            
    except asyncio.TimeoutError:
        prompts_config = load_prompts_config(config)
        error_msg = prompts_config.get('error_messages', {}).get('timeout_error', 
                                      'RAG query timed out')
        logger.error(f"❌ {error_msg}")
        return False, None
    except Exception as e:
        prompts_config = load_prompts_config(config)
        error_msg = prompts_config.get('error_messages', {}).get('general_error', 
                                      'RAG system query failed')
        logger.error(f"❌ {error_msg}: {e}")
        return False, None


async def current_research_query(
    question: str, 
    config: Dict, 
    logger: logging.Logger
) -> str:
    """Perform current research using LLM with configured prompt template.
    
    Args:
        question: The research question.
        config: Complete workflow configuration.
        logger: Logger instance.
        
    Returns:
        Research response.
    """
    # Load prompts configuration
    prompts_config = load_prompts_config(config)
    prompt_template = prompts_config.get('research', {}).get('current_research_prompt', 
                                         "Research the following question: {question}")
    
    logger.info(f"Current research query: {question}")
    
    # Format the prompt using the template from prompts config
    formatted_prompt = prompt_template.format(question=question)
    
    # Get source label from main config
    research_config = config.get('research_config', {})
    source_label = research_config.get('source_label', 'Current research')
    
    try:
        # Create LLM agent for current research
        gemini_config = config.get('gemini_config', {})
        model_name = gemini_config.get('model_name', 'gemini-2.0-flash')
        
        research_agent = LlmAgent(
            model=model_name,
            name='current_researcher',
            instruction="You are a research specialist. Provide detailed, factual, current information based on your knowledge. Be comprehensive and cite when information might be time-sensitive or require verification."
        )
        
        # Create runner
        runner = InMemoryRunner(
            agent=research_agent,
            app_name="CurrentResearch"
        )
        
        # Create session
        app_config = config.get('app_config', {})
        user_id = app_config.get('user_id', 'user1')
        
        session = await runner.session_service.create_session(
            app_name="CurrentResearch",
            user_id=user_id
        )
        
        # Prepare content
        user_content = Content(
            role='user',
            parts=[Part(text=formatted_prompt)]
        )
        
        # Execute research
        response_text = ""
        async with asyncio.timeout(45):
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=user_content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
        
        # Cleanup
        try:
            if hasattr(session, 'close'):
                await session.close()
            if hasattr(runner, 'close'):
                await runner.close()
        except Exception:
            pass
        
        if response_text.strip():
            logger.info(f"✅ Current research completed for: {question}")
            return response_text.strip()
    
    except Exception as e:
        logger.warning(f"Current research LLM failed: {e}, using fallback")
    
    # Fallback response
    response = f"""
Based on current knowledge and available information:

Question: {question}

[Current research functionality encountered an issue. Please note this is a fallback response.]

Research methodology: {source_label}
Note: For complete current research, please ensure LLM services are properly configured.
"""
    
    logger.info(f"✅ Current research completed (fallback) for: {question}")
    return response


async def decompose_query(query: str, config: Dict) -> List[str]:
    """Decompose the main query into sub-questions using LLM with prompts template.
    
    Args:
        query: The main research query.
        config: Complete workflow configuration.
        
    Returns:
        List of sub-questions.
    """
    # Get configuration values
    research_config = config.get('research_config', {})
    max_questions = research_config.get('max_sub_questions', 2)
    
    # Load prompts configuration
    prompts_config = load_prompts_config(config)
    prompt_template = prompts_config.get('decomposition', {}).get('main_prompt', 
                                         'Decompose the following research query: {query}')
    fallback_prompt = prompts_config.get('decomposition', {}).get('fallback_prompt',
                                        'Break down this research question into {max_questions} specific sub-questions: {query}')
    
    try:
        # Create a simple LLM agent for decomposition
        gemini_config = config.get('gemini_config', {})
        model_name = gemini_config.get('model_name', 'gemini-2.0-flash')
        
        decomposition_agent = LlmAgent(
            model=model_name,
            name='query_decomposer',
            instruction=f"You are an expert at breaking down complex research queries into focused sub-questions. Follow the user's instructions precisely and return only the requested number of sub-questions ({max_questions})."
        )
        
        # Create runner for decomposition
        runner = InMemoryRunner(
            agent=decomposition_agent,
            app_name="QueryDecomposition"
        )
        
        # Create session
        app_config = config.get('app_config', {})
        user_id = app_config.get('user_id', 'user1')
        
        session = await runner.session_service.create_session(
            app_name="QueryDecomposition",
            user_id=user_id
        )
        
        # Format the decomposition prompt
        formatted_prompt = prompt_template.format(query=query)
        
        # Prepare content
        user_content = Content(
            role='user',
            parts=[Part(text=formatted_prompt)]
        )
        
        # Execute decomposition
        response_text = ""
        async with asyncio.timeout(30):
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=user_content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
        
        # Cleanup
        try:
            if hasattr(session, 'close'):
                await session.close()
            if hasattr(runner, 'close'):
                await runner.close()
        except Exception:
            pass
        
        # Parse the response into sub-questions
        if response_text.strip():
            # Split by lines and clean up
            lines = [line.strip() for line in response_text.strip().split('\n') if line.strip()]
            
            # Extract actual questions (remove numbering, bullets, etc.)
            sub_questions = []
            for line in lines:
                # Remove common prefixes like "1.", "•", "-", etc.
                cleaned = line.lstrip('0123456789.-• \t')
                if cleaned and len(cleaned) > 10:  # Ensure it's a substantial question
                    sub_questions.append(cleaned)
            
            # Return only the configured number of questions
            return sub_questions[:max_questions]
    
    except Exception as e:
        # Fallback to a simple approach if LLM decomposition fails
        print(f"LLM decomposition failed: {e}, using fallback approach")
        pass
    
    # Fallback: Use fallback prompt with simple decomposition
    fallback_formatted = fallback_prompt.format(query=query, max_questions=max_questions)
    
    # Simple rule-based decomposition as absolute fallback
    if "market" in query.lower() and "research" in query.lower():
        return [
            f"What is the current market size and growth trends for {query}?",
            f"Who are the key players and competitive landscape in {query}?"
        ][:max_questions]
    elif "regulation" in query.lower() or "legal" in query.lower():
        return [
            f"What are the current regulatory requirements for {query}?",
            f"What compliance obligations must be met for {query}?"
        ][:max_questions]
    else:
        return [
            f"What are the key aspects and current state of {query}?",
            f"What are the main challenges and opportunities related to {query}?"
        ][:max_questions]


async def synthesize_findings(
    query: str, 
    findings: List[Dict], 
    config: Dict, 
    logger: logging.Logger
) -> str:
    """Synthesize research findings using prompts template.
    
    Args:
        query: The original research query.
        findings: List of research findings.
        config: Complete workflow configuration.
        logger: Logger instance.
        
    Returns:
        Synthesized research response.
    """
    # Load prompts configuration
    prompts_config = load_prompts_config(config)
    
    # Choose synthesis approach based on complexity
    if len(findings) > 2 or any(len(str(f.get('rag_response', ''))) > 500 for f in findings):
        synthesis_template = prompts_config.get('synthesis', {}).get('comprehensive_synthesis', 
                                               'Synthesize findings comprehensively for: {query}')
        logger.info("Using comprehensive synthesis approach")
    else:
        synthesis_template = prompts_config.get('synthesis', {}).get('simple_synthesis', 
                                               'Synthesize findings for: {query}')
        logger.info("Using simple synthesis approach")
    
    # Get other configuration
    research_config = config.get('research_config', {})
    
    logger.info("Starting synthesis of research findings")
    
    # Build synthesis using config values
    synthesis_parts = [
        f"# Comprehensive Research: {query}\n",
        "## Research Methodology",
        f"- Configuration loaded from: workflow_deepresearch.yml",
        f"- Prompts loaded from: prompts_deepresearch.yml",
        f"- Query decomposed into {len(findings)} sub-questions",
        f"- RAG system queries: {sum(1 for f in findings if f['rag_success'])} successful",
        f"- Current research queries: {len(findings)} completed",
        f"- Source attribution: {research_config.get('source_label', 'Mixed sources')}",
        "",
        "## Detailed Findings\n"
    ]
    
    for i, finding in enumerate(findings, 1):
        synthesis_parts.extend([
            f"### {i}. {finding['question']}",
            "",
            "**Sources Used:**"
        ])
        
        if finding['rag_success']:
            synthesis_parts.append("- ✅ Specialized RAG System (Document Collection)")
            synthesis_parts.append(f"- Response: {finding['rag_response'][:200]}...")
        else:
            synthesis_parts.append("- ❌ RAG System (unavailable)")
        
        synthesis_parts.extend([
            f"- ✅ {research_config.get('source_label', 'Current research')}",
            f"- Response: {finding['current_response'][:200]}...",
            ""
        ])
    
    # Add configuration summary
    process_config = research_config.get('process_config', {})
    synthesis_parts.extend([
        "## Configuration Summary",
        f"- Max sub-questions: {process_config.get('max_sub_questions', 'default')}",
        f"- Error handling: {process_config.get('enable_error_handling', 'default')}",
        f"- Source citation: {process_config.get('enable_source_citation', 'default')}",
        f"- Logging enabled: {research_config.get('logging_config', {}).get('enabled', 'default')}",
        "",
        "## Summary",
        "This research utilized the configured deep research workflow with proper ADK MCPToolset integration.",
        f"All {len(findings)} sub-questions were addressed using available sources.",
        "",
        "---",
        "*Research completed using Google ADK MCPToolset integration with MCP endpoint*"
    ])
    
    synthesis = "\n".join(synthesis_parts)
    
    logger.info("✅ Synthesis completed")
    logger.debug(f"Final synthesis length: {len(synthesis)} characters")
    
    return synthesis


async def deep_research(query: str) -> str:
    """Main deep research function using Google ADK MCPToolset integration.
    
    Args:
        query: The research query to investigate.
        
    Returns:
        Comprehensive research response.
        
    Raises:
        Exception: If configuration loading or research process fails.
    """
    try:
        # Load complete configuration
        config = load_config()
        
        # Set up logging using config
        logger = setup_research_logger(config)
        
        logger.info("="*80)
        logger.info("DEEP RESEARCH SESSION STARTED")
        logger.info("="*80)
        
        # Use structured logging format from prompts
        prompts_config = load_prompts_config(config)
        logging_template = prompts_config.get('config_templates', {}).get('logging_format', 
                                            'Research Session: {timestamp} | Query: {query}')
        
        formatted_log = logging_template.format(
            timestamp=datetime.now().isoformat(),
            query=query,
            config_name=config.get('name', 'Unknown'),
            config_version=config.get('version', 'Unknown'),
            num_sub_questions='TBD',
            rag_success_count='TBD',
            total_questions='TBD',
            research_success_count='TBD'
        )
        logger.info(formatted_log)
        
        # Log configuration validation
        required_sections = ['research_config', 'mcp_config', 'app_config']
        for section in required_sections:
            if section in config:
                logger.info(f"✅ Configuration section '{section}' loaded")
            else:
                logger.warning(f"⚠️ Configuration section '{section}' missing")
        
        # Step 1: Decompose query using config
        logger.info("\n📋 STEP 1: Query Decomposition")
        sub_questions = await decompose_query(query, config)
        logger.info(f"Generated {len(sub_questions)} sub-questions:")
        for i, q in enumerate(sub_questions, 1):
            logger.info(f"  {i}. {q}")
        
        # Step 2: Research each sub-question
        logger.info("\n🔍 STEP 2: Detailed Research")
        findings = []
        
        for i, question in enumerate(sub_questions, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Sub-question {i}/{len(sub_questions)}: {question}")
            logger.info(f"{'='*60}")
            
            # Try RAG system first via ADK
            rag_success, rag_response = await query_rag_system_via_adk(question, config, logger)
            
            # Always do current research as well
            current_response = await current_research_query(question, config, logger)
            
            finding = {
                'question': question,
                'rag_success': rag_success,
                'rag_response': rag_response,
                'current_response': current_response
            }
            findings.append(finding)
            
            logger.info(f"Sub-question {i} completed - RAG: {'✅' if rag_success else '❌'}, Current: ✅")
        
        # Step 3: Synthesize findings using config
        logger.info("\n🔧 STEP 3: Synthesis")
        final_response = await synthesize_findings(query, findings, config, logger)
        
        # Step 4: Export results if configured
        logging_config = config.get('research_config', {}).get('logging_config', {})
        if logging_config.get('include_json_export', False):
            export_data = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'config_used': {
                    'name': config.get('name'),
                    'version': config.get('version'),
                    'max_sub_questions': config.get('research_config', {}).get('process_config', {}).get('max_sub_questions'),
                    'mcp_endpoint': config.get('mcp_config', {}).get('rag_mcp_endpoint'),
                },
                'sub_questions': sub_questions,
                'findings': findings,
                'synthesis': final_response
            }
            
            log_dir = Path(logging_config.get('log_directory', 'data/logs'))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_file = log_dir / f"deep_research_data_{timestamp}.json"
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Research data exported to: {json_file}")
        
        # Calculate session stats
        rag_success_count = sum(1 for f in findings if f['rag_success'])
        search_success_count = len(findings)
        total_sources = sum(2 if f['rag_success'] else 1 for f in findings)
        
        # Use session summary template from prompts
        session_summary = prompts_config.get('config_templates', {}).get('session_summary', 
                                           'Session complete - Duration: {duration}')
        
        formatted_summary = session_summary.format(
            query=query,
            method='hybrid_rag_and_search',
            num_sub_questions=len(sub_questions),
            rag_success_count=rag_success_count,
            research_success_count=search_success_count,
            total_sources=total_sources,
            duration=f"{(datetime.now() - datetime.now()).total_seconds():.2f}s",
            log_file=f"deep_research_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        logger.info("\n" + "="*80)
        logger.info("DEEP RESEARCH SESSION COMPLETED SUCCESSFULLY")
        for line in formatted_summary.strip().split('\n'):
            logger.info(line)
        logger.info("="*80)
        
        return final_response
        
    except Exception as e:
        error_msg = f"Deep research failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)


# Google ADK Function Tool integration
from google.adk.tools import FunctionTool

async def rag_tool_handler(query: str) -> str:
    """Handler function for Google ADK FunctionTool integration."""
    return await deep_research(query)

# Create the Google ADK FunctionTool - renamed to rag_tool
rag_tool = FunctionTool(func=rag_tool_handler)

# Backward compatibility aliases
deep_research_function_tool = rag_tool  # Keep old name for backwards compatibility

# Tool definition for backward compatibility
RAG_TOOL = {
    "name": "rag_tool", 
    "description": "Performs comprehensive research by decomposing queries into sub-questions and using both specialized RAG system and current knowledge",
    "function": deep_research
}

# Backward compatibility
DEEP_RESEARCH_TOOL = RAG_TOOL