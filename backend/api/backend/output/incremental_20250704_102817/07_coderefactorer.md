# CodeRefactorer Output
**Agent**: CodeRefactorer
**Execution Order**: 7
**Timestamp**: 2025-07-04 10:33:18

---

## Refactored Code Implementation

### Summary of Changes
This refactoring addresses critical security vulnerabilities, significantly improves performance through asynchronous programming, and enhances code quality by refining the data flow and addressing mocking patterns.

**Key improvements made:**
*   **Critical Security Fix:** Replaced the dangerous `eval()` function with `json.loads()` for parsing JSON responses from LLMs, eliminating a severe Remote Code Execution (RCE) vulnerability.
*   **Asynchronous Operations:** Migrated all I/O-bound operations (LLM calls, simulated data interactions) to use Python's `asyncio` framework. This includes marking methods as `async def` and using `await` for calls, enabling non-blocking operations and concurrent execution.
*   **Parallel Analysis:** Leveraged `asyncio.gather` in the `APIGateway` to run the independent analysis services (Industry, Market Trends, Technology Adoption) concurrently, drastically reducing overall report generation time.
*   **Improved Executive Summary Flow:** Corrected the logic where the `ReportGenerationService` was mocking the executive summary. Now, the `StrategicInsightsService` is solely responsible for generating the executive summary, which is then passed as a complete object to the `ReportGenerationService`. This ensures single responsibility and clear data flow.
*   **Enhanced Error Handling:** Added more specific `try-except` blocks and detailed logging around critical operations, particularly LLM interactions and JSON parsing.
*   **Simulated Persistence & Caching Comments:** Added comments and placeholders to `KnowledgeStoreService` and `LLMOrchestrator` to emphasize the need for robust database integration and caching mechanisms in a production environment.
*   **Updated Mocks:** Adjusted mock LLM responses to be valid JSON strings to work seamlessly with `json.loads()`.
*   **Comprehensive Logging:** Ensured consistent and informative logging across all services.
*   **Test Updates:** Modified existing unit tests to correctly mock and test `async` functions using `unittest.mock.AsyncMock`.

### Refactored Code

```python
# requirements.txt
# pydantic==2.5.2
# aiohttp # For real async HTTP requests if mocking is removed
# python-dotenv # For loading environment variables securely
# Other potential dependencies for a real system (mocked in this framework):
# fastapi
# uvicorn
# requests
# google-generativeai
# openai
# apache-kafka-python (or confluent-kafka)
# celery
# redis
# psycopg2-binary (for PostgreSQL)
# neo4j
# pinecone-client (or weaviate-client, qdrant-client)
# pandas
# scrapy (or beautifulsoup4, selenium)
```

```python
# src/main.py
import logging
import asyncio
from typing import Dict, Any, Optional

from src.api_gateway import APIGateway
from src.models.report_data_models import ResearchRequest, MarketResearchReport
from src.utils.logger_config import configure_logging

# Configure logging for the application
configure_logging()
logger = logging.getLogger(__name__)

class ReportGeneratorFramework:
    """
    Orchestrates the end-to-end process of generating a Gartner-style market research report.
    This class simulates the API Gateway's interaction with various microservices.
    """

    def __init__(self) -> None:
        """
        Initializes the ReportGeneratorFramework with an API Gateway instance.
        """
        self.api_gateway = APIGateway()
        logger.info("ReportGeneratorFramework initialized.")

    async def generate_report(self, request_data: Dict[str, Any]) -> Optional[MarketResearchReport]:
        """
        Generates a comprehensive market research report based on the provided request data.

        Args:
            request_data: A dictionary containing the research requirements,
                          e.g., {"industry": "AI Software", "target_market_segment": "Enterprise"}.

        Returns:
            An instance of MarketResearchReport if successful, None otherwise.
        """
        try:
            research_request = ResearchRequest(**request_data)
            logger.info(f"Received request to generate report for: {research_request.industry} - {research_request.target_market_segment}")

            # Simulate API Gateway processing the request
            report = await self.api_gateway.process_research_request(research_request)

            if report:
                logger.info("Market research report generated successfully.")
                return report
            else:
                logger.error("Failed to generate market research report.")
                return None
        except Exception as e:
            logger.exception(f"An error occurred during report generation: {e}")
            return None

    async def continuous_update_cycle(self) -> None:
        """
        Simulates a continuous update cycle for market data and reports.
        In a real system, this would be managed by a Scheduler/Workflow Orchestrator.
        """
        logger.info("Starting continuous update cycle simulation...")
        # This function would trigger data ingestion, processing, and re-analysis periodically.
        # For this framework, we'll just log the intent and simulate a delay.
        await asyncio.sleep(1) # Simulate background processing
        logger.info("Continuous update cycle complete. New data would have been ingested and processed.")

if __name__ == "__main__":
    framework = ReportGeneratorFramework()

    # Example Research Request
    example_request_data = {
        "industry": "Cloud Computing",
        "target_market_segment": "SME",
        "specific_metrics": ["growth_rate", "customer_acquisition_cost"],
        "competitors_of_interest": ["AWS", "Microsoft Azure", "Google Cloud"]
    }

    print("\n--- Generating Initial Report ---")
    report = asyncio.run(framework.generate_report(example_request_data))

    if report:
        print("\n--- Executive Summary ---")
        print(report.executive_summary.summary)
        print("\n--- Key Findings ---")
        for finding in report.executive_summary.key_findings:
            print(f"- {finding.title}: {finding.description}")
        print("\n--- Actionable Recommendations ---")
        for rec in report.strategic_recommendations.actionable_recommendations:
            print(f"- {rec.recommendation}: {rec.details}")
        print("\n--- Full Report Content ---")
        # In a real scenario, this would be a large formatted document.
        # Here we just print the structured data.
        print(f"Industry Analysis Overview: {report.industry_analysis.overview[:100]}...")
        print(f"Market Trends Overview: {report.market_trends.overview[:100]}...")
        print(f"Technology Adoption Overview: {report.technology_adoption.overview[:100]}...")

    print("\n--- Simulating Continuous Update ---")
    asyncio.run(framework.continuous_update_cycle())
    print("Framework operations complete.")

```

```python
# src/api_gateway.py
import logging
import asyncio
from typing import Optional

from src.models.report_data_models import ResearchRequest, MarketResearchReport, ExecutiveSummary
from src.services.data_ingestion import DataIngestionService
from src.services.data_processing import DataProcessingService
from src.services.knowledge_store import KnowledgeStoreService
from src.services.llm_orchestrator import LLMOrchestrator
from src.services.industry_competitive_analysis import IndustryCompetitiveAnalysisService
from src.services.market_trends_prediction import MarketTrendsPredictionService
from src.services.technology_adoption_analysis import TechnologyAdoptionAnalysisService
from src.services.strategic_insights import StrategicInsightsService
from src.services.report_generation import ReportGenerationService
from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class APIGateway:
    """
    Simulates the API Gateway, acting as the single entry point for research requests.
    It orchestrates calls to various backend microservices.
    """
    def __init__(self) -> None:
        """
        Initializes the API Gateway with instances of all necessary services.
        """
        self.data_ingestion_service = DataIngestionService()
        self.data_processing_service = DataProcessingService()
        self.knowledge_store_service = KnowledgeStoreService()
        self.llm_orchestrator = LLMOrchestrator()
        self.industry_analysis_service = IndustryCompetitiveAnalysisService(self.llm_orchestrator, self.knowledge_store_service)
        self.market_trends_service = MarketTrendsPredictionService(self.llm_orchestrator, self.knowledge_store_service)
        self.technology_adoption_service = TechnologyAdoptionAnalysisService(self.llm_orchestrator, self.knowledge_store_service)
        self.strategic_insights_service = StrategicInsightsService(
            self.llm_orchestrator,
            self.knowledge_store_service,
            self.industry_analysis_service,
            self.market_trends_service,
            self.technology_adoption_service
        )
        # Note: ReportGenerationService no longer generates ExecutiveSummary internally, it receives it.
        self.report_generation_service = ReportGenerationService()
        logger.info("API Gateway initialized with all services.")

    async def process_research_request(self, request: ResearchRequest) -> Optional[MarketResearchReport]:
        """
        Processes a research request by orchestrating calls to various microservices.

        Args:
            request: The ResearchRequest object containing details for the report.

        Returns:
            An optional MarketResearchReport object if the report is generated successfully.
        """
        logger.info(f"Processing research request for industry: {request.industry}")

        try:
            # 1. Data Ingestion (simulated asynchronously)
            raw_data = await self.data_ingestion_service.ingest_data(request.industry, request.competitors_of_interest)
            logger.info(f"Ingested {len(raw_data)} raw data entries.")

            # 2. Data Processing (simulated asynchronously)
            processed_data = await self.data_processing_service.process_data(raw_data)
            logger.info(f"Processed {len(processed_data)} data entries.")

            # 3. Knowledge Store Update (simulated asynchronously)
            await self.knowledge_store_service.update_knowledge_base(processed_data)
            logger.info("Knowledge base updated.")

            # 4. Analysis Services (executed in parallel where possible)
            logger.info("Initiating analysis services in parallel...")
            industry_analysis_task = self.industry_analysis_service.analyze(request.industry, request.competitors_of_interest)
            market_trends_task = self.market_trends_service.analyze(request.industry, request.target_market_segment)
            technology_adoption_task = self.technology_adoption_service.analyze(request.industry)

            industry_analysis_result, market_trends_result, technology_adoption_result = await asyncio.gather(
                industry_analysis_task,
                market_trends_task,
                technology_adoption_task
            )
            logger.info("All analysis services completed.")

            # 5. Strategic Insights and Recommendations
            strategic_insights_result = await self.strategic_insights_service.generate_insights(
                request,
                industry_analysis_result,
                market_trends_result,
                technology_adoption_result
            )
            logger.info("Strategic insights generated.")

            # 6. Executive Summary Generation (now handled by StrategicInsightsService)
            executive_summary = await self.strategic_insights_service.generate_executive_summary(
                request,
                industry_analysis_result,
                market_trends_result,
                technology_adoption_result,
                strategic_insights_result
            )
            logger.info("Executive summary generated.")

            # 7. Report Generation
            report = await self.report_generation_service.generate_report(
                request,
                executive_summary, # Pass the actual generated executive summary
                industry_analysis_result,
                market_trends_result,
                technology_adoption_result,
                strategic_insights_result
            )
            logger.info("Report generation complete.")
            return report

        except Exception as e:
            logger.error(f"Error processing research request: {e}", exc_info=True)
            return None

```

