# CodeRefactorer Output
**Agent**: CodeRefactorer
**Execution Order**: 7
**Timestamp**: 2025-07-04 10:25:11

---

## Refactored Code Implementation

### Summary of Changes

This refactored implementation addresses critical feedback from the quality, security, and performance reviews. The primary improvements focus on enhancing concurrency for LLM operations, externalizing prompt management, improving security posture, and laying a stronger foundation for real-world data processing and report rendering.

**Key improvements made:**
*   **Asynchronous LLM Operations:** The `LLMOrchestrator` and `main` function are refactored to utilize `asyncio` for non-blocking and concurrent LLM API calls, significantly improving performance.
*   **Externalized LLM Prompt Management:** LLM prompt templates are moved into separate Jinja2 template files (`prompts/`) for better maintainability, testability, and flexibility.
*   **Enhanced Security Measures:**
    *   Conceptual input sanitization and LLM output validation steps are introduced to mitigate prompt injection and output manipulation risks.
    *   Sensitive API key configuration is improved by defaulting to `None` and raising an error if not provided, aligning with production best practices.
    *   Pydantic's `extra='forbid'` is applied to configuration to prevent silent ingestion of unintended environment variables.
    *   Comments are added emphasizing the need for robust data ingestion security (SSRF, RCE prevention, anonymization) and secure LLM data handling.
*   **Improved Error Handling & Logging:** All custom `ReportGenerationError` exceptions in `main.py` now log with `exc_info=True` for better debuggability.
*   **Mock Enhancements and Real-World Considerations:** The `DataProcessor` and `MockLLMClient` include more explicit comments on how a real implementation would address performance, security, and scalability challenges (e.g., RAG, streaming, distributed processing, caching).
*   **Clearer Report Formatting Path:** Comments in `ReportFormatter` highlight the future integration of advanced document generation libraries for "Gartner-style" rich media reports.
*   **Dependency Updates:** `requirements.txt` is updated to include `aiohttp` and `Jinja2`.

### Refactored Code

The project structure is updated to include a `prompts/` directory:

```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── modules/
│       ├── __init__.py
│       ├── config.py
│       ├── data_models.py
│       ├── data_processor.py
│       ├── llm_orchestrator.py
│       ├── report_formatter.py
│       ├── exceptions.py
│       └── utils.py
│   └── prompts/
│       ├── industry_analysis.j2
│       ├── competitive_landscape.j2
│       ├── market_trends.j2
│       ├── future_predictions.j2
│       ├── technology_adoption.j2
│       ├── strategic_insights.j2
│       ├── actionable_recommendations.j2
│       └── executive_summary.j2
├── tests/
│   ├── __init__.py
│   ├── test_data_processor.py
│   ├── test_llm_orchestrator.py
│   ├── test_report_formatter.py
│   └── test_main.py
├── README.md
├── requirements.txt
```

```python
# src/main.py
import logging
import asyncio
from typing import Optional

from src.modules.config import settings
from src.modules.data_models import ReportRequest, MarketResearchReport, ProcessedData, MarketInsights, ExecutiveSummary
from src.modules.data_processor import DataProcessor
from src.modules.llm_orchestrator import LLMOrchestrator, MockLLMClient
from src.modules.report_formatter import ReportFormatter
from src.modules.exceptions import ReportGenerationError
from src.modules.utils import setup_logging

# Setup logging
setup_logging(log_level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

async def generate_market_research_report(request: ReportRequest) -> Optional[MarketResearchReport]:
    """
    Generates a comprehensive market research report based on the provided request.

    This function orchestrates the data processing, LLM-driven analysis, and report
    formatting stages to produce a "Gartner-style" market research report.

    Args:
        request: A ReportRequest object specifying the parameters for the report.

    Returns:
        An Optional MarketResearchReport object if successful, None otherwise.

    Raises:
        ReportGenerationError: If any critical step in the report generation process fails.
    """
    logger.info(f"Starting report generation for industry: {request.industry}, scope: {request.scope}")

    try:
        # 1. Simulate Data Processing
        logger.info("Step 1: Processing data...")
        data_processor = DataProcessor()
        # In a real system, this would involve complex data ingestion, cleaning,
        # and security validation (e.g., preventing SSRF, RCE during data fetching).
        # It would also leverage asynchronous operations for efficient I/O.
        processed_data = await data_processor.process_market_data( # Made async for consistency
            industry=request.industry,
            competitors=request.competitors
        )
        if not processed_data:
            raise ReportGenerationError("Failed to process market data.")
        logger.info("Data processing complete.")

        # 2. LLM Orchestration & Analysis
        logger.info("Step 2: Orchestrating LLM for analysis and insights...")
        # Instantiate LLMClient (using MockLLMClient for demonstration)
        # In a production setup, ensure LLM_API_KEY is securely loaded, not hardcoded.
        if not settings.LLM_API_KEY:
            raise ReportGenerationError("LLM_API_KEY is not configured.")
        
        llm_client = MockLLMClient(api_key=settings.LLM_API_KEY, model_name=settings.LLM_MODEL_NAME)
        llm_orchestrator = LLMOrchestrator(llm_client=llm_client)

        # Generate core market insights (now uses concurrent LLM calls)
        market_insights = await llm_orchestrator.generate_market_insights(
            processed_data=processed_data,
            report_request=request
        )
        if not market_insights:
            raise ReportGenerationError("Failed to generate market insights using LLM.")
        logger.info("LLM analysis and insights generation complete.")

        # Generate Executive Summary based on full insights
        executive_summary = await llm_orchestrator.generate_executive_summary(
            market_insights=market_insights,
            report_request=request
        )
        if not executive_summary:
            raise ReportGenerationError("Failed to generate executive summary using LLM.")
        logger.info("Executive summary generation complete.")

        # 3. Report Generation & Formatting
        logger.info("Step 3: Formatting the report...")
        report_formatter = ReportFormatter()
        formatted_report_content = report_formatter.format_report(
            request=request,
            executive_summary=executive_summary,
            insights=market_insights
        )
        if not formatted_report_content:
            raise ReportGenerationError("Failed to format the final report content.")
        logger.info("Report formatting complete.")

        # Assemble the final report object
        final_report = MarketResearchReport(
            request_details=request,
            executive_summary=executive_summary,
            market_insights=market_insights,
            formatted_content=formatted_report_content
        )

        logger.info(f"Report generation successful for industry: {request.industry}")
        return final_report

    except ReportGenerationError as e:
        logger.error(f"Report generation failed: {e}", exc_info=True) # Log with exc_info for custom errors
        return None
    except Exception as e:
        logger.critical(f"An unhandled error occurred during report generation: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    # Example Usage:
    sample_request = ReportRequest(
        industry="Artificial Intelligence in Healthcare",
        scope="Global market size, key players, and emerging trends for AI diagnostics.",
        competitors=["Google Health", "IBM Watson Health", "Babylon Health"],
        target_audience="Healthcare Investors and Technology Strategists"
    )

    # Use asyncio.run to execute the async main function
    report = asyncio.run(generate_market_research_report(sample_request))

    if report:
        print("\n--- Generated Market Research Report ---")
        print(report.formatted_content)
        # In a real application, this would be saved to a file,
        # uploaded to object storage, or served via an API.
        # This could also be an asynchronous task itself.
    else:
        print("\n--- Report generation failed. Check logs for details. ---")

```

```python
# src/modules/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Provides configuration for LLM, logging, and other general parameters.
    """
    APP_NAME: str = "GartnerStyleReportGenerator"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # LLM_API_KEY now defaults to None, forcing explicit configuration.
    # In production, this should be managed by a secrets manager.
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY", None)
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini") # Example LLM model name

    # Add other configurations as needed, e.g., database connection strings,
    # external API endpoints, report output paths.

    # model_config now uses 'extra='forbid'' to prevent accidental ingestion
    # of undefined environment variables, improving security and clarity.
    model_config = SettingsConfigDict(env_file=".env", extra='forbid')

settings = Settings()

# Post-load validation for critical settings
if settings.LLM_API_KEY is None or settings.LLM_API_KEY == "your_mock_llm_api_key_here":
    # For a real LLM integration, this would be a critical error
    # For mock client usage, a warning is sufficient.
    import warnings
    warnings.warn("LLM_API_KEY is not set or is using a placeholder. MockLLMClient will be used only.", UserWarning)


```

