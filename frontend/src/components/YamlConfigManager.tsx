import { useState, useCallback, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Label } from "@/components/ui/label";
import { Upload, Download, Save, RefreshCw, FileText, CheckCircle, AlertCircle, File, X } from "lucide-react";
import { useDropzone } from "react-dropzone";
import { useToast } from "@/hooks/use-toast";
import Editor from "@monaco-editor/react";
import yaml from "js-yaml";

interface YamlFile {
    name: string;
    content: string;
    isValid: boolean;
    error?: string;
    lastModified?: Date;
    warnings?: string[];
}

interface InputFile {
    name: string;
    content: string;
    type: string;
    size: number;
    lastModified: Date;
}

interface ExistingInputFile {
    name: string;
    size: number;
    type: string;
    last_modified: string;
    path: string;
}

interface InputFilesResponse {
    files: ExistingInputFile[];
    total_count: number;
    total_size: number;
}

interface YamlConfigManagerProps {
    onConfigurationReady: (configs: Record<string, YamlFile>, inputFiles?: InputFile[]) => void;
    isDisabled?: boolean;
}

// Required keys for each configuration type
const REQUIRED_KEYS = {
    workflow: {
        required: ['name', 'description', 'version', 'main_agent', 'agents'],
        nested: {
            'agents[]': ['name', 'type', 'description'],
            'api_config': ['provider', 'model'],
        },
        description: {
            name: 'Workflow name',
            description: 'Workflow description',
            version: 'Version number',
            main_agent: 'Main orchestrating agent name',
            agents: 'List of workflow agents',
            'agents[].name': 'Agent name',
            'agents[].type': 'Agent type (LlmAgent, SequentialAgent, etc.)',
            'agents[].description': 'Agent description'
        }
    },
    gemini: {
        required: ['api_config'],
        nested: {
            'api_config': ['provider', 'model'],
        },
        description: {
            api_config: 'API configuration section',
            'api_config.provider': 'API provider (should be "gemini")',
            'api_config.model': 'Gemini model name'
        }
    },
    prompts: {
        required: [],
        nested: {},
        description: {},
        customValidation: (data: any) => {
            const errors: string[] = [];
            const warnings: string[] = [];

            if (!data || typeof data !== 'object') {
                errors.push('Prompts configuration must be an object');
                return { errors, warnings };
            }

            // Check for common prompt patterns
            const commonAgents = ['requirement_analyzer', 'architectural_designer', 'code_generator'];
            let hasPrompts = false;

            Object.keys(data).forEach(key => {
                if (typeof data[key] === 'object' && data[key] !== null) {
                    hasPrompts = true;
                    const prompt = data[key];

                    if (!prompt.system && !prompt.template) {
                        warnings.push(`Prompt '${key}' should have either 'system' or 'template' field`);
                    }

                    if (prompt.template && typeof prompt.template !== 'string') {
                        errors.push(`Prompt '${key}' template must be a string`);
                    }

                    if (prompt.system && typeof prompt.system !== 'string') {
                        errors.push(`Prompt '${key}' system message must be a string`);
                    }
                }
            });

            if (!hasPrompts) {
                warnings.push('No prompt configurations found. Consider adding prompts for your agents.');
            }

            // Check for missing common agent prompts
            commonAgents.forEach(agent => {
                if (!data[agent]) {
                    warnings.push(`Missing prompt for common agent: ${agent}`);
                }
            });

            return { errors, warnings };
        }
    }
};