```python
# src/models/report_data_models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ResearchRequest(BaseModel):
    """Defines the input schema for a market research report request."""
    industry: str = Field(..., description="The primary industry to research.")
    target_market_segment: Optional[str] = Field(None, description="Specific market segment within the industry.")
    specific_metrics: Optional[List[str]] = Field(None, description="List of specific metrics of interest (e.g., 'CAGR', 'customer_churn_rate').")
    competitors_of_interest: Optional[List[str]] = Field(None, description="List of specific competitors to focus on.")
    report_format: str = Field("markdown", description="Desired output format for the report (e.g., 'pdf', 'docx', 'markdown').")

class KeyFinding(BaseModel):
    """Represents a single key finding in the executive summary."""
    title: str = Field(..., description="A concise title for the finding.")
    description: str = Field(..., description="Detailed description of the finding.")
    impact: str = Field(..., description="The potential impact of this finding on the market/business.")

class StrategicRecommendation(BaseModel):
    """Represents a single actionable strategic recommendation."""
    recommendation: str = Field(..., description="The concise recommendation.")
    details: str = Field(..., description="Detailed explanation and rationale for the recommendation.")
    action_items: List[str] = Field(default_factory=list, description="Specific steps to implement the recommendation.")
    target_audience: Optional[str] = Field(None, description="Recommended audience for this action (e.g., 'Marketing Dept', 'Product Team').")

class ExecutiveSummary(BaseModel):
    """The executive summary section of the report."""
    summary: str = Field(..., description="A high-level overview of the report's key insights.")
    key_findings: List[KeyFinding] = Field(default_factory=list, description="A list of critical findings.")

class CompetitiveLandscape(BaseModel):
    """Details about a specific competitor."""
    name: str = Field(..., description="Name of the competitor.")
    market_share: Optional[float] = Field(None, description="Estimated market share (as a percentage).")
    swot_analysis: Dict[str, List[str]] = Field(default_factory=dict, description="SWOT analysis (Strengths, Weaknesses, Opportunities, Threats).")
    key_products_services: List[str] = Field(default_factory=list, description="List of key products or services.")
    emerging_disruptor: bool = Field(False, description="True if this competitor is an emerging disruptive force.")

class IndustryAnalysis(BaseModel):
    """The industry analysis section."""
    overview: str = Field(..., description="General overview of the industry.")
    market_size: Optional[str] = Field(None, description="Estimated current market size and forecast.")
    key_players: List[CompetitiveLandscape] = Field(default_factory=list, description="List of key players and their competitive landscape.")
    emerging_competitors: List[str] = Field(default_factory=list, description="Names of emerging competitors identified.")
    disruptive_forces: List[str] = Field(default_factory=list, description="Identified disruptive forces in the industry.")

class MarketTrend(BaseModel):
    """Details about a specific market trend."""
    name: str = Field(..., description="Name of the market trend.")
    description: str = Field(..., description="Detailed description of the trend.")
    impact: str = Field(..., description="Impact of the trend on the market.")
    prediction: str = Field(..., description="Future prediction related to this trend.")
    data_points: List[str] = Field(default_factory=list, description="Key data points supporting the trend/prediction.")

class MarketTrends(BaseModel):
    """The market trends and future predictions section."""
    overview: str = Field(..., description="Overview of prevailing market trends.")
    identified_trends: List[MarketTrend] = Field(default_factory=list, description="List of identified market trends and predictions.")
    macroeconomic_factors: List[str] = Field(default_factory=list, description="Relevant macroeconomic factors.")
    regulatory_changes: List[str] = Field(default_factory=list, description="Relevant regulatory changes.")

class TechnologyAdoptionDetails(BaseModel):
    """Details about technology adoption."""
    technology_name: str = Field(..., description="Name of the technology.")
    current_adoption_rate: Optional[str] = Field(None, description="Estimated current adoption rate or status.")
    potential_impact: str = Field(..., description="Potential impact of the technology on the market.")
    recommendation: Optional[str] = Field(None, description="Specific recommendations regarding this technology.")

class TechnologyAdoption(BaseModel):
    """The technology adoption analysis section."""
    overview: str = Field(..., description="Overview of technology adoption in the industry.")
    current_technologies: List[TechnologyAdoptionDetails] = Field(default_factory=list, description="Currently adopted key technologies.")
    emerging_technologies: List[TechnologyAdoptionDetails] = Field(default_factory=list, description="Emerging technologies and their potential impact.")
    adoption_strategy_recommendations: List[str] = Field(default_factory=list, description="General recommendations for technology adoption strategies.")

class StrategicInsights(BaseModel):
    """The strategic insights section."""
    overall_insights: str = Field(..., description="Synthesized strategic insights based on all analyses.")
    actionable_recommendations: List[StrategicRecommendation] = Field(default_factory=list, description="List of clear, concise, and actionable recommendations.")
    customer_specific_actions: List[str] = Field(default_factory=list, description="Action items tailored to specific customer interactions/data.")

class MarketResearchReport(BaseModel):
    """The complete structure for a Gartner-style market research report."""
    request_details: ResearchRequest = Field(..., description="Details of the original research request.")
    executive_summary: ExecutiveSummary = Field(..., description="Executive summary with key findings.")
    industry_analysis: IndustryAnalysis = Field(..., description="Detailed industry analysis and competitive landscape.")
    market_trends: MarketTrends = Field(..., description="Analysis of market trends and future predictions.")
    technology_adoption: TechnologyAdoption = Field(..., description="Analysis of technology adoption and recommendations.")
    strategic_recommendations: StrategicInsights = Field(..., description="Strategic insights and actionable recommendations.")
    generated_at: str = Field(..., description="Timestamp when the report was generated.")
    disclaimer: str = Field("This report is generated by an AI framework and should be used for informational purposes only. "
                            "Decisions based on this report should be validated with human expertise and additional data.",
                            description="Disclaimer for the AI-generated report.")

```

```python
# src/services/analysis_service.py
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import asyncio # Required for await in abstract methods if they are async

from src.services.llm_orchestrator import LLMOrchestrator
from src.services.knowledge_store import KnowledgeStoreService
from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class BaseAnalysisService(ABC):
    """
    Abstract Base Class for all specialized analysis services.
    Ensures a common interface for analysis and dependency injection of LLM and Knowledge Store.
    """
    def __init__(self, llm_orchestrator: LLMOrchestrator, knowledge_store: KnowledgeStoreService) -> None:
        """
        Initializes the base analysis service.

        Args:
            llm_orchestrator: An instance of LLMOrchestrator for LLM interactions.
            knowledge_store: An instance of KnowledgeStoreService for data retrieval.
        """
        self.llm_orchestrator = llm_orchestrator
        self.knowledge_store = knowledge_store
        logger.debug(f"{self.__class__.__name__} initialized.")

    @abstractmethod
    async def analyze(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Abstract method to perform specific analysis.
        Concrete implementations must override this.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            A dictionary containing the analysis results.
        """
        pass

```

```python
# src/services/data_ingestion.py
import logging
from typing import List, Dict, Any
import asyncio # Required for async operations

from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class DataIngestionService:
    """
    Handles the ingestion of raw data from various sources.
    In a real system, this would involve API calls, web scraping, database queries, etc.
    """
    def __init__(self) -> None:
        """
        Initializes the DataIngestionService.
        """
        logger.info("DataIngestionService initialized.")

    async def ingest_data(self, industry: str, competitors: List[str]) -> List[Dict[str, Any]]:
        """
        Simulates ingesting raw data relevant to the specified industry and competitors.

        Args:
            industry: The industry for which to ingest data.
            competitors: A list of competitors to gather data on.

        Returns:
            A list of dictionaries, each representing a raw data entry.
        """
        logger.info(f"Simulating data ingestion for industry: '{industry}' and competitors: {competitors}")
        await asyncio.sleep(0.2) # Simulate I/O latency for data retrieval

        # Placeholder for actual data ingestion logic
        # In a real scenario, this would call external APIs (e.g., financial data, news, social media),
        # perform web scraping (e.g., SEC filings, company websites), or query market databases.
        simulated_data = []

        # Simulate industry news
        simulated_data.append({"type": "news", "source": "IndustryTimes", "content": f"New regulations impacting {industry} sector expected by Q4."})
        simulated_data.append({"type": "news", "source": "TechCrunch", "content": f"Emerging AI startups disrupting traditional {industry} models."})

        # Simulate company reports for competitors
        for comp in competitors:
            simulated_data.append({"type": "company_report", "source": f"{comp} Analytics", "content": f"{comp} reports Q3 revenue growth of 15% in the {industry} market."})
            simulated_data.append({"type": "social_media", "source": "Twitter", "content": f"Users are discussing {comp}'s new cloud service, positive sentiment around scalability."})

        # Simulate general market data
        simulated_data.append({"type": "market_data", "source": "GlobalMarketStats", "content": f"Overall {industry} market size projected to reach $X billion by 2028."})
        simulated_data.append({"type": "research_paper", "source": "AcademicJournal", "content": f"A study on {industry} technology adoption rates in SMBs."})

        logger.info(f"Successfully simulated ingestion of {len(simulated_data)} data points.")
        return simulated_data

```

```python
# src/services/data_processing.py
import logging
from typing import List, Dict, Any
import asyncio # Required for async operations

from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class DataProcessingService:
    """
    Cleans, transforms, and normalizes raw data ingested by the DataIngestionService.
    This service would typically handle deduplication, entity extraction,
    standardization, and basic NLP tasks.
    """
    def __init__(self) -> None:
        """
        Initializes the DataProcessingService.
        """
        logger.info("DataProcessingService initialized.")

    async def process_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simulates the processing of raw data.

        Args:
            raw_data: A list of dictionaries, each representing a raw data entry.

        Returns:
            A list of dictionaries, representing processed and normalized data.
        """
        logger.info(f"Starting data processing for {len(raw_data)} raw data entries.")
        await asyncio.sleep(0.3) # Simulate processing time
        processed_data = []

        for entry in raw_data:
            processed_entry = entry.copy()
            # Simulate data cleansing (e.g., removing extra spaces, standardizing case)
            if "content" in processed_entry and isinstance(processed_entry["content"], str):
                processed_entry["content"] = processed_entry["content"].strip().lower()

            # Simulate entity extraction (e.g., identifying company names, technologies, trends)
            # This would typically use more advanced NLP libraries or LLM calls
            extracted_entities = self._extract_entities(processed_entry.get("content", ""))
            processed_entry["extracted_entities"] = extracted_entities

            # Simulate normalization or transformation if needed
            # For example, converting dates, standardizing units, etc.

            processed_data.append(processed_entry)

        logger.info(f"Successfully processed {len(processed_data)} data entries.")
        return processed_data

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Helper method to simulate entity extraction.
        In a real system, this would use a robust NLP library (e.g., spaCy, NLTK)
        or an LLM for named entity recognition (NER).
        """
        entities: Dict[str, List[str]] = {
            "companies": [],
            "technologies": [],
            "trends": [],
            "industries": []
        }
        text_lower = text.lower()

        # Simple keyword-based extraction for demonstration
        if "aws" in text_lower:
            entities["companies"].append("AWS")
        if "microsoft azure" in text_lower:
            entities["companies"].append("Microsoft Azure")
        if "google cloud" in text_lower:
            entities["companies"].append("Google Cloud")
        if "ai" in text_lower or "artificial intelligence" in text_lower:
            entities["technologies"].append("AI")
        if "cloud service" in text_lower:
            entities["technologies"].append("Cloud Computing")
        if "digital transformation" in text_lower:
            entities["trends"].append("Digital Transformation")
        if "sustainability" in text_lower:
            entities["trends"].append("Sustainability")

        # More sophisticated logic would be here
        return entities

```

