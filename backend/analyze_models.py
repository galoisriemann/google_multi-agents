#!/usr/bin/env python3
"""
Model Analysis Utility for Flexible Agent Workflow

This script analyzes your workflow configuration to:
1. Show which models are used by each agent
2. Identify potential bottlenecks from model overload  
3. Provide recommendations for load balancing
4. Suggest alternative models for better reliability

Usage:
    python backend/analyze_models.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict, Counter

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.core.config.config_loader import ConfigLoader


class ModelAnalyzer:
    """Analyzes model usage across flexible workflow agents."""
    
    def __init__(self, config_dir: Path = None):
        """Initialize the model analyzer."""
        if config_dir is None:
            config_dir = Path(__file__).parent / "config" / "flexible_agent"
        
        self.config_dir = config_dir
        self.workflow_config = ConfigLoader(config_dir / "workflow_flexible.yml")
        self.gemini_config = ConfigLoader(config_dir / "gemini_config_flexible.yml")
        
        # Load configurations
        self.workflow_data = self.workflow_config.load_config()
        self.gemini_data = self.gemini_config.load_config()
    
    def analyze_model_usage(self) -> Dict[str, Any]:
        """Analyze model usage across all agents."""
        results = {
            "agents_by_model": defaultdict(list),
            "model_usage_count": Counter(),
            "agent_details": [],
            "recommendations": [],
            "potential_issues": []
        }
        
        agents = self.workflow_data.get("agents", [])
        default_model = self.workflow_data.get("core_config", {}).get("model", "gemini-1.5-flash")
        
        for agent in agents:
            agent_name = agent.get("name", "Unknown")
            agent_type = agent.get("type", "Unknown")
            agent_model = agent.get("model", default_model)
            
            # Record model usage
            results["agents_by_model"][agent_model].append(agent_name)
            results["model_usage_count"][agent_model] += 1
            
            # Store agent details
            agent_detail = {
                "name": agent_name,
                "type": agent_type,
                "model": agent_model,
                "description": agent.get("description", ""),
                "temperature": agent.get("parameters", {}).get("temperature", 0.0),
                "max_tokens": agent.get("parameters", {}).get("max_tokens", 4096),
                "tools": agent.get("tools", [])
            }
            results["agent_details"].append(agent_detail)
        
        # Analyze potential issues
        self._analyze_potential_issues(results)
        
        # Generate recommendations
        self._generate_recommendations(results)
        
        return results
    
    def _analyze_potential_issues(self, results: Dict[str, Any]) -> None:
        """Identify potential issues with current model configuration."""
        model_counts = results["model_usage_count"]
        
        for model, count in model_counts.items():
            if count > 5:
                results["potential_issues"].append({
                    "type": "high_load_risk",
                    "model": model,
                    "agent_count": count,
                    "description": f"Model '{model}' is used by {count} agents. Risk of overload during parallel execution.",
                    "severity": "high" if count > 8 else "medium"
                })
            
            # Check if using newest/experimental models
            if "2.0" in model:
                results["potential_issues"].append({
                    "type": "experimental_model",
                    "model": model,
                    "description": f"Model '{model}' is newer and might have higher failure rates or be overloaded.",
                    "severity": "medium"
                })
        
        # Check for single model dependency
        if len(model_counts) == 1:
            results["potential_issues"].append({
                "type": "single_point_failure",
                "description": "All agents use the same model. If this model goes down, entire workflow fails.",
                "severity": "high"
            })
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> None:
        """Generate recommendations for better model distribution."""
        model_counts = results["model_usage_count"]
        
        # Recommend model diversification
        if len(model_counts) <= 2:
            results["recommendations"].append({
                "type": "diversification",
                "title": "Diversify Model Usage",
                "description": "Consider using different models for different agent types to reduce load and improve reliability.",
                "suggested_models": {
                    "heavy_tasks": ["gemini-1.5-pro"],
                    "light_tasks": ["gemini-1.5-flash", "gemini-1.0-pro"],
                    "parallel_agents": ["gemini-1.5-flash"]
                }
            })
        
        # Recommend load balancing for heavily used models
        overused_models = [model for model, count in model_counts.items() if count > 5]
        if overused_models:
            results["recommendations"].append({
                "type": "load_balancing",
                "title": "Balance Model Load",
                "description": f"Models {overused_models} are overused. Consider distributing agents across multiple models.",
                "action": "Move some agents to alternative models like gemini-1.5-flash or gemini-1.0-pro"
            })
        
        # Recommend fallback strategies
        results["recommendations"].append({
            "type": "fallback_strategy",
            "title": "Implement Model Fallbacks",
            "description": "Configure backup models for when primary models are overloaded.",
            "implementation": "Add fallback_models configuration to each agent"
        })
        
        # Recommend retry strategies
        results["recommendations"].append({
            "type": "retry_strategy", 
            "title": "Configure Retries and Backoff",
            "description": "Implement exponential backoff for overloaded model errors.",
            "implementation": "Increase max_retries and backoff_factor in gemini_config_flexible.yml"
        })
    
    def get_alternative_models(self, current_model: str) -> List[str]:
        """Get list of alternative models based on current model."""
        alternatives = {
            "gemini-2.0-flash": ["gemini-1.5-flash", "gemini-1.5-pro"],
            "gemini-1.5-pro": ["gemini-1.5-flash", "gemini-2.0-flash"],
            "gemini-1.5-flash": ["gemini-1.0-pro", "gemini-1.5-pro"],
            "gemini-1.0-pro": ["gemini-1.5-flash"]
        }
        return alternatives.get(current_model, ["gemini-1.5-flash"])
    
    def generate_balanced_config(self) -> Dict[str, Any]:
        """Generate a load-balanced version of the workflow configuration."""
        agents = self.workflow_data.get("agents", [])
        balanced_agents = []
        
        # Model assignment strategy
        model_assignment = {
            "RequirementAnalyzer": "gemini-1.5-flash",      # Light analysis
            "ArchitecturalDesigner": "gemini-1.5-pro",     # Complex design thinking
            "CodeGenerator": "gemini-1.5-pro",             # Complex code generation
            "SecurityReviewer": "gemini-1.5-flash",        # Focused security checks
            "PerformanceReviewer": "gemini-1.5-flash",     # Focused performance checks
            "QualityReviewer": "gemini-1.5-flash",         # Focused quality checks
            "CodeRefactorer": "gemini-1.5-pro",            # Complex refactoring
            "DocumentationGenerator": "gemini-1.5-flash",   # Documentation writing
        }
        
        for agent in agents:
            balanced_agent = agent.copy()
            agent_name = agent.get("name", "")
            
            # Assign balanced model if agent is in our strategy
            if agent_name in model_assignment:
                balanced_agent["model"] = model_assignment[agent_name]
            
            # Adjust parameters based on model
            if balanced_agent.get("model") == "gemini-1.5-pro":
                # More powerful model, can handle more tokens
                if "parameters" not in balanced_agent:
                    balanced_agent["parameters"] = {}
                balanced_agent["parameters"]["max_tokens"] = min(
                    balanced_agent["parameters"].get("max_tokens", 4096), 8192
                )
            
            balanced_agents.append(balanced_agent)
        
        # Create balanced configuration
        balanced_config = self.workflow_data.copy()
        balanced_config["agents"] = balanced_agents
        balanced_config["metadata"]["version"] = "2.1.0-balanced"
        balanced_config["metadata"]["description"] += " (Load-balanced model distribution)"
        
        return balanced_config
    
    def print_analysis_report(self) -> None:
        """Print a comprehensive analysis report."""
        analysis = self.analyze_model_usage()
        
        print("=" * 80)
        print("🔍 FLEXIBLE WORKFLOW MODEL ANALYSIS REPORT")
        print("=" * 80)
        
        # Model usage summary
        print("\n📊 MODEL USAGE SUMMARY")
        print("-" * 40)
        for model, agents in analysis["agents_by_model"].items():
            print(f"🤖 {model}: {len(agents)} agents")
            for agent in agents:
                print(f"   - {agent}")
        
        # Agent details
        print(f"\n📱 AGENT CONFIGURATION DETAILS")
        print("-" * 40)
        for agent in analysis["agent_details"]:
            print(f"Agent: {agent['name']}")
            print(f"   Type: {agent['type']}")
            print(f"   Model: {agent['model']}")
            print(f"   Temperature: {agent['temperature']}")
            print(f"   Max Tokens: {agent['max_tokens']}")
            print(f"   Tools: {agent['tools']}")
            print()
        
        # Potential issues
        if analysis["potential_issues"]:
            print("⚠️  POTENTIAL ISSUES")
            print("-" * 40)
            for issue in analysis["potential_issues"]:
                severity_emoji = "🔴" if issue["severity"] == "high" else "🟡"
                print(f"{severity_emoji} {issue['type'].upper()}")
                print(f"   {issue['description']}")
                if "model" in issue:
                    alternatives = self.get_alternative_models(issue["model"])
                    print(f"   Suggested alternatives: {', '.join(alternatives)}")
                print()
        
        # Recommendations
        if analysis["recommendations"]:
            print("💡 RECOMMENDATIONS")
            print("-" * 40)
            for rec in analysis["recommendations"]:
                print(f"📌 {rec['title']}")
                print(f"   {rec['description']}")
                if "action" in rec:
                    print(f"   Action: {rec['action']}")
                if "implementation" in rec:
                    print(f"   Implementation: {rec['implementation']}")
                print()
        
        # Model alternatives
        print("🔄 MODEL ALTERNATIVES")
        print("-" * 40)
        for model in analysis["model_usage_count"].keys():
            alternatives = self.get_alternative_models(model)
            print(f"{model} → {', '.join(alternatives)}")
        
        print("\n" + "=" * 80)


def main():
    """Main function to run model analysis."""
    try:
        analyzer = ModelAnalyzer()
        analyzer.print_analysis_report()
        
        # Generate balanced configuration
        print("\n🔧 GENERATING LOAD-BALANCED CONFIGURATION...")
        balanced_config = analyzer.generate_balanced_config()
        
        # Save balanced configuration
        output_file = Path("backend/config/flexible_agent/workflow_flexible_balanced.yml")
        import yaml
        
        with open(output_file, 'w') as f:
            yaml.dump(balanced_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Balanced configuration saved to: {output_file}")
        print("\nTo use the balanced configuration:")
        print("1. Backup your current workflow_flexible.yml")
        print("2. Replace it with workflow_flexible_balanced.yml")
        print("3. Test with a simple request first")
        
    except Exception as e:
        print(f"❌ Error analyzing models: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 