const DEFAULT_CONFIGS = {
    workflow: {
        name: "workflow_flexible.yml",
        content: `name: "Flexible Agent Workflow - Load Balanced"
description: "Advanced configurable workflow with load-balanced model distribution"
version: "0.2"

# Agent Configuration - main agent identifier
agent_config:
  name: "FlexiblePipelineAgent"
  description: "Orchestrates flexible workflows with load-balanced model distribution"

# API Configuration 
api_config:
  provider: "gemini"
  model: "gemini-2.0-flash-exp"
  temperature: 0.0
  max_tokens: 4096
  timeout: 60

# Core Configuration (standardized across all agents)
core_config:
  model: "gemini-2.5-flash"
  temperature: 0.0
  max_tokens: 4096
  timeout: 60

# App Configuration (standardized across all agents)
app_config:
  app_name: "flexible_agent_app"
  user_id: "flexible_user"
  session_id: "flexible_session"
  output_dir: "backend/output"

# Main agent orchestrating the workflow
main_agent: "MainFlexibleOrchestrator"

# Flexible workflow agents with LOAD-BALANCED model distribution
agents:
  # Individual LLM Agents - ALL USING SAME MODEL TO AVOID QUOTA LIMITS
  - name: "RequirementAnalyzer"
    type: "LlmAgent"
    model: "gemini-2.5-flash"
    description: "Analyzes user requirements and creates specifications"
    prompt_key: "requirement_analyzer"
    output_key: "analyzed_requirements"
    input_keys: 
      - "coding_standards.docx"
      - "project_requirements.txt"
      - "test.xlsx"
      - "test_ppt.pptx"
    parameters:
      temperature: 0.0
      max_tokens: 2048
    tools: ["text_analyzer"]

  - name: "ArchitecturalDesigner"
    type: "LlmAgent"
    model: "gemini-2.5-flash"
    description: "Designs system architecture based on requirements"
    prompt_key: "architectural_designer"
    output_key: "system_architecture"
    input_key: null
    parameters:
      temperature: 0.0
      max_tokens: 4096

  - name: "CodeGenerator"
    type: "LlmAgent"
    model: "gemini-2.5-flash"
    description: "Generates code based on architecture and requirements"
    prompt_key: "code_generator"
    output_key: "generated_code"
    input_key: null
    parameters:
      temperature: 0.0
      max_tokens: 4096
    tools: ["code_formatter"]

  # Parallel agents for code review - ALL USING SAME MODEL FOR CONSISTENCY
  - name: "SecurityReviewer"
    type: "LlmAgent"
    model: "gemini-2.5-flash"
    description: "Reviews code for security vulnerabilities"
    prompt_key: "security_reviewer"
    output_key: "security_review"
    input_key: null
    parameters:
      temperature: 0.0
      max_tokens: 1024

  - name: "PerformanceReviewer"
    type: "LlmAgent"
    model: "gemini-2.5-flash"
    description: "Reviews code for performance optimization"
    prompt_key: "performance_reviewer"
    output_key: "performance_review"
    input_key: null
    parameters:
      temperature: 0.0
      max_tokens: 1024

  - name: "QualityReviewer"
    type: "LlmAgent"
    model: "gemini-2.5-flash"
    description: "Reviews code quality and best practices"
    prompt_key: "quality_reviewer"
    output_key: "quality_review"
    input_key: null
    parameters:
      temperature: 0.0
      max_tokens: 1024

  # Parallel agent orchestrator
  - name: "ParallelReviewOrchestrator"
    type: "ParallelAgent"
    model: "gemini-2.5-flash"
    description: "Orchestrates parallel code reviews using same model for consistency"
    sub_agents: ["SecurityReviewer", "PerformanceReviewer", "QualityReviewer"]

  # Code refactorer
  - name: "CodeRefactorer"
    type: "LlmAgent"
    model: "gemini-2.5-flash"
    description: "Refactors code based on review feedback"
    prompt_key: "code_refactorer"
    output_key: "refactored_code"
    input_key: null
    parameters:
      temperature: 0.0
      max_tokens: 4096
    tools: ["code_formatter", "data_validator"]

  # Documentation generator
  - name: "DocumentationGenerator"
    type: "LlmAgent"
    model: "gemini-2.5-flash"
    description: "Generates comprehensive documentation"
    prompt_key: "documentation_generator"
    output_key: "documentation"
    input_key: null
    parameters:
      temperature: 0.1
      max_tokens: 4096
    tools: ["text_processor"]

  # Main orchestrator - runs everything sequentially
  - name: "MainFlexibleOrchestrator"
    type: "SequentialAgent"
    description: "Main flexible workflow orchestrator with load balancing"
    sub_agents: 
      - "RequirementAnalyzer"
      - "ArchitecturalDesigner"
      - "CodeGenerator"
      - "ParallelReviewOrchestrator"
      - "CodeRefactorer"
      - "DocumentationGenerator"

# Model strategy explanation
model_strategy:
  gemini-2.5-flash:
    agents: ["RequirementAnalyzer", "ArchitecturalDesigner", "CodeGenerator", "SecurityReviewer", "PerformanceReviewer", "QualityReviewer", "CodeRefactorer", "DocumentationGenerator"]
    use_case: "All tasks using experimental model to avoid quota limits"
    benefits:
      - "Avoids quota exhaustion on 1.5-pro model"
      - "Uses latest experimental features"
      - "Simplified configuration with single model"
      - "Consistent performance across all agents"
    concurrent_capacity: "High - experimental model with potentially higher quotas"

# Flexible-specific configuration
flexible_config:
  enable_parallel_processing: true
  enable_loop_workflows: false
  max_loop_iterations: 5
  supported_agent_types:
    - "LlmAgent"
    - "SequentialAgent"
    - "ParallelAgent"
    - "LoopAgent"
  languages:
    - "python"
    - "javascript"
    - "typescript"
    - "java"
    - "go"
  enable_linting: true
  enable_testing: true
  enable_documentation: true
  code_style: "pythonic"
  
  # Model fallback settings
  model_fallbacks:
    enabled: true
    retry_with_fallback_model: true
    fallback_models:
      gemini-2.0-flash-exp: ["gemini-1.5-flash", "gemini-2.0-flash"]
      gemini-2.0-flash: ["gemini-1.5-flash"]
      gemini-1.5-flash: ["gemini-1.0-pro"]

metadata:
  created_at: "2024-12-20"
  author: "System"
  agent_type: "flexible"
  description: "Flexible workflow using gemini-2.0-flash-exp to avoid quota limits"
  tags:
    - "flexible-architecture"
    - "multi-agent"
    - "parallel-processing"
    - "quota-optimized"
    - "experimental-model"
    - "fault-tolerant"
    - "code-generation"
    - "code-review"
    - "documentation"`,
        isValid: true,
    },
    gemini: {
        name: "gemini_config_flexible.yml",
        content: `# Gemini API Configuration for Flexible Agent Workflow
# This file contains configuration for Google's Gemini API integration

# API Configuration
api_config:
  provider: "gemini"
  
  # API Key - Set your Google API key here
  # You can also set this via environment variable: GOOGLE_API_KEY
  api_key: "AIzaSyCs7T6qdSPA3r16W_q01fCzKZvn-5DAioI"
  
  # Default model to use
  default_model: "gemini-2.0-flash"
  
  # API endpoints
  base_url: "https://generativelanguage.googleapis.com"
  api_version: "v1beta"

# Model Configuration
model_config:
  # Available models with their configurations
  models:
    gemini-1.5-pro:
      max_tokens: 8192
      supports_tools: true
      supports_multimodal: true
      cost_tier: "premium"
      
    gemini-1.5-flash:
      max_tokens: 4096
      supports_tools: true
      supports_multimodal: true
      cost_tier: "standard"
      
    gemini-1.0-pro:
      max_tokens: 4096
      supports_tools: false
      supports_multimodal: false
      cost_tier: "basic"

# Performance Configuration
performance_config:
  # Request timeout in seconds
  timeout_seconds: 120
  
  # Retry configuration
  max_retries: 3
  retry_delay: 1.0
  backoff_factor: 2.0
  
  # Rate limiting
  max_requests_per_minute: 60
  max_tokens_per_minute: 32000
  
  # Connection pooling
  max_connections: 10
  keep_alive: true

# Security Configuration
security_config:
  # Validate SSL certificates
  verify_ssl: true
  
  # Content filtering
  enable_safety_settings: true
  
  # Block categories (adjust as needed)
  safety_settings:
    HARM_CATEGORY_HARASSMENT: "BLOCK_MEDIUM_AND_ABOVE"
    HARM_CATEGORY_HATE_SPEECH: "BLOCK_MEDIUM_AND_ABOVE"
    HARM_CATEGORY_SEXUALLY_EXPLICIT: "BLOCK_MEDIUM_AND_ABOVE"
    HARM_CATEGORY_DANGEROUS_CONTENT: "BLOCK_MEDIUM_AND_ABOVE"

# Generation Configuration Defaults
generation_config:
  # Default temperature for flexible agent workflows
  temperature: 0.0
  
  # Token limits
  max_output_tokens: 4096
  
  # Sampling parameters
  top_p: 0.95
  top_k: 40
  
  # Stop sequences
  stop_sequences: []
  
  # Candidate count
  candidate_count: 1

# Flexible Agent Specific Configuration
flexible_agent_config:
  # Model selection strategy for different agent types
  agent_model_mapping:
    RequirementAnalyzer: "gemini-2.0-flash"
    ArchitecturalDesigner: "gemini-2.0-flash"
    CodeGenerator: "gemini-2.0-flash"
    SecurityReviewer: "gemini-2.0-flash"
    PerformanceReviewer: "gemini-2.0-flash"
    QualityReviewer: "gemini-2.0-flash"
    CodeRefactorer: "gemini-2.0-flash"
    DocumentationGenerator: "gemini-2.0-flash"
    
  # Temperature settings for different agent types
  agent_temperature_mapping:
    RequirementAnalyzer: 0.1
    ArchitecturalDesigner: 0.0
    CodeGenerator: 0.0
    SecurityReviewer: 0.0
    PerformanceReviewer: 0.0
    QualityReviewer: 0.0
    CodeRefactorer: 0.0
    DocumentationGenerator: 0.1
    
  # Enable/disable features per agent type
  agent_features:
    parallel_processing: true
    tool_calling: true
    multimodal_input: false
    streaming_response: false

# Logging Configuration
logging_config:
  # Log level for API calls
  log_level: "INFO"
  
  # Log API requests and responses
  log_requests: true
  log_responses: false
  
  # Log file location
  log_file: "flexible_agent_api.log"
  
  # Log rotation
  max_log_size_mb: 100
  backup_count: 5

# Development Configuration
development_config:
  # Enable debug mode
  debug_mode: false
  
  # Mock API responses for testing
  mock_responses: false
  
  # Validate configurations on startup
  validate_config: true
  
  # Enable metrics collection
  enable_metrics: true

# Monitoring Configuration
monitoring_config:
  # Track API usage
  track_usage: true
  
  # Usage limits and alerts
  daily_token_limit: 1000000
  alert_threshold: 0.8
  
  # Performance monitoring
  track_latency: true
  track_errors: true
  
  # Health check configuration
  health_check_interval: 300
  health_check_timeout: 30

metadata:
  created_at: "2024-12-20"
  version: "2.0.0"
  description: "Gemini API configuration for flexible agent workflow system"
  author: "System"`,
        isValid: true,
    },
    prompts: {
        name: "prompts_flexible.yml",
        content: `prompts:
  # Requirement Analyzer Agent
  requirement_analyzer: |
    You are a Senior Business Analyst and Requirements Engineer. Your task is to analyze user requirements and create detailed, structured specifications.
    
    **Your responsibilities:**
    1. Parse and understand user requirements thoroughly
    2. Identify functional and non-functional requirements
    3. Clarify ambiguities and ask relevant questions
    4. Create structured requirement specifications
    5. Identify potential risks and constraints
    6. Suggest best practices and industry standards
    
    **Output Format:**
    Please provide your analysis in the following structured format:
    
    ## Requirements Analysis
    
    ### Functional Requirements
    - List all functional requirements clearly
    
    ### Non-Functional Requirements
    - Performance requirements
    - Security requirements
    - Scalability requirements
    - Usability requirements
    
    ### Technical Constraints
    - Technology stack preferences
    - Platform constraints
    - Integration requirements
    
    ### Assumptions and Clarifications
    - Any assumptions made
    - Questions that need clarification
    
    ### Risk Assessment
    - Potential technical risks
    - Mitigation strategies
    
    Based on the user's request, provide a comprehensive analysis following the format above.

  # Architectural Designer Agent
  architectural_designer: |
    You are a Senior Software Architect with expertise in designing scalable, maintainable systems. Your task is to create a comprehensive system architecture based on the analyzed requirements.
    
    **Your responsibilities:**
    1. Design overall system architecture
    2. Select appropriate design patterns and architectural patterns
    3. Define component interactions and interfaces
    4. Consider scalability, performance, and maintainability
    5. Choose appropriate technologies and frameworks
    6. Create clear architectural documentation
    
    **Design Principles to Follow:**
    - SOLID principles
    - Clean Architecture
    - Microservices where appropriate
    - Domain-Driven Design
    - Security by Design
    - Performance optimization
    
    **Output Format:**
    Please provide your architectural design in the following format:
    
    ## System Architecture Design
    
    ### High-Level Architecture
    - Overall system design and components
    - Architecture pattern (e.g., layered, microservices, event-driven)
    
    ### Component Design
    - Core components and their responsibilities
    - Component interfaces and contracts
    - Data flow between components
    
    ### Technology Stack
    - Programming languages and frameworks
    - Databases and storage solutions
    - Infrastructure and deployment considerations
    
    ### Design Patterns
    - Architectural patterns used
    - Design patterns for implementation
    
    ### Quality Attributes
    - How the design addresses scalability
    - Security considerations
    - Performance optimizations
    - Maintainability features
    
    **Requirements Context:**
    {analyzed_requirements:No requirements analysis available yet. Please design based on the user request.}
    
    Create a detailed architectural design following the format above.

  # Code Generator Agent
  code_generator: |
    You are an Expert Software Developer with mastery in multiple programming languages and frameworks. Your task is to generate high-quality, production-ready code based on the architectural design and requirements.
    
    **Your responsibilities:**
    1. Write clean, efficient, and maintainable code
    2. Follow language-specific best practices and conventions
    3. Implement proper error handling and logging
    4. Include comprehensive type hints and documentation
    5. Write unit tests for critical functionality
    6. Ensure code follows SOLID principles
    
    **Code Quality Standards:**
    - Use meaningful variable and function names
    - Write self-documenting code with clear comments
    - Follow PEP 8 for Python (or equivalent for other languages)
    - Implement proper exception handling
    - Include comprehensive docstrings (Google style)
    - Use type hints throughout
    - Write modular, reusable code
    
    **Output Format:**
    Please provide your code implementation with the following structure:
    
    ## Code Implementation
    
    ### Project Structure
    \`\`\`
    project/
    ├── src/
    │   ├── __init__.py
    │   ├── main.py
    │   └── modules/
    └── tests/
        └── test_main.py
    \`\`\`
    
    ### Main Implementation
    \`\`\`python
    # Main code with proper imports, type hints, and documentation
    \`\`\`
    
    ### Supporting Modules
    \`\`\`python
    # Additional modules and utilities
    \`\`\`
    
    ### Unit Tests
    \`\`\`python
    # Comprehensive unit tests
    \`\`\`
    
    ### Installation and Usage Instructions
    \`\`\`bash
    # Setup and usage commands
    \`\`\`
    
    **Context from Previous Steps:**
    Architecture: {system_architecture:No architecture design available yet. Please design based on the requirements.}
    Requirements: {analyzed_requirements:No requirements analysis available yet. Please code based on the user request.}
    
    Generate complete, production-ready code following the format above.

  # Security Reviewer Agent
  security_reviewer: |
    You are a Cybersecurity Expert and Code Security Auditor. Your task is to perform a comprehensive security review of the provided code.
    
    **Your responsibilities:**
    1. Identify potential security vulnerabilities
    2. Review input validation and sanitization
    3. Check for proper authentication and authorization
    4. Analyze data handling and storage security
    5. Review error handling for information leakage
    6. Check for secure coding practices
    
    **Security Areas to Review:**
    - Input validation and injection attacks (SQL, XSS, etc.)
    - Authentication and session management
    - Authorization and access control
    - Data encryption and storage
    - Error handling and information disclosure
    - Dependency and third-party library security
    - Configuration and deployment security
    
    **Output Format:**
    ## Security Review Report
    
    ### Security Score: [1-10]
    
    ### Critical Issues (High Priority)
    - List any critical security vulnerabilities
    
    ### Medium Priority Issues
    - Security improvements needed
    
    ### Low Priority Issues
    - Minor security enhancements
    
    ### Security Best Practices Followed
    - Positive security practices identified
    
    ### Recommendations
    - Specific actionable recommendations
    - Security tools and libraries to consider
    
    ### Compliance Notes
    - OWASP Top 10 considerations
    - Industry standard compliance
    
    **Context for Review:**
    Code to Review: {generated_code:No code has been generated yet. Please provide a general security analysis based on the architecture and requirements.}
    System Architecture: {system_architecture:Not available}
    Requirements: {analyzed_requirements:Not available}
    
    Provide a comprehensive security analysis following the format above.

  # Performance Reviewer Agent
  performance_reviewer: |
    You are a Performance Engineering Expert specializing in code optimization and system performance analysis. Your task is to review code for performance bottlenecks and optimization opportunities.
    
    **Your responsibilities:**
    1. Identify performance bottlenecks and inefficiencies
    2. Analyze algorithmic complexity (Big O)
    3. Review memory usage and potential leaks
    4. Check for proper use of data structures
    5. Identify opportunities for caching and optimization
    6. Review database queries and I/O operations
    
    **Performance Areas to Analyze:**
    - Algorithmic efficiency and complexity
    - Memory usage and garbage collection
    - I/O operations and database queries
    - Concurrency and parallelization opportunities
    - Caching strategies
    - Network and API call efficiency
    - Resource utilization
    
    **Output Format:**
    ## Performance Review Report
    
    ### Performance Score: [1-10]
    
    ### Critical Performance Issues
    - Major bottlenecks that need immediate attention
    
    ### Optimization Opportunities
    - Areas where performance can be improved
    
    ### Algorithmic Analysis
    - Time and space complexity analysis
    - Suggestions for better algorithms/data structures
    
    ### Resource Utilization
    - Memory usage patterns
    - CPU utilization efficiency
    - I/O operation efficiency
    
    ### Scalability Assessment
    - How well the code will scale with increased load
    - Horizontal and vertical scaling considerations
    
    ### Recommendations
    - Specific performance improvement suggestions
    - Tools and techniques for optimization
    - Monitoring and profiling recommendations
    
    **Context for Review:**
    Code to Review: {generated_code:No code has been generated yet. Please provide a general performance analysis based on the architecture and requirements.}
    System Architecture: {system_architecture:Not available}
    Requirements: {analyzed_requirements:Not available}
    
    Provide a detailed performance analysis following the format above.

  # Quality Reviewer Agent
  quality_reviewer: |
    You are a Senior Code Quality Expert and Technical Lead. Your task is to perform a comprehensive code quality review focusing on maintainability, readability, and best practices.
    
    **Your responsibilities:**
    1. Review code structure and organization
    2. Check adherence to coding standards and conventions
    3. Evaluate code readability and maintainability
    4. Review documentation and comments
    5. Check for proper error handling
    6. Assess test coverage and quality
    
    **Quality Areas to Review:**
    - Code structure and modularity
    - Naming conventions and clarity
    - Documentation and comments
    - Error handling and logging
    - Test coverage and quality
    - Adherence to SOLID principles
    - Code duplication and reusability
    
    **Output Format:**
    ## Code Quality Review Report
    
    ### Quality Score: [1-10]
    
    ### Strengths
    - Well-implemented aspects of the code
    
    ### Areas for Improvement
    - Code quality issues that need attention
    
    ### Code Structure
    - Organization and modularity assessment
    - Design pattern usage
    
    ### Documentation
    - Quality of comments and docstrings
    - README and inline documentation
    
    ### Testing
    - Test coverage analysis
    - Test quality and comprehensiveness
    
    ### Maintainability
    - How easy is it to modify and extend the code
    - Technical debt assessment
    
    ### Recommendations
    - Specific improvements for better code quality
    - Tools and practices to adopt
    - Refactoring suggestions
    
    **Context for Review:**
    Code to Review: {generated_code:No code has been generated yet. Please provide a general code quality analysis based on the architecture and requirements.}
    System Architecture: {system_architecture:Not available}
    Requirements: {analyzed_requirements:Not available}
    
    Provide a thorough code quality analysis following the format above.

  # Code Refactorer Agent
  code_refactorer: |
    You are a Refactoring Expert and Clean Code Specialist. Your task is to refactor code based on review feedback while maintaining functionality and improving quality, security, and performance.
    
    **Your responsibilities:**
    1. Refactor code based on review feedback
    2. Improve code structure and organization
    3. Enhance security and performance
    4. Maintain backward compatibility
    5. Update tests and documentation
    6. Follow clean code principles
    
    **Refactoring Principles:**
    - Preserve existing functionality
    - Improve code readability and maintainability
    - Eliminate code smells and anti-patterns
    - Enhance error handling and logging
    - Optimize performance where identified
    - Strengthen security measures
    
    **Output Format:**
    ## Refactored Code Implementation
    
    ### Summary of Changes
    - Overview of refactoring performed
    - Key improvements made
    
    ### Refactored Code
    \`\`\`python
    # Complete refactored implementation
    \`\`\`
    
    ### Security Improvements
    - Security vulnerabilities addressed
    - New security measures implemented
    
    ### Performance Optimizations
    - Performance improvements made
    - Optimization techniques applied
    
    ### Quality Enhancements
    - Code quality improvements
    - Better error handling and logging
    
    ### Updated Tests
    \`\`\`python
    # Updated and new unit tests
    \`\`\`
    
    ### Migration Guide
    - How to migrate from old to new implementation
    - Breaking changes (if any)
    
    **Context and Review Inputs:**
    Original Code: {generated_code:No code has been generated yet. Please create a new implementation based on the architecture and requirements.}
    System Architecture: {system_architecture:Not available}
    Requirements: {analyzed_requirements:Not available}
    Security Review: {security_review:No security review available yet}
    Performance Review: {performance_review:No performance review available yet}
    Quality Review: {quality_review:No quality review available yet}
    
    Provide refactored code that addresses all identified issues.

  # Documentation Generator Agent
  documentation_generator: |
    You are a Technical Writing Expert and Documentation Specialist. Your task is to create comprehensive, user-friendly documentation for the developed software.
    
    **Your responsibilities:**
    1. Create clear, comprehensive documentation
    2. Write user guides and API documentation
    3. Provide setup and installation instructions
    4. Create code examples and tutorials
    5. Document architecture and design decisions
    6. Write troubleshooting guides
    
    **Documentation Standards:**
    - Clear, concise, and well-structured
    - Include practical examples
    - Cover all major features and use cases
    - Provide troubleshooting information
    - Include diagrams where helpful
    - Follow documentation best practices
    
    **Output Format:**
    ## Complete Documentation Package
    
    ### README.md
    \`\`\`markdown
    # Project Title
    
    ## Overview
    Brief description and features
    
    ## Installation
    Step-by-step setup instructions
    
    ## Quick Start
    Basic usage examples
    
    ## Features
    Detailed feature descriptions
    \`\`\`
    
    ### API Documentation
    \`\`\`markdown
    # API Reference
    
    ## Classes and Methods
    Detailed API documentation
    
    ## Examples
    Code examples for each major function
    \`\`\`
    
    ### User Guide
    \`\`\`markdown
    # User Guide
    
    ## Getting Started
    ## Advanced Usage
    ## Best Practices
    ## Troubleshooting
    \`\`\`
    
    ### Developer Guide
    \`\`\`markdown
    # Developer Guide
    
    ## Architecture Overview
    ## Contributing Guidelines
    ## Testing Instructions
    ## Deployment Guide
    \`\`\`
    
    ### Quality and Security Notes
    \`\`\`markdown
    # Quality and Security Report
    
    ## Code Quality Summary
    ## Security Assessment
    ## Performance Characteristics
    ## Known Limitations
    \`\`\`
    
    ### Changelog
    \`\`\`markdown
    # Changelog
    
    ## Version History
    ## Breaking Changes
    ## Migration Guides
    \`\`\`
    
    **Complete Context for Documentation:**
    Final Code: {refactored_code:No refactored code available yet. Please document based on the architecture and requirements.}
    System Architecture: {system_architecture:Not available}
    Requirements: {analyzed_requirements:Not available}
    Security Review Summary: {security_review:No security review available yet}
    Performance Review Summary: {performance_review:No performance review available yet}
    Quality Review Summary: {quality_review:No quality review available yet}
    
    Create comprehensive documentation following the format above.

metadata:
  created_at: "2024-12-20"
  version: "2.1.0"
  description: "Enhanced prompts for flexible agent workflow system with proper data flow"
  author: "System"
  agent_count: 7
  workflow_type: "flexible_multi_agent"
  data_flow_optimized: true
  tags:
    - "requirements-analysis"
    - "architectural-design"
    - "code-generation"
    - "security-review"
    - "performance-review"
    - "quality-review"
    - "code-refactoring"
    - "documentation"`,
        isValid: true,
    },
};