```python
# src/services/knowledge_store.py
import logging
from typing import List, Dict, Any, Optional
import asyncio # Required for async operations

from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class KnowledgeStoreService:
    """
    Manages the structured and semi-structured knowledge base derived from processed data.
    This simulates a database interaction (e.g., PostgreSQL for structured data,
    Elasticsearch for search, or a Vector Database for embeddings).
    """
    def __init__(self) -> None:
        """
        Initializes the KnowledgeStoreService.
        In a real setup, this would connect to actual databases (PostgreSQL, Neo4j, Vector DB).
        """
        self._knowledge_base: List[Dict[str, Any]] = []
        logger.info("KnowledgeStoreService initialized. Using in-memory store for simulation. Replace with a real DB (e.g., PostgreSQL, Neo4j, Vector DB) for persistence and scalability.")

    async def update_knowledge_base(self, processed_data: List[Dict[str, Any]]) -> None:
        """
        Simulates updating the knowledge base with processed data.
        In a real scenario, this would involve inserting/updating records in a database.

        Args:
            processed_data: A list of dictionaries, representing processed and normalized data.
        """
        logger.info(f"Updating knowledge base with {len(processed_data)} new entries.")
        await asyncio.sleep(0.1) # Simulate database write latency
        self._knowledge_base.extend(processed_data)
        logger.info(f"Knowledge base now contains {len(self._knowledge_base)} entries.")

    async def query_knowledge_base(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simulates querying the knowledge base for relevant information.
        This would be complex in a real system, involving sophisticated database queries
        or semantic searches on a vector database, with proper indexing for performance.

        Args:
            query_params: A dictionary of parameters to filter the knowledge base (e.g., {"industry": "AI"}).

        Returns:
            A list of relevant knowledge entries.
        """
        logger.info(f"Querying knowledge base with params: {query_params}")
        await asyncio.sleep(0.15) # Simulate database read latency
        results = []
        # Simple simulation: linear scan. In real system, use indexed queries for O(log N) or better.
        for entry in self._knowledge_base:
            match = True
            for key, value in query_params.items():
                if key == "industry" and value.lower() not in entry.get("content", "").lower():
                    match = False
                    break
                if key == "competitors" and isinstance(value, list) and not any(comp.lower() in entry.get("content", "").lower() for comp in value):
                    match = False
                    break
                if key == "type" and entry.get("type") != value:
                    match = False
                    break
            if match:
                results.append(entry)
        logger.info(f"Found {len(results)} entries matching the query.")
        return results

    async def get_all_knowledge(self) -> List[Dict[str, Any]]:
        """
        Retrieves all current knowledge entries.
        Used primarily for testing or full data dumps.
        """
        await asyncio.sleep(0.05) # Simulate quick read
        return self._knowledge_base

```

```python
# src/services/llm_orchestrator.py
import logging
import asyncio
import json # Import json for secure parsing
import os # For environment variables
from typing import Dict, Any, List, Optional
# from dotenv import load_dotenv # Uncomment and `pip install python-dotenv` for local .env files

from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

# load_dotenv() # Load environment variables from .env file

class LLMOrchestrator:
    """
    Manages interactions with various Large Language Models (LLMs).
    Handles prompt engineering, context management, and parsing LLM responses.
    This class would abstract different LLM providers (e.g., OpenAI, Anthropic, Google Gemini).
    """
    def __init__(self, default_model: str = "gemini-pro-mock") -> None:
        """
        Initializes the LLMOrchestrator.

        Args:
            default_model: The default LLM model to use for requests.
                           In a real scenario, this would map to actual LLM APIs.
        """
        self.default_model = default_model
        # Placeholder for API keys, client objects, rate limiters etc.
        # Use secure secrets management (e.g., environment variables, cloud secrets manager)
        self._llm_api_key: str = os.getenv("LLM_API_KEY", "MOCK_API_KEY_123")
        self._llm_clients: Dict[str, Any] = {} # Real clients like google.generativeai.GenerativeModel
        self._cache: Dict[str, Any] = {} # Simple in-memory cache for demonstration. Use Redis for production.
        logger.info(f"LLMOrchestrator initialized with default model: {default_model}. LLM API Key status: {'Loaded' if self._llm_api_key != 'MOCK_API_KEY_123' else 'Mock'}")

    async def _call_llm_api(self, model: str, prompt: str, temperature: float) -> str:
        """
        Simulates a call to an LLM API.
        In a real application, this would make an actual API call (e.g., using httpx, google-generativeai, openai).
        Includes basic prompt injection mitigation advice.

        Args:
            model: The name of the LLM model to use.
            prompt: The engineered prompt to send to the LLM.
            temperature: Controls the randomness of the output.

        Returns:
            The simulated text response from the LLM.
        """
        logger.debug(f"Calling simulated LLM '{model}' with prompt snippet: {prompt[:100]}...")
        # CRITICAL SECURITY CONSIDERATION: Input validation and sanitization for prompts
        # In a real system, user inputs (e.g., ResearchRequest fields) that directly
        # influence `prompt` should be strictly validated and sanitized to prevent
        # prompt injection attacks. Use guardrails and input filtering.
        await asyncio.sleep(0.5) # Simulate network latency and processing time

        # Simple caching mechanism for demonstration
        prompt_hash = hash((model, prompt, temperature))
        if prompt_hash in self._cache:
            logger.debug("Returning cached LLM response.")
            return self._cache[prompt_hash]

        # Basic mock responses based on prompt content (now returning valid JSON strings)
        if "industry overview" in prompt.lower():
            response = "The AI software industry is experiencing rapid growth driven by innovation in machine learning and automation. Key players include Google, Microsoft, and Amazon. Emerging trends include responsible AI and edge computing."
        elif "swot analysis for google" in prompt.lower():
            response = '{"Strengths": ["Strong R&D", "Vast user base"], "Weaknesses": ["Regulatory scrutiny"], "Opportunities": ["Cloud expansion"], "Threats": ["Intense competition"]}'
        elif "market trends for cloud computing" in prompt.lower():
            response = '{"overview": "Cloud computing continues to expand, with hybrid and multi-cloud strategies gaining traction.", "identified_trends": [{"name": "Hybrid Cloud Adoption", "description": "Businesses are increasingly combining on-premise infrastructure with public cloud services.", "impact": "Increased flexibility", "prediction": "Dominant strategy", "data_points": ["Survey data", "Deployment trends"]}]}'
        elif "technology adoption for cloud computing" in prompt.lower():
            response = '{"overview": "Cloud native technologies like Kubernetes and serverless functions are seeing widespread adoption.", "current_technologies": [{"technology_name": "AWS Lambda", "current_adoption_rate": "High", "potential_impact": "Cost optimization"}, {"technology_name": "Kubernetes", "current_adoption_rate": "Very High", "potential_impact": "Scalability, portability"}], "emerging_technologies": [{"technology_name": "WebAssembly for Cloud", "potential_impact": "Faster cold starts, polyglot environments."}]}'
        elif "strategic insights" in prompt.lower():
            response = '{"overall_insights": "The market demands flexible cloud solutions and robust AI integration.", "actionable_recommendations": [{"recommendation": "Invest in hybrid cloud solutions", "details": "To cater to diverse enterprise needs.", "action_items": ["Feasibility study", "Pilot program"], "target_audience": "IT Leadership"}]}'
        elif "executive summary" in prompt.lower():
            response = '{"summary": "The Cloud Computing market is dynamic, characterized by strong growth and rapid technological evolution.", "key_findings": [{"title": "Market Expansion", "description": "Cloud market continues robust growth.", "impact": "Increased revenue opportunities."}]}'
        else:
            response = "LLM response: Simulated generic response based on your query. More specific prompts yield better results."

        self._cache[prompt_hash] = response # Cache the response
        return response

    async def generate_text(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> str:
        """
        Generates text using the specified (or default) LLM.

        Args:
            prompt: The text prompt to send to the LLM.
            model: The LLM model to use. If None, uses the default_model.
            temperature: Controls the randomness of the output. Higher values mean more random.

        Returns:
            The generated text from the LLM.
        """
        selected_model = model if model else self.default_model
        response = await self._call_llm_api(selected_model, prompt, temperature)
        logger.debug(f"LLM text generation complete for model {selected_model}.")
        return response

    async def generate_json(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generates a JSON object using the specified (or default) LLM.
        Assumes the LLM is instructed to return JSON.

        Args:
            prompt: The text prompt, instructing the LLM to return JSON.
            model: The LLM model to use. If None, uses the default_model.
            temperature: Controls the randomness of the output.

        Returns:
            A dictionary parsed from the LLM's JSON response.
        """
        text_response = await self.generate_text(prompt, model, temperature)
        try:
            # CRITICAL SECURITY FIX: Replace eval() with json.loads()
            # This prevents Remote Code Execution if LLM output contains malicious code.
            return json.loads(text_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}. Raw response: '{text_response}'")
            # Implement robust fallback/retry strategy for malformed JSON from LLM
            return {"error": "Invalid JSON response from LLM", "raw_response": text_response}
        except Exception as e:
            logger.error(f"An unexpected error occurred during JSON parsing: {e}. Raw response: '{text_response}'")
            return {"error": f"Unexpected parsing error: {str(e)}", "raw_response": text_response}

    async def summarize(self, text: str, context: Optional[str] = None, model: Optional[str] = None) -> str:
        """
        Summarizes the given text using an LLM.

        Args:
            text: The text to summarize.
            context: Additional context to guide the summarization.
            model: The LLM model to use.

        Returns:
            The summarized text.
        """
        prompt = f"Summarize the following text:\n\n{text}"
        if context:
            prompt = f"Given the context: '{context}', summarize the following text:\n\n{text}"
        return await self.generate_text(prompt, model)

    async def extract_info(self, text: str, info_schema: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
        """
        Extracts structured information from text based on a provided schema using an LLM.

        Args:
            text: The text from which to extract information.
            info_schema: A dictionary describing the structure of information to extract.
                         e.g., {"company_name": "string", "revenue": "number"}.
            model: The LLM model to use.

        Returns:
            A dictionary containing the extracted information.
        """
        prompt = (
            f"Extract information from the following text based on this JSON schema:\n"
            f"{json.dumps(info_schema, indent=2)}\n\nText: {text}\n\nReturn only the JSON object."
        )
        return await self.generate_json(prompt, model, temperature=0.3)

    async def retrieve_context_for_rag(self, query: str) -> List[str]:
        """
        Simulates retrieving relevant context from a vector database for RAG.
        In a real scenario, this would query a vector database (e.g., Pinecone, Weaviate)
        using embeddings of the query to find similar document chunks.

        Args:
            query: The user query or current context for which to retrieve relevant documents.

        Returns:
            A list of strings, where each string is a retrieved document chunk.
        """
        logger.debug(f"Simulating context retrieval for RAG with query: {query[:50]}...")
        await asyncio.sleep(0.1) # Simulate vector DB lookup latency
        # Placeholder for actual vector database query
        mock_contexts = {
            "cloud computing": ["Cloud computing involves delivering computing services over the internet.", "Hybrid cloud solutions combine public and private clouds."],
            "ai software": ["AI software is revolutionizing various industries.", "Machine learning algorithms are at the core of modern AI systems."]
        }
        # Simple keyword-based matching for mock context retrieval
        for keyword, contexts in mock_contexts.items():
            if keyword in query.lower():
                logger.debug(f"Found mock context for '{keyword}'.")
                return contexts
        return ["No specific context found for the query."]

```