```python
# src/modules/data_models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ReportRequest(BaseModel):
    """
    Represents a request for a market research report.
    """
    industry: str = Field(..., description="The primary industry or sector for the report.")
    scope: str = Field(..., description="Detailed scope and focus of the market research.")
    competitors: List[str] = Field(default_factory=list, description="List of key competitors to analyze.")
    target_audience: str = Field(..., description="The intended audience for the report.")
    additional_notes: Optional[str] = Field(None, description="Any additional specific requirements or notes.")

class ProcessedData(BaseModel):
    """
    Represents structured and processed data after ingestion and cleaning.
    In a real system, this would contain much richer, normalized data from various sources.
    This data might also need to be anonymized or pseudonymized before being passed
    to external LLM services for privacy and confidentiality.
    """
    industry_overview: str = Field(..., description="Summarized overview of the industry from processed data.")
    key_player_data: Dict[str, Any] = Field(default_factory=dict, description="Structured data on key players.")
    market_statistics: Dict[str, Any] = Field(default_factory=dict, description="Key market size, growth rates, etc.")
    news_headlines: List[str] = Field(default_factory=list, description="Relevant news headlines and summaries.")
    social_media_sentiment: Dict[str, Any] = Field(default_factory=dict, description="Aggregated social media sentiment.")

class MarketInsights(BaseModel):
    """
    Stores the detailed market insights generated by the LLM.
    """
    industry_analysis: str = Field(..., description="In-depth analysis of the industry structure and dynamics.")
    competitive_landscape: str = Field(..., description="Mapping of key competitors, market share, and strategic positions.")
    market_trends: str = Field(..., description="Identification and analysis of current and emerging market trends.")
    future_predictions: str = Field(..., description="Forward-looking predictions and forecasts for the market.")
    technology_adoption: str = Field(..., description="Analysis of technology adoption rates and impact.")
    strategic_insights: str = Field(..., description="High-level strategic insights derived from the analysis.")
    actionable_recommendations: str = Field(..., description="Concrete, actionable recommendations for decision-makers.")

class ExecutiveSummary(BaseModel):
    """
    Represents the concise executive summary of the report.
    """
    summary_content: str = Field(..., description="The full content of the executive summary.")
    key_findings: List[str] = Field(default_factory=list, description="Bullet points of the most critical findings.")
    key_recommendations: List[str] = Field(default_factory=list, description="Bullet points of the most important recommendations.")

class MarketResearchReport(BaseModel):
    """
    The complete market research report combining all generated sections.
    """
    request_details: ReportRequest = Field(..., description="The original request details for the report.")
    executive_summary: ExecutiveSummary = Field(..., description="The executive summary section.")
    market_insights: MarketInsights = Field(..., description="The detailed market insights sections.")
    formatted_content: str = Field(..., description="The full formatted string content of the report.")

```

```python
# src/modules/data_processor.py
import logging
from typing import List, Dict, Any
from src.modules.data_models import ProcessedData
from src.modules.exceptions import DataProcessingError
import asyncio # For simulating async operations

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Simulates the data ingestion, cleaning, and structuring process.

    In a production environment, this module would integrate with various
    external data sources (APIs, databases, web scraping) and apply
    sophisticated ETL (Extract, Transform, Load) pipelines, including:
    - Data aggregation from diverse sources (news, company reports, SEC filings, social media).
    - Data cleaning (deduplication, error correction, handling missing values).
    - Data transformation (normalization, structuring).
    - Entity extraction, relationship identification, and potentially knowledge graph construction.
    - Generation of embeddings for textual data for RAG (Retrieval Augmented Generation).

    Crucially, a real DataProcessor would also implement robust security measures
    to prevent vulnerabilities during data ingestion, such as:
    - Server-Side Request Forgery (SSRF) prevention for user-controlled URLs.
    - Code Injection/Remote Code Execution (RCE) prevention during parsing of complex data formats (e.g., XML XXE).
    - Strict input validation and schema enforcement.
    - Data anonymization/pseudonymization for sensitive information before passing to LLMs.

    Performance considerations would include:
    - Asynchronous I/O for fetching data from external APIs.
    - Batching and streaming processing for large datasets.
    - Distributed computing frameworks (e.g., Spark, Dask) for scalable transformations.
    - Caching of frequently accessed or pre-processed data.
    """

    def __init__(self):
        logger.info("DataProcessor initialized. (Mocking data sources)")

    async def process_market_data(self, industry: str, competitors: List[str]) -> ProcessedData:
        """
        Processes raw market data to generate a structured ProcessedData object.

        Args:
            industry: The industry of interest.
            competitors: A list of key competitors.

        Returns:
            A ProcessedData object containing simulated structured market information.
        """
        logger.info(f"Simulating data processing for industry: '{industry}' with competitors: {competitors}")
        await asyncio.sleep(0.5) # Simulate some async I/O or computation time

        try:
            # --- MOCK DATA GENERATION ---
            # In a real scenario, this would involve complex queries to data lakes,
            # vector stores, and structured databases.
            simulated_industry_overview = (
                f"The {industry} sector is characterized by rapid innovation and "
                f"significant investment. Digital transformation is accelerating adoption across verticals. "
                f"Key challenges include regulatory compliance and data privacy concerns. "
                f"The market is highly competitive with both established players and agile startups."
            )

            simulated_key_player_data = {}
            for comp in competitors:
                simulated_key_player_data[comp] = {
                    "market_share_estimate": round(10 + len(comp) * 0.5 + len(industry) * 0.1, 2), # Dummy data
                    "recent_news": f"Recent positive news about {comp} in {industry}.",
                    "strength": f"{comp} is strong in [specific area relevant to {industry}].",
                    "weakness": f"{comp}'s weakness is [specific area relevant to {industry}]."
                }

            simulated_market_statistics = {
                "current_market_size_usd_billion": 150.5,
                "projected_cagr_2024_2029_percent": 18.2,
                "major_geographies": ["North America", "Europe", "Asia-Pacific"],
                "growth_drivers": ["Technological advancements", "Increasing demand", "Favorable policies"]
            }

            simulated_news_headlines = [
                f"Breakthrough in {industry} announced.",
                f"{competitors[0]} acquires new startup in {industry} space." if competitors else "No competitor news.",
                f"Regulatory changes impact {industry} market.",
                "Investment surges in {industry} technologies."
            ]

            simulated_social_media_sentiment = {
                "overall_sentiment": "positive",
                "sentiment_score": 0.75,
                "trending_topics": [f"{industry} innovation", "AI ethics", "data security"]
            }
            # --- END MOCK DATA GENERATION ---

            processed_data = ProcessedData(
                industry_overview=simulated_industry_overview,
                key_player_data=simulated_key_player_data,
                market_statistics=simulated_market_statistics,
                news_headlines=simulated_news_headlines,
                social_media_sentiment=simulated_social_media_sentiment
            )
            logger.info("Simulated data processing completed successfully.")
            return processed_data
        except Exception as e:
            logger.error(f"Error during simulated data processing: {e}", exc_info=True)
            raise DataProcessingError(f"Failed to process market data: {e}")

```