export const YamlConfigManager = ({ onConfigurationReady, isDisabled = false }: YamlConfigManagerProps) => {
    const [configs, setConfigs] = useState<Record<string, YamlFile>>(DEFAULT_CONFIGS);
    const [inputFiles, setInputFiles] = useState<InputFile[]>([]);
    const [activeTab, setActiveTab] = useState("workflow");
    const [isValidating, setIsValidating] = useState(false);
    const { toast } = useToast();
    const [existingFiles, setExistingFiles] = useState<ExistingInputFile[]>([]);
    const [loadingExistingFiles, setLoadingExistingFiles] = useState(false);

    // Fetch existing input files from backend
    const fetchExistingFiles = async () => {
        setLoadingExistingFiles(true);
        try {
            const response = await fetch('http://localhost:8000/api/v1/input-files');
            if (response.ok) {
                const data: InputFilesResponse = await response.json();
                setExistingFiles(data.files);
            } else {
                console.error('Failed to fetch existing input files');
            }
        } catch (error) {
            console.error('Error fetching existing input files:', error);
        } finally {
            setLoadingExistingFiles(false);
        }
    };

    // Fetch existing files when component mounts or when Input Files tab is selected
    useEffect(() => {
        if (activeTab === 'input-files') {
            fetchExistingFiles();
        }
    }, [activeTab]);

    const validateYamlContent = useCallback((content: string, configType: string): { isValid: boolean; error?: string; warnings?: string[] } => {
        try {
            const data = yaml.load(content);
            const config = REQUIRED_KEYS[configType as keyof typeof REQUIRED_KEYS];

            if (!config) {
                return { isValid: false, error: `Unknown configuration type: ${configType}` };
            }

            const errors: string[] = [];
            const warnings: string[] = [];

            // Custom validation for prompts
            if (configType === 'prompts' && config.customValidation) {
                const result = config.customValidation(data);
                errors.push(...result.errors);
                warnings.push(...result.warnings);
            } else {
                // Standard validation for other config types
                if (!data || typeof data !== 'object') {
                    return { isValid: false, error: 'Configuration must be a valid YAML object' };
                }

                // Check required top-level keys
                config.required.forEach(key => {
                    if (!(key in data)) {
                        errors.push(`Missing required key: '${key}' - ${config.description[key] || 'Required field'}`);
                    }
                });

                // Check nested required keys
                Object.entries(config.nested).forEach(([path, requiredKeys]) => {
                    if (path.endsWith('[]')) {
                        // Array validation
                        const arrayPath = path.slice(0, -2);
                        const arrayData = getNestedValue(data, arrayPath);

                        if (Array.isArray(arrayData)) {
                            arrayData.forEach((item, index) => {
                                if (typeof item === 'object' && item !== null) {
                                    requiredKeys.forEach(key => {
                                        if (!(key in item)) {
                                            errors.push(`Missing required key in ${arrayPath}[${index}]: '${key}' - ${config.description[`${arrayPath}[].${key}`] || 'Required field'}`);
                                        }
                                    });
                                }
                            });
                        }
                    } else {
                        // Object validation
                        const objectData = getNestedValue(data, path);
                        if (objectData && typeof objectData === 'object') {
                            requiredKeys.forEach(key => {
                                if (!(key in objectData)) {
                                    errors.push(`Missing required key in ${path}: '${key}' - ${config.description[`${path}.${key}`] || 'Required field'}`);
                                }
                            });
                        } else if (data[path] !== undefined) {
                            errors.push(`Expected '${path}' to be an object`);
                        }
                    }
                });

                // Workflow-specific validations
                if (configType === 'workflow') {
                    // Validate main_agent exists in agents list
                    if (data.main_agent && data.agents) {
                        const agentNames = data.agents.map((agent: any) => agent.name);
                        if (!agentNames.includes(data.main_agent)) {
                            errors.push(`Main agent '${data.main_agent}' not found in agents list`);
                        }
                    }

                    // Validate agent types
                    if (data.agents && Array.isArray(data.agents)) {
                        const validAgentTypes = ['LlmAgent', 'SequentialAgent', 'ParallelAgent', 'LoopAgent'];
                        data.agents.forEach((agent: any, index: number) => {
                            if (agent.type && !validAgentTypes.includes(agent.type)) {
                                errors.push(`Invalid agent type '${agent.type}' in agents[${index}]. Valid types: ${validAgentTypes.join(', ')}`);
                            }

                            // Check for duplicate agent names
                            const duplicates = data.agents.filter((a: any) => a.name === agent.name);
                            if (duplicates.length > 1) {
                                warnings.push(`Duplicate agent name '${agent.name}' found`);
                            }
                        });
                    }
                }

                // Gemini-specific validations
                if (configType === 'gemini') {
                    if (data.api_config?.provider && data.api_config.provider !== 'gemini') {
                        warnings.push(`Provider is '${data.api_config.provider}', expected 'gemini'`);
                    }

                    if (data.api_config?.model) {
                        const validModels = ['gemini-1.0-pro', 'gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-2.5-flash'];
                        if (!validModels.some(model => data.api_config.model.includes(model.split('-')[0]))) {
                            warnings.push(`Model '${data.api_config.model}' may not be a valid Gemini model`);
                        }
                    }
                }
            }

            if (errors.length > 0) {
                return {
                    isValid: false,
                    error: errors.join('; '),
                    warnings: warnings.length > 0 ? warnings : undefined
                };
            }

            return {
                isValid: true,
                warnings: warnings.length > 0 ? warnings : undefined
            };

        } catch (error) {
            return {
                isValid: false,
                error: error instanceof Error ? `YAML parsing error: ${error.message}` : "Invalid YAML format"
            };
        }
    }, []);

    // Helper function to get nested values
    function getNestedValue(obj: any, path: string): any {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }

    const updateConfig = useCallback((configType: string, content: string) => {
        const validation = validateYamlContent(content, configType);
        setConfigs(prev => ({
            ...prev,
            [configType]: {
                ...prev[configType],
                content,
                isValid: validation.isValid,
                error: validation.error,
                warnings: validation.warnings,
                lastModified: new Date(),
            }
        }));
    }, [validateYamlContent]);

    const onDrop = useCallback((acceptedFiles: File[], configType: string) => {
        acceptedFiles.forEach(file => {
            const reader = new FileReader();
            reader.onload = () => {
                const content = reader.result as string;
                updateConfig(configType, content);
                toast({
                    title: "File Uploaded",
                    description: `${file.name} has been loaded successfully`,
                });
            };
            reader.readAsText(file);
        });
    }, [updateConfig, toast]);

    const createDropzone = (configType: string) => {
        return useDropzone({
            onDrop: (files) => onDrop(files, configType),
            accept: {
                'text/yaml': ['.yml', '.yaml'],
                'text/plain': ['.txt']
            },
            multiple: false,
            disabled: isDisabled
        });
    };

    const downloadConfig = (configType: string) => {
        const config = configs[configType];
        const blob = new Blob([config.content], { type: 'text/yaml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = config.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        toast({
            title: "Download Complete",
            description: `${config.name} has been downloaded`,
        });
    };

    // Input file handling functions
    const onInputFileDrop = useCallback((acceptedFiles: File[]) => {
        acceptedFiles.forEach(file => {
            const reader = new FileReader();
            reader.onload = () => {
                const content = reader.result as string;
                const inputFile: InputFile = {
                    name: file.name,
                    content,
                    type: file.type || 'text/plain',
                    size: file.size,
                    lastModified: new Date(file.lastModified),
                };

                setInputFiles(prev => {
                    // Check if file already exists, replace if it does
                    const existingIndex = prev.findIndex(f => f.name === file.name);
                    if (existingIndex >= 0) {
                        const updated = [...prev];
                        updated[existingIndex] = inputFile;
                        return updated;
                    } else {
                        return [...prev, inputFile];
                    }
                });

                toast({
                    title: "Input File Uploaded",
                    description: `${file.name} has been added to input files`,
                });
            };
            reader.readAsText(file);
        });
    }, [toast]);

    const createInputFileDropzone = () => {
        return useDropzone({
            onDrop: onInputFileDrop,
            accept: {
                'text/plain': ['.txt', '.md', '.csv'],
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
                'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
                'application/pdf': ['.pdf'],
                'application/json': ['.json'],
                'text/yaml': ['.yml', '.yaml'],
            },
            multiple: true,
            disabled: isDisabled
        });
    };

    // Format file size for display
    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Handle file removal for both uploaded and existing files
    const removeInputFile = (fileName: string) => {
        // Check if it's an uploaded file
        const uploadedIndex = inputFiles.findIndex(f => f.name === fileName);
        if (uploadedIndex !== -1) {
            const updatedFiles = inputFiles.filter((_, index) => index !== uploadedIndex);
            setInputFiles(updatedFiles);
            onConfigurationReady(configs, updatedFiles);

            toast({
                title: "File Removed",
                description: `${fileName} has been removed.`,
            });
        } else {
            // For existing files, show a warning that they can't be removed through the UI
            toast({
                title: "Cannot Remove",
                description: "Existing server files cannot be removed through this interface.",
                variant: "destructive"
            });
        }
    };

    // Handle file download
    const downloadInputFile = (file: InputFile | { name: string; content: string; type: string; size: number; lastModified: Date }) => {
        // For uploaded files with content, download directly
        if ('content' in file && file.content) {
            const blob = new Blob([file.content], { type: file.type });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } else {
            // For existing server files, show a message that they should be downloaded from the server
            toast({
                title: "Download Not Available",
                description: "Please download existing server files directly from the backend/input directory.",
                variant: "default"
            });
        }
    };

    const validateAllConfigs = async () => {
        setIsValidating(true);

        // Simulate validation delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        const allValid = Object.values(configs).every(config => config.isValid);

        if (allValid) {
            onConfigurationReady(configs, inputFiles);
            toast({
                title: "Configuration Ready",
                description: `All YAML files are valid and ${inputFiles.length} input files are ready for workflow execution`,
            });
        } else {
            toast({
                title: "Configuration Invalid",
                description: "Please fix the YAML errors before proceeding",
                variant: "destructive",
            });
        }

        setIsValidating(false);
    };

    const resetToDefaults = () => {
        setConfigs(DEFAULT_CONFIGS);
        toast({
            title: "Reset Complete",
            description: "All configurations have been reset to defaults",
        });
    };

    const getStatusIcon = (config: YamlFile) => {
        if (config.isValid) {
            return <CheckCircle className="h-4 w-4 text-green-500" />;
        } else {
            return <AlertCircle className="h-4 w-4 text-red-500" />;
        }
    };

    const getStatusBadge = (config: YamlFile) => {
        if (config.isValid) {
            return <Badge className="bg-green-100 text-green-800">Valid</Badge>;
        } else {
            return <Badge className="bg-red-100 text-red-800">Invalid</Badge>;
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">YAML Configuration Manager</h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Upload, edit, and validate your workflow configuration files
                    </p>
                </div>
                <div className="flex space-x-2">
                    <Button variant="outline" onClick={resetToDefaults} disabled={isDisabled}>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Reset to Defaults
                    </Button>
                    <Button
                        onClick={validateAllConfigs}
                        disabled={isDisabled || isValidating}
                        className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
                    >
                        {isValidating ? (
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                            <CheckCircle className="w-4 h-4 mr-2" />
                        )}
                        {isValidating ? "Validating..." : "Validate & Ready"}
                    </Button>
                </div>
            </div>

            {/* Configuration Status */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <Card className="p-4">
                    <div className="flex items-center space-x-2">
                        <FileText className="w-5 h-5 text-blue-500" />
                        <div>
                            <p className="text-sm font-medium">Workflow Config</p>
                            <p className="text-xs text-gray-500">
                                {configs.workflow ? 'Loaded' : 'Default'}
                            </p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center space-x-2">
                        <FileText className="w-5 h-5 text-green-500" />
                        <div>
                            <p className="text-sm font-medium">LLM Config</p>
                            <p className="text-xs text-gray-500">
                                {configs.gemini ? 'Loaded' : 'Default'}
                            </p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center space-x-2">
                        <FileText className="w-5 h-5 text-purple-500" />
                        <div>
                            <p className="text-sm font-medium">Prompts Config</p>
                            <p className="text-xs text-gray-500">
                                {configs.prompts ? 'Loaded' : 'Default'}
                            </p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center space-x-2">
                        <File className="w-5 h-5 text-orange-500" />
                        <div>
                            <p className="text-sm font-medium">Input Files</p>
                            <p className="text-xs text-gray-500">
                                {inputFiles.length} uploaded, {existingFiles.length} existing
                            </p>
                        </div>
                    </div>
                </Card>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid grid-cols-4 w-full mb-6">
                    <TabsTrigger value="workflow" className="text-sm">
                        Workflow Config
                    </TabsTrigger>
                    <TabsTrigger value="gemini" className="text-sm">
                        LLM Config
                    </TabsTrigger>
                    <TabsTrigger value="prompts" className="text-sm">
                        Prompts Config
                    </TabsTrigger>
                    <TabsTrigger value="input-files" className="text-sm">
                        Input Files ({inputFiles.length + existingFiles.length})
                    </TabsTrigger>
                </TabsList>

                {Object.entries(configs).map(([configType, config]) => {
                    const dropzone = createDropzone(configType);

                    return (
                        <TabsContent key={configType} value={configType} className="space-y-4">
                            <Card className="p-4">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-2">
                                        {getStatusIcon(config)}
                                        <Label className="font-semibold">{config.name}</Label>
                                        {config.lastModified && (
                                            <span className="text-xs text-gray-500">
                                                Modified: {config.lastModified.toLocaleTimeString()}
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex space-x-2">
                                        <Button variant="outline" size="sm" onClick={() => downloadConfig(configType)}>
                                            <Download className="w-4 h-4 mr-1" />
                                            Download
                                        </Button>
                                    </div>
                                </div>

                                {/* File Upload Area */}
                                <div
                                    {...dropzone.getRootProps()}
                                    className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${dropzone.isDragActive
                                        ? 'border-blue-400 bg-blue-50'
                                        : 'border-gray-300 hover:border-gray-400'
                                        } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                    <input {...dropzone.getInputProps()} />
                                    <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                                    <p className="text-sm text-gray-600">
                                        {dropzone.isDragActive
                                            ? 'Drop the YAML file here...'
                                            : 'Drag & drop a YAML file here, or click to select'}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">
                                        Supports .yml, .yaml, and .txt files
                                    </p>
                                </div>

                                {/* Error and Warning Display */}
                                {!config.isValid && config.error && (
                                    <Alert variant="destructive" className="mt-4">
                                        <AlertCircle className="h-4 w-4" />
                                        <AlertDescription>
                                            <div className="space-y-1">
                                                <div className="font-semibold">Configuration Error:</div>
                                                <div className="text-sm">{config.error}</div>
                                            </div>
                                        </AlertDescription>
                                    </Alert>
                                )}

                                {config.warnings && config.warnings.length > 0 && (
                                    <Alert className="mt-4 border-yellow-200 bg-yellow-50">
                                        <AlertCircle className="h-4 w-4 text-yellow-600" />
                                        <AlertDescription>
                                            <div className="space-y-1">
                                                <div className="font-semibold text-yellow-800">Configuration Warnings:</div>
                                                <ul className="text-sm text-yellow-700 space-y-1">
                                                    {config.warnings.map((warning, index) => (
                                                        <li key={index} className="flex items-start">
                                                            <span className="mr-2">•</span>
                                                            <span>{warning}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        </AlertDescription>
                                    </Alert>
                                )}

                                {/* YAML Editor */}
                                <div className="mt-4">
                                    <Label className="text-sm font-medium">Edit Configuration</Label>
                                    <div className="mt-2 border rounded-md overflow-hidden">
                                        <Editor
                                            height="400px"
                                            language="yaml"
                                            theme="vs-dark"
                                            value={config.content}
                                            onChange={(value) => value && updateConfig(configType, value)}
                                            options={{
                                                minimap: { enabled: false },
                                                scrollBeyondLastLine: false,
                                                fontSize: 14,
                                                wordWrap: 'on',
                                                lineNumbers: 'on',
                                                readOnly: isDisabled,
                                            }}
                                        />
                                    </div>
                                </div>
                            </Card>
                        </TabsContent>
                    );
                })}

                {/* Input Files Tab */}
                <TabsContent value="input-files" className="space-y-4">
                    <Card className="p-4">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-2">
                                <File className="h-4 w-4 text-blue-500" />
                                <Label className="font-semibold">Input Files</Label>
                                <Badge className="bg-blue-100 text-blue-800">
                                    {inputFiles.length} files
                                </Badge>
                            </div>
                        </div>

                        {/* Input File Upload Area */}
                        <div>
                            {(() => {
                                const inputDropzone = createInputFileDropzone();
                                return (
                                    <div
                                        {...inputDropzone.getRootProps()}
                                        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${inputDropzone.isDragActive
                                            ? 'border-green-400 bg-green-50'
                                            : 'border-gray-300 hover:border-gray-400'
                                            } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    >
                                        <input {...inputDropzone.getInputProps()} />
                                        <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                                        <p className="text-sm text-gray-600">
                                            {inputDropzone.isDragActive
                                                ? 'Drop input files here...'
                                                : 'Drag & drop input files here, or click to select'}
                                        </p>
                                        <p className="text-xs text-gray-500 mt-1">
                                            Supports .txt, .md, .csv, .docx, .xlsx, .pptx, .pdf, .json, .yml files
                                        </p>
                                    </div>
                                );
                            })()}
                        </div>

                        {/* Input Files List */}
                        {inputFiles.length > 0 && (
                            <div className="mt-4">
                                <Label className="text-sm font-medium mb-2 block">Uploaded Files</Label>
                                <ScrollArea className="h-64 border rounded-md p-2">
                                    <div className="space-y-2">
                                        {inputFiles.map((file, index) => (
                                            <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded border">
                                                <div className="flex items-center space-x-3">
                                                    <File className="h-4 w-4 text-blue-500" />
                                                    <div className="flex-1 min-w-0">
                                                        <p className="text-sm font-medium text-gray-900 truncate">
                                                            {file.name}
                                                        </p>
                                                        <p className="text-xs text-gray-500">
                                                            {formatFileSize(file.size)}
                                                        </p>
                                                        <p className="text-xs text-gray-400">
                                                            Modified: {file.lastModified.toLocaleString()}
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="flex space-x-1">
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => downloadInputFile(file)}
                                                        disabled={isDisabled}
                                                    >
                                                        <Download className="w-3 h-3" />
                                                    </Button>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => removeInputFile(file.name)}
                                                        disabled={isDisabled}
                                                        className="text-red-600 hover:text-red-700"
                                                    >
                                                        <X className="w-3 h-3" />
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </ScrollArea>
                            </div>
                        )}

                        {/* Existing Files */}
                        {loadingExistingFiles ? (
                            <div className="mt-4">Loading existing files...</div>
                        ) : (
                            <div className="mt-4">
                                <Label className="text-sm font-medium mb-2 block">Existing Files</Label>
                                <ScrollArea className="h-64 border rounded-md p-2">
                                    <div className="space-y-2">
                                        {existingFiles.map((file, index) => (
                                            <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded border">
                                                <div className="flex items-center space-x-3">
                                                    <File className="h-4 w-4 text-blue-500" />
                                                    <div className="flex-1 min-w-0">
                                                        <p className="text-sm font-medium text-gray-900 truncate">
                                                            {file.name}
                                                        </p>
                                                        <p className="text-xs text-gray-500">
                                                            {formatFileSize(file.size)}
                                                        </p>
                                                        <p className="text-xs text-gray-400">
                                                            Modified: {new Date(file.last_modified).toLocaleString()}
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="flex space-x-1">
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => downloadInputFile({
                                                            name: file.name,
                                                            content: '',
                                                            type: file.type,
                                                            size: file.size,
                                                            lastModified: new Date(file.last_modified)
                                                        })}
                                                        disabled={isDisabled}
                                                    >
                                                        <Download className="w-3 h-3" />
                                                    </Button>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => removeInputFile(file.name)}
                                                        disabled={isDisabled}
                                                        className="text-red-600 hover:text-red-700"
                                                    >
                                                        <X className="w-3 h-3" />
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </ScrollArea>
                            </div>
                        )}

                        {/* Usage Instructions */}
                        <Alert className="mt-4 border-blue-200 bg-blue-50">
                            <File className="h-4 w-4 text-blue-600" />
                            <AlertDescription>
                                <div className="space-y-1">
                                    <div className="font-semibold text-blue-800">How to Reference Input Files:</div>
                                    <div className="text-sm text-blue-700">
                                        <p>Reference these files in your workflow configuration using the <code>input_keys</code> field:</p>
                                        <pre className="mt-2 p-2 bg-blue-100 rounded text-xs">
                                            {`input_keys:
  - "${inputFiles.length > 0 ? inputFiles[0].name : 'your-file.txt'}"
  - "requirements.pdf"
  - "data.xlsx"`}
                                        </pre>
                                    </div>
                                </div>
                            </AlertDescription>
                        </Alert>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}; 