```python
# src/services/industry_competitive_analysis.py
import logging
from typing import Dict, Any, List, Optional
import asyncio # Required for async operations

from src.services.analysis_service import BaseAnalysisService
from src.services.llm_orchestrator import LLMOrchestrator
from src.services.knowledge_store import KnowledgeStoreService
from src.models.report_data_models import IndustryAnalysis, CompetitiveLandscape
from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class IndustryCompetitiveAnalysisService(BaseAnalysisService):
    """
    Performs industry analysis and competitive landscape mapping.
    Identifies key players, their SWOT, market share, and disruptive forces.
    """
    def __init__(self, llm_orchestrator: LLMOrchestrator, knowledge_store: KnowledgeStoreService) -> None:
        """
        Initializes the IndustryCompetitiveAnalysisService.
        """
        super().__init__(llm_orchestrator, knowledge_store)
        logger.info("IndustryCompetitiveAnalysisService initialized.")

    async def analyze(self, industry: str, competitors_of_interest: Optional[List[str]] = None) -> IndustryAnalysis:
        """
        Analyzes the specified industry and maps its competitive landscape.

        Args:
            industry: The industry to analyze.
            competitors_of_interest: Optional list of specific competitors to focus on.

        Returns:
            An IndustryAnalysis object containing the results.
        """
        logger.info(f"Performing industry and competitive analysis for: {industry}")

        # 1. Gather relevant data from Knowledge Store
        industry_data = await self.knowledge_store.query_knowledge_base({"industry": industry, "type": "news"})
        competitor_data_tasks = []
        if competitors_of_interest:
            for comp in competitors_of_interest:
                competitor_data_tasks.append(self.knowledge_store.query_knowledge_base({"competitors": [comp], "type": "company_report"}))
            competitor_data_lists = await asyncio.gather(*competitor_data_tasks)
            competitor_data = [item for sublist in competitor_data_lists for item in sublist]
        else:
            all_relevant_data = await self.knowledge_store.query_knowledge_base({"industry": industry})
            competitor_data = [d for d in all_relevant_data if "company_report" in d.get("type", "")]


        # 2. Use LLM for Industry Overview
        industry_overview_prompt = (
            f"Based on the following data, provide a concise industry overview for the '{industry}' sector, "
            f"highlighting its current state, major trends, and key drivers:\n\n"
            f"Data: {industry_data}\n\n"
            f"Ensure the overview is suitable for a Gartner-style market research report."
        )
        industry_overview = await self.llm_orchestrator.generate_text(industry_overview_prompt)

        # 3. Use LLM for Competitive Landscape Mapping (SWOT, market share, etc.)
        competitive_landscapes: List[CompetitiveLandscape] = []
        identified_emerging_competitors: List[str] = []
        identified_disruptive_forces: List[str] = []

        # Simulate identifying key players from data
        mock_key_players_names = competitors_of_interest if competitors_of_interest else ["CloudCorp Inc.", "DataMinds Ltd."]

        swot_tasks = []
        for competitor_name in mock_key_players_names:
            comp_prompt_data = [d for d in competitor_data if competitor_name.lower() in d.get("content", "").lower()]
            swot_prompt = (
                f"Perform a SWOT analysis for '{competitor_name}' in the '{industry}' industry "
                f"based on this information:\n\n"
                f"Information: {comp_prompt_data}\n\n"
                f"Return only a JSON object with 'Strengths', 'Weaknesses', 'Opportunities', 'Threats' as keys, "
                f"each containing a list of strings."
            )
            swot_tasks.append(self.llm_orchestrator.generate_json(swot_prompt, temperature=0.5))

        swot_results = await asyncio.gather(*swot_tasks)

        for i, competitor_name in enumerate(mock_key_players_names):
            swot_analysis = swot_results[i]
            # Handle potential LLM parsing errors
            if "error" in swot_analysis:
                logger.warning(f"LLM failed to generate valid SWOT for {competitor_name}: {swot_analysis['error']}")
                swot_analysis = {'Strengths': ['N/A'], 'Weaknesses': ['N/A'], 'Opportunities': ['N/A'], 'Threats': ['N/A']}

            # Mock market share and products
            market_share = 0.0
            if competitor_name == "CloudCorp Inc.": market_share = 25.5
            elif competitor_name == "DataMinds Ltd.": market_share = 18.2
            key_products = [f"{competitor_name} Cloud Platform", f"{competitor_name} AI Solutions"]

            # Simulate emerging/disruptive flag
            is_emerging_disruptor = False
            if "emerging" in competitor_name.lower() or "disrupt" in competitor_name.lower():
                is_emerging_disruptor = True
                identified_emerging_competitors.append(competitor_name)

            competitive_landscapes.append(
                CompetitiveLandscape(
                    name=competitor_name,
                    market_share=market_share if market_share > 0 else None,
                    swot_analysis=swot_analysis,
                    key_products_services=key_products,
                    emerging_disruptor=is_emerging_disruptor
                )
            )
            if is_emerging_disruptor:
                identified_disruptive_forces.append(f"{competitor_name} as a disruptive force")


        # Simulate identifying general disruptive forces from industry data
        disruptive_forces_prompt = (
            f"Based on the following data, identify any general disruptive forces "
            f"or emerging threats in the '{industry}' sector:\n\n"
            f"Data: {industry_data}\n\n"
            f"Return a list of strings."
        )
        # Using a simplified mock response for lists
        mock_disruptive_forces = ["AI-powered automation", "Stringent data privacy regulations", "Supply chain disruptions"]
        for force in mock_disruptive_forces:
            if force not in identified_disruptive_forces:
                identified_disruptive_forces.append(force)


        logger.info(f"Completed industry and competitive analysis for {industry}.")
        return IndustryAnalysis(
            overview=industry_overview,
            market_size=f"Estimated market size: $500B by 2025 (mock data for {industry})", # Mock data
            key_players=competitive_landscapes,
            emerging_competitors=identified_emerging_competitors,
            disruptive_forces=identified_disruptive_forces
        )

```

```python
# src/services/market_trends_prediction.py
import logging
from typing import Dict, Any, List, Optional
import asyncio # Required for async operations

from src.services.analysis_service import BaseAnalysisService
from src.services.llm_orchestrator import LLMOrchestrator
from src.services.knowledge_store import KnowledgeStoreService
from src.models.report_data_models import MarketTrends, MarketTrend
from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class MarketTrendsPredictionService(BaseAnalysisService):
    """
    Identifies prevailing market trends, patterns, and shifts, and makes future predictions.
    Also tracks macroeconomic factors and regulatory changes.
    """
    def __init__(self, llm_orchestrator: LLMOrchestrator, knowledge_store: KnowledgeStoreService) -> None:
        """
        Initializes the MarketTrendsPredictionService.
        """
        super().__init__(llm_orchestrator, knowledge_store)
        logger.info("MarketTrendsPredictionService initialized.")

    async def analyze(self, industry: str, target_market_segment: Optional[str] = None) -> MarketTrends:
        """
        Analyzes market data to identify trends and make predictions.

        Args:
            industry: The primary industry under consideration.
            target_market_segment: Optional specific market segment to focus on.

        Returns:
            A MarketTrends object containing the analysis results.
        """
        logger.info(f"Performing market trends and prediction analysis for: {industry}, segment: {target_market_segment}")

        # 1. Gather relevant data from Knowledge Store
        query_params = {"industry": industry}
        if target_market_segment:
            query_params["segment"] = target_market_segment

        market_data = await self.knowledge_store.query_knowledge_base(query_params)
        # Add some general economic and regulatory data for broader context
        economic_data = await self.knowledge_store.query_knowledge_base({"type": "macroeconomic"})
        regulatory_data = await self.knowledge_store.query_knowledge_base({"type": "regulatory_change"})
        all_relevant_data = market_data + economic_data + regulatory_data

        # 2. Use LLM for Market Trends Overview
        overview_prompt = (
            f"Based on the following market data and context, provide an overview of the "
            f"prevailing market trends and shifts in the '{industry}' industry (and '{target_market_segment}' segment if applicable):\n\n"
            f"Data: {all_relevant_data}\n\n"
            f"The overview should be concise and insightful for a market research report."
        )
        trends_overview = await self.llm_orchestrator.generate_text(overview_prompt)

        # 3. Use LLM to identify specific trends and make predictions
        trends_identification_prompt = (
            f"Analyze the following market data for the '{industry}' industry and identify "
            f"key market trends, their impact, and future predictions. "
            f"Also, identify any correlations between data points that suggest emerging trends.\n\n"
            f"Data: {all_relevant_data}\n\n"
            f"Return a JSON list of objects, each with 'name', 'description', 'impact', 'prediction', and 'data_points' (list of strings)."
        )
        identified_trends_raw = await self.llm_orchestrator.generate_json(trends_identification_prompt, temperature=0.6)
        identified_trends: List[MarketTrend] = []

        # Robust parsing for demonstration
        if isinstance(identified_trends_raw, list):
            for trend_dict in identified_trends_raw:
                try:
                    identified_trends.append(MarketTrend(**trend_dict))
                except Exception as e:
                    logger.warning(f"Failed to parse identified trend: {trend_dict}, error: {e}")
        else: # Handle cases where LLM returns a single object or error
             logger.warning(f"LLM did not return a list for identified trends: {identified_trends_raw}. Providing default mock trend.")
             # Provide a default mock trend if parsing fails
             identified_trends.append(
                 MarketTrend(
                     name="Digital Transformation Acceleration",
                     description="Businesses are rapidly adopting digital technologies to enhance operations and customer experiences.",
                     impact="Increased demand for cloud services and cybersecurity solutions.",
                     prediction="Continued growth in SaaS and platform-as-a-service offerings.",
                     data_points=["Increased cloud spending reports", "Growth in cybersecurity incidents"]
                 )
             )

        # 4. Identify Macroeconomic Factors and Regulatory Changes
        macro_factors_prompt = (
            f"Based on the following data, list key macroeconomic factors impacting the '{industry}' market:\n\n"
            f"Data: {all_relevant_data}\n\n"
            f"Return a list of strings."
        )
        # Mocking for brevity. In a real scenario, this would be an LLM call:
        # macroeconomic_factors = await self.llm_orchestrator.generate_json(macro_factors_prompt)
        macroeconomic_factors = ["Global inflation rates", "Interest rate hikes", "Supply chain stability"]

        regulatory_changes_prompt = (
            f"Based on the following data, list key regulatory changes impacting the '{industry}' market:\n\n"
            f"Data: {all_relevant_data}\n\n"
            f"Return a list of strings."
        )
        # Mocking for brevity. In a real scenario, this would be an LLM call:
        # regulatory_changes = await self.llm_orchestrator.generate_json(regulatory_changes_prompt)
        regulatory_changes = ["New data privacy laws (e.g., GDPR variants)", "AI governance frameworks"]

        logger.info(f"Completed market trends and prediction analysis for {industry}.")
        return MarketTrends(
            overview=trends_overview,
            identified_trends=identified_trends,
            macroeconomic_factors=macroeconomic_factors,
            regulatory_changes=regulatory_changes
        )

```

