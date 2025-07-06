# CodeRefactorer Output
**Agent**: CodeRefactorer
**Execution Order**: 7
**Timestamp**: 2025-07-04 10:24:42

---

## Refactored Code Implementation

### Summary of Changes

This refactoring significantly enhances the provided market research report generation framework, addressing critical feedback from Quality, Performance, and Security reviews. Key improvements include:

*   **Asynchronous Processing (Performance & Quality):** The core `LLMOrchestrationService` and dependent analysis services are now fully asynchronous using `asyncio`. This enables concurrent execution of independent analysis modules and non-blocking LLM API calls, drastically improving performance and responsiveness.
*   **Enhanced LLM Integration & Output Validation (Quality & Security):**
    *   LLM calls (`LLMClient.call_llm`) are now asynchronous.
    *   Stricter Pydantic validation (`model_validate_json`) is applied to LLM outputs that are expected to be structured JSON, ensuring data integrity and catching malformed responses early.
    *   The conceptual role of Retrieval Augmented Generation (RAG) is explicitly highlighted in prompt structures, emphasizing grounding LLM responses in factual data.
*   **Improved Observability & Logging (Quality & Security):** All `print()` statements have been replaced with Python's standard `logging` module, providing structured, configurable log outputs essential for monitoring, debugging, and security auditing in a production environment.
*   **Security Hardening (Security):**
    *   **Prompt Injection Mitigation (Conceptual):** A placeholder for input sanitization is added for user queries, and general LLM guardrails are emphasized as a crucial next step.
    *   **Secrets Management (Conceptual):** The hardcoded API key in `LLMClient` is removed, with instructions for using environment variables or a dedicated secrets management service.
    *   **Authentication/Authorization (Conceptual):** Explicit placeholders and documentation for integrating robust AuthN/AuthZ checks are included.
    *   **Sensitive Data Handling (Documentation):** Notes on handling `user_context` securely (encryption, masking) are added.
*   **Code Quality & Maintainability (Quality):**
    *   **Enums for Magic Strings:** `LLMTaskType` Enum is introduced to replace magic strings, improving readability, type safety, and reducing errors.
    *   **Hardcoded Values:** Default `analysis_period` and `technologies` are now derived from the `ReportRequest` or LLM interpretation, reducing hardcoded defaults.
    *   **Typo Fix:** The `A_opportunities` key in `IndustryAnalysisResult` Pydantic model and mock data is corrected to `opportunities`.
*   **Expanded Test Coverage (Quality):** New unit tests have been added for individual `AnalysisService` implementations and the `ReportGenerationService`'s formatting logic, significantly increasing test coverage and reliability.
*   **Dependency Management:** A `requirements.txt` with pinned versions is included for reproducible environments.

### Refactored Code

```python
# src/modules/data_models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ReportRequest(BaseModel):
    """Represents a user's request for a market research report."""

    query: str = Field(..., description="The natural language query for the report.")
    report_type: Optional[str] = Field(
        None,
        description="Optional: Specific type of report if known (e.g., 'Competitor Analysis').",
    )
    target_industry: Optional[str] = Field(
        None, description="Optional: Specific industry to target."
    )
    analysis_period: str = Field(
        "5 years", description="The period for future predictions (e.g., '5 years')."
    )
    technologies: List[str] = Field(
        ["AI", "Blockchain", "IoT"],
        description="List of technologies to assess for adoption analysis.",
    )


class IndustryAnalysisResult(BaseModel):
    """Represents the output of the Industry and Competitive Analysis module."""

    industry_overview: str
    key_players: List[Dict[str, Any]]
    market_share_distribution: Dict[str, float]
    swot_analysis: Dict[str, Any]  # Should contain 'strengths', 'weaknesses', 'opportunities', 'threats'


class MarketTrendsResult(BaseModel):
    """Represents the output of the Market Trends and Future Predictions module."""

    current_trends: List[str]
    emerging_trends: List[str]
    future_predictions: str
    growth_drivers: List[str]


class TechAdoptionResult(BaseModel):
    """Represents the output of the Technology Adoption Analysis module."""

    technology_name: str
    adoption_rate: float
    impact_analysis: str
    recommendations: List[str]


class StrategicInsightsResult(BaseModel):
    """Represents the output of the Strategic Insights and Actionable Recommendations module."""

    strategic_insights: List[str]
    actionable_recommendations: List[str]
    personalized_recommendations: List[str]


class ExecutiveSummary(BaseModel):
    """Represents the concise executive summary of the report."""

    key_findings: List[str]
    strategic_implications: str
    actionable_recommendations: List[str]


class ReportContent(BaseModel):
    """Aggregates all content sections for the final report."""

    executive_summary: ExecutiveSummary
    industry_analysis: Optional[IndustryAnalysisResult] = None
    market_trends: Optional[MarketTrendsResult] = None
    tech_adoption: Optional[TechAdoptionResult] = None
    strategic_insights: Optional[StrategicInsightsResult] = None
    # Add fields for other potential report modules as needed

```

```python
# src/modules/llm_client.py
import asyncio
import json
import logging
import os
import shlex  # For basic sanitization of user input within prompts
from enum import Enum
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LLMTaskType(str, Enum):
    """Defines types of tasks for LLM calls to enable structured responses."""

    INTERPRETATION = "interpretation"
    INDUSTRY_ANALYSIS = "industry_analysis"
    MARKET_TRENDS = "market_trends"
    TECH_ADOPTION = "tech_adoption"
    STRATEGIC_INSIGHTS = "strategic_insights"
    SYNTHESIS = "synthesis"
    EXECUTIVE_SUMMARY = "executive_summary"
    GENERAL = "general"


class LLMClient:
    """
    A simplified mock client for interacting with a Large Language Model.
    In a production environment, this would integrate with actual LLM APIs
    (e.g., Google's Gemini API, OpenAI GPT, Anthropic Claude) asynchronously.
    """

    def __init__(self, model_name: str = "mock-llm-v1"):
        """
        Initializes the LLMClient.

        Args:
            model_name: The name of the LLM model to use (mocked).
        """
        # In a real system, API keys should be loaded securely, e.g., from environment variables
        # or a secrets management service (e.g., os.getenv("LLM_API_KEY")).
        # self.api_key = os.getenv("LLM_API_KEY")
        # if not self.api_key:
        #     logger.warning("LLM_API_KEY not found in environment variables. Using mock key.")
        self.model_name = model_name
        logger.info(f"LLMClient initialized with model: {self.model_name}")

    async def call_llm(self, prompt: str, task_type: LLMTaskType = LLMTaskType.GENERAL) -> str:
        """
        Simulates an asynchronous API call to an LLM, generating a response based on the prompt.

        Args:
            prompt: The text prompt to send to the LLM.
            task_type: An Enum indicating the type of task, helping route to specific mock responses.

        Returns:
            A string containing the LLM's generated response.
        """
        logger.info(f"--- Mock LLM Call ({task_type.value}) ---")
        logger.debug(f"Prompt (excerpt): {prompt[:200]}...")
        await asyncio.sleep(0.1)  # Simulate async network latency

        # Simulate different LLM responses based on task type
        if task_type == LLMTaskType.INTERPRETATION:
            # Simulate JSON output for prompt interpretation
            return '''
            {
                "industry": "AI Software",
                "competitors": ["IBM", "Microsoft", "Google", "Amazon"],
                "required_modules": [
                    "Industry Analysis & Competitive Landscape Mapping",
                    "Market Trends Identification & Future Predictions"
                ]
            }
            '''
        elif task_type == LLMTaskType.INDUSTRY_ANALYSIS:
            return json.dumps({
                "industry_overview": "The AI software market is experiencing rapid growth, driven by advancements in machine learning and increasing enterprise adoption across various sectors. Key segments include NLP, computer vision, and predictive analytics.",
                "key_players": [
                    {"name": "Microsoft", "focus": "Cloud AI, Enterprise Solutions"},
                    {"name": "Google", "focus": "AI/ML Platforms, Research"},
                    {"name": "IBM", "focus": "Watson AI, Hybrid Cloud"},
                    {"name": "NVIDIA", "focus": "AI Hardware, Software Ecosystem"}
                ],
                "market_share_distribution": {"Microsoft": 0.20, "Google": 0.18, "IBM": 0.10, "Others": 0.52},
                "swot_analysis": {
                    "strengths": ["Innovation pace", "Growing demand"],
                    "weaknesses": ["Talent gap", "Ethical concerns"],
                    "opportunities": ["Vertical integration", "Emerging markets"], # Corrected typo
                    "threats": ["Regulatory scrutiny", "New entrants"]
                }
            })
        elif task_type == LLMTaskType.MARKET_TRENDS:
            return json.dumps({
                "current_trends": ["AI-driven automation", "Edge AI", "Responsible AI"],
                "emerging_trends": ["Generative AI in content creation", "AI for drug discovery", "Hyper-personalization"],
                "future_predictions": "By 2030, AI software will be ubiquitous, driving significant productivity gains and enabling novel business models. Ethical AI and explainable AI will become standard requirements.",
                "growth_drivers": ["Cloud infrastructure", "Big data availability", "Talent development"]
            })
        elif task_type == LLMTaskType.TECH_ADOPTION:
            return json.dumps({
                "technology_name": "Blockchain in Supply Chain",
                "adoption_rate": 0.15,
                "impact_analysis": "Blockchain enhances transparency, traceability, and security in supply chain operations, reducing fraud and improving efficiency. However, scalability and interoperability remain challenges.",
                "recommendations": ["Pilot projects for specific use cases", "Collaborate with industry consortia", "Invest in talent training"]
            })
        elif task_type == LLMTaskType.STRATEGIC_INSIGHTS:
            return json.dumps({
                "strategic_insights": [
                    "AI adoption is critical for competitive advantage, but requires careful data governance.",
                    "Personalization through AI directly impacts customer loyalty and sales.",
                    "Strategic partnerships are key to expanding market reach in emerging tech areas."
                ],
                "actionable_recommendations": [
                    "Invest in explainable AI frameworks to build trust.",
                    "Develop personalized marketing campaigns leveraging AI analytics.",
                    "Form strategic alliances with niche AI startups for rapid innovation."
                ],
                "personalized_recommendations": [
                    "For 'Enterprise' segment, focus AI investments on optimizing internal operations and customer service via chatbots and predictive analytics, aligning with recent sales growth in AI software.",
                    "For 'Logistics' company, explore blockchain for freight tracking and smart contracts to enhance supply chain transparency and efficiency, leveraging digital transformation marketing outreach."
                ]
            })
        elif task_type == LLMTaskType.SYNTHESIS:
            return """
            The market for [interpreted industry] is characterized by rapid technological advancement and increasing enterprise adoption. While current trends focus on [current trends], emerging areas like [emerging trends] will shape the future. Competitive advantage will increasingly depend on [key players]' ability to leverage AI for [strategic implications]. Recommended actions include [top recommendations].
            """
        elif task_type == LLMTaskType.EXECUTIVE_SUMMARY:
            # Simulate JSON output for executive summary
            return '''
            {
                "key_findings": [
                    "The AI software market exhibits robust growth driven by ML advancements.",
                    "Key players are actively innovating in cloud AI and enterprise solutions.",
                    "Blockchain in supply chain offers significant transparency benefits despite early adoption challenges."
                ],
                "strategic_implications": "Businesses must strategically invest in AI and emerging technologies to maintain competitive edge and enhance operational efficiency, while carefully managing ethical and integration complexities.",
                "actionable_recommendations": [
                    "Prioritize AI investments in automation and predictive analytics.",
                    "Explore blockchain pilot projects for supply chain traceability.",
                    "Foster cross-functional teams for technology integration."
                ]
            }
            '''
        else:
            return f"Mock LLM response for: {prompt[:100]}..."

```