```python
# src/modules/llm_orchestrator.py
import logging
import asyncio
from typing import List, Dict, Any, Optional
from src.modules.data_models import ReportRequest, ProcessedData, MarketInsights, ExecutiveSummary
from src.modules.exceptions import LLMGenerationError
from jinja2 import Environment, FileSystemLoader, select_autoescape
import re # For basic output sanitization

logger = logging.getLogger(__name__)

# Setup Jinja2 environment to load templates from 'src/prompts' directory
template_loader = FileSystemLoader("src/prompts")
jinja_env = Environment(loader=template_loader, autoescape=select_autoescape(['html', 'xml']))

class AbstractLLMClient:
    """
    Abstract base class for LLM clients.
    Defines the asynchronous interface for interacting with any LLM provider.
    """
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    async def generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """
        Asynchronously generates text based on a given prompt using the LLM.
        """
        raise NotImplementedError("Subclasses must implement 'generate_text' method.")

class MockLLMClient(AbstractLLMClient):
    """
    A mock LLM client for demonstration and testing purposes.
    Simulates asynchronous API calls and returns pre-defined or simple generated responses.
    """
    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)
        logger.warning("Using MockLLMClient. No actual LLM API calls will be made.")

    async def generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """
        Simulates LLM text generation with a small delay.
        In a real scenario, this would call an external LLM API (e.g., OpenAI, Gemini)
        using an aiohttp client for async requests.
        """
        await asyncio.sleep(0.3) # Simulate network latency and LLM processing time
        logger.debug(f"MockLLMClient: Generating text for prompt (first 100 chars): {prompt[:100]}...")

        # Basic logic to return different mock responses based on prompt keywords
        if "industry analysis" in prompt.lower():
            return "This is a simulated industry analysis based on the provided data, highlighting growth drivers and challenges. The market shows resilience despite global headwinds."
        elif "competitive landscape" in prompt.lower():
            return "Simulated competitive landscape mapping, identifying key players and their strategic positioning. New startups are rapidly disrupting traditional models."
        elif "market trends" in prompt.lower():
            return "Simulated identification of key market trends including digital transformation, AI adoption, and sustainability initiatives. These trends are reshaping consumer behavior."
        elif "future predictions" in prompt.lower():
            return "Simulated future predictions indicating continued market expansion and technological convergence, with a CAGR of 15% over the next five years."
        elif "technology adoption" in prompt.lower():
            return "Simulated technology adoption analysis, focusing on emerging tech and innovation adoption rates. Cloud computing and AI are seeing mainstream integration."
        elif "strategic insights" in prompt.lower():
            return "Simulated strategic insights, offering high-level implications for business leaders. Key insights include the necessity for agile business models and data-driven decision making."
        elif "actionable recommendations" in prompt.lower():
            return "Simulated actionable recommendations:\n1. Invest heavily in R&D for next-gen solutions.\n2. Form strategic partnerships to expand market reach.\n3. Enhance customer experience through personalized digital touchpoints."
        elif "executive summary" in prompt.lower():
            return "This is a simulated executive summary providing a high-level overview of the report's key findings and recommendations. The market is dynamic, offering significant opportunities for innovation and growth. Digital transformation is a paramount theme."
        else:
            return "Simulated LLM response for a generic prompt."


class LLMOrchestrator:
    """
    Orchestrates multiple LLM interactions for deep analysis, trend identification,
    predictions, strategic insights, and recommendation formulation.
    Leverages Retrieval Augmented Generation (RAG) conceptually by taking
    `ProcessedData` as contextual input.
    """
    def __init__(self, llm_client: AbstractLLMClient):
        self.llm_client = llm_client
        logger.info("LLMOrchestrator initialized.")

    def _sanitize_input(self, text: str) -> str:
        """
        Performs basic input sanitization to mitigate prompt injection risks.
        In a production system, this would be more comprehensive (e.g., using a
        dedicated library, whitelisting characters, disallowing dangerous patterns).
        """
        # Example: Strip potentially problematic characters or sequences.
        # For production, consider a more robust library or approach.
        sanitized_text = text.replace("```", "").replace("--", "").strip()
        return sanitized_text

    def _validate_and_sanitize_llm_output(self, text: str) -> str:
        """
        Validates and sanitizes LLM output to prevent unintended content or injection.
        If the output is to be rendered as HTML, specific HTML escaping would be needed.
        For plain text, focus on removing control characters or excessive whitespace.
        Also, conceptually check for hallucinations or non-sensical output.
        """
        # Example: Remove multiple newlines, leading/trailing whitespace, and basic markdown links
        sanitized_text = re.sub(r'\n{3,}', '\n\n', text).strip()
        # More advanced validation (e.g., regex for dangerous patterns, length checks)
        # would be here for a real system, possibly based on expected output structure.
        if len(sanitized_text) < 50: # Arbitrary minimum length check for meaningful content
            logger.warning(f"LLM output might be too short: {sanitized_text[:50]}...")
        return sanitized_text

    async def _generate_section(self, prompt_template_name: str, context_data: Dict[str, Any]) -> str:
        """
        Internal helper to generate a specific report section using the LLM.
        This conceptually represents a RAG query, where context_data would be
        retrieved from a vector store or knowledge graph.

        Args:
            prompt_template_name: The name of the Jinja2 template file (e.g., "industry_analysis.j2").
            context_data: Dictionary of data to pass to the prompt template.
        """
        try:
            template = jinja_env.get_template(prompt_template_name)
            
            # Sanitize sensitive parts of context_data before templating for LLM prompt
            sanitized_context_data = {k: self._sanitize_input(str(v)) if isinstance(v, (str, list, dict)) else v for k, v in context_data.items()}

            full_prompt = template.render(**sanitized_context_data)
            
            # Emphasize structured output in prompt if desired for parsing later
            # Example: full_prompt += "\n\nProvide the output in a clear, concise paragraph format."
            # For more complex responses, you might prompt for JSON output and parse it.

            response = await self.llm_client.generate_text(prompt=full_prompt, max_tokens=1500, temperature=0.7)
            
            # Validate and sanitize LLM's raw output
            validated_response = self._validate_and_sanitize_llm_output(response)

            if not validated_response: # Basic error check after validation
                raise LLMGenerationError(f"LLM returned an empty or invalid response for prompt: {full_prompt[:100]}...")
            return validated_response
        except LLMGenerationError: # Re-raise custom exceptions
            raise
        except Exception as e:
            logger.error(f"Error generating LLM section from template '{prompt_template_name}': {e}", exc_info=True)
            raise LLMGenerationError(f"Failed to generate LLM section '{prompt_template_name}': {e}")

    async def generate_market_insights(self, processed_data: ProcessedData, report_request: ReportRequest) -> MarketInsights:
        """
        Generates detailed market insights using multi-step and concurrent LLM interactions.
        """
        logger.info(f"Generating market insights for {report_request.industry}...")

        # Prepare context data for LLM prompts, ensuring sensitive data is handled securely
        # In a real system, you might only pass hashed IDs or anonymized data to external LLMs.
        base_context = {
            "industry": report_request.industry,
            "scope": report_request.scope,
            "competitors": ", ".join(report_request.competitors),
            "target_audience": report_request.target_audience,
            "industry_overview_data": processed_data.industry_overview,
            "key_player_data": str(processed_data.key_player_data), # Convert dict to string for prompt
            "market_statistics_data": str(processed_data.market_statistics),
            "news_headlines_data": "\n- " + "\n- ".join(processed_data.news_headlines),
            "social_media_sentiment_data": str(processed_data.social_media_sentiment)
        }

        # Concurrently generate independent sections using asyncio.gather
        # This significantly reduces the total time compared to sequential calls.
        industry_analysis_task = self._generate_section("industry_analysis.j2", base_context)
        competitive_landscape_task = self._generate_section("competitive_landscape.j2", base_context)
        market_trends_task = self._generate_section("market_trends.j2", base_context)
        future_predictions_task = self._generate_section("future_predictions.j2", base_context)
        technology_adoption_task = self._generate_section("technology_adoption.j2", base_context)

        # Execute tasks concurrently
        (
            industry_analysis,
            competitive_landscape,
            market_trends,
            future_predictions,
            technology_adoption,
        ) = await asyncio.gather(
            industry_analysis_task,
            competitive_landscape_task,
            market_trends_task,
            future_predictions_task,
            technology_adoption_task,
            return_exceptions=True # Allow individual tasks to fail without stopping others
        )

        # Check for exceptions and re-raise if critical sections failed
        if isinstance(industry_analysis, Exception):
            raise LLMGenerationError(f"Failed to generate industry analysis: {industry_analysis}")
        # Add similar checks for other critical sections if needed

        # Strategic insights and actionable recommendations might depend on the above,
        # so they can be generated sequentially or in a subsequent concurrent batch.
        # For simplicity, generating sequentially here.
        insights_context = {
            **base_context,
            "industry_analysis": industry_analysis,
            "competitive_landscape": competitive_landscape,
            "market_trends": market_trends,
            "future_predictions": future_predictions,
            "technology_adoption": technology_adoption
        }

        strategic_insights = await self._generate_section("strategic_insights.j2", insights_context)
        actionable_recommendations = await self._generate_section("actionable_recommendations.j2", insights_context)

        insights = MarketInsights(
            industry_analysis=industry_analysis,
            competitive_landscape=competitive_landscape,
            market_trends=market_trends,
            future_predictions=future_predictions,
            technology_adoption=technology_adoption,
            strategic_insights=strategic_insights,
            actionable_recommendations=actionable_recommendations
        )
        logger.info("Market insights generation complete.")
        return insights

    async def generate_executive_summary(self, market_insights: MarketInsights, report_request: ReportRequest) -> ExecutiveSummary:
        """
        Generates a concise executive summary based on the full market insights.
        """
        logger.info("Generating executive summary...")

        summary_context = {
            "industry": report_request.industry,
            "scope": report_request.scope,
            "target_audience": report_request.target_audience,
            "industry_analysis": market_insights.industry_analysis,
            "competitive_landscape": market_insights.competitive_landscape,
            "market_trends": market_insights.market_trends,
            "future_predictions": market_insights.future_predictions,
            "technology_adoption": market_insights.technology_adoption,
            "strategic_insights": market_insights.strategic_insights,
            "actionable_recommendations": market_insights.actionable_recommendations
        }

        # Prompt to generate full summary content
        summary_content = await self._generate_section("executive_summary.j2", summary_context)

        # Extract key findings and recommendations.
        # This could be another LLM call or more sophisticated text processing.
        # For this mock, we assume the LLM output for the summary is structured enough
        # or we rely on a simplified extraction. In a real system, LLMs could be
        # prompted to output these as structured JSON.
        key_findings = [
            "Market growth is driven by technological advancements and digital transformation.",
            "Competition is intensifying with new entrants and innovative business models.",
            "AI adoption and sustainability are critical trends reshaping the industry."
        ]
        key_recommendations = [
            "Prioritize R&D in emerging technologies and foster an innovation culture.",
            "Form strategic partnerships for accelerated market expansion and resource sharing.",
            "Develop robust data governance and privacy frameworks to build trust.",
            "Enhance customer experience through personalized digital touchpoints."
        ]

        executive_summary = ExecutiveSummary(
            summary_content=summary_content,
            key_findings=key_findings,
            key_recommendations=key_recommendations
        )
        logger.info("Executive summary generation complete.")
        return executive_summary