```python
# src/services/technology_adoption_analysis.py
import logging
from typing import Dict, Any, List, Optional
import asyncio # Required for async operations

from src.services.analysis_service import BaseAnalysisService
from src.services.llm_orchestrator import LLMOrchestrator
from src.services.knowledge_store import KnowledgeStoreService
from src.models.report_data_models import TechnologyAdoption, TechnologyAdoptionDetails
from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class TechnologyAdoptionAnalysisService(BaseAnalysisService):
    """
    Assesses the current state of technology adoption, identifies emerging technologies,
    and provides recommendations for technology adoption strategies.
    """
    def __init__(self, llm_orchestrator: LLMOrchestrator, knowledge_store: KnowledgeStoreService) -> None:
        """
        Initializes the TechnologyAdoptionAnalysisService.
        """
        super().__init__(llm_orchestrator, knowledge_store)
        logger.info("TechnologyAdoptionAnalysisService initialized.")

    async def analyze(self, industry: str, focus_technologies: Optional[List[str]] = None) -> TechnologyAdoption:
        """
        Analyzes technology adoption within the specified industry.

        Args:
            industry: The industry to analyze.
            focus_technologies: Optional list of specific technologies to focus on.

        Returns:
            A TechnologyAdoption object containing the analysis results.
        """
        logger.info(f"Performing technology adoption analysis for: {industry}")

        # 1. Gather relevant data from Knowledge Store
        tech_adoption_data = await self.knowledge_store.query_knowledge_base({"industry": industry, "type": "research_paper"})
        tech_news_data = await self.knowledge_store.query_knowledge_base({"industry": industry, "type": "news"})
        competitor_tech_data = await self.knowledge_store.query_knowledge_base({"industry": industry, "type": "company_report"})
        all_relevant_tech_data = tech_adoption_data + tech_news_data + competitor_tech_data

        # 2. Use LLM for Technology Adoption Overview
        overview_prompt = (
            f"Based on the following data, provide an overview of the current state of technology adoption "
            f"within the '{industry}' industry:\n\n"
            f"Data: {all_relevant_tech_data}\n\n"
            f"The overview should be concise and suitable for a market research report."
        )
        tech_overview = await self.llm_orchestrator.generate_text(overview_prompt)

        # 3. Identify Current and Emerging Technologies and their Impact
        tech_details_prompt = (
            f"Analyze the following data for the '{industry}' industry to identify key currently adopted "
            f"technologies and emerging technologies. For each, describe its potential impact.\n\n"
            f"Data: {all_relevant_tech_data}\n\n"
            f"Return a JSON object with two keys: 'current_technologies' and 'emerging_technologies'. "
            f"Each value should be a list of objects, with 'technology_name', 'current_adoption_rate' (for current), "
            f"'potential_impact', and 'recommendation' (optional)."
        )
        tech_data_raw = await self.llm_orchestrator.generate_json(tech_details_prompt, temperature=0.5)

        current_technologies: List[TechnologyAdoptionDetails] = []
        emerging_technologies: List[TechnologyAdoptionDetails] = []

        # Robust parsing for demonstration
        mock_current = [
            {"technology_name": "Cloud ERP", "current_adoption_rate": "High in enterprises", "potential_impact": "Streamlined operations", "recommendation": "Optimize existing deployments."},
            {"technology_name": "Data Analytics Platforms", "current_adoption_rate": "Moderate", "potential_impact": "Improved decision making", "recommendation": "Invest in advanced analytics training."}
        ]
        mock_emerging = [
            {"technology_name": "Generative AI for Marketing", "potential_impact": "Automated content creation, personalized campaigns.", "recommendation": "Pilot programs in specific departments."},
            {"technology_name": "Quantum Computing (early stage)", "potential_impact": "Revolutionary computational power for specific problems.", "recommendation": "Monitor research, identify potential use cases."}
        ]

        # Use mock data for parsing flexibility, in a real system, LLM's raw output should be parsed.
        # This demonstrates how to robustly parse the expected LLM output structure.
        if isinstance(tech_data_raw, dict):
            for tech_dict in tech_data_raw.get("current_technologies", []):
                try:
                    current_technologies.append(TechnologyAdoptionDetails(**tech_dict))
                except Exception as e:
                    logger.warning(f"Failed to parse current tech: {tech_dict}, error: {e}")
            for tech_dict in tech_data_raw.get("emerging_technologies", []):
                try:
                    emerging_technologies.append(TechnologyAdoptionDetails(**tech_dict))
                except Exception as e:
                    logger.warning(f"Failed to parse emerging tech: {tech_dict}, error: {e}")
        else:
            logger.warning(f"LLM did not return expected dict for technology adoption: {tech_data_raw}. Using default mock data.")
            for tech_dict in mock_current:
                current_technologies.append(TechnologyAdoptionDetails(**tech_dict))
            for tech_dict in mock_emerging:
                emerging_technologies.append(TechnologyAdoptionDetails(**tech_dict))

        # 4. Provide Technology Adoption Strategy Recommendations
        strategy_recommendations_prompt = (
            f"Based on the analysis of current and emerging technologies in the '{industry}' industry, "
            f"provide actionable recommendations for technology adoption strategies.\n\n"
            f"Data: {all_relevant_tech_data}\n\n"
            f"Return a list of strategic recommendations (strings)."
        )
        # Mocking for brevity. In a real scenario, this would be an LLM call:
        # adoption_strategy_recommendations = await self.llm_orchestrator.generate_json(strategy_recommendations_prompt)
        adoption_strategy_recommendations = [
            "Prioritize investment in AI-driven automation for efficiency gains.",
            "Establish a cross-functional innovation lab to explore emerging technologies.",
            "Develop robust cybersecurity frameworks to protect new technology deployments.",
            "Foster a culture of continuous learning and upskilling for new technologies."
        ]


        logger.info(f"Completed technology adoption analysis for {industry}.")
        return TechnologyAdoption(
            overview=tech_overview,
            current_technologies=current_technologies,
            emerging_technologies=emerging_technologies,
            adoption_strategy_recommendations=adoption_strategy_recommendations
        )

```

```python
# src/services/strategic_insights.py
import logging
from typing import Dict, Any, List, Optional
import asyncio # Required for async operations

from src.services.analysis_service import BaseAnalysisService
from src.services.llm_orchestrator import LLMOrchestrator
from src.services.knowledge_store import KnowledgeStoreService
from src.services.industry_competitive_analysis import IndustryCompetitiveAnalysisService
from src.services.market_trends_prediction import MarketTrendsPredictionService
from src.services.technology_adoption_analysis import TechnologyAdoptionAnalysisService
from src.models.report_data_models import (
    ResearchRequest, StrategicInsights, StrategicRecommendation,
    IndustryAnalysis, MarketTrends, TechnologyAdoption, KeyFinding, ExecutiveSummary
)
from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class StrategicInsightsService(BaseAnalysisService):
    """
    Synthesizes insights from various analysis services and generates strategic insights
    and actionable recommendations, including customer-specific actions.
    Also responsible for generating the Executive Summary.
    """
    def __init__(
        self,
        llm_orchestrator: LLMOrchestrator,
        knowledge_store: KnowledgeStoreService,
        industry_analysis_service: IndustryCompetitiveAnalysisService,
        market_trends_service: MarketTrendsPredictionService,
        technology_adoption_service: TechnologyAdoptionAnalysisService
    ) -> None:
        """
        Initializes the StrategicInsightsService with dependencies on other analysis services.
        """
        super().__init__(llm_orchestrator, knowledge_store)
        self.industry_analysis_service = industry_analysis_service
        self.market_trends_service = market_trends_service
        self.technology_adoption_service = technology_adoption_service
        logger.info("StrategicInsightsService initialized.")

    async def analyze(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        This method is not used directly as `generate_insights` is the primary entry point.
        It's here to satisfy the abstract base class requirement.
        """
        raise NotImplementedError("Use 'generate_insights' method for this service.")

    async def generate_insights(
        self,
        request: ResearchRequest,
        industry_analysis: IndustryAnalysis,
        market_trends: MarketTrends,
        technology_adoption: TechnologyAdoption
    ) -> StrategicInsights:
        """
        Synthesizes findings from all analysis modules to generate strategic insights
        and actionable recommendations.

        Args:
            request: The original research request.
            industry_analysis: The results from the industry analysis.
            market_trends: The results from the market trends analysis.
            technology_adoption: The results from the technology adoption analysis.

        Returns:
            A StrategicInsights object containing overall insights and recommendations.
        """
        logger.info(f"Generating strategic insights for industry: {request.industry}")

        # Combine all analysis data for synthesis by LLM
        combined_analysis_data = {
            "request_details": request.dict(),
            "industry_analysis": industry_analysis.dict(),
            "market_trends": market_trends.dict(),
            "technology_adoption": technology_adoption.dict()
        }

        # 1. Generate Overall Strategic Insights
        insights_prompt = (
            f"Based on the following comprehensive market research data for the '{request.industry}' industry "
            f"(and segment '{request.target_market_segment}' if specified), "
            f"synthesize overall strategic insights. Focus on key takeaways, opportunities, and challenges.\n\n"
            f"Data: {combined_analysis_data}\n\n"
            f"Provide a concise, high-level strategic overview."
        )
        overall_insights = await self.llm_orchestrator.generate_text(insights_prompt, temperature=0.7)

        # 2. Generate Actionable Recommendations
        recommendations_prompt = (
            f"Based on the combined market research data for the '{request.industry}' industry, "
            f"generate clear, concise, and actionable strategic recommendations. "
            f"For each recommendation, provide detailed rationale and specific action items.\n\n"
            f"Data: {combined_analysis_data}\n\n"
            f"Return a JSON list of objects, each with 'recommendation', 'details', 'action_items' (list of strings), "
            f"and 'target_audience' (optional)."
        )
        actionable_recommendations_raw = await self.llm_orchestrator.generate_json(recommendations_prompt, temperature=0.6)
        actionable_recommendations: List[StrategicRecommendation] = []

        if isinstance(actionable_recommendations_raw, list):
            for rec_dict in actionable_recommendations_raw:
                try:
                    actionable_recommendations.append(StrategicRecommendation(**rec_dict))
                except Exception as e:
                    logger.warning(f"Failed to parse recommendation: {rec_dict}, error: {e}")
        else:
            logger.warning(f"LLM did not return a list for recommendations: {actionable_recommendations_raw}. Providing default mock recommendations.")
            # Fallback mock recommendations
            actionable_recommendations.append(
                StrategicRecommendation(
                    recommendation="Diversify Cloud Provider Portfolio",
                    details="Reduce vendor lock-in and optimize costs by utilizing multiple cloud providers for different workloads.",
                    action_items=["Conduct multi-cloud feasibility study", "Identify suitable workloads for migration", "Establish multi-cloud governance policy"],
                    target_audience="IT Leadership, Procurement"
                )
            )

        # 3. Derive Customer-Specific Action Items (Simulated)
        # In a real system, this would involve processing specific customer interaction data, sales trends, etc.
        customer_specific_actions: List[str] = [
            f"For existing '{request.industry}' clients: Upsell new AI-powered analytics features based on market trend for data-driven decisions.",
            f"For prospective clients in '{request.target_market_segment}': Highlight our competitive advantages against {request.competitors_of_interest[0] if request.competitors_of_interest else 'key competitor'} based on SWOT analysis."
        ]
        logger.info("Strategic insights and recommendations generated.")

        return StrategicInsights(
            overall_insights=overall_insights,
            actionable_recommendations=actionable_recommendations,
            customer_specific_actions=customer_specific_actions
        )

    async def generate_executive_summary(
        self,
        request: ResearchRequest,
        industry_analysis: IndustryAnalysis,
        market_trends: MarketTrends,
        technology_adoption: TechnologyAdoption,
        strategic_insights: StrategicInsights
    ) -> ExecutiveSummary:
        """
        Generates a concise executive summary with key findings from the entire report.

        Args:
            request: The original research request.
            industry_analysis: The results from the industry analysis.
            market_trends: The results from the market trends analysis.
            technology_adoption: The results from the technology adoption analysis.
            strategic_insights: The results from the strategic insights generation.

        Returns:
            An ExecutiveSummary object.
        """
        logger.info("Generating executive summary...")

        # Combine key elements from all sections for the summary
        summary_context = f"""
        Industry: {request.industry}
        Target Segment: {request.target_market_segment if request.target_market_segment else 'N/A'}

        Industry Overview: {industry_analysis.overview[:300]}...
        Key Players: {', '.join([p.name for p in industry_analysis.key_players[:3]]) if industry_analysis.key_players else 'N/A'}...
        Market Trends Overview: {market_trends.overview[:300]}...
        Top Trend: {market_trends.identified_trends[0].name if market_trends.identified_trends else 'N/A'}
        Technology Adoption Overview: {technology_adoption.overview[:300]}...
        Emerging Tech: {technology_adoption.emerging_technologies[0].technology_name if technology_adoption.emerging_technologies else 'N/A'}
        Overall Strategic Insights: {strategic_insights.overall_insights[:300]}...
        Top Recommendation: {strategic_insights.actionable_recommendations[0].recommendation if strategic_insights.actionable_recommendations else 'N/A'}
        """

        summary_prompt = (
            f"Based on the following condensed market research context, generate a high-level executive summary "
            f"for a Gartner-style report. Highlight the most critical findings, insights, and recommendations.\n\n"
            f"Context: {summary_context}\n\n"
            f"Return a JSON object with a 'summary' string and 'key_findings' as a list of objects. "
            f"Each key finding object should have 'title', 'description', and 'impact'."
        )
        executive_summary_raw = await self.llm_orchestrator.generate_json(summary_prompt, temperature=0.7)

        summary_text: str = executive_summary_raw.get("summary", "Executive Summary not available.")
        key_findings_list: List[KeyFinding] = []

        if isinstance(executive_summary_raw.get("key_findings"), list):
            for finding_dict in executive_summary_raw["key_findings"]:
                try:
                    key_findings_list.append(KeyFinding(**finding_dict))
                except Exception as e:
                    logger.warning(f"Failed to parse key finding: {finding_dict}, error: {e}")
        else:
            logger.warning(f"LLM did not return a list for key findings: {executive_summary_raw.get('key_findings')}. Providing default mock key findings.")
            # Fallback mock key findings
            key_findings_list.append(
                KeyFinding(
                    title="Rapid Market Expansion",
                    description=f"The {request.industry} market demonstrates significant growth potential, driven by evolving digital demands.",
                    impact="Opens new avenues for market entry and product innovation."
                )
            )
            key_findings_list.append(
                KeyFinding(
                    title="Technology as a Differentiator",
                    description="Adoption of advanced technologies like AI and hybrid cloud is crucial for competitive advantage.",
                    impact="Requires strategic investments in R&D and talent development."
                )
            )

        logger.info("Executive summary generated.")
        return ExecutiveSummary(summary=summary_text, key_findings=key_findings_list)

```