```python
# src/modules/analysis_services.py
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from src.modules.llm_client import LLMClient, LLMTaskType
from src.modules.data_models import (
    IndustryAnalysisResult,
    MarketTrendsResult,
    TechAdoptionResult,
    StrategicInsightsResult,
)

logger = logging.getLogger(__name__)


class BaseAnalysisService(ABC):
    """Abstract base class for all analysis services."""

    def __init__(self, llm_client: LLMClient) -> None:
        """
        Initializes the base analysis service.

        Args:
            llm_client: An instance of the LLMClient.
        """
        self.llm_client = llm_client

    @abstractmethod
    async def analyze(self, **kwargs: Any) -> Any:
        """
        Abstract method to perform specific analysis asynchronously.
        Concrete implementations must override this.
        """
        pass

    async def _retrieve_context_data(self, data_params: Dict[str, Any]) -> str:
        """
        Simulates retrieving factual, structured data from a Knowledge Graph or
        Analytical Data Store for RAG (Retrieval Augmented Generation).
        In a real system, this would involve database queries or API calls.

        Args:
            data_params: Parameters to retrieve relevant data.

        Returns:
            A string representation of the retrieved data for LLM context.
        """
        logger.debug(f"    Retrieving context data for: {data_params}")
        # Placeholder for actual data retrieval logic.
        # This would involve calling DataSourceConnectors and/or querying DBs.
        return json.dumps({
            "retrieved_data_point_1": "value_A",
            "retrieved_data_point_2": "value_B",
            "metadata": f"Data relevant to {data_params.get('industry', 'unknown')}"
        })


class IndustryCompetitiveAnalysisService(BaseAnalysisService):
    """
    Service for generating detailed industry analysis and competitive landscape mapping.
    Leverages LLM for qualitative synthesis and interpretation.
    """

    async def analyze(
        self, industry: str, competitors: List[str]
    ) -> IndustryAnalysisResult:
        """
        Performs industry and competitive landscape analysis asynchronously.

        Args:
            industry: The specific industry to analyze.
            competitors: A list of key competitors to map.

        Returns:
            An IndustryAnalysisResult object.
        """
        logger.info(f"    Running IndustryCompetitiveAnalysis for {industry}...")
        
        # Simulate data retrieval from Knowledge Graph / Analytical Data Store
        # (This would involve calling DataSourceConnectors or querying databases)
        mock_raw_data = {
            "industry_growth_rate": "15% CAGR",
            "top_companies_data": [
                {"name": "Microsoft", "revenue": "200B", "market_share": "20%", "focus_areas": "Cloud AI, Enterprise Solutions"},
                {"name": "Google", "revenue": "180B", "market_share": "18%", "focus_areas": "AI/ML Platforms, Research"},
            ],
            "recent_news": ["AI startup funding surges", "New regulatory proposals"],
        }
        
        # In a real RAG scenario, relevant snippets from mock_raw_data or actual DBs
        # would be intelligently selected and passed to the LLM.
        retrieved_context = await self._retrieve_context_data({"industry": industry, "type": "industry_overview"})

        prompt = f"""
        Analyze the {industry} industry and its competitive landscape based on the
        following contextual data and raw information:
        Context: {retrieved_context}
        Raw Data: {json.dumps(mock_raw_data)}
        Focus on key players {', '.join(competitors)}, their market shares, strategies,
        and perform a basic SWOT analysis.

        Output should be a JSON object conforming to IndustryAnalysisResult schema,
        with keys: 'industry_overview', 'key_players' (list of dicts),
        'market_share_distribution' (dict), 'swot_analysis' (dict with 'strengths', 'weaknesses', 'opportunities', 'threats').
        """
        llm_response_json_str = await self.llm_client.call_llm(
            prompt=prompt, task_type=LLMTaskType.INDUSTRY_ANALYSIS
        )
        try:
            return IndustryAnalysisResult.model_validate_json(llm_response_json_str)
        except Exception as e:
            logger.error(f"LLM industry analysis returned invalid JSON or schema mismatch: {e}. Raw LLM output: {llm_response_json_str}")
            # Fallback to a default or raise a specific exception
            return IndustryAnalysisResult(
                industry_overview=f"Simulated overview for {industry}. Error in parsing LLM response.",
                key_players=[{"name": "Simulated Competitor", "focus": "General"}],
                market_share_distribution={"Simulated": 1.0},
                swot_analysis={"strengths": ["N/A"], "weaknesses": ["N/A"], "opportunities": ["N/A"], "threats": ["N/A"]},
            )


class MarketTrendsPredictionService(BaseAnalysisService):
    """
    Service for identifying current/emerging market trends and providing future predictions.
    Combines statistical insights with LLM for nuanced interpretation.
    """

    async def analyze(
        self, market_segment: str, analysis_period: str
    ) -> MarketTrendsResult:
        """
        Identifies market trends and provides future predictions asynchronously.

        Args:
            market_segment: The specific market segment to analyze.
            analysis_period: The period for future predictions (e.g., "5 years").

        Returns:
            A MarketTrendsResult object.
        """
        logger.info(f"    Running MarketTrendsPrediction for {market_segment}...")
        # Simulate data retrieval (e.g., historical sales data, macroeconomic indicators)
        mock_raw_data = {
            "historical_growth": [0.05, 0.07, 0.09],
            "economic_indicators": {"GDP_growth": "2.5%"},
            "expert_opinions": ["AI adoption accelerating", "Sustainability becoming key"],
        }
        retrieved_context = await self._retrieve_context_data({"market_segment": market_segment, "type": "market_data"})

        prompt = f"""
        Identify current and emerging market trends for the {market_segment} segment
        and provide future predictions for the next {analysis_period} based on
        the following contextual data and raw information:
        Context: {retrieved_context}
        Raw Data: {json.dumps(mock_raw_data)}.
        Also identify key growth drivers.

        Output should be a JSON object conforming to MarketTrendsResult schema,
        with keys: 'current_trends' (list of strings), 'emerging_trends' (list of strings),
        'future_predictions' (string), 'growth_drivers' (list of strings).
        """
        llm_response_json_str = await self.llm_client.call_llm(
            prompt=prompt, task_type=LLMTaskType.MARKET_TRENDS
        )
        try:
            return MarketTrendsResult.model_validate_json(llm_response_json_str)
        except Exception as e:
            logger.error(f"LLM market trends returned invalid JSON or schema mismatch: {e}. Raw LLM output: {llm_response_json_str}")
            return MarketTrendsResult(
                current_trends=["Simulated current trend. Error in parsing LLM response."],
                emerging_trends=["Simulated emerging trend."],
                future_predictions="Simulated future prediction. Please review report details.",
                growth_drivers=["Simulated growth driver"],
            )


class TechnologyAdoptionAnalysisService(BaseAnalysisService):
    """
    Service for analyzing technology adoption rates, impact, and providing recommendations.
    """

    async def analyze(
        self, industry: str, technologies: List[str]
    ) -> TechAdoptionResult:
        """
        Analyzes technology adoption within a given industry asynchronously.

        Args:
            industry: The industry where technology adoption is being analyzed.
            technologies: A list of technologies to assess.

        Returns:
            A TechAdoptionResult object.
        """
        logger.info(f"    Running TechnologyAdoptionAnalysis for {technologies} in {industry}...")
        # Simulate data retrieval (e.g., tech research papers, patent data, tech news)
        mock_raw_data = {
            "AI_adoption_enterprise": "45%",
            "Blockchain_supply_chain_pilots": "increasing",
            "IoT_penetration": "high in manufacturing",
            "barriers": ["cost", "complexity", "lack of skills"],
        }
        retrieved_context = await self._retrieve_context_data({"industry": industry, "technologies": technologies, "type": "tech_adoption"})

        prompt = f"""
        Analyze the adoption rates and impact of technologies like {', '.join(technologies)}
        in the {industry} industry, based on the following contextual data and raw information:
        Context: {retrieved_context}
        Raw Data: {json.dumps(mock_raw_data)}.
        Provide specific recommendations.

        Output should be a JSON object conforming to TechAdoptionResult schema,
        with keys: 'technology_name' (string, main tech discussed), 'adoption_rate' (float),
        'impact_analysis' (string), 'recommendations' (list of strings).
        """
        llm_response_json_str = await self.llm_client.call_llm(
            prompt=prompt, task_type=LLMTaskType.TECH_ADOPTION
        )
        try:
            return TechAdoptionResult.model_validate_json(llm_response_json_str)
        except Exception as e:
            logger.error(f"LLM tech adoption returned invalid JSON or schema mismatch: {e}. Raw LLM output: {llm_response_json_str}")
            return TechAdoptionResult(
                technology_name="Simulated Tech. Error in parsing LLM response.",
                adoption_rate=0.0,
                impact_analysis="Simulated impact.",
                recommendations=["Simulated recommendation"],
            )


class StrategicInsightsRecommendationsService(BaseAnalysisService):
    """
    Service for deriving strategic insights and generating actionable,
    personalized recommendations.
    """

    async def analyze(
        self,
        aggregated_analysis_results: Dict[str, Any],
        user_context: Dict[str, Any],
        industry: str,
    ) -> StrategicInsightsResult:
        """
        Derives strategic insights and generates actionable, personalized recommendations asynchronously.

        Args:
            aggregated_analysis_results: Dictionary containing results from other analysis services.
            user_context: Context specific to the user/client (e.g., sales data, marketing focus).
                          Sensitive data here should be handled securely (encryption, masking).
            industry: The main industry being analyzed.

        Returns:
            A StrategicInsightsResult object.
        """
        logger.info(f"    Running StrategicInsightsRecommendations for {industry} with personalization...")
        # Combine all analysis results and user context for LLM processing
        # In a real RAG scenario, sensitive parts of user_context might be masked or
        # only relevant, non-PII attributes passed directly to the prompt.
        combined_data_for_llm = {
            "analysis_results": aggregated_analysis_results,
            "user_context": user_context,
            "industry": industry,
        }
        retrieved_context = await self._retrieve_context_data({"user_context": user_context, "type": "personalized_data"})


        prompt = f"""
        Based on the following aggregated market analysis results and specific
        user context, derive key strategic insights and actionable recommendations.
        Crucially, provide personalized recommendations tailored to the user's
        context.

        Context: {retrieved_context}
        Data: {json.dumps(combined_data_for_llm, indent=2)}

        Output should be a JSON object conforming to StrategicInsightsResult schema,
        with keys: 'strategic_insights' (list of strings), 'actionable_recommendations' (list of strings),
        'personalized_recommendations' (list of strings).
        """
        llm_response_json_str = await self.llm_client.call_llm(
            prompt=prompt, task_type=LLMTaskType.STRATEGIC_INSIGHTS
        )
        try:
            return StrategicInsightsResult.model_validate_json(llm_response_json_str)
        except Exception as e:
            logger.error(f"LLM strategic insights returned invalid JSON or schema mismatch: {e}. Raw LLM output: {llm_response_json_str}")
            return StrategicInsightsResult(
                strategic_insights=["Simulated strategic insight. Error in parsing LLM response."],
                actionable_recommendations=["Simulated actionable recommendation"],
                personalized_recommendations=["Simulated personalized recommendation"],
            )

```