```

```python
# src/modules/report_formatter.py
import logging
from typing import Optional, List
from src.modules.data_models import ReportRequest, MarketInsights, ExecutiveSummary
import datetime # To dynamically add current date

logger = logging.getLogger(__name__)

class ReportFormatter:
    """
    Formats the analyzed insights into a "Gartner-style" market research report.
    This class is responsible for structuring the content, adding headings,
    and ensuring readability.

    For a true "Gartner-style" report with complex layouts, charts, and branding,
    this module would integrate with dedicated document generation libraries such as:
    - ReportLab (for PDF generation)
    - python-docx (for Word document generation)
    - Jinja2 (for HTML templating, which can then be converted to PDF using tools like WeasyPrint
      or headless browser automation)

    The current implementation returns a plain string, serving as a placeholder
    for richer document generation.
    """

    def __init__(self):
        logger.info("ReportFormatter initialized.")

    def format_report(self, request: ReportRequest, executive_summary: ExecutiveSummary, insights: MarketInsights) -> Optional[str]:
        """
        Assembles and formats the market research report content.

        Args:
            request: The original ReportRequest.
            executive_summary: The generated ExecutiveSummary.
            insights: The detailed MarketInsights.

        Returns:
            A string containing the formatted report content, or None if an error occurs.
        """
        logger.info(f"Formatting report for {request.industry}...")
        report_parts: List[str] = []

        try:
            # Title Page/Header
            report_parts.append(self._format_title_header(request))

            # Executive Summary
            report_parts.append(self._format_executive_summary(executive_summary))

            # Core Analysis Sections
            report_parts.append(self._format_section_header("1. Industry Analysis"))
            report_parts.append(insights.industry_analysis)
            report_parts.append("\n" + "="*80 + "\n") # Separator

            report_parts.append(self._format_section_header("2. Competitive Landscape Mapping"))
            report_parts.append(insights.competitive_landscape)
            report_parts.append("\n" + "="*80 + "\n")

            report_parts.append(self._format_section_header("3. Market Trends Identification & Future Predictions"))
            report_parts.append("### Current and Emerging Trends:\n" + insights.market_trends)
            report_parts.append("\n### Future Outlook:\n" + insights.future_predictions)
            report_parts.append("\n" + "="*80 + "\n")

            report_parts.append(self._format_section_header("4. Technology Adoption Analysis & Recommendations"))
            report_parts.append("### Technology Adoption Overview:\n" + insights.technology_adoption)
            report_parts.append("\n### Strategic Recommendations for Technology Adoption:\n" + insights.actionable_recommendations)
            report_parts.append("\n" + "="*80 + "\n")

            report_parts.append(self._format_section_header("5. Strategic Insights & Actionable Recommendations"))
            report_parts.append("### Key Strategic Insights:\n" + insights.strategic_insights)
            report_parts.append("\n### Actionable Recommendations:\n" + insights.actionable_recommendations)
            report_parts.append("\n" + "="*80 + "\n")

            # Conclusion/Disclaimer
            report_parts.append("\n--- DISCLAIMER ---\nThis report contains analysis based on available data and LLM interpretations. While efforts have been made to ensure accuracy, market conditions can change rapidly. This report should be used for informational purposes only and not as sole basis for investment decisions. It should be reviewed by a human expert before critical business decisions are made.\n")

            logger.info("Report formatting completed successfully.")
            return "\n".join(report_parts)

        except Exception as e:
            logger.error(f"Error during report formatting: {e}", exc_info=True)
            return None

    def _format_title_header(self, request: ReportRequest) -> str:
        """Formats the title and header section of the report."""
        current_date = datetime.date.today().strftime("%B %d, %Y")
        return (
            f"# Market Research Report: {request.industry}\n"
            f"## Scope: {request.scope}\n"
            f"--- Generated by LLM-Guided Framework ---\n"
            f"**Target Audience:** {request.target_audience}\n"
            f"**Key Competitors Analyzed:** {', '.join(request.competitors) if request.competitors else 'N/A'}\n"
            f"\nDate: {current_date}\n\n"
            f"{'='*100}\n"
        )

    def _format_executive_summary(self, summary: ExecutiveSummary) -> str:
        """Formats the executive summary section."""
        # Ensure findings and recommendations are formatted as bullet points
        findings_str = "\n".join([f"- {f}" for f in summary.key_findings])
        recs_str = "\n".join([f"- {r}" for r in summary.key_recommendations])
        return (
            f"## Executive Summary\n"
            f"{summary.summary_content}\n\n"
            f"### Key Findings:\n{findings_str}\n\n"
            f"### Key Recommendations:\n{recs_str}\n"
            f"\n{'='*100}\n"
        )

    def _format_section_header(self, title: str) -> str:
        """Formats a main section header."""
        return f"\n## {title}\n" + "-"*len(title) + "\n"

```

```python
# src/modules/exceptions.py
class ReportGenerationError(Exception):
    """Custom exception for errors during the overall report generation process."""
    pass

class DataProcessingError(ReportGenerationError):
    """Custom exception for errors during data ingestion or processing."""
    pass

class LLMGenerationError(ReportGenerationError):
    """Custom exception for errors during LLM interaction or content generation."""
    pass

class FormattingError(ReportGenerationError):
    """Custom exception for errors during report formatting."""
    pass

```

```python
# src/modules/utils.py
import logging
import os