```python
# src/services/report_generation.py
import logging
from datetime import datetime
from typing import Dict, Any, List
import asyncio # Required for async operations

from src.services.llm_orchestrator import LLMOrchestrator
from src.models.report_data_models import (
    ResearchRequest, MarketResearchReport, ExecutiveSummary,
    IndustryAnalysis, MarketTrends, TechnologyAdoption, StrategicInsights, KeyFinding, StrategicRecommendation
)
from src.utils.logger_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

class ReportGenerationService:
    """
    Compiles and formats the analysis outputs into a professional "Gartner-style" market research report.
    This service is responsible for structuring the final report document.
    """
    def __init__(self) -> None: # llm_orchestrator is no longer directly needed here as ES is pre-generated
        """
        Initializes the ReportGenerationService.
        """
        logger.info("ReportGenerationService initialized.")

    async def generate_report(
        self,
        request: ResearchRequest,
        executive_summary: ExecutiveSummary, # Executive Summary is now passed in
        industry_analysis: IndustryAnalysis,
        market_trends: MarketTrends,
        technology_adoption: TechnologyAdoption,
        strategic_insights: StrategicInsights
    ) -> MarketResearchReport:
        """
        Generates the final comprehensive market research report.

        Args:
            request: The original research request.
            executive_summary: The pre-generated ExecutiveSummary object.
            industry_analysis: The results from the industry analysis.
            market_trends: The results from the market trends analysis.
            technology_adoption: The results from the technology adoption analysis.
            strategic_insights: The results from the strategic insights generation.

        Returns:
            A MarketResearchReport object containing the complete structured report.
        """
        logger.info(f"Finalizing report for '{request.industry}'...")
        await asyncio.sleep(0.2) # Simulate report assembly time

        # Assemble the final report
        report = MarketResearchReport(
            request_details=request,
            executive_summary=executive_summary, # Use the passed executive summary
            industry_analysis=industry_analysis,
            market_trends=market_trends,
            technology_adoption=technology_adoption,
            strategic_recommendations=strategic_insights,
            generated_at=datetime.now().isoformat()
        )

        logger.info("Report structure assembled.")
        # In a real application, this would involve rendering to PDF, DOCX, or a web template.
        # For simplicity, we just return the Pydantic model.
        return report

```

```python
# src/utils/logger_config.py
import logging

def configure_logging(level: int = logging.INFO) -> None:
    """
    Configures the logging for the application.

    Args:
        level: The minimum logging level to capture (e.g., logging.INFO, logging.DEBUG).
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Outputs logs to console
            # logging.FileHandler("app.log") # Uncomment to also log to a file
        ]
    )
    # Optional: Set higher level for specific noisy loggers
    logging.getLogger('httpx').setLevel(logging.WARNING) # If using aiohttp or httpx for real LLM calls
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('pydantic').setLevel(logging.WARNING) # Pydantic can be noisy with validations
    logging.info("Logging configured.")

```

```python
# tests/test_data_ingestion.py
import unittest
import logging
from unittest.mock import AsyncMock # Use AsyncMock for async methods

from src.services.data_ingestion import DataIngestionService
from src.utils.logger_config import configure_logging
import asyncio

# Configure logging for tests
configure_logging(level=logging.DEBUG)

class TestDataIngestionService(unittest.IsolatedAsyncioTestCase): # Use IsolatedAsyncioTestCase for async tests
    """
    Unit tests for the DataIngestionService.
    """
    def setUp(self) -> None:
        """Set up for test methods."""
        self.ingestion_service = DataIngestionService()
        self.test_industry = "Renewable Energy"
        self.test_competitors = ["SolarCo", "WindPower Inc."]

    async def test_ingest_data_returns_list_of_dicts(self) -> None:
        """
        Test that ingest_data returns a list of dictionaries.
        """
        result = await self.ingestion_service.ingest_data(self.test_industry, self.test_competitors)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], dict)

    async def test_ingest_data_contains_expected_types(self) -> None:
        """
        Test that ingested data contains expected 'type' keys.
        """
        result = await self.ingestion_service.ingest_data(self.test_industry, self.test_competitors)
        types = {entry.get("type") for entry in result}
        self.assertIn("news", types)
        self.assertIn("company_report", types)
        self.assertIn("social_media", types)
        self.assertIn("market_data", types)
        self.assertIn("research_paper", types)

    async def test_ingest_data_contains_competitor_names(self) -> None:
        """
        Test that ingested data content mentions competitor names.
        """
        result = await self.ingestion_service.ingest_data(self.test_industry, self.test_competitors)
        found_competitor_mention = False
        for entry in result:
            if "content" in entry and any(comp.lower() in entry["content"].lower() for comp in self.test_competitors):
                found_competitor_mention = True
                break
        self.assertTrue(found_competitor_mention, "Competitor names should be mentioned in ingested data.")

    async def test_ingest_data_with_empty_competitor_list(self) -> None:
        """
        Test ingestion when no specific competitors are provided.
        Should still return general industry data.
        """
        result = await self.ingestion_service.ingest_data(self.test_industry, [])
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        # Ensure that at least general news/market data is present
        types = {entry.get("type") for entry in result}
        self.assertIn("news", types)
        self.assertIn("market_data", types)

if __name__ == '__main__':
    unittest.main()

```