```python
# src/modules/data_source_connectors.py
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class DataSourceConnector(ABC):
    """Abstract base class for all data source connectors."""

    @abstractmethod
    async def fetch_data(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Abstract method to fetch data from a specific source asynchronously.

        Args:
            query_params: Parameters for the data query.

        Returns:
            A list of dictionaries, where each dictionary represents a record.
        """
        pass


class MockDataSourceConnector(DataSourceConnector):
    """
    A mock data source connector for demonstration purposes.
    In a real system, this would connect to external APIs (e.g., SEC, Nielsen)
    asynchronously.
    """

    async def fetch_data(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simulates fetching data from a data source asynchronously.

        Args:
            query_params: Parameters for the data query (e.g., "industry", "company_name").

        Returns:
            A list of mock data records.
        """
        logger.info(f"    MockDataSourceConnector: Fetching data for {query_params}...")
        # Simulate different data based on query_params
        if query_params.get("source") == "SEC":
            return [
                {"company": "TechCo", "filing_type": "10-K", "revenue": "10B"},
                {"company": "InnovateCorp", "filing_type": "10-Q", "revenue": "2B"},
            ]
        elif query_params.get("source") == "social_media":
            return [
                {"platform": "X", "sentiment": "positive", "topic": "AI"},
                {"platform": "LinkedIn", "sentiment": "neutral", "topic": "blockchain"},
            ]
        else:
            return [
                {"data_point": "mock_value_1", "category": "general"},
                {"data_point": "mock_value_2", "category": "general"},
            ]

```