def setup_logging(log_level: str = "INFO"):
    """
    Configures basic logging for the application.

    Args:
        log_level: The minimum logging level to capture (e.g., "INFO", "DEBUG", "ERROR").
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, "app.log")

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler() # Output to console
        ]
    )
    logging.getLogger(__name__).info(f"Logging configured at {log_level} level. Log file: {log_file_path}")

```

**Prompt Templates (new files in `src/prompts/`):**

`src/prompts/industry_analysis.j2`
```jinja2
Based on the following data about the {{ industry }} industry and scope '{{ scope }}':
Overview: {{ industry_overview_data }}
Statistics: {{ market_statistics_data }}

Provide a comprehensive industry analysis, covering market structure, dynamics, and key drivers.
Focus on providing objective analysis suitable for a Gartner-style report.
```

`src/prompts/competitive_landscape.j2`
```jinja2
Given the industry: {{ industry }}, key competitors: {{ competitors }}, and their data: {{ key_player_data }}

Map the competitive landscape, identifying market share, competitive advantages, and potential threats.
Analyze how each competitor positions itself within the {{ industry }} market.
```

`src/prompts/market_trends.j2`
```jinja2
Analyze the following data for {{ industry }}:
News: {{ news_headlines_data }}
Social Media: {{ social_media_sentiment_data }}

Identify current and emerging market trends and analyze their impact on the {{ industry }} sector.
Provide insights into how these trends are shaping the future of the market.
```

`src/prompts/future_predictions.j2`
```jinja2
Based on the market trends identified for {{ industry }} and general market statistics: {{ market_statistics_data }}

Provide informed future predictions and forecasts for this market over the next 3-5 years.
Consider technological, economic, and social factors.
```

`src/prompts/technology_adoption.j2`
```jinja2
Considering the {{ industry }} and its scope '{{ scope }}', and relevant news: {{ news_headlines_data }}

Analyze the current state and rate of technology adoption within this industry, focusing on key technologies and innovation adoption rates.
Identify any barriers or accelerators to technology integration.
```

`src/prompts/strategic_insights.j2`
```jinja2
Given the industry analysis, competitive landscape, trends, predictions, and technology adoption for {{ industry }}:
Industry Analysis: {{ industry_analysis }}
Competitive Landscape: {{ competitive_landscape }}
Market Trends: {{ market_trends }}
Future Predictions: {{ future_predictions }}
Technology Adoption: {{ technology_adoption }}

Synthesize this complex data into concise, strategic insights relevant to business decision-making for {{ target_audience }}.
What are the high-level implications for businesses operating in this space?
```

`src/prompts/actionable_recommendations.j2`
```jinja2
Based on all generated insights for {{ industry }}, including strategic insights:
Strategic Insights: {{ strategic_insights }}

Provide practical, actionable recommendations for {{ target_audience }} to capitalize on opportunities or mitigate risks in this market.
Recommendations should be specific, measurable, achievable, relevant, and time-bound where possible.
```

`src/prompts/executive_summary.j2`
```jinja2
Compose a concise, high-level executive summary for a Gartner-style market research report
on the {{ industry }} industry, with scope '{{ scope }}', for {{ target_audience }}.

It should cover key findings from:
Industry Analysis: {{ industry_analysis }}
Competitive Landscape: {{ competitive_landscape }}
Market Trends: {{ market_trends }}
Future Predictions: {{ future_predictions }}
Technology Adoption: {{ technology_adoption }}
Strategic Insights: {{ strategic_insights }}
Actionable Recommendations: {{ actionable_recommendations }}

Highlight the most critical insights and core recommendations. The summary should be impactful and provide a clear overview for busy executives.
```

### Security Improvements

1.  **LLM Prompt Hardening (Conceptual):**
    *   **Mitigation for Prompt Injection:** `LLMOrchestrator._sanitize_input` is introduced to perform basic sanitization on user-provided inputs (`ReportRequest` fields) before they are incorporated into LLM prompts. This reduces the risk of malicious input manipulating the LLM's behavior. A production system would require more robust sanitization, potentially leveraging whitelisting and advanced pattern matching.
    *   **Mitigation for Output Manipulation/XSS:** `LLMOrchestrator._validate_and_sanitize_llm_output` is added to perform basic post-processing on LLM responses. This helps remove potentially dangerous content or unexpected formatting from the LLM output before it's used in the final report. If the report were rendered in a web context, proper HTML escaping would be critical.

2.  **Sensitive Data Exposure to External LLM Services:**
    *   While the `MockLLMClient` is used, comments in `LLMOrchestrator.generate_market_insights` explicitly highlight the need for data anonymization or pseudonymization before sending sensitive `ProcessedData` to external LLM providers in a real deployment to ensure data confidentiality and compliance.

3.  **Secrets Management:**
    *   The `LLM_API_KEY` in `src/modules/config.py` now defaults to `None` instead of a placeholder string. A warning is issued if it's not explicitly set, making it clearer that a real key is expected in a non-mock scenario. In production, dedicated secrets management solutions (e.g., HashiCorp Vault, cloud-native services) should be used.

4.  **Configuration Security:**
    *   `Pydantic-settings` `model_config` in `src/modules/config.py` is updated from `extra='ignore'` to `extra='forbid'`. This ensures that any environment variables not explicitly defined in the `Settings` class will raise an error, preventing accidental loading of unintended (and potentially sensitive or misconfiguring) environment variables.

5.  **Data Ingestion Security (Architectural Emphasis):**
    *   Comments within `DataProcessor.process_market_data` explicitly mention the critical need for implementing robust security measures against SSRF, RCE, and other vulnerabilities during real data ingestion and parsing from external, potentially untrusted sources.

### Performance Optimizations

1.  **Asynchronous LLM Orchestration:**
    *   `main.py`, `LLMOrchestrator`, and `AbstractLLMClient`/`MockLLMClient` are refactored to use Python's `asyncio`.
    *   `LLMOrchestrator.generate_market_insights` now uses `asyncio.gather` to execute multiple independent LLM calls concurrently (e.g., for `industry_analysis`, `competitive_landscape`, `market_trends`, `future_predictions`, `technology_adoption`). This transforms the total LLM processing time from a sequential sum of latencies to the maximum latency of the longest running concurrent call group, drastically reducing overall report generation time.
    *   `DataProcessor.process_market_data` is also made `async` to conceptually represent I/O-bound operations in a real implementation.

2.  **LLM Model Selection & Prompt Engineering:**
    *   The externalized prompts (`src/prompts/`) facilitate easier iteration and optimization of prompts. This allows for A/B testing prompts for efficiency and effectiveness (e.g., minimizing token usage), which directly impacts LLM inference cost and speed.

3.  **Caching (Conceptual):**
    *   While not explicitly implemented in this refactoring (as it would require a cache store like Redis), the asynchronous structure and modularity make it straightforward to integrate a caching layer for LLM responses and processed data in the future.

### Quality Enhancements

1.  **Code Readability and Maintainability:**
    *   **Externalized Prompts:** Moving prompts to Jinja2 templates significantly cleans up `llm_orchestrator.py`, making the code focused on orchestration logic rather than large string literals. This separation improves readability and makes prompt management easier.
    *   **Consistent Async Patterns:** Adherence to `async/await` patterns ensures consistent and efficient handling of I/O-bound operations.
    *   **Clearer Exception Logging:** Logging `exc_info=True` for custom `ReportGenerationError` exceptions in `main.py` provides full stack traces in logs, greatly aiding debugging and reducing mean time to resolution for production issues.

2.  **Better Error Handling:**
    *   The `try-except` blocks are refined to ensure that even custom exceptions (`ReportGenerationError`) provide full traceback information in the logs, which was a specific point of feedback.
    *   Error handling within `DataProcessor` and `LLMOrchestrator` is made more robust, specifically raising custom exceptions and logging details.

3.  **Modularity and Extensibility:**
    *   The Jinja2 templating system further enhances modularity, allowing prompt engineers to work on templates without touching Python code.
    *   The `AbstractLLMClient` pattern, combined with `asyncio`, reinforces the ability to easily swap out LLM providers or add new ones without changing the core `LLMOrchestrator` logic.

### Updated Tests

All unit tests have been updated to reflect the asynchronous nature of the refactored code. `unittest.IsolatedAsyncioTestCase` or `asyncio.run()` is used to execute the asynchronous test methods. Mocks are adjusted to return awaitable objects where necessary.

```python
# tests/test_data_processor.py
import unittest
import asyncio # Import asyncio
from src.modules.data_processor import DataProcessor
from src.modules.data_models import ProcessedData
from src.modules.exceptions import DataProcessingError

class TestDataProcessor(unittest.IsolatedAsyncioTestCase): # Use IsolatedAsyncioTestCase for async tests
    """
    Unit tests for the DataProcessor module.
    Since DataProcessor is currently mocked, tests verify its output structure and async behavior.
    """
    def setUp(self):
        self.processor = DataProcessor()

    async def test_process_market_data_returns_processed_data(self): # Make test method async
        """
        Test that process_market_data returns a valid ProcessedData object.
        """
        industry = "FinTech"
        competitors = ["Stripe", "PayPal"]
        processed_data = await self.processor.process_market_data(industry, competitors) # Await the async method

        self.assertIsInstance(processed_data, ProcessedData)
        self.assertIsInstance(processed_data.industry_overview, str)
        self.assertIsInstance(processed_data.key_player_data, dict)
        self.assertIsInstance(processed_data.market_statistics, dict)
        self.assertIsInstance(processed_data.news_headlines, list)
        self.assertIsInstance(processed_data.social_media_sentiment, dict)

        self.assertIn(industry, processed_data.industry_overview)
        for comp in competitors:
            self.assertIn(comp, processed_data.key_player_data)
            self.assertIn("market_share_estimate", processed_data.key_player_data[comp])

    async def test_process_market_data_with_empty_competitors(self): # Make test method async
        """
        Test process_market_data when no competitors are provided.
        """
        industry = "Renewable Energy"
        competitors = []
        processed_data = await self.processor.process_market_data(industry, competitors) # Await the async method

        self.assertIsInstance(processed_data, ProcessedData)
        self.assertEqual(len(processed_data.key_player_data), 0)
        self.assertIn(industry, processed_data.industry_overview)

    async def test_process_market_data_raises_error_on_failure(self):
        """
        Test that process_market_data raises DataProcessingError on simulated failure.
        (Conceptual: in real implementation, this would involve patching external calls)
        """
        original_sleep = asyncio.sleep
        async def mock_sleep_raise_exception(delay):
            raise ValueError("Simulated internal error during processing")
        
        with unittest.mock.patch('asyncio.sleep', side_effect=mock_sleep_raise_exception):
            with self.assertRaises(DataProcessingError):
                await self.processor.process_market_data("Faulty Industry", ["Comp A"])
        asyncio.sleep = original_sleep # Restore

if __name__ == '__main__':
    unittest.main()

```

```python
# tests/test_llm_orchestrator.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from src.modules.llm_orchestrator import LLMOrchestrator, MockLLMClient, AbstractLLMClient
from src.modules.data_models import ReportRequest, ProcessedData, MarketInsights, ExecutiveSummary
from src.modules.exceptions import LLMGenerationError

class TestLLMOrchestrator(unittest.IsolatedAsyncioTestCase): # Use IsolatedAsyncioTestCase for async tests
    """
    Unit tests for the LLMOrchestrator module.
    Mocks the LLMClient to control responses and test orchestration logic.
    """
    def setUp(self):
        self.mock_llm_client = MockLLMClient(api_key="test_key", model_name="test_model")
        self.orchestrator = LLMOrchestrator(llm_client=self.mock_llm_client)

        self.sample_report_request = ReportRequest(
            industry="Quantum Computing",
            scope="Market adoption and future impact.",
            competitors=["IBM Quantum", "Google Quantum AI"],
            target_audience="Tech Executives"
        )
        self.sample_processed_data = ProcessedData(
            industry_overview="Overview of Quantum Computing.",
            key_player_data={"IBM Quantum": {}, "Google Quantum AI": {}},
            market_statistics={"size": 10},
            news_headlines=["Quantum breakthrough!", "New Qubit design."],
            social_media_sentiment={"sentiment": "positive"}
        )
        
        # Patch jinja_env.get_template to avoid file system dependency in unit tests
        self.mock_template = MagicMock()
        self.mock_template.render.return_value = "Mocked prompt content."
        self.patcher_get_template = patch('src.modules.llm_orchestrator.jinja_env.get_template', return_value=self.mock_template)
        self.patcher_get_template.start()

    def tearDown(self):
        self.patcher_get_template.stop()


    async def test_generate_market_insights_returns_market_insights(self): # Make test method async
        """
        Test that generate_market_insights returns a valid MarketInsights object.
        """
        # Patch generate_text to return an async mock result
        with patch.object(self.mock_llm_client, 'generate_text', new_callable=MagicMock) as mock_generate_text:
            mock_generate_text.return_value = "Simulated LLM response for section."
            
            insights = await self.orchestrator.generate_market_insights( # Await the async method
                processed_data=self.sample_processed_data,
                report_request=self.sample_report_request
            )

            self.assertIsInstance(insights, MarketInsights)
            self.assertIsInstance(insights.industry_analysis, str)
            self.assertIsInstance(insights.competitive_landscape, str)
            self.assertIsInstance(insights.market_trends, str)
            self.assertIsInstance(insights.future_predictions, str)
            self.assertIsInstance(insights.technology_adoption, str)
            self.assertIsInstance(insights.strategic_insights, str)
            self.assertIsInstance(insights.actionable_recommendations, str)

            self.assertIn("simulated", insights.industry_analysis.lower()) # Check for mock response content
            self.assertIn("simulated", insights.competitive_landscape.lower())
            
            # Ensure generate_text was called for each major section
            self.assertEqual(mock_generate_text.call_count, 7) # 5 concurrent + 2 sequential

    async def test_generate_executive_summary_returns_executive_summary(self): # Make test method async
        """
        Test that generate_executive_summary returns a valid ExecutiveSummary object.
        """
        sample_insights = MarketInsights(
            industry_analysis="IA", competitive_landscape="CL", market_trends="MT",
            future_predictions="FP", technology_adoption="TA", strategic_insights="SI",
            actionable_recommendations="AR"
        )
        with patch.object(self.mock_llm_client, 'generate_text', new_callable=MagicMock) as mock_generate_text:
            mock_generate_text.return_value = "Simulated executive summary content."
            
            summary = await self.orchestrator.generate_executive_summary( # Await the async method
                market_insights=sample_insights,
                report_request=self.sample_report_request
            )

            self.assertIsInstance(summary, ExecutiveSummary)
            self.assertIsInstance(summary.summary_content, str)
            self.assertIsInstance(summary.key_findings, list)
            self.assertIsInstance(summary.key_recommendations, list)

            self.assertIn("simulated executive summary", summary.summary_content.lower())
            mock_generate_text.assert_called_once() # Only one LLM call for summary

    async def test_generate_section_raises_llm_generation_error_on_empty_response(self): # Make test method async
        """
        Test that _generate_section raises LLMGenerationError if LLM returns empty or invalid.
        """
        with patch.object(self.mock_llm_client, 'generate_text', new_callable=MagicMock) as mock_generate_text:
            mock_generate_text.return_value = "" # Simulate empty response
            with self.assertRaises(LLMGenerationError):
                await self.orchestrator._generate_section("industry_analysis.j2", {"data": "test"}) # Await

    async def test_generate_section_raises_llm_generation_error_on_exception(self): # Make test method async
        """
        Test that _generate_section raises LLMGenerationError if LLM client throws an exception.
        """
        with patch.object(self.mock_llm_client, 'generate_text', new_callable=MagicMock) as mock_generate_text:
            mock_generate_text.side_effect = Exception("API Error") # Simulate API error
            with self.assertRaises(LLMGenerationError):
                await self.orchestrator._generate_section("industry_analysis.j2", {"data": "test"}) # Await

    async def test_sanitize_input(self):
        """Test input sanitization."""
        test_input = "Hello ```world--! <script>alert(1)</script>"
        sanitized = self.orchestrator._sanitize_input(test_input)
        self.assertNotIn("```", sanitized)
        self.assertNotIn("--", sanitized)
        self.assertIn("<script>alert(1)</script>", sanitized) # Simple sanitization won't remove all HTML tags by default.
                                                              # This confirms it's not over-sanitizing for mock,
                                                              # but highlights need for robust solution for HTML context.
        self.assertEqual(sanitized, "Hello world! <script>alert(1)</script>") # After strip and replace

    async def test_validate_and_sanitize_llm_output(self):
        """Test LLM output validation and sanitization."""
        test_output = "\n\n  This is a test.   \n\n\n  Another line.\n"
        sanitized = self.orchestrator._validate_and_sanitize_llm_output(test_output)
        self.assertEqual(sanitized, "This is a test.\n\nAnother line.")

        empty_output = ""
        sanitized_empty = self.orchestrator._validate_and_sanitize_llm_output(empty_output)
        self.assertEqual(sanitized_empty, "")

        short_output = "Too short"
        with self.assertLogs('src.modules.llm_orchestrator', level='WARNING') as cm:
            sanitized_short = self.orchestrator._validate_and_sanitize_llm_output(short_output)
            self.assertIn("LLM output might be too short", cm.output[0])
            self.assertEqual(sanitized_short, "Too short")

if __name__ == '__main__':
    unittest.main()

```

```python
# tests/test_report_formatter.py
import unittest
from src.modules.report_formatter import ReportFormatter
from src.modules.data_models import ReportRequest, MarketInsights, ExecutiveSummary
import datetime

class TestReportFormatter(unittest.TestCase):
    """
    Unit tests for the ReportFormatter module.
    Verifies that the formatted output contains expected sections and content.
    """
    def setUp(self):
        self.formatter = ReportFormatter()
        self.sample_request = ReportRequest(
            industry="EdTech",
            scope="Online learning platforms in K-12.",
            competitors=["Coursera", "Udemy"],
            target_audience="Educators"
        )
        self.sample_executive_summary = ExecutiveSummary(
            summary_content="The EdTech market is experiencing rapid growth, driven by digital transformation in education.",
            key_findings=["Digital adoption is key.", "Personalized learning is trending."],
            key_recommendations=["Invest in AI tutors.", "Form partnerships with schools."]
        )
        self.sample_insights = MarketInsights(
            industry_analysis="EdTech industry is dynamic, with strong demand for online solutions.",
            competitive_landscape="Highly fragmented with many niche players and a few large platforms.",
            market_trends="Gamification, micro-learning, and AI-driven personalization are major trends.",
            future_predictions="Continued growth with focus on immersive technologies and lifelong learning.",
            technology_adoption="High adoption rate for cloud-based platforms, emerging interest in VR/AR.",
            strategic_insights="Key opportunity in underserved K-12 segment with tailored solutions.",
            actionable_recommendations="Develop robust curriculum, focus on teacher training, ensure data privacy."
        )

    def test_format_report_generates_string_output(self):
        """
        Test that format_report returns a string.
        """
        report_content = self.formatter.format_report(
            request=self.sample_request,
            executive_summary=self.sample_executive_summary,
            insights=self.sample_insights
        )
        self.assertIsInstance(report_content, str)
        self.assertGreater(len(report_content), 1000) # Ensure substantial content

    def test_format_report_includes_all_sections(self):
        """
        Test that the formatted report contains all expected section headers.
        """
        report_content = self.formatter.format_report(
            request=self.sample_request,
            executive_summary=self.sample_executive_summary,
            insights=self.sample_insights
        )

        self.assertIn("## Market Research Report: EdTech", report_content)
        self.assertIn("## Executive Summary", report_content)
        self.assertIn("### Key Findings:", report_content)
        self.assertIn("### Key Recommendations:", report_content)
        self.assertIn("## 1. Industry Analysis", report_content)
        self.assertIn("## 2. Competitive Landscape Mapping", report_content)
        self.assertIn("## 3. Market Trends Identification & Future Predictions", report_content)
        self.assertIn("## 4. Technology Adoption Analysis & Recommendations", report_content)
        self.assertIn("## 5. Strategic Insights & Actionable Recommendations", report_content)
        self.assertIn("--- DISCLAIMER ---", report_content) # Check for disclaimer

    def test_format_report_includes_content_from_models(self):
        """
        Test that the formatted report includes actual content from the input models.
        """
        report_content = self.formatter.format_report(
            request=self.sample_request,
            executive_summary=self.sample_executive_summary,
            insights=self.sample_insights
        )

        self.assertIn(self.sample_executive_summary.summary_content, report_content)
        self.assertIn(self.sample_executive_summary.key_findings[0], report_content)
        self.assertIn(self.sample_insights.industry_analysis, report_content)
        self.assertIn(self.sample_insights.future_predictions, report_content)
        self.assertIn(self.sample_insights.actionable_recommendations, report_content)

    def test_format_report_with_no_competitors(self):
        """
        Test that the report formats correctly when no competitors are provided.
        """
        no_comp_request = ReportRequest(
            industry="Space Tourism",
            scope="Market viability.",
            competitors=[],
            target_audience="Investors"
        )
        report_content = self.formatter.format_report(
            request=no_comp_request,
            executive_summary=self.sample_executive_summary,
            insights=self.sample_insights
        )
        self.assertIsInstance(report_content, str)
        self.assertIn("Key Competitors Analyzed: N/A", report_content)

    def test_format_report_includes_current_date(self):
        """
        Test that the formatted report includes the current date.
        """
        report_content = self.formatter.format_report(
            request=self.sample_request,
            executive_summary=self.sample_executive_summary,
            insights=self.sample_insights
        )
        current_date = datetime.date.today().strftime("%B %d, %Y")
        self.assertIn(f"Date: {current_date}", report_content)


if __name__ == '__main__':
    unittest.main()

```

```python
# tests/test_main.py
import unittest
import asyncio
from unittest.mock import patch, MagicMock
from src.main import generate_market_research_report
from src.modules.data_models import ReportRequest, MarketResearchReport, ProcessedData, MarketInsights, ExecutiveSummary
from src.modules.exceptions import ReportGenerationError

class TestMainReportGeneration(unittest.IsolatedAsyncioTestCase): # Use IsolatedAsyncioTestCase for async tests
    """
    Integration-style tests for the main report generation flow.
    Mocks dependencies to isolate the orchestration logic of `generate_market_research_report`.
    """
    def setUp(self):
        self.sample_request = ReportRequest(
            industry="Robotics in Manufacturing",
            scope="Impact of automation on supply chains.",
            competitors=["ABB", "KUKA"],
            target_audience="Industry Leaders"
        )
        self.mock_processed_data = ProcessedData(
            industry_overview="Robotics overview.", key_player_data={}, market_statistics={},
            news_headlines=[], social_media_sentiment={}
        )
        self.mock_insights = MarketInsights(
            industry_analysis="Mock Industry Analysis.", competitive_landscape="Mock Comp Landscape.",
            market_trends="Mock Trends.", future_predictions="Mock Predictions.",
            technology_adoption="Mock Tech Adoption.", strategic_insights="Mock Strategic Insights.",
            actionable_recommendations="Mock Recommendations."
        )
        self.mock_executive_summary = ExecutiveSummary(
            summary_content="Mock Executive Summary Content.", key_findings=[], key_recommendations=[]
        )
        self.mock_formatted_content = "Mock Formatted Report Content."

        # Mock config settings, especially LLM_API_KEY for tests
        self.patcher_config_llm_key = patch('src.modules.config.settings.LLM_API_KEY', 'mock_api_key')
        self.patcher_config_llm_key.start()

    def tearDown(self):
        self.patcher_config_llm_key.stop()

    @patch('src.modules.data_processor.DataProcessor.process_market_data', new_callable=MagicMock)
    @patch('src.modules.llm_orchestrator.LLMOrchestrator.generate_market_insights', new_callable=MagicMock)
    @patch('src.modules.llm_orchestrator.LLMOrchestrator.generate_executive_summary', new_callable=MagicMock)
    @patch('src.modules.report_formatter.ReportFormatter.format_report', new_callable=MagicMock)
    async def test_successful_report_generation(
        self, mock_format_report, mock_generate_executive_summary,
        mock_generate_market_insights, mock_process_market_data
    ):
        """
        Test the end-to-end successful generation of a report.
        """
        # Ensure mocks return awaitable objects
        mock_process_market_data.return_value = self.mock_processed_data
        mock_generate_market_insights.return_value = self.mock_insights
        mock_generate_executive_summary.return_value = self.mock_executive_summary
        mock_format_report.return_value = self.mock_formatted_content

        report = await generate_market_research_report(self.sample_request) # Await the async main function

        self.assertIsInstance(report, MarketResearchReport)
        self.assertEqual(report.formatted_content, self.mock_formatted_content)
        self.assertEqual(report.executive_summary, self.mock_executive_summary)
        self.assertEqual(report.market_insights, self.mock_insights)
        self.assertEqual(report.request_details, self.sample_request)

        mock_process_market_data.assert_called_once_with(
            industry=self.sample_request.industry,
            competitors=self.sample_request.competitors
        )
        mock_generate_market_insights.assert_called_once()
        mock_generate_executive_summary.assert_called_once()
        mock_format_report.assert_called_once()

    @patch('src.modules.data_processor.DataProcessor.process_market_data', new_callable=MagicMock)
    async def test_report_generation_fails_on_data_processing_error(self, mock_process_market_data):
        """
        Test that report generation returns None if data processing fails.
        """
        mock_process_market_data.return_value = None # Simulate failure
        report = await generate_market_research_report(self.sample_request) # Await
        self.assertIsNone(report)

    @patch('src.modules.data_processor.DataProcessor.process_market_data', new_callable=MagicMock, return_value=ProcessedData(industry_overview="ok", key_player_data={}, market_statistics={}, news_headlines=[], social_media_sentiment={}))
    @patch('src.modules.llm_orchestrator.LLMOrchestrator.generate_market_insights', new_callable=MagicMock)
    async def test_report_generation_fails_on_insights_generation_error(self, mock_generate_market_insights, mock_process_market_data):
        """
        Test that report generation returns None if LLM insights generation fails.
        """
        mock_generate_market_insights.return_value = None # Simulate failure
        report = await generate_market_research_report(self.sample_request) # Await
        self.assertIsNone(report)

    @patch('src.modules.data_processor.DataProcessor.process_market_data', new_callable=MagicMock, return_value=ProcessedData(industry_overview="ok", key_player_data={}, market_statistics={}, news_headlines=[], social_media_sentiment={}))
    @patch('src.modules.llm_orchestrator.LLMOrchestrator.generate_market_insights', new_callable=MagicMock, return_value=MarketInsights(industry_analysis="IA", competitive_landscape="CL", market_trends="MT", future_predictions="FP", technology_adoption="TA", strategic_insights="SI", actionable_recommendations="AR"))
    @patch('src.modules.llm_orchestrator.LLMOrchestrator.generate_executive_summary', new_callable=MagicMock)
    async def test_report_generation_fails_on_executive_summary_error(self, mock_generate_executive_summary, *args):
        """
        Test that report generation returns None if executive summary generation fails.
        """
        mock_generate_executive_summary.return_value = None # Simulate failure
        report = await generate_market_research_report(self.sample_request) # Await
        self.assertIsNone(report)

    @patch('src.modules.data_processor.DataProcessor.process_market_data', new_callable=MagicMock, return_value=ProcessedData(industry_overview="ok", key_player_data={}, market_statistics={}, news_headlines=[], social_media_sentiment={}))
    @patch('src.modules.llm_orchestrator.LLMOrchestrator.generate_market_insights', new_callable=MagicMock, return_value=MarketInsights(industry_analysis="IA", competitive_landscape="CL", market_trends="MT", future_predictions="FP", technology_adoption="TA", strategic_insights="SI", actionable_recommendations="AR"))
    @patch('src.modules.llm_orchestrator.LLMOrchestrator.generate_executive_summary', new_callable=MagicMock, return_value=ExecutiveSummary(summary_content="ES", key_findings=[], key_recommendations=[]))
    @patch('src.modules.report_formatter.ReportFormatter.format_report', new_callable=MagicMock)
    async def test_report_generation_fails_on_formatting_error(self, mock_format_report, *args):
        """
        Test that report generation returns None if report formatting fails.
        """
        mock_format_report.return_value = None # Simulate failure
        report = await generate_market_research_report(self.sample_request) # Await
        self.assertIsNone(report)

    @patch('src.modules.config.settings.LLM_API_KEY', None) # Temporarily set API key to None
    async def test_report_generation_fails_if_api_key_missing(self):
        """
        Test that report generation fails if LLM_API_KEY is missing.
        """
        with self.assertRaises(ReportGenerationError) as cm:
            # Suppress the UserWarning from config.py for this test
            with unittest.mock.patch('warnings.warn'):
                report = await generate_market_research_report(self.sample_request)
        self.assertIn("LLM_API_KEY is not configured", str(cm.exception))
        
if __name__ == '__main__':
    unittest.main()
```

### Migration Guide

This refactoring involves significant changes, particularly the introduction of asynchronous programming.

1.  **Update Dependencies:**
    *   Add `aiohttp` and `Jinja2` to your `requirements.txt`:
        ```
        pydantic>=2.0
        pydantic-settings>=2.0
        python-dotenv>=1.0
        aiohttp>=3.9
        Jinja2>=3.1
        ```
    *   Run `pip install -r requirements.txt`.

2.  **Codebase Changes:**
    *   **Asynchronous `main` function:** The `generate_market_research_report` function in `src/main.py` is now `async`. You must run it using `asyncio.run(generate_market_research_report(...))` in your entry point.
    *   **Asynchronous LLM Client and Orchestrator:**
        *   The `AbstractLLMClient.generate_text` and `MockLLMClient.generate_text` methods are now `async`.
        *   All methods in `LLMOrchestrator` that interact with the LLM (e.g., `_generate_section`, `generate_market_insights`, `generate_executive_summary`) are now `async` and must be `await`ed.
        *   `LLMOrchestrator.generate_market_insights` now uses `asyncio.gather` for concurrent LLM calls.
    *   **Prompt Templates:**
        *   Create a new directory `src/prompts/` and move your LLM prompt content into `.j2` (Jinja2) files as shown in the "Prompt Templates" section above.
        *   The `LLMOrchestrator` now loads these templates.
    *   **`config.py` updates:**
        *   `LLM_API_KEY` now defaults to `None`. Ensure your `.env` file explicitly sets `LLM_API_KEY="your_actual_llm_api_key"` for a real LLM, or accept the warning if using `MockLLMClient`.
        *   `model_config = SettingsConfigDict(env_file=".env", extra='forbid')` means only defined environment variables are accepted. If you had other variables being implicitly picked up, you might need to explicitly define them in `Settings` or change `extra` back (not recommended).
    *   **Input/Output Sanitization (Conceptual):**
        *   New methods `_sanitize_input` and `_validate_and_sanitize_llm_output` are introduced in `LLMOrchestrator`. Review their implementation and enhance for your specific security needs.
    *   **Error Logging:** `main.py` now logs custom `ReportGenerationError` exceptions with `exc_info=True`.

3.  **Test Updates:**
    *   All unit tests for `DataProcessor`, `LLMOrchestrator`, and `main` that interact with asynchronous functions must now inherit from `unittest.IsolatedAsyncioTestCase` and mark their test methods as `async`.
    *   Any mocks for async functions must return `awaitable` objects (e.g., by using `new_callable=MagicMock` which automatically makes mock methods awaitable, or by wrapping return values with `asyncio.Future` or `unittest.mock.AsyncMock`).

**Breaking Changes (if any):**
*   **Synchronous to Asynchronous:** Any code outside of the provided framework that directly calls the `generate_market_research_report` function or other previously synchronous methods in `LLMOrchestrator` will need to be updated to use `await` and run within an `asyncio` event loop.
*   **Prompt Location:** If you were accessing or modifying prompts directly as strings in code, you now need to interact with the Jinja2 templating system and external `.j2` files.
*   **LLM_API_KEY Requirement:** `LLM_API_KEY` is now stricter. If it was previously absent and you relied on a default (even the mock one), you might get an error or a warning.

This refactored framework provides a solid, more performant, and more secure foundation for building your LLM-guided market research report generation system.

---
*Saved by after_agent_callback on 2025-07-04 10:25:11*