```python
# tests/test_llm_orchestrator.py
import unittest
import logging
from unittest.mock import patch, AsyncMock # Use AsyncMock for async methods
import asyncio # Required for async tests

from src.services.llm_orchestrator import LLMOrchestrator
from src.utils.logger_config import configure_logging
import json # For mock JSON loads

# Configure logging for tests
configure_logging(level=logging.DEBUG)

class TestLLMOrchestrator(unittest.IsolatedAsyncioTestCase): # Use IsolatedAsyncioTestCase for async tests
    """
    Unit tests for the LLMOrchestrator service.
    Mocks the actual LLM API calls.
    """
    def setUp(self) -> None:
        """Set up for test methods."""
        self.llm_orchestrator = LLMOrchestrator()

    @patch('src.services.llm_orchestrator.LLMOrchestrator._call_llm_api', new_callable=AsyncMock)
    async def test_generate_text(self, mock_call_llm_api: AsyncMock) -> None:
        """
        Test that generate_text calls the LLM API and returns its response.
        """
        mock_call_llm_api.return_value = "This is a test response."
        prompt = "Hello LLM"
        result = await self.llm_orchestrator.generate_text(prompt)

        mock_call_llm_api.assert_awaited_once_with(self.llm_orchestrator.default_model, prompt, 0.7)
        self.assertEqual(result, "This is a test response.")

    @patch('src.services.llm_orchestrator.LLMOrchestrator._call_llm_api', new_callable=AsyncMock)
    async def test_generate_json(self, mock_call_llm_api: AsyncMock) -> None:
        """
        Test that generate_json calls the LLM API and parses a JSON string.
        """
        mock_json_response = '{"key": "value", "number": 123}' # Ensure valid JSON string
        mock_call_llm_api.return_value = mock_json_response
        prompt = "Generate JSON"
        result = await self.llm_orchestrator.generate_json(prompt)

        mock_call_llm_api.assert_awaited_once()
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value', 'number': 123})

    @patch('src.services.llm_orchestrator.LLMOrchestrator._call_llm_api', new_callable=AsyncMock)
    async def test_generate_json_invalid_response(self, mock_call_llm_api: AsyncMock) -> None:
        """
        Test that generate_json handles invalid JSON responses gracefully.
        """
        mock_call_llm_api.return_value = "This is not JSON"
        prompt = "Generate Invalid JSON"
        result = await self.llm_orchestrator.generate_json(prompt)

        mock_call_llm_api.assert_awaited_once()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid JSON response from LLM")

    @patch('src.services.llm_orchestrator.LLMOrchestrator._call_llm_api', new_callable=AsyncMock)
    async def test_summarize(self, mock_call_llm_api: AsyncMock) -> None:
        """
        Test that summarize constructs the correct prompt and returns summary.
        """
        mock_call_llm_api.return_value = "Summary of text."
        text = "This is a long piece of text that needs to be summarized."
        result = await self.llm_orchestrator.summarize(text)

        expected_prompt_start = "Summarize the following text:"
        mock_call_llm_api.assert_awaited_once()
        args, kwargs = mock_call_llm_api.call_args
        self.assertIn(expected_prompt_start, args[1])
        self.assertEqual(result, "Summary of text.")

    @patch('src.services.llm_orchestrator.LLMOrchestrator._call_llm_api', new_callable=AsyncMock)
    async def test_extract_info(self, mock_call_llm_api: AsyncMock) -> None:
        """
        Test that extract_info constructs the correct prompt for info extraction.
        """
        mock_call_llm_api.return_value = '{"name": "Company A", "revenue": 1000}' # Ensure valid JSON string
        text = "Company A had a revenue of $1000 last quarter."
        schema = {"name": "string", "revenue": "number"}
        result = await self.llm_orchestrator.extract_info(text, schema)

        expected_prompt_start = "Extract information from the following text based on this JSON schema:"
        mock_call_llm_api.assert_awaited_once()
        args, kwargs = mock_call_llm_api.call_args
        self.assertIn(expected_prompt_start, args[1])
        self.assertIn(json.dumps(schema), args[1]) # Use json.dumps for schema comparison
        self.assertEqual(result, {'name': 'Company A', 'revenue': 1000})

    async def test_retrieve_context_for_rag(self) -> None:
        """
        Test that retrieve_context_for_rag returns relevant mock contexts.
        """
        query = "cloud computing solutions"
        context = await self.llm_orchestrator.retrieve_context_for_rag(query)
        self.assertIsInstance(context, list)
        self.assertGreater(len(context), 0)
        self.assertIn("Cloud computing involves delivering computing services over the internet.", context)
        self.assertIn("Hybrid cloud solutions combine public and private clouds.", context)

        query_no_match = "unrelated query"
        context_no_match = await self.llm_orchestrator.retrieve_context_for_rag(query_no_match)
        self.assertIsInstance(context_no_match, list)
        self.assertEqual(len(context_no_match), 1)
        self.assertEqual(context_no_match[0], "No specific context found for the query.")

    @patch('src.services.llm_orchestrator.LLMOrchestrator._call_llm_api', new_callable=AsyncMock)
    async def test_llm_cache(self, mock_call_llm_api: AsyncMock) -> None:
        """
        Test that LLM responses are cached.
        """
        mock_call_llm_api.return_value = "First response."
        prompt = "Cached query"

        # First call, should hit LLM
        result1 = await self.llm_orchestrator.generate_text(prompt)
        mock_call_llm_api.assert_called_once()
        self.assertEqual(result1, "First response.")

        # Second call with same prompt, should hit cache
        mock_call_llm_api.reset_mock() # Reset mock to check if it's called again
        result2 = await self.llm_orchestrator.generate_text(prompt)
        mock_call_llm_api.assert_not_called() # Should not call LLM API again
        self.assertEqual(result2, "First response.")

if __name__ == '__main__':
    unittest.main()

```

```python
# tests/test_strategic_insights.py
import unittest
import logging
from unittest.mock import AsyncMock, patch # Use AsyncMock for async methods

from src.services.strategic_insights import StrategicInsightsService
from src.services.llm_orchestrator import LLMOrchestrator
from src.services.knowledge_store import KnowledgeStoreService
from src.services.industry_competitive_analysis import IndustryCompetitiveAnalysisService
from src.services.market_trends_prediction import MarketTrendsPredictionService
from src.services.technology_adoption_analysis import TechnologyAdoptionAnalysisService
from src.models.report_data_models import (
    ResearchRequest, IndustryAnalysis, MarketTrends, TechnologyAdoption,
    StrategicInsights, StrategicRecommendation, ExecutiveSummary, KeyFinding
)
from src.utils.logger_config import configure_logging
import asyncio

# Configure logging for tests
configure_logging(level=logging.DEBUG)

class TestStrategicInsightsService(unittest.IsolatedAsyncioTestCase): # Use IsolatedAsyncioTestCase
    """
    Unit tests for the StrategicInsightsService.
    Mocks dependencies on other services and LLM calls.
    """
    def setUp(self) -> None:
        """Set up for test methods."""
        self.mock_llm_orchestrator = AsyncMock(spec=LLMOrchestrator)
        self.mock_knowledge_store = AsyncMock(spec=KnowledgeStoreService)
        # Mock analysis services with AsyncMock
        self.mock_industry_analysis_service = AsyncMock(spec=IndustryCompetitiveAnalysisService)
        self.mock_market_trends_service = AsyncMock(spec=MarketTrendsPredictionService)
        self.mock_technology_adoption_service = AsyncMock(spec=TechnologyAdoptionAnalysisService)

        self.strategic_insights_service = StrategicInsightsService(
            self.mock_llm_orchestrator,
            self.mock_knowledge_store,
            self.mock_industry_analysis_service,
            self.mock_market_trends_service,
            self.mock_technology_adoption_service
        )

        self.mock_research_request = ResearchRequest(
            industry="AI Software",
            target_market_segment="Enterprise",
            competitors_of_interest=["IBM", "Google"]
        )
        self.mock_industry_analysis = IndustryAnalysis(
            overview="Industry is growing.",
            key_players=[],
            emerging_competitors=[],
            disruptive_forces=[]
        )
        self.mock_market_trends = MarketTrends(
            overview="Trends are positive.",
            identified_trends=[],
            macroeconomic_factors=[],
            regulatory_changes=[]
        )
        self.mock_technology_adoption = TechnologyAdoption(
            overview="Tech adoption is high.",
            current_technologies=[],
            emerging_technologies=[],
            adoption_strategy_recommendations=[]
        )

    async def test_generate_insights_returns_strategic_insights(self) -> None:
        """
        Test that generate_insights returns a StrategicInsights object
        and calls LLM for overall insights and recommendations.
        """
        self.mock_llm_orchestrator.generate_text.return_value = "Overall strategic insights text."
        # Ensure mock JSON return is a list of dicts
        self.mock_llm_orchestrator.generate_json.return_value = [
            {'recommendation': 'Invest in R&D', 'details': 'To stay competitive.', 'action_items': ['Hire more engineers'], 'target_audience': 'Product Team'}
        ]

        result = await self.strategic_insights_service.generate_insights(
            self.mock_research_request,
            self.mock_industry_analysis,
            self.mock_market_trends,
            self.mock_technology_adoption
        )

        self.assertIsInstance(result, StrategicInsights)
        self.assertEqual(result.overall_insights, "Overall strategic insights text.")
        self.assertIsInstance(result.actionable_recommendations, list)
        self.assertGreater(len(result.actionable_recommendations), 0)
        self.assertIsInstance(result.actionable_recommendations[0], StrategicRecommendation)
        self.mock_llm_orchestrator.generate_text.assert_awaited_once()
        self.mock_llm_orchestrator.generate_json.assert_awaited_once()

    async def test_generate_executive_summary_returns_executive_summary(self) -> None:
        """
        Test that generate_executive_summary returns an ExecutiveSummary object
        and calls LLM for summary and key findings.
        """
        # Ensure mock JSON return is a dict with 'summary' and 'key_findings' list
        self.mock_llm_orchestrator.generate_json.return_value = {
            'summary': 'Executive Summary text.',
            'key_findings': [{'title': 'Finding 1', 'description': 'Desc 1', 'impact': 'Imp 1'}]
        }

        # Create a mock StrategicInsights object for the input
        mock_strategic_insights = StrategicInsights(
            overall_insights="Synthesized insights here.",
            actionable_recommendations=[StrategicRecommendation(recommendation="Test", details="Test", action_items=[])],
            customer_specific_actions=[]
        )

        result = await self.strategic_insights_service.generate_executive_summary(
            self.mock_research_request,
            self.mock_industry_analysis,
            self.mock_market_trends,
            self.mock_technology_adoption,
            mock_strategic_insights
        )

        self.assertIsInstance(result, ExecutiveSummary)
        self.assertEqual(result.summary, "Executive Summary text.")
        self.assertIsInstance(result.key_findings, list)
        self.assertGreater(len(result.key_findings), 0)
        self.assertIsInstance(result.key_findings[0], KeyFinding)
        self.mock_llm_orchestrator.generate_json.assert_awaited_once()

    async def test_analyze_method_raises_not_implemented_error(self) -> None:
        """
        Test that the abstract analyze method is not directly callable.
        """
        with self.assertRaises(NotImplementedError):
            await self.strategic_insights_service.analyze()

if __name__ == '__main__':
    unittest.main()

```

```python
# tests/test_report_generation.py
import unittest
import logging
from unittest.mock import MagicMock, AsyncMock, patch # Use AsyncMock for async methods

from src.services.report_generation import ReportGenerationService
from src.services.llm_orchestrator import LLMOrchestrator # Still needed for spec
from src.models.report_data_models import (
    ResearchRequest, IndustryAnalysis, MarketTrends, TechnologyAdoption,
    StrategicInsights, MarketResearchReport, ExecutiveSummary, KeyFinding, StrategicRecommendation
)
from src.utils.logger_config import configure_logging
import asyncio
from datetime import datetime

# Configure logging for tests
configure_logging(level=logging.DEBUG)

class TestReportGenerationService(unittest.IsolatedAsyncioTestCase): # Use IsolatedAsyncioTestCase
    """
    Unit tests for the ReportGenerationService.
    Mocks the LLM orchestrator and provides dummy data for analysis results.
    """
    def setUp(self) -> None:
        """Set up for test methods."""
        # No longer need to pass LLMOrchestrator to ReportGenerationService's constructor
        self.report_generation_service = ReportGenerationService()

        # Create dummy data for report generation
        self.mock_request = ResearchRequest(
            industry="AI Software",
            target_market_segment="Healthcare",
            specific_metrics=["ROI"],
            competitors_of_interest=["DeepMind"]
        )
        self.mock_executive_summary = ExecutiveSummary( # Pre-generated ExecutiveSummary
            summary="A comprehensive overview of AI in Healthcare.",
            key_findings=[
                KeyFinding(
                    title="AI Adoption Growth",
                    description="AI in healthcare is growing due to efficiency gains.",
                    impact="Improved patient outcomes."
                )
            ]
        )
        self.mock_industry_analysis = IndustryAnalysis(
            overview="AI in healthcare is booming.",
            market_size="$50B",
            key_players=[], # Simplified for test
            emerging_competitors=[],
            disruptive_forces=[]
        )
        self.mock_market_trends = MarketTrends(
            overview="Focus on ethical AI.",
            identified_trends=[], # Simplified
            macroeconomic_factors=[],
            regulatory_changes=[]
        )
        self.mock_technology_adoption = TechnologyAdoption(
            overview="NLP and computer vision lead.",
            current_technologies=[], # Simplified
            emerging_technologies=[],
            adoption_strategy_recommendations=[]
        )
        self.mock_strategic_insights = StrategicInsights(
            overall_insights="Healthcare AI needs robust data governance.",
            actionable_recommendations=[
                StrategicRecommendation(
                    recommendation="Implement AI ethics guidelines",
                    details="Ensure responsible AI deployment.",
                    action_items=["Draft policy", "Train staff"],
                    target_audience="Legal"
                )
            ],
            customer_specific_actions=["Recommend a pilot program to Hospital A."]
        )

    @patch('src.services.report_generation.datetime')
    async def test_generate_report_returns_market_research_report(self, mock_datetime: MagicMock) -> None:
        """
        Test that generate_report correctly assembles a MarketResearchReport object.
        """
        # Mock datetime for consistent generated_at timestamp
        mock_datetime.now.return_value = datetime(2023, 10, 27, 10, 0, 0)
        mock_datetime.now.return_value.isoformat.return_value = "2023-10-27T10:00:00.000000"


        report = await self.report_generation_service.generate_report(
            self.mock_request,
            self.mock_executive_summary, # Pass the pre-generated ES
            self.mock_industry_analysis,
            self.mock_market_trends,
            self.mock_technology_adoption,
            self.mock_strategic_insights
        )

        self.assertIsInstance(report, MarketResearchReport)
        self.assertEqual(report.request_details, self.mock_request)
        self.assertEqual(report.executive_summary, self.mock_executive_summary) # Assert it's the passed ES
        self.assertEqual(report.industry_analysis, self.mock_industry_analysis)
        self.assertEqual(report.market_trends, self.mock_market_trends)
        self.assertEqual(report.technology_adoption, self.mock_technology_adoption)
        self.assertEqual(report.strategic_recommendations, self.mock_strategic_insights)
        self.assertEqual(report.generated_at, "2023-10-27T10:00:00.000000")
        self.assertIn("This report is generated by an AI framework", report.disclaimer)

    async def test_executive_summary_content_in_generated_report(self) -> None:
        """
        Test that the generated report uses the correctly passed executive summary.
        """
        report = await self.report_generation_service.generate_report(
            self.mock_request,
            self.mock_executive_summary, # Pass the pre-generated ES
            self.mock_industry_analysis,
            self.mock_market_trends,
            self.mock_technology_adoption,
            self.mock_strategic_insights
        )
        self.assertEqual(report.executive_summary.summary, self.mock_executive_summary.summary)
        self.assertEqual(report.executive_summary.key_findings, self.mock_executive_summary.key_findings)

if __name__ == '__main__':
    unittest.main()

```