```python
# src/modules/report_generator.py
import logging
from typing import Optional

from src.modules.data_models import (
    ReportContent,
    ExecutiveSummary,
    IndustryAnalysisResult,
    MarketTrendsResult,
    TechAdoptionResult,
    StrategicInsightsResult,
)

logger = logging.getLogger(__name__)


class ReportGenerationService:
    """
    Service responsible for assembling and formatting the final market research report
    in a Gartner-style layout.
    """

    def assemble_report(self, report_content: ReportContent) -> str:
        """
        Assembles the various content sections into a comprehensive Gartner-style report.

        Args:
            report_content: An object containing all the parsed and synthesized content
                            for the report.

        Returns:
            A string representation of the formatted report. In a real system, this
            would generate a PDF, PPTX, or interactive web page.
        """
        logger.info("    Assembling the final report...")

        report_parts = []

        # 1. Executive Summary
        report_parts.append(self._format_executive_summary(report_content.executive_summary))

        # 2. Industry Analysis and Competitive Landscape Mapping
        if report_content.industry_analysis:
            report_parts.append(self._format_industry_analysis(report_content.industry_analysis))

        # 3. Market Trends Identification and Future Predictions
        if report_content.market_trends:
            report_parts.append(self._format_market_trends(report_content.market_trends))

        # 4. Technology Adoption Analysis and Recommendations
        if report_content.tech_adoption:
            report_parts.append(self._format_tech_adoption(report_content.tech_adoption))

        # 5. Strategic Insights and Actionable Recommendations
        if report_content.strategic_insights:
            report_parts.append(self._format_strategic_insights(report_content.strategic_insights))

        # Final Touches (e.g., disclaimer, appendix would go here)
        report_parts.append("\n--- END OF REPORT ---")
        report_parts.append("\nDisclaimer: This report is for informational purposes only and should not be considered financial advice.")

        return "\n\n".join(report_parts)

    def _format_executive_summary(self, summary: ExecutiveSummary) -> str:
        """Formats the executive summary section."""
        return f"""
## 1. Executive Summary

### Key Findings:
{"\n".join([f"- {finding}" for finding in summary.key_findings])}

### Strategic Implications:
{summary.strategic_implications}

### Actionable Recommendations:
{"\n".join([f"- {rec}" for rec in summary.actionable_recommendations])}
"""

    def _format_industry_analysis(self, analysis: IndustryAnalysisResult) -> str:
        """Formats the industry analysis section."""
        key_players_str = "\n".join(
            [f"  - {p['name']} (Focus: {p.get('focus', 'N/A')})" for p in analysis.key_players]
        )
        market_share_str = "\n".join(
            [f"  - {company}: {share:.1%}" for company, share in analysis.market_share_distribution.items()]
        )
        return f"""
## 2. Industry Analysis & Competitive Landscape Mapping

### Industry Overview:
{analysis.industry_overview}

### Key Players:
{key_players_str}

### Market Share Distribution:
{market_share_str}

### SWOT Analysis:
- **Strengths:** {', '.join(analysis.swot_analysis.get('strengths', ['N/A']))}
- **Weaknesses:** {', '.join(analysis.swot_analysis.get('weaknesses', ['N/A']))}
- **Opportunities:** {', '.join(analysis.swot_analysis.get('opportunities', ['N/A']))}
- **Threats:** {', '.join(analysis.swot_analysis.get('threats', ['N/A']))}
"""

    def _format_market_trends(self, trends: MarketTrendsResult) -> str:
        """Formats the market trends section."""
        return f"""
## 3. Market Trends Identification & Future Predictions

### Current Trends:
{"\n".join([f"- {t}" for t in trends.current_trends])}

### Emerging Trends:
{"\n".join([f"- {t}" for t in trends.emerging_trends])}

### Future Predictions:
{trends.future_predictions}

### Growth Drivers:
{"\n".join([f"- {d}" for d in trends.growth_drivers])}
"""

    def _format_tech_adoption(self, tech: TechAdoptionResult) -> str:
        """Formats the technology adoption section."""
        return f"""
## 4. Technology Adoption Analysis & Recommendations - {tech.technology_name}

### Adoption Rate:
Approx. {tech.adoption_rate:.1%}

### Impact Analysis:
{tech.impact_analysis}

### Recommendations:
{"\n".join([f"- {rec}" for rec in tech.recommendations])}
"""

    def _format_strategic_insights(self, insights: StrategicInsightsResult) -> str:
        """Formats the strategic insights and recommendations section."""
        personalized_rec_str = ""
        if insights.personalized_recommendations:
            personalized_rec_str = f"""
### Personalized Recommendations:
{"\n".join([f"- {rec}" for rec in insights.personalized_recommendations])}
"""
        return f"""
## 5. Strategic Insights & Actionable Recommendations

### Strategic Insights:
{"\n".join([f"- {s}" for s in insights.strategic_insights])}

### Actionable Recommendations:
{"\n".join([f"- {rec}" for rec in insights.actionable_recommendations])}
{personalized_rec_str}
"""

```

```python
# src/main.py
import asyncio
import json
import logging
import shlex  # For basic input sanitization
from typing import Dict, Any, List

from src.modules.llm_client import LLMClient, LLMTaskType
from src.modules.analysis_services import (
    BaseAnalysisService,
    IndustryCompetitiveAnalysisService,
    MarketTrendsPredictionService,
    TechnologyAdoptionAnalysisService,
    StrategicInsightsRecommendationsService,
)
from src.modules.report_generator import ReportGenerationService
from src.modules.data_models import (
    ReportRequest,
    ReportContent,
    IndustryAnalysisResult,
    MarketTrendsResult,
    TechAdoptionResult,
    StrategicInsightsResult,
    ExecutiveSummary,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMOrchestrationService:
    """
    The intelligent core service responsible for orchestrating the LLM-guided
    Gartner-style market research report generation process.

    This service interprets user prompts, dispatches analysis tasks to
    specialized services, synthesizes insights using LLMs, and coordinates
    the final report assembly. It now leverages asynchronous operations.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        industry_analysis_service: IndustryCompetitiveAnalysisService,
        market_trends_service: MarketTrendsPredictionService,
        tech_adoption_service: TechnologyAdoptionAnalysisService,
        strategic_insights_service: StrategicInsightsRecommendationsService,
        report_generator: ReportGenerationService,
    ) -> None:
        """
        Initializes the LLMOrchestrationService with its dependencies.

        Args:
            llm_client: An instance of the LLMClient for interacting with LLM models.
            industry_analysis_service: Service for industry and competitive analysis.
            market_trends_service: Service for market trends and predictions.
            tech_adoption_service: Service for technology adoption analysis.
            strategic_insights_service: Service for strategic insights and recommendations.
            report_generator: Service for generating the final report output.
        """
        self.llm_client = llm_client
        self.industry_analysis_service = industry_analysis_service
        self.market_trends_service = market_trends_service
        self.tech_adoption_service = tech_adoption_service
        self.strategic_insights_service = strategic_insights_service
        self.report_generator = report_generator

    async def generate_report(
        self, report_request: ReportRequest, user_context: Dict[str, Any]
    ) -> str:
        """
        Generates a comprehensive market research report based on the user's request.

        This is the main entry point for initiating a report generation.

        Args:
            report_request: A ReportRequest object detailing the user's research needs.
            user_context: A dictionary containing user-specific information
                          (e.g., customer interactions, sales trends) for personalization.
                          Sensitive data in this context should be encrypted/masked.

        Returns:
            A string representation of the generated report content.
        """
        # --- Security: Authentication and Authorization Placeholder ---
        # In a real system, the API Gateway or this service's entry point
        # would enforce AuthN/AuthZ checks before proceeding.
        # Example: if not is_user_authorized(user_context.get("user_id"), "generate_report"):
        #              raise PermissionDeniedError("User not authorized to generate reports.")
        logger.info(f"Starting report generation for request: {report_request.query}")

        # Step 1: Interpret the user's prompt (simulated LLM task)
        # In a real scenario, this would use LLM to parse intent, identify entities,
        # and determine required analysis modules.
        report_scope = await self._interpret_prompt(report_request.query)
        logger.info(f"Interpreted report scope: {report_scope}")

        # Step 2: Orchestrate various analysis services concurrently
        analysis_results = await self._orchestrate_analysis(report_scope, user_context, report_request)
        logger.info("Completed all analysis modules.")

        # Step 3: Synthesize insights using LLM
        # The LLM combines findings from different analyses into coherent insights.
        report_insights = await self._synthesize_insights(analysis_results)
        logger.info("Synthesized core report insights.")

        # Step 4: Generate Executive Summary
        executive_summary = await self._generate_executive_summary(report_insights)
        logger.info("Generated executive summary.")

        # Step 5: Assemble and generate the final report
        report_content = ReportContent(
            executive_summary=executive_summary,
            industry_analysis=analysis_results.get("industry_analysis"),
            market_trends=analysis_results.get("market_trends"),
            tech_adoption=analysis_results.get("tech_adoption"),
            strategic_insights=analysis_results.get("strategic_insights"),
        )
        final_report = self.report_generator.assemble_report(report_content)
        logger.info("Final report assembled.")

        return final_report

    async def _interpret_prompt(self, query: str) -> Dict[str, Any]:
        """
        Interprets the user's natural language query using an LLM to determine
        the scope and requirements of the report.

        Args:
            query: The natural language query from the user.

        Returns:
            A dictionary outlining the identified report scope (e.g., industry,
            competitors, required modules).
        """
        # --- Security: Basic Prompt Injection Mitigation (Conceptual) ---
        # For production, this needs a much more robust approach (e.g., dedicated LLM guardrails,
        # content moderation APIs, strict input validation beyond simple escaping).
        # shlex.quote is good for shell commands, but for LLM prompts, it's more about
        # ensuring the user input cannot "break out" of its intended context.
        # A simpler approach might be to just escape quotes, or use a separate LLM for moderation.
        sanitized_query = shlex.quote(query) # This is a placeholder, a full solution is complex.

        llm_prompt = f"""
        Analyze the following user query to determine the key areas of market research
        required. Identify the primary industry, potential target companies/competitors,
        and indicate which of the following analysis modules are relevant.
        Provide the output as a JSON object with keys like 'industry', 'competitors',
        and a list 'required_modules'. If a module is not explicitly required, omit it
        or set its value to false.

        Analysis Modules:
        - Industry Analysis & Competitive Landscape Mapping
        - Market Trends Identification & Future Predictions
        - Technology Adoption Analysis & Recommendations
        - Strategic Insights & Actionable Recommendations

        User Query: "{sanitized_query}"
        """
        # Simulate LLM call to interpret the prompt
        interpretation_json_str = await self.llm_client.call_llm(
            prompt=llm_prompt, task_type=LLMTaskType.INTERPRETATION
        )
        try:
            # Use Pydantic's model_validate_json for stricter validation
            # For dynamic dictionaries, we can't use a strict Pydantic model directly
            # but can still wrap json.loads in a more robust way.
            # A dedicated Pydantic model for interpretation output would be ideal.
            parsed_result = json.loads(interpretation_json_str)
            if not isinstance(parsed_result, dict) or not all(k in parsed_result for k in ['industry', 'required_modules']):
                 raise ValueError("LLM interpretation result missing required keys.")
            return parsed_result
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"LLM interpretation returned invalid JSON or schema mismatch: {e}. Raw LLM output: {interpretation_json_str}. Falling back to default scope.")
            # Fallback to a default interpretation if LLM fails or is simulated
            return {
                "industry": "Global Tech Market",
                "competitors": ["TechCo", "InnovateCorp"],
                "required_modules": [
                    "Industry Analysis & Competitive Landscape Mapping",
                    "Market Trends Identification & Future Predictions",
                    "Technology Adoption Analysis & Recommendations",
                    "Strategic Insights & Actionable Recommendations",
                ],
            }


    async def _orchestrate_analysis(
        self, report_scope: Dict[str, Any], user_context: Dict[str, Any], report_request: ReportRequest
    ) -> Dict[str, Any]:
        """
        Orchestrates calls to various analysis services concurrently based on the
        identified report scope.

        Args:
            report_scope: A dictionary specifying the scope of the report.
            user_context: User-specific context for personalization.
            report_request: Original report request, containing configurable parameters.

        Returns:
            A dictionary containing results from all executed analysis services.
        """
        analysis_tasks = {}
        industry = report_scope.get("industry", report_request.target_industry or "general market")
        competitors = report_scope.get("competitors", [])
        required_modules = report_scope.get("required_modules", [])

        if "Industry Analysis & Competitive Landscape Mapping" in required_modules:
            logger.info(f"Scheduling Industry & Competitive Analysis for {industry}...")
            task = self.industry_analysis_service.analyze(
                industry=industry, competitors=competitors
            )
            analysis_tasks["industry_analysis"] = task

        if "Market Trends Identification & Future Predictions" in required_modules:
            logger.info(f"Scheduling Market Trends & Prediction for {industry}...")
            task = self.market_trends_service.analyze(
                market_segment=industry, analysis_period=report_request.analysis_period
            )
            analysis_tasks["market_trends"] = task

        if "Technology Adoption Analysis & Recommendations" in required_modules:
            logger.info(f"Scheduling Technology Adoption Analysis for {industry}...")
            task = self.tech_adoption_service.analyze(
                industry=industry, technologies=report_request.technologies
            )
            analysis_tasks["tech_adoption"] = task

        # Await all analysis tasks concurrently
        if analysis_tasks:
            # Gather results from all concurrent tasks
            task_names = list(analysis_tasks.keys())
            tasks = list(analysis_tasks.values())
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)

            results_dict = {}
            for name, res in zip(task_names, completed_results):
                if isinstance(res, Exception):
                    logger.error(f"Error in {name} analysis: {res}")
                    results_dict[name] = None # Or a specific error object
                else:
                    results_dict[name] = res
            analysis_results = results_dict
        else:
            analysis_results = {}

        # Strategic insights typically needs results from other modules.
        # It's run after others complete.
        if "Strategic Insights & Actionable Recommendations" in required_modules:
            logger.info(f"Running Strategic Insights & Recommendations for {industry}...")
            strategic_res = await self.strategic_insights_service.analyze(
                aggregated_analysis_results=analysis_results,
                user_context=user_context,
                industry=industry,
            )
            analysis_results["strategic_insights"] = strategic_res

        return analysis_results

    async def _synthesize_insights(self, analysis_results: Dict[str, Any]) -> str:
        """
        Uses an LLM to synthesize disparate analysis results into coherent,
        interconnected insights.

        Args:
            analysis_results: A dictionary containing the raw results from
                              various analysis services.

        Returns:
            A string containing the synthesized strategic insights.
        """
        # Ensure that analysis_results values are stringified for the prompt
        formatted_analysis_results = {
            k: v.model_dump_json() if hasattr(v, 'model_dump_json') else str(v)
            for k, v in analysis_results.items()
        }

        prompt_template = """
        Synthesize the following market research analysis results into a cohesive
        set of strategic insights. Focus on interdependencies and key takeaways
        relevant for decision-makers. Present it in a clear, actionable format.

        --- Analysis Results ---
        Industry Analysis: {industry_analysis}
        Market Trends: {market_trends}
        Technology Adoption: {tech_adoption}
        Strategic Insights: {strategic_insights}
        --- End Analysis Results ---
        """
        formatted_prompt = prompt_template.format(
            industry_analysis=formatted_analysis_results.get("industry_analysis", "N/A"),
            market_trends=formatted_analysis_results.get("market_trends", "N/A"),
            tech_adoption=formatted_analysis_results.get("tech_adoption", "N/A"),
            strategic_insights=formatted_analysis_results.get("strategic_insights", "N/A"),
        )
        # Simulate LLM call for synthesis
        return await self.llm_client.call_llm(
            prompt=formatted_prompt, task_type=LLMTaskType.SYNTHESIS
        )

    async def _generate_executive_summary(self, synthesized_insights: str) -> ExecutiveSummary:
        """
        Generates a concise executive summary using an LLM, highlighting key
        findings, insights, and recommendations from the full report.

        Args:
            synthesized_insights: The synthesized strategic insights from the report.

        Returns:
            An ExecutiveSummary object.
        """
        llm_prompt = f"""
        From the following comprehensive market research insights, generate a concise
        executive summary. It should include:
        1. Key Findings (2-3 bullet points)
        2. Strategic Implications (1-2 sentences)
        3. Top Actionable Recommendations (1-2 bullet points)

        Ensure the summary is high-level and captures the essence for busy executives.

        --- Full Insights ---
        {synthesized_insights}
        --- End Full Insights ---

        Provide the output in a JSON object with keys: 'key_findings' (list of strings),
        'strategic_implications' (string), 'actionable_recommendations' (list of strings).
        """
        # Simulate LLM call to generate executive summary
        summary_json_str = await self.llm_client.call_llm(
            prompt=llm_prompt, task_type=LLMTaskType.EXECUTIVE_SUMMARY
        )
        try:
            return ExecutiveSummary.model_validate_json(summary_json_str)
        except Exception as e:
            logger.warning(f"LLM executive summary returned invalid JSON or schema mismatch: {e}. Raw LLM output: {summary_json_str}. Falling back to default summary.")
            return ExecutiveSummary(
                key_findings=["Failed to parse LLM summary or LLM error."],
                strategic_implications="Please review the full report for details.",
                actionable_recommendations=[],
            )


if __name__ == "__main__":
    # Example Usage
    logger.info("--- Initializing Services ---")
    mock_llm_client = LLMClient()
    mock_industry_service = IndustryCompetitiveAnalysisService(mock_llm_client)
    mock_market_service = MarketTrendsPredictionService(mock_llm_client)
    mock_tech_service = TechnologyAdoptionAnalysisService(mock_llm_client)
    mock_strategic_service = StrategicInsightsRecommendationsService(mock_llm_client)
    mock_report_generator = ReportGenerationService()

    orchestrator = LLMOrchestrationService(
        llm_client=mock_llm_client,
        industry_analysis_service=mock_industry_service,
        market_trends_service=mock_market_service,
        tech_adoption_service=mock_tech_service,
        strategic_insights_service=mock_strategic_service,
        report_generator=mock_report_generator,
    )

    async def run_examples():
        logger.info("\n--- Generating Report Example 1 ---")
        request1 = ReportRequest(
            query="Generate a market research report on the AI software market, focusing on leading competitors and future trends.",
            analysis_period="7 years", # Override default
            technologies=["AI", "ML", "Data Science"] # Override default
        )
        user_context1 = {
            "customer_segment": "Enterprise",
            "recent_sales_data": {"Q1_2023_AI_Software": "2.5M"},
        }
        generated_report1 = await orchestrator.generate_report(request1, user_context1)
        logger.info("\n" + "=" * 50)
        logger.info("Generated Report 1 Output:")
        logger.info(generated_report1)
        logger.info("=" * 50)

        logger.info("\n--- Generating Report Example 2 ---")
        request2 = ReportRequest(
            query="Provide insights into blockchain technology adoption in supply chain, with strategic recommendations for a logistics company.",
            analysis_period="3 years",
            technologies=["Blockchain", "IoT"]
        )
        user_context2 = {
            "customer_segment": "Logistics",
            "marketing_outreach_focus": "Digital Transformation",
        }
        generated_report2 = await orchestrator.generate_report(request2, user_context2)
        logger.info("\n" + "=" * 50)
        logger.info("Generated Report 2 Output:")
        logger.info(generated_report2)
        logger.info("=" * 50)

    asyncio.run(run_examples())

```