### Security Improvements
1.  **Critical: `eval()` replaced with `json.loads()`**: This is the most significant security improvement. By switching to `json.loads()`, the risk of Remote Code Execution (RCE) from malicious LLM outputs or prompt injection is eliminated. `json.loads()` is designed to safely parse JSON strings and will raise an error for invalid JSON or executable code.
    *   **File:** `src/services/llm_orchestrator.py`
    *   **Before:** `return eval(text_response)`
    *   **After:** `return json.loads(text_response)` (with `import json`)
2.  **Explicit Comment for Prompt Injection Mitigation**: Added a prominent comment in `LLMOrchestrator._call_llm_api` to highlight the importance of robust input validation and sanitization for user-controlled inputs before they are used in LLM prompts. This is a critical reminder for a production-grade system.
3.  **Secure Secrets Management Placeholder**: Added a placeholder for loading LLM API keys from environment variables (`os.getenv`), emphasizing that hardcoding or insecure storage of credentials is a vulnerability. In a real deployment, a dedicated secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager) would be used.
4.  **Enhanced JSON Parsing Error Handling**: The `generate_json` method now explicitly catches `json.JSONDecodeError`, providing more specific logging and a structured error response if the LLM returns malformed JSON, improving robustness against unexpected outputs.

### Performance Optimizations
1.  **Asynchronous Programming (`async`/`await`)**:
    *   **Impact:** This is the primary performance optimization. By making I/O-bound operations (LLM calls, simulated data access) non-blocking, the application can handle multiple requests concurrently without waiting for slow external operations to complete. This significantly improves throughput and responsiveness.
    *   **Implementation:**
        *   All methods that perform simulated I/O (e.g., `_call_llm_api`, `ingest_data`, `process_data`, `update_knowledge_base`, `query_knowledge_base`, `retrieve_context_for_rag`) are now `async def`.
        *   All calls to these `async` methods are now prefixed with `await`.
        *   `time.sleep()` calls, which are blocking, have been replaced with `await asyncio.sleep()`.
        *   The `main.py` entry point now uses `asyncio.run()` to execute the asynchronous workflow.
2.  **Parallel Execution of Analysis Services**:
    *   **Impact:** The `APIGateway.process_research_request` now uses `asyncio.gather()` to concurrently execute the `IndustryCompetitiveAnalysisService`, `MarketTrendsPredictionService`, and `TechnologyAdoptionAnalysisService`. Since these services are largely independent in their initial data gathering and LLM analysis, running them in parallel reduces the overall report generation time, leveraging the asynchronous nature of the system.
    *   **Implementation:** `await asyncio.gather(industry_analysis_task, market_trends_task, technology_adoption_task)`
3.  **LLM Response Caching (Simulated)**:
    *   **Impact:** Introduced a basic in-memory cache in `LLMOrchestrator` to store LLM responses. For repetitive prompts, this can drastically reduce latency and LLM API costs by serving cached results instead of making new API calls.
    *   **Implementation:** A `_cache` dictionary is used, with prompt hashing for lookup. For production, `Redis` would be integrated.
4.  **Placeholder for Database Optimizations**: Comments in `KnowledgeStoreService` explicitly mention the need to replace the in-memory list with a proper database (e.g., PostgreSQL, Neo4j, Vector Database) and implement indexing for `O(log N)` or better query performance, which is crucial for handling large data volumes efficiently.

### Quality Enhancements
1.  **Corrected Executive Summary Generation Flow**:
    *   **Impact:** The `StrategicInsightsService` is now the sole owner of the `generate_executive_summary` method, aligning with the Single Responsibility Principle. The `APIGateway` orchestrates the call to this service and then passes the *actual* generated `ExecutiveSummary` object to the `ReportGenerationService`. This removes the redundant mock `ExecutiveSummary` creation within `ReportGenerationService`, making the data flow clearer and more logically consistent.
    *   **Changes:**
        *   `StrategicInsightsService.generate_executive_summary` now directly generates and returns `ExecutiveSummary`.
        *   `ReportGenerationService.__init__` no longer requires `llm_orchestrator` as a dependency.
        *   `ReportGenerationService.generate_report` now accepts `executive_summary: ExecutiveSummary` as an argument.
        *   `APIGateway.process_research_request` now explicitly calls `self.strategic_insights_service.generate_executive_summary` and passes its result to `self.report_generation_service.generate_report`.
2.  **Enhanced Error Logging for LLM Parsing**: The `LLMOrchestrator.generate_json` method now logs the raw LLM response upon `json.JSONDecodeError`, which is invaluable for debugging issues where LLMs fail to return correctly formatted JSON.
3.  **Refined Mocking Patterns**: While still using mock data, the parsing logic for LLM-generated JSON is more robust, gracefully handling cases where the LLM might not return the *exact* expected structure (e.g., an empty list for findings). Default fallback data is provided with clear logging warnings.
4.  **`BaseAnalysisService` Updated**: The abstract `analyze` method is now `async def`, ensuring all concrete analysis services adhere to the asynchronous pattern.
5.  **Test Suite Modernization**:
    *   All relevant test classes (e.g., `TestDataIngestionService`, `TestLLMOrchestrator`, `TestStrategicInsightsService`, `TestReportGenerationService`) now inherit from `unittest.IsolatedAsyncioTestCase` to correctly run asynchronous tests.
    *   `unittest.mock.MagicMock` instances used for mocking `async` methods are now explicitly `unittest.mock.AsyncMock`.
    *   Assertions like `assert_awaited_once_with` are used for `AsyncMock` instances.

### Updated Tests

The provided test files (`tests/test_data_ingestion.py`, `tests/test_llm_orchestrator.py`, `tests/test_strategic_insights.py`, `tests/test_report_generation.py`) have been updated to support asynchronous testing and reflect the changes in the core services.

### Migration Guide

This refactoring introduces **breaking changes** due to the adoption of asynchronous programming (`async`/`await`) and changes in service interfaces (specifically `ReportGenerationService`).

**Steps to Migrate from Old to New Implementation:**

1.  **Update Dependencies:**
    *   Add `python-dotenv` to your `requirements.txt` if you plan to use local `.env` files for secrets (recommended for development).
    *   Consider `httpx` if you plan to move from mocked LLM calls to real asynchronous HTTP requests.
    *   Ensure `pydantic` version is compatible (tested with `2.5.2`).
    *   Update `requirements.txt` based on the provided one in the refactored code.
    *   Run `pip install -r requirements.txt`.

2.  **Code Changes for Asynchronous Execution:**
    *   **Top-level Execution:** In your application's entry point (`main.py` or equivalent), wrap the call to `ReportGeneratorFramework.generate_report` (and any other `async` methods) with `asyncio.run()`.
        ```python
        # Old:
        # report = framework.generate_report(example_request_data)
        # New:
        # report = asyncio.run(framework.generate_report(example_request_data))
        ```
    *   **Cascading `async`/`await`:** Any function that calls an `async` function must itself be `async def` and must `await` the result of the `async` call. You will need to propagate `async def` and `await` up your call stack for any path that eventually hits an I/O operation.
        *   Review `src/main.py`, `src/api_gateway.py`, and all files in `src/services/`.
        *   Methods like `process_research_request`, `ingest_data`, `process_data`, `update_knowledge_base`, `query_knowledge_base`, `_call_llm_api`, `generate_text`, `generate_json`, `summarize`, `extract_info`, `retrieve_context_for_rag`, `analyze` (in analysis services), `generate_insights`, `generate_executive_summary`, and `generate_report` are now `async def`.
        *   All calls to these methods within the framework must use `await`.
    *   **Parallel Execution:** If you were previously calling analysis services sequentially, adopt `asyncio.gather()` as demonstrated in `api_gateway.py` for concurrent execution.

3.  **`ReportGenerationService` Interface Change:**
    *   The constructor `ReportGenerationService.__init__()` no longer accepts `llm_orchestrator` as an argument.
    *   The `generate_report` method now requires an `executive_summary: ExecutiveSummary` object as its second argument (after `request`). Ensure that the `StrategicInsightsService.generate_executive_summary` method is called to produce this object before calling `ReportGenerationService.generate_report`.

4.  **Test Suite Updates:**
    *   Change unit test classes for `async` components to inherit from `unittest.IsolatedAsyncioTestCase`.
    *   Update mock objects to `unittest.mock.AsyncMock` for `async` methods.
    *   Replace `assert_called_once_with` with `assert_awaited_once_with` and similar `assert_called` variants with `assert_awaited` variants where applicable for `AsyncMock`.
    *   Ensure mock return values for `generate_json` methods are valid JSON *strings* (e.g., `'{"key": "value"}'` instead of `{'key': 'value'}`).

5.  **Security Configuration:**
    *   If using an LLM API key, set it as an environment variable (e.g., `LLM_API_KEY`) rather than hardcoding it.
    *   Be mindful of prompt injection and consider implementing input sanitization on user inputs that feed into LLM prompts.

This refactored codebase provides a more robust, secure, and performant foundation for the LLM-guided market research report generation framework.

---
*Saved by after_agent_callback on 2025-07-04 10:33:18*