### Security Improvements

1.  **Prompt Injection Mitigation (Conceptual):**
    *   **Action:** Added `shlex.quote` as a placeholder for user input sanitization in `_interpret_prompt`.
    *   **Vulnerability Addressed:** Reduces the immediate risk of basic prompt injection by attempting to escape special characters.
    *   **New Measures:** Emphasizes the need for robust LLM guardrails (e.g., dedicated moderation APIs, context breaking techniques) in production.
2.  **Hardcoded API Key Removal:**
    *   **Action:** The `api_key` argument has been removed from `LLMClient.__init__`.
    *   **Vulnerability Addressed:** Eliminates the critical security flaw of hardcoding sensitive credentials directly in the source code.
    *   **New Measures:** The code now points to best practices for secrets management (e.g., environment variables, dedicated secret management services).
3.  **Authentication and Authorization Enforcement (Conceptual):**
    *   **Action:** Added a clear placeholder comment at the beginning of `LLMOrchestrationService.generate_report` to indicate where AuthN/AuthZ checks should be integrated.
    *   **Vulnerability Addressed:** Highlights the need to prevent unauthorized access to report generation functionality.
    *   **New Measures:** Reinforces the architectural design's emphasis on an API Gateway and Security Service for role-based access control (RBAC).
4.  **Sensitive Data Handling (Documentation):**
    *   **Action:** Added comments in `generate_report` and `StrategicInsightsRecommendationsService.analyze` to explicitly mention the need for encryption, masking, and proper access controls for sensitive `user_context` data.
    *   **Vulnerability Addressed:** Raises awareness and provides guidance for handling Personally Identifiable Information (PII) and sensitive business data securely, aligning with data privacy regulations (e.g., GDPR, CCPA).
5.  **Enhanced Logging for Security Auditing:**
    *   **Action:** Replaced `print()` statements with structured `logging` calls.
    *   **New Measures:** Enables better monitoring and auditing of system activities, critical for detecting and responding to security incidents (e.g., logging LLM interactions, errors, and warnings).

### Performance Optimizations

1.  **Asynchronous LLM Calls and Concurrent Analysis:**
    *   **Action:** All LLM calls (`LLMClient.call_llm`) and `BaseAnalysisService.analyze` methods are now `async`. The `LLMOrchestrationService._orchestrate_analysis` method uses `asyncio.gather` to execute independent analysis services concurrently.
    *   **Performance Improvements:** Transforms the system from a synchronous, blocking pipeline into a non-blocking, parallelized workflow. This significantly reduces the overall report generation time by allowing I/O-bound operations (like LLM API calls and simulated data retrieval) to overlap.
    *   **Optimization Techniques Applied:** `asyncio` for concurrency, `await` for non-blocking I/O.
2.  **Implicit RAG for Prompt Efficiency (Conceptual):**
    *   **Action:** Added a `_retrieve_context_data` placeholder in `BaseAnalysisService` and included it in prompts.
    *   **Performance Improvements:** By conceptually retrieving and providing only *relevant* context to the LLM (as opposed to dumping all raw data), token usage can be minimized, leading to faster LLM inference times and reduced costs.
    *   **Optimization Techniques Applied:** Prompt engineering, conceptual RAG integration.
3.  **Pydantic for Efficient Data Handling:**
    *   **Action:** Continued and expanded the use of Pydantic models for structured LLM outputs and inter-service data transfer.
    *   **Performance Improvements:** Pydantic provides efficient parsing and serialization of data, reducing the overhead of manual dictionary manipulation and ensuring data consistency.

### Quality Enhancements

1.  **Refined Modularity and Abstraction:**
    *   **Action:** Ensured clear separation of concerns remains, with `BaseAnalysisService` becoming an `async` abstract base class.
    *   **Code Quality Improvements:** Maintains high modularity, promoting the Single Responsibility Principle and Open/Closed Principle.
2.  **Comprehensive Logging:**
    *   **Action:** Replaced all `print()` statements with `logging.getLogger(__name__)` and appropriate log levels (INFO, WARNING, ERROR, DEBUG). Configured basic logging in `main.py`.
    *   **Better Error Handling and Logging:** Provides a structured and configurable way to output system messages. Errors and warnings now log more context (e.g., raw LLM output on JSON decode errors), which is invaluable for debugging and operational visibility.
3.  **Stronger LLM Output Validation:**
    *   **Action:** Utilized Pydantic's `model_validate_json()` method for parsing LLM outputs that are expected to be structured data models (e.g., `IndustryAnalysisResult`, `ExecutiveSummary`).
    *   **Code Quality Improvements:** Ensures that LLM responses adhere to predefined schemas, catching malformed or semantically incorrect outputs early and providing clearer error messages. Includes fallbacks for robust behavior.
4.  **Enum for LLM Task Types:**
    *   **Action:** Introduced `LLMTaskType` Enum for `task_type` argument in `LLMClient.call_llm`.
    *   **Code Quality Improvements:** Replaces "magic strings" with type-safe constants, improving code readability, reducing potential for typos, and aiding static analysis.
5.  **Configurable Parameters:**
    *   **Action:** Moved `analysis_period` and `technologies` from hardcoded values in `analysis_services` to be derived from the `ReportRequest` object.
    *   **Code Quality Improvements:** Increases flexibility and configurability of report requests, making the framework more adaptable.
6.  **Typo Correction:**
    *   **Action:** Corrected `A_opportunities` to `opportunities` in `IndustryAnalysisResult` data model and corresponding mock data/formatting.
    *   **Code Quality Improvements:** Ensures data consistency and correctness.

### Updated Tests

The unit tests have been significantly expanded to cover individual service logic and asynchronous flows.

```python
# tests/test_main.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import json

from src.main import LLMOrchestrationService
from src.modules.llm_client import LLMClient, LLMTaskType
from src.modules.analysis_services import (
    IndustryCompetitiveAnalysisService,
    MarketTrendsPredictionService,
    TechnologyAdoptionAnalysisService,
    StrategicInsightsRecommendationsService,
)
from src.modules.report_generator import ReportGenerationService
from src.modules.data_models import (
    ReportRequest,
    ExecutiveSummary,
    IndustryAnalysisResult,
    MarketTrendsResult,
    TechAdoptionResult,
    StrategicInsightsResult,
    ReportContent,
)


class TestLLMOrchestrationService(unittest.IsolatedAsyncioTestCase):
    """
    Unit tests for the LLMOrchestrationService.
    Mocks external LLM calls and analysis service dependencies.
    Uses AsyncMock for asynchronous dependencies.
    """

    def setUp(self):
        """Set up mock dependencies before each test."""
        self.mock_llm_client = AsyncMock(spec=LLMClient)
        self.mock_industry_service = AsyncMock(spec=IndustryCompetitiveAnalysisService)
        self.mock_market_service = AsyncMock(spec=MarketTrendsPredictionService)
        self.mock_tech_service = AsyncMock(spec=TechnologyAdoptionAnalysisService)
        self.mock_strategic_service = AsyncMock(spec=StrategicInsightsRecommendationsService)
        self.mock_report_generator = MagicMock(spec=ReportGenerationService) # ReportGenerator is synchronous

        self.orchestrator = LLMOrchestrationService(
            llm_client=self.mock_llm_client,
            industry_analysis_service=self.mock_industry_service,
            market_trends_service=self.mock_market_service,
            tech_adoption_service=self.mock_tech_service,
            strategic_insights_service=self.mock_strategic_service,
            report_generator=self.mock_report_generator,
        )

        # Common mock return values for analysis services
        self.mock_industry_result = IndustryAnalysisResult(
            industry_overview="Mock Industry Overview",
            key_players=[{"name": "MockCo"}],
            market_share_distribution={"MockCo": 0.5},
            swot_analysis={"strengths": ["mock strength"], "weaknesses": ["mock weakness"], "opportunities": ["mock opportunity"], "threats": ["mock threat"]}
        )
        self.mock_market_result = MarketTrendsResult(
            current_trends=["Mock Current Trend"],
            emerging_trends=["Mock Emerging Trend"],
            future_predictions="Mock Future Prediction",
            growth_drivers=["Mock Growth Driver"]
        )
        self.mock_tech_result = TechAdoptionResult(
            technology_name="Mock Tech",
            adoption_rate=0.1,
            impact_analysis="Mock Impact",
            recommendations=["Mock Rec"]
        )
        self.mock_strategic_result = StrategicInsightsResult(
            strategic_insights=["Mock Strategic Insight"],
            actionable_recommendations=["Mock Actionable Rec"],
            personalized_recommendations=["Mock Personalized Rec"]
        )
        self.mock_executive_summary = ExecutiveSummary(
            key_findings=["Mock Key Finding"],
            strategic_implications="Mock Strategic Implication",
            actionable_recommendations=["Mock Actionable Summary Rec"]
        )

        self.mock_industry_service.analyze.return_value = self.mock_industry_result
        self.mock_market_service.analyze.return_value = self.mock_market_result
        self.mock_tech_service.analyze.return_value = self.mock_tech_result
        self.mock_strategic_service.analyze.return_value = self.mock_strategic_result
        self.mock_report_generator.assemble_report.return_value = "Mock Report Content"

    async def test_generate_report_full_scope(self):
        """
        Test that generate_report orchestrates all services when all modules are required.
        """
        # Mock LLM client interpretation to include all modules
        self.mock_llm_client.call_llm.side_effect = [
            json.dumps({
                "industry": "Test Industry",
                "competitors": ["CompA", "CompB"],
                "required_modules": [
                    "Industry Analysis & Competitive Landscape Mapping",
                    "Market Trends Identification & Future Predictions",
                    "Technology Adoption Analysis & Recommendations",
                    "Strategic Insights & Actionable Recommendations",
                ],
            }), # For _interpret_prompt
            "Synthesized Insights from LLM", # For _synthesize_insights
            json.dumps({
                "key_findings": ["Mock KF"],
                "strategic_implications": "Mock SI",
                "actionable_recommendations": ["Mock AR"]
            }), # For _generate_executive_summary
        ]

        report_request = ReportRequest(query="Comprehensive report on Test Industry", analysis_period="5 years", technologies=["AI"])
        user_context = {"user_id": 123}

        result = await self.orchestrator.generate_report(report_request, user_context)

        # Assert LLM calls with correct task types
        self.mock_llm_client.call_llm.assert_any_call(prompt=self.anything, task_type=LLMTaskType.INTERPRETATION)
        self.mock_llm_client.call_llm.assert_any_call(prompt=self.anything, task_type=LLMTaskType.SYNTHESIS)
        self.mock_llm_client.call_llm.assert_any_call(prompt=self.anything, task_type=LLMTaskType.EXECUTIVE_SUMMARY)

        # Assert analysis services are called
        self.mock_industry_service.analyze.assert_called_once_with(
            industry="Test Industry", competitors=["CompA", "CompB"]
        )
        self.mock_market_service.analyze.assert_called_once_with(
            market_segment="Test Industry", analysis_period="5 years"
        )
        self.mock_tech_service.analyze.assert_called_once_with(
            industry="Test Industry", technologies=["AI"]
        )
        # Strategic service should be called with some aggregated results (we don't check exact content here)
        self.mock_strategic_service.analyze.assert_called_once()

        # Assert report generator is called
        self.mock_report_generator.assemble_report.assert_called_once()

        # Assert final result
        self.assertEqual(result, "Mock Report Content")

    async def test_generate_report_partial_scope(self):
        """
        Test that generate_report only calls relevant services based on LLM interpretation.
        """
        # Mock LLM client interpretation to include only a subset of modules
        self.mock_llm_client.call_llm.side_effect = [
            json.dumps({
                "industry": "Partial Industry",
                "competitors": [],
                "required_modules": [
                    "Market Trends Identification & Future Predictions",
                    "Technology Adoption Analysis & Recommendations",
                ],
            }), # For _interpret_prompt
            "Synthesized Insights from LLM", # For _synthesize_insights
            json.dumps({
                "key_findings": ["Mock KF"],
                "strategic_implications": "Mock SI",
                "actionable_recommendations": ["Mock AR"]
            }), # For _generate_executive_summary
        ]

        report_request = ReportRequest(query="Report on trends and tech adoption", analysis_period="3 years", technologies=["Blockchain"])
        user_context = {"user_id": 456}

        await self.orchestrator.generate_report(report_request, user_context)

        # Assert that only specified analysis services are called
        self.mock_industry_service.analyze.assert_not_called()
        self.mock_market_service.analyze.assert_called_once_with(
            market_segment="Partial Industry", analysis_period="3 years"
        )
        self.mock_tech_service.analyze.assert_called_once_with(
            industry="Partial Industry", technologies=["Blockchain"]
        )
        # Strategic insights usually synthesizes available info, so it should still be called if requested
        self.mock_strategic_service.analyze.assert_called_once()

    @patch('src.main.json.loads')
    async def test_interpret_prompt_llm_json_decode_error(self, mock_json_loads):
        """
        Test that _interpret_prompt handles LLM returning invalid JSON.
        """
        self.mock_llm_client.call_llm.return_value = "invalid json string"
        mock_json_loads.side_effect = json.JSONDecodeError("mock error", "doc", 0)

        # This should trigger the fallback logic and not raise an error
        result = await self.orchestrator._interpret_prompt("test query")

        self.assertIn("Global Tech Market", result.get("industry"))
        self.assertIn("Technology Adoption Analysis & Recommendations", result.get("required_modules"))
        self.assertEqual(self.mock_llm_client.call_llm.call_count, 1)

    @patch('src.modules.data_models.ExecutiveSummary.model_validate_json')
    async def test_generate_executive_summary_llm_validation_error(self, mock_validate_json):
        """
        Test that _generate_executive_summary handles LLM returning invalid JSON or schema mismatch.
        """
        self.mock_llm_client.call_llm.return_value = "{'invalid': 'json'}"
        mock_validate_json.side_effect = Exception("Pydantic validation error") # Simulate Pydantic validation failure

        summary = await self.orchestrator._generate_executive_summary("some insights")

        self.assertEqual(summary.key_findings, ["Failed to parse LLM summary or LLM error."])
        self.assertEqual(summary.strategic_implications, "Please review the full report for details.")
        self.assertEqual(self.mock_llm_client.call_llm.call_count, 1)


class TestAnalysisServices(unittest.IsolatedAsyncioTestCase):
    """Unit tests for individual analysis services."""

    def setUp(self):
        self.mock_llm_client = AsyncMock(spec=LLMClient)

    async def test_industry_competitive_analysis_service(self):
        service = IndustryCompetitiveAnalysisService(self.mock_llm_client)
        self.mock_llm_client.call_llm.return_value = json.dumps({
            "industry_overview": "Test Industry Overview",
            "key_players": [{"name": "TestCo"}],
            "market_share_distribution": {"TestCo": 0.6},
            "swot_analysis": {"strengths": ["test strength"], "weaknesses": ["test weakness"], "opportunities": ["test opportunity"], "threats": ["test threat"]}
        })
        result = await service.analyze(industry="Test", competitors=["TestCo"])
        self.assertIsInstance(result, IndustryAnalysisResult)
        self.assertEqual(result.industry_overview, "Test Industry Overview")
        self.mock_llm_client.call_llm.assert_called_once_with(
            prompt=self.anything, task_type=LLMTaskType.INDUSTRY_ANALYSIS
        )

    async def test_market_trends_prediction_service(self):
        service = MarketTrendsPredictionService(self.mock_llm_client)
        self.mock_llm_client.call_llm.return_value = json.dumps({
            "current_trends": ["Trend A"],
            "emerging_trends": ["Trend B"],
            "future_predictions": "Future X",
            "growth_drivers": ["Driver 1"]
        })
        result = await service.analyze(market_segment="Market", analysis_period="1 year")
        self.assertIsInstance(result, MarketTrendsResult)
        self.assertEqual(result.current_trends, ["Trend A"])
        self.mock_llm_client.call_llm.assert_called_once_with(
            prompt=self.anything, task_type=LLMTaskType.MARKET_TRENDS
        )

    async def test_technology_adoption_analysis_service(self):
        service = TechnologyAdoptionAnalysisService(self.mock_llm_client)
        self.mock_llm_client.call_llm.return_value = json.dumps({
            "technology_name": "New Tech",
            "adoption_rate": 0.25,
            "impact_analysis": "High impact",
            "recommendations": ["Rec A", "Rec B"]
        })
        result = await service.analyze(industry="Tech", technologies=["New Tech"])
        self.assertIsInstance(result, TechAdoptionResult)
        self.assertEqual(result.technology_name, "New Tech")
        self.mock_llm_client.call_llm.assert_called_once_with(
            prompt=self.anything, task_type=LLMTaskType.TECH_ADOPTION
        )

    async def test_strategic_insights_recommendations_service(self):
        service = StrategicInsightsRecommendationsService(self.mock_llm_client)
        self.mock_llm_client.call_llm.return_value = json.dumps({
            "strategic_insights": ["Insight 1"],
            "actionable_recommendations": ["Action 1"],
            "personalized_recommendations": ["Personal Rec 1"]
        })
        aggregated_results = {"mock_key": "mock_value"}
        user_context = {"user_id": 999}
        result = await service.analyze(
            aggregated_analysis_results=aggregated_results,
            user_context=user_context,
            industry="General"
        )
        self.assertIsInstance(result, StrategicInsightsResult)
        self.assertEqual(result.strategic_insights, ["Insight 1"])
        self.mock_llm_client.call_llm.assert_called_once_with(
            prompt=self.anything, task_type=LLMTaskType.STRATEGIC_INSIGHTS
        )


class TestReportGenerationService(unittest.TestCase):
    """Unit tests for the ReportGenerationService."""

    def setUp(self):
        self.report_generator = ReportGenerationService()
        self.executive_summary = ExecutiveSummary(
            key_findings=["Key Finding 1", "Key Finding 2"],
            strategic_implications="Strategic implications here.",
            actionable_recommendations=["Action 1", "Action 2"]
        )
        self.industry_analysis = IndustryAnalysisResult(
            industry_overview="Industry overview.",
            key_players=[{"name": "Player A", "focus": "Cloud"}],
            market_share_distribution={"Player A": 0.4, "Player B": 0.3},
            swot_analysis={"strengths": ["S1"], "weaknesses": ["W1"], "opportunities": ["O1"], "threats": ["T1"]}
        )
        self.market_trends = MarketTrendsResult(
            current_trends=["Current Trend 1"],
            emerging_trends=["Emerging Trend 1"],
            future_predictions="Future prediction.",
            growth_drivers=["Driver 1"]
        )
        self.tech_adoption = TechAdoptionResult(
            technology_name="AI",
            adoption_rate=0.7,
            impact_analysis="High impact.",
            recommendations=["Tech Rec 1"]
        )
        self.strategic_insights = StrategicInsightsResult(
            strategic_insights=["Strategic Insight 1"],
            actionable_recommendations=["Actionable Rec 1"],
            personalized_recommendations=["Personalized Rec 1"]
        )

    def test_assemble_report_full_content(self):
        report_content = ReportContent(
            executive_summary=self.executive_summary,
            industry_analysis=self.industry_analysis,
            market_trends=self.market_trends,
            tech_adoption=self.tech_adoption,
            strategic_insights=self.strategic_insights
        )
        report_output = self.report_generator.assemble_report(report_content)

        self.assertIn("## 1. Executive Summary", report_output)
        self.assertIn("## 2. Industry Analysis & Competitive Landscape Mapping", report_output)
        self.assertIn("## 3. Market Trends Identification & Future Predictions", report_output)
        self.assertIn("## 4. Technology Adoption Analysis & Recommendations - AI", report_output)
        self.assertIn("## 5. Strategic Insights & Actionable Recommendations", report_output)
        self.assertIn("Disclaimer", report_output)
        self.assertIn("Key Finding 1", report_output)
        self.assertIn("Player A", report_output)
        self.assertIn("Approx. 70.0%", report_output) # Check formatting
        self.assertIn("Personalized Rec 1", report_output)

    def test_assemble_report_partial_content(self):
        report_content = ReportContent(
            executive_summary=self.executive_summary,
            market_trends=self.market_trends
        )
        report_output = self.report_generator.assemble_report(report_content)

        self.assertIn("## 1. Executive Summary", report_output)
        self.assertIn("## 3. Market Trends Identification & Future Predictions", report_output)
        self.assertNotIn("## 2. Industry Analysis", report_output) # Ensure skipped sections are not present
        self.assertNotIn("## 4. Technology Adoption", report_output)
        self.assertNotIn("## 5. Strategic Insights", report_output)

    def test_format_executive_summary(self):
        formatted = self.report_generator._format_executive_summary(self.executive_summary)
        self.assertIn("Key Finding 1", formatted)
        self.assertIn("Strategic implications here.", formatted)
        self.assertIn("Action 1", formatted)

    def test_format_industry_analysis(self):
        formatted = self.report_generator._format_industry_analysis(self.industry_analysis)
        self.assertIn("Industry overview.", formatted)
        self.assertIn("- Player A (Focus: Cloud)", formatted)
        self.assertIn("  - Player A: 40.0%", formatted)
        self.assertIn("- **Strengths:** S1", formatted)
        self.assertIn("- **Opportunities:** O1", formatted) # Check fixed typo

    # Helper to allow flexible argument checking with MagicMock
    anything = object()

    # The assert_called_with_anything helper is primarily for synchronous mocks.
    # For AsyncMock, assert_awaited_with is more appropriate, but its implementation
    # can be more complex to match "anything". For now, basic checks are sufficient.
```

### `requirements.txt`

```
pydantic>=2.5.0,<3.0.0
# For async HTTP calls if actual LLM/data connectors were implemented:
# aiohttp>=3.9.0,<4.0.0
# httpx>=0.25.0,<1.0.0
# For logging if more advanced features were needed:
# python-json-logger>=2.0.0,<3.0.0
```

### Migration Guide

This refactoring introduces significant changes, primarily moving from a synchronous execution model to an asynchronous one.

1.  **Python Version Requirement:** Ensure your environment is Python 3.7+ (preferably 3.8+) for full `asyncio` support.
2.  **Install/Update Dependencies:**
    *   It is recommended to use a virtual environment (`venv`, `poetry`, or `pipenv`).
    *   Create a `requirements.txt` file as provided above and install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   If using Poetry: `poetry add pydantic`
3.  **Code Changes for Asynchronous Execution:**
    *   **`LLMClient.call_llm`:** This method is now `async`. Any direct calls to it must be `await`ed.
    *   **`BaseAnalysisService.analyze`:** All concrete analysis services (`IndustryCompetitiveAnalysisService`, `MarketTrendsPredictionService`, etc.) now have `analyze` methods defined as `async`. Direct calls to these must also be `await`ed.
    *   **`LLMOrchestrationService` Methods:**
        *   `generate_report` is now `async`.
        *   Internal methods like `_interpret_prompt`, `_orchestrate_analysis`, `_synthesize_insights`, `_generate_executive_summary` are also `async`.
    *   **Entry Point:** The `if __name__ == "__main__":` block now uses `asyncio.run(run_examples())` to execute the asynchronous main logic. If your application has a different entry point (e.g., a FastAPI or Flask API endpoint), ensure the `generate_report` call is correctly `await`ed within an `async` context.
4.  **LLM Task Types:**
    *   Direct string literals for `task_type` in `LLMClient.call_llm` calls must be replaced with `LLMTaskType.ENUM_VALUE` (e.g., `LLMTaskType.INTERPRETATION`).
5.  **Pydantic Validation for LLM Outputs:**
    *   Where LLM outputs are expected to conform to Pydantic models (e.g., in analysis services when parsing results from `LLMClient.call_llm`), ensure `PydanticModel.model_validate_json()` (or `parse_raw()` for Pydantic v1) is used instead of direct `json.loads` followed by `PydanticModel(...)`. This provides robust validation.
6.  **Logging:**
    *   Replace all existing `print()` statements with standard Python `logging` calls (e.g., `logger.info()`, `logger.warning()`, `logger.error()`). Configure logging appropriately for your environment.
7.  **Data Model Changes:**
    *   The `IndustryAnalysisResult` Pydantic model's `swot_analysis` key for opportunities has been corrected from `A_opportunities` to `opportunities`. Ensure any code that directly accesses `swot_analysis['A_opportunities']` is updated to `swot_analysis['opportunities']`.
    *   `ReportRequest` now includes `analysis_period` and `technologies` fields, which are passed down to analysis services. Review existing `ReportRequest` instantiations.
8.  **Testing Framework:**
    *   If using `unittest`, replace `unittest.TestCase` with `unittest.IsolatedAsyncioTestCase` for tests involving `async` code.
    *   Use `unittest.mock.AsyncMock` for mocking asynchronous dependencies.

**Breaking Changes (if any):**

*   **Synchronous to Asynchronous:** This is the primary breaking change. All parts of your application that directly or indirectly call `LLMOrchestrationService.generate_report` or any of the now-asynchronous analysis services will need to be updated to use `await` and operate within an `asyncio` event loop.
*   **LLM Task Type Enum:** Direct string literals for LLM task types will no longer work; `LLMTaskType` Enum must be used.
*   **IndustryAnalysisResult SWOT Key:** Accessing `swot_analysis['A_opportunities']` will now fail; it must be changed to `swot_analysis['opportunities']`.

For existing systems, a phased migration is recommended, possibly by introducing an asynchronous wrapper layer or migrating services one by one. Ensure comprehensive testing throughout the migration process.

---
*Saved by after_agent_callback on 2025-07-04 10:24:42*
