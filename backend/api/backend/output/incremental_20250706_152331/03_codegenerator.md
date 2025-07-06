# CodeGenerator Output
**Agent**: CodeGenerator
**Execution Order**: 3
**Timestamp**: 2025-07-06 15:25:33

---

## Code Implementation

The following code implements a foundational framework for an LLM-guided Gartner-style market research report generator. It adheres to the microservices and event-driven architectural principles outlined in the design, focusing on the core report generation workflow. Due to the complexity of a full distributed system, external components like actual message brokers (Kafka), data lakes (S3), and external LLM APIs are abstracted or simulated. The emphasis is on the modularity, clear interfaces, and logical flow between the conceptual services.

### Project Structure

```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── core/
│       ├── __init__.py
│       ├── interfaces.py         # Defines abstract interfaces for services
│       ├── models.py             # Data models and DTOs
│       ├── services.py           # Core business logic services
│       └── utils.py              # Utility functions and mock data
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── core/
│       ├── __init__.py
│       └── test_services.py
├── requirements.txt
└── README.md
```

### Main Implementation

This `main.py` file orchestrates the high-level report generation workflow, simulating the interactions between different services.

```python
# src/main.py
import logging

from src.core.interfaces import (
    IDataIngestionService,
    IDataProcessingService,
    ILLMOrchestrationService,
    IMarketIntelligenceService,
    IReportGenerationService,
)
from src.core.models import ReportRequest, GartnerReport
from src.core.services import (
    MockDataIngestionService,
    MockDataProcessingService,
    ConcreteLLMOrchestrationService,
    ConcreteMarketIntelligenceService,
    ConcreteReportGenerationService,
)
from src.core.utils import get_mock_llm_response, DATA_SOURCES_MOCK

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerationFramework:
    """
    Orchestrates the end-to-end process of generating a Gartner-style market research report.

    This class simulates the high-level flow of microservices interacting to fulfill a report request.
    In a real-world scenario, these interactions would be mediated by an API Gateway and a Message Broker.
    """

    def __init__(
        self,
        data_ingestion_service: IDataIngestionService,
        data_processing_service: IDataProcessingService,
        llm_orchestration_service: ILLMOrchestrationService,
        market_intelligence_service: IMarketIntelligenceService,
        report_generation_service: IReportGenerationService,
    ) -> None:
        """
        Initializes the ReportGenerationFramework with concrete service implementations.

        Args:
            data_ingestion_service: Service responsible for ingesting raw data.
            data_processing_service: Service responsible for processing and cleaning data.
            llm_orchestration_service: Service for managing LLM interactions.
            market_intelligence_service: Service for analyzing market insights from LLM outputs.
            report_generation_service: Service for compiling the final report.
        """
        self.data_ingestion_service = data_ingestion_service
        self.data_processing_service = data_processing_service
        self.llm_orchestration_service = llm_orchestration_service
        self.market_intelligence_service = market_intelligence_service
        self.report_generation_service = report_generation_service

    def generate_report(self, request: ReportRequest) -> GartnerReport:
        """
        Generates a Gartner-style market research report based on the given request.

        Args:
            request: A ReportRequest object specifying the report parameters.

        Returns:
            A GartnerReport object containing the generated report sections.

        Raises:
            Exception: If any step in the report generation process fails.
        """
        logger.info(f"Initiating report generation for request: {request.report_id}")
        try:
            # Step 1: Data Ingestion (Simulated)
            logger.info("Step 1: Data Ingestion - Simulating raw data collection.")
            raw_data = self.data_ingestion_service.ingest_data(
                sources=request.data_sources,
                industry=request.industry,
                competitors=request.competitors
            )
            logger.info(f"Ingested {len(raw_data.data)} mock raw data entries.")

            # Step 2: Data Processing (Simulated)
            logger.info("Step 2: Data Processing - Cleaning and transforming raw data.")
            processed_data = self.data_processing_service.process_data(raw_data)
            logger.info(f"Processed {len(processed_data.data)} mock processed data entries.")

            # Step 3: LLM Orchestration & Analysis for each section
            logger.info("Step 3: LLM Orchestration - Generating insights for report sections.")
            llm_outputs = self.llm_orchestration_service.orchestrate_analysis(
                request=request,
                processed_data=processed_data
            )
            logger.info(f"Generated LLM outputs for {len(llm_outputs.sections)} report sections.")

            # Step 4: Market Intelligence Analysis
            logger.info("Step 4: Market Intelligence Analysis - Synthesizing LLM outputs into structured insights.")
            market_insights = self.market_intelligence_service.analyze_insights(
                llm_outputs=llm_outputs,
                processed_data=processed_data,
                personalization_data=request.personalization_data
            )
            logger.info("Market intelligence analysis complete.")

            # Step 5: Report Generation
            logger.info("Step 5: Report Generation - Compiling the final Gartner-style report.")
            final_report = self.report_generation_service.generate_report(
                request=request,
                market_insights=market_insights
            )
            logger.info(f"Report '{final_report.report_title}' generated successfully.")

            return final_report

        except Exception as e:
            logger.error(f"An error occurred during report generation for {request.report_id}: {e}", exc_info=True)
            raise

if __name__ == "__main__":
    # Initialize concrete service implementations
    # In a real system, these would be instantiated by a dependency injection framework
    # or retrieved from a service registry.
    data_ingestion = MockDataIngestionService()
    data_processing = MockDataProcessingService()
    
    # Pass the mock LLM function to the LLM Orchestration service
    llm_orchestration = ConcreteLLMOrchestrationService(llm_client=get_mock_llm_response)
    
    market_intelligence = ConcreteMarketIntelligenceService()
    report_generation = ConcreteReportGenerationService()

    framework = ReportGenerationFramework(
        data_ingestion_service=data_ingestion,
        data_processing_service=data_processing,
        llm_orchestration_service=llm_orchestration,
        market_intelligence_service=market_intelligence,
        report_generation_service=report_generation,
    )

    # Example Report Request
    example_request = ReportRequest(
        report_id="REP-001-AI-2024",
        industry="Artificial Intelligence",
        competitors=["OpenAI", "Google", "Anthropic"],
        market_segments=["Generative AI", "AI in Healthcare"],
        data_sources=DATA_SOURCES_MOCK,
        output_format="markdown",
        personalization_data={"customer_id": "CUST-001", "sales_region": "North America"}
    )

    try:
        generated_report = framework.generate_report(example_request)
        print("\n--- Generated Gartner-Style Market Research Report ---")
        print(f"Report ID: {generated_report.report_id}")
        print(f"Title: {generated_report.report_title}")
        print(f"Executive Summary:\n{generated_report.executive_summary.content[:200]}...\n")
        print(f"Industry Analysis:\n{generated_report.industry_analysis.content[:200]}...\n")
        print(f"Market Trends:\n{generated_report.market_trends.content[:200]}...\n")
        print(f"Technology Adoption:\n{generated_report.technology_adoption.content[:200]}...\n")
        print(f"Strategic Insights:\n{generated_report.strategic_insights.content[:200]}...\n")
        # In a real application, you would save this to a file or a database
        # For simplicity, we just print parts of it.

        # Optionally, print the full report structure (for debugging/verification)
        # print("\n--- Full Report Content (JSON representation) ---")
        # print(generated_report.model_dump_json(indent=2))

    except Exception as e:
        print(f"\nReport generation failed: {e}")

```

### Supporting Modules

#### `src/core/interfaces.py`

Defines abstract base classes (ABCs) for each core service. This promotes modularity, testability, and adherence to the Dependency Inversion Principle (part of SOLID).

```python
# src/core/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable

from src.core.models import (
    ReportRequest,
    RawData,
    ProcessedData,
    LLMOutputBundle,
    MarketInsights,
    GartnerReport,
    LLMResponse
)

# Define a type hint for the LLM client callable
LLMClientCallable = Callable[[str, Dict[str, Any]], LLMResponse]


class IDataIngestionService(ABC):
    """Abstract Base Class for data ingestion service."""

    @abstractmethod
    def ingest_data(self, sources: List[str], industry: str, competitors: List[str]) -> RawData:
        """
        Ingests raw data from various sources.

        Args:
            sources: A list of data source identifiers (e.g., "news_api", "sec_filings").
            industry: The target industry for data collection.
            competitors: A list of competitor names to focus data collection on.

        Returns:
            A RawData object containing the ingested data.
        """
        pass


class IDataProcessingService(ABC):
    """Abstract Base Class for data processing service."""

    @abstractmethod
    def process_data(self, raw_data: RawData) -> ProcessedData:
        """
        Processes and cleans raw data, performing normalization, deduplication, etc.

        Args:
            raw_data: A RawData object to be processed.

        Returns:
            A ProcessedData object containing the cleaned and transformed data.
        """
        pass


class ILLMOrchestrationService(ABC):
    """Abstract Base Class for LLM orchestration service."""

    @abstractmethod
    def orchestrate_analysis(self, request: ReportRequest, processed_data: ProcessedData) -> LLMOutputBundle:
        """
        Orchestrates LLM calls to generate insights for different report sections.

        Args:
            request: The original ReportRequest.
            processed_data: The processed data to be used as context for LLMs.

        Returns:
            An LLMOutputBundle containing outputs for each requested section.
        """
        pass


class IMarketIntelligenceService(ABC):
    """Abstract Base Class for market intelligence analysis service."""

    @abstractmethod
    def analyze_insights(
        self, llm_outputs: LLMOutputBundle, processed_data: ProcessedData, personalization_data: Dict[str, Any]
    ) -> MarketInsights:
        """
        Analyzes and synthesizes LLM outputs into structured market insights.

        Args:
            llm_outputs: The bundle of LLM outputs for various sections.
            processed_data: The processed data for additional context and validation.
            personalization_data: Customer-specific data for tailoring recommendations.

        Returns:
            A MarketInsights object containing structured insights for the report.
        """
        pass


class IReportGenerationService(ABC):
    """Abstract Base Class for report generation service."""

    @abstractmethod
    def generate_report(self, request: ReportRequest, market_insights: MarketInsights) -> GartnerReport:
        """
        Generates the final Gartner-style market research report.

        Args:
            request: The original ReportRequest.
            market_insights: The structured market insights to compile the report from.

        Returns:
            A GartnerReport object representing the complete report.
        """
        pass

```

#### `src/core/models.py`

Defines the data structures (using `pydantic` for validation and serialization) that flow between services.

```python
# src/core/models.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ReportRequest(BaseModel):
    """Represents a request for a market research report."""
    report_id: str = Field(..., description="Unique identifier for the report request.")
    industry: str = Field(..., description="The target industry for the report.")
    competitors: List[str] = Field(default_factory=list, description="List of specific competitors to analyze.")
    market_segments: List[str] = Field(default_factory=list, description="List of market segments to focus on.")
    data_sources: List[str] = Field(default_factory=list, description="List of data sources to use for analysis.")
    output_format: str = Field(default="markdown", description="Desired output format (e.g., 'pdf', 'docx', 'markdown').")
    personalization_data: Dict[str, Any] = Field(default_factory=dict, description="Customer-specific data for personalization.")

class RawDataEntry(BaseModel):
    """Represents a single entry of raw, un-processed data."""
    source: str
    timestamp: datetime = Field(default_factory=datetime.now)
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RawData(BaseModel):
    """Container for raw data ingested from various sources."""
    request_id: str
    data: List[RawDataEntry] = Field(default_factory=list)

class ProcessedDataEntry(BaseModel):
    """Represents a single entry of processed data, ready for analysis."""
    original_source: str
    processed_content: str
    entities: List[str] = Field(default_factory=list, description="Extracted key entities (companies, products, technologies).")
    topics: List[str] = Field(default_factory=list, description="Identified key topics.")
    sentiment: Optional[str] = None
    relevance_score: float = 0.0

class ProcessedData(BaseModel):
    """Container for processed and cleaned data."""
    request_id: str
    data: List[ProcessedDataEntry] = Field(default_factory=list)

class LLMResponse(BaseModel):
    """Represents a structured response from an LLM."""
    model_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    # The actual content can be a string, or a structured dict/JSON depending on prompt
    content: Any
    token_usage: Dict[str, int] = Field(default_factory=dict, description="e.g., {'prompt_tokens': 100, 'completion_tokens': 50}")
    # Any other LLM-specific metadata (e.g., safety ratings, finish reason)

class LLMOutput(BaseModel):
    """Represents the LLM's output for a specific report section."""
    section_name: str
    llm_response: LLMResponse

class LLMOutputBundle(BaseModel):
    """A bundle of LLM outputs, one for each report section."""
    report_id: str
    sections: List[LLMOutput] = Field(default_factory=list)

class ReportSectionContent(BaseModel):
    """Represents the structured content for a single report section."""
    title: str
    content: str
    key_findings: List[str] = Field(default_factory=list, description="Bullet points of key findings for this section.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations related to this section.")
    charts_and_figures: List[str] = Field(default_factory=list, description="Placeholders for chart/figure descriptions.")

class MarketInsights(BaseModel):
    """
    Structured insights derived from LLM outputs, ready for report compilation.
    This acts as the intermediary between raw LLM outputs and final report formatting.
    """
    report_id: str
    executive_summary_data: ReportSectionContent
    industry_analysis_data: ReportSectionContent
    market_trends_data: ReportSectionContent
    technology_adoption_data: ReportSectionContent
    strategic_insights_data: ReportSectionContent
    # Potentially add cross-cutting insights or overall conclusions

class GartnerReport(BaseModel):
    """Represents the final Gartner-style market research report."""
    report_id: str
    report_title: str
    generated_date: datetime = Field(default_factory=datetime.now)
    executive_summary: ReportSectionContent
    industry_analysis: ReportSectionContent
    market_trends: ReportSectionContent
    technology_adoption: ReportSectionContent
    strategic_insights: ReportSectionContent
    # Add other common report metadata like authors, confidentiality, disclaimer etc.
    # For simplicity, we keep it minimal.
```

#### `src/core/services.py`

Contains the concrete implementations of the services defined in `interfaces.py`.

```python
# src/core/services.py
import logging
from typing import Dict, Any, List
import json
from datetime import datetime

from src.core.interfaces import (
    IDataIngestionService,
    IDataProcessingService,
    ILLMOrchestrationService,
    IMarketIntelligenceService,
    IReportGenerationService,
    LLMClientCallable
)
from src.core.models import (
    ReportRequest,
    RawData,
    RawDataEntry,
    ProcessedData,
    ProcessedDataEntry,
    LLMOutputBundle,
    LLMOutput,
    MarketInsights,
    GartnerReport,
    ReportSectionContent,
    LLMResponse
)
from src.core.utils import (
    get_mock_llm_response,
    DATA_SOURCES_MOCK,
    PROMPT_TEMPLATES,
    _parse_llm_structured_output
)

logger = logging.getLogger(__name__)

class MockDataIngestionService(IDataIngestionService):
    """
    Mock implementation of IDataIngestionService.
    In a real system, this would connect to various external data sources.
    """

    def ingest_data(self, sources: List[str], industry: str, competitors: List[str]) -> RawData:
        """
        Simulates ingesting raw data.
        """
        logger.info(f"Mocking data ingestion from sources: {sources} for industry: {industry}")
        mock_data_entries: List[RawDataEntry] = []
        # Simulate diverse data based on the request
        for source_name in sources:
            if source_name in DATA_SOURCES_MOCK:
                content = f"Simulated data from {source_name} for {industry} market. " \
                          f"Mentions of {' and '.join(competitors)}."
                mock_data_entries.append(RawDataEntry(source=source_name, content=content, metadata={"mock": True}))
            else:
                logger.warning(f"Unknown mock data source: {source_name}")

        return RawData(request_id=f"mock_ingest_{datetime.now().timestamp()}", data=mock_data_entries)


class MockDataProcessingService(IDataProcessingService):
    """
    Mock implementation of IDataProcessingService.
    In a real system, this would perform complex NLP, cleaning, and transformation.
    """

    def process_data(self, raw_data: RawData) -> ProcessedData:
        """
        Simulates processing raw data into a structured format.
        """
        logger.info(f"Mocking data processing for request: {raw_data.request_id}")
        processed_entries: List[ProcessedDataEntry] = []
        for entry in raw_data.data:
            # Simulate some processing: extract entities and topics
            processed_content = f"PROCESSED: {entry.content.replace('Simulated data', 'Cleaned Data')}"
            entities = ["LLM", "AI", "Market Research"] + ([comp for comp in ["OpenAI", "Google", "Anthropic"] if comp in entry.content] if entry.content else [])
            topics = ["Innovation", "Growth", "Competition"]
            sentiment = "positive" if "growth" in entry.content.lower() else "neutral"

            processed_entries.append(
                ProcessedDataEntry(
                    original_source=entry.source,
                    processed_content=processed_content,
                    entities=list(set(entities)),  # Remove duplicates
                    topics=list(set(topics)),
                    sentiment=sentiment,
                    relevance_score=0.8
                )
            )
        return ProcessedData(request_id=raw_data.request_id, data=processed_entries)


class ConcreteLLMOrchestrationService(ILLMOrchestrationService):
    """
    Concrete implementation of ILLMOrchestrationService.
    This service manages interactions with the LLM, crafting prompts and parsing responses.
    """

    def __init__(self, llm_client: LLMClientCallable) -> None:
        """
        Initializes the LLMOrchestrationService with an LLM client callable.

        Args:
            llm_client: A callable that simulates or interfaces with an actual LLM API.
                        It should accept (prompt_template_key: str, context: Dict[str, Any])
                        and return an LLMResponse.
        """
        self.llm_client = llm_client

    def _prepare_llm_context(self, request: ReportRequest, processed_data: ProcessedData) -> Dict[str, Any]:
        """
        Prepares the context for the LLM based on the request and processed data.
        In a real scenario, this would include RAG (Retrieval Augmented Generation)
        from a vector store.
        """
        # For simplicity, concatenate processed content for context
        # In a real system, this would involve sophisticated summarization,
        # filtering relevant snippets, and potentially chunking for token limits.
        all_processed_content = "\n".join([entry.processed_content for entry in processed_data.data])
        all_entities = list(set([e for entry in processed_data.data for e in entry.entities]))
        all_topics = list(set([t for entry in processed_data.data for t in entry.topics]))

        context = {
            "industry": request.industry,
            "competitors": ", ".join(request.competitors),
            "market_segments": ", ".join(request.market_segments),
            "processed_data_summary": all_processed_content[:2000],  # Truncate for example
            "extracted_entities": ", ".join(all_entities),
            "extracted_topics": ", ".join(all_topics),
        }
        return context

    def orchestrate_analysis(self, request: ReportRequest, processed_data: ProcessedData) -> LLMOutputBundle:
        """
        Orchestrates LLM calls for each required report section.
        """
        logger.info(f"Orchestrating LLM analysis for report ID: {request.report_id}")
        llm_outputs: List[LLMOutput] = []

        report_sections_to_generate = [
            "executive_summary",
            "industry_analysis",
            "market_trends",
            "technology_adoption",
            "strategic_insights",
        ]

        llm_context = self._prepare_llm_context(request, processed_data)

        for section_name in report_sections_to_generate:
            logger.info(f"  Calling LLM for section: {section_name}")
            try:
                # The llm_client is expected to know how to use PROMPT_TEMPLATES
                llm_response = self.llm_client(section_name, llm_context)
                llm_outputs.append(LLMOutput(section_name=section_name, llm_response=llm_response))
            except Exception as e:
                logger.error(f"Error calling LLM for section '{section_name}': {e}")
                # Append a placeholder or raise a specific exception
                llm_outputs.append(LLMOutput(section_name=section_name, llm_response=LLMResponse(
                    model_id="error", content=f"Error generating this section: {e}", token_usage={}
                )))

        return LLMOutputBundle(report_id=request.report_id, sections=llm_outputs)


class ConcreteMarketIntelligenceService(IMarketIntelligenceService):
    """
    Concrete implementation of IMarketIntelligenceService.
    This service synthesizes LLM outputs and raw data into structured market insights.
    It's where the "business logic" and "correlation analysis" reside.
    """

    def analyze_insights(
        self, llm_outputs: LLMOutputBundle, processed_data: ProcessedData, personalization_data: Dict[str, Any]
    ) -> MarketInsights:
        """
        Analyzes and synthesizes LLM outputs into structured market insights.
        """
        logger.info(f"Analyzing market insights for report ID: {llm_outputs.report_id}")

        insights_data: Dict[str, ReportSectionContent] = {}

        for llm_output in llm_outputs.sections:
            section_name = llm_output.section_name
            llm_content = llm_output.llm_response.content

            try:
                # Attempt to parse structured output from LLM
                parsed_content = _parse_llm_structured_output(llm_content)

                # Simulate additional analysis based on processed_data
                # e.g., if this was Industry Analysis, cross-reference entities from processed_data
                # with LLM's competitive landscape.
                additional_findings = []
                additional_recommendations = []

                if "customer_id" in personalization_data and section_name == "strategic_insights":
                    additional_recommendations.append(
                        f"Personalized recommendation for customer {personalization_data['customer_id']} in "
                        f"{personalization_data.get('sales_region', 'your region')} based on their sales trends."
                    )
                    logger.info("  Added personalization to strategic insights.")

                insights_data[section_name] = ReportSectionContent(
                    title=parsed_content.get("title", section_name.replace("_", " ").title()),
                    content=parsed_content.get("content", "Content not parsed or generated."),
                    key_findings=list(set(parsed_content.get("key_findings", []) + additional_findings)),
                    recommendations=list(set(parsed_content.get("recommendations", []) + additional_recommendations)),
                    charts_and_figures=parsed_content.get("charts_and_figures", [])
                )
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON for section '{section_name}'. Using raw LLM output.")
                insights_data[section_name] = ReportSectionContent(
                    title=section_name.replace("_", " ").title(),
                    content=str(llm_content), # Fallback to raw content if parsing fails
                    key_findings=["Could not parse structured findings."],
                    recommendations=["Review LLM output for formatting issues."]
                )
            except Exception as e:
                logger.error(f"Error processing insights for section '{section_name}': {e}", exc_info=True)
                insights_data[section_name] = ReportSectionContent(
                    title=section_name.replace("_", " ").title(),
                    content=f"Error during insight processing: {e}",
                    key_findings=[],
                    recommendations=[]
                )

        # Ensure all required sections are present, even if empty due to error
        # This makes the final report generation robust
        required_sections = [
            "executive_summary", "industry_analysis", "market_trends",
            "technology_adoption", "strategic_insights"
        ]
        for section in required_sections:
            if section not in insights_data:
                insights_data[section] = ReportSectionContent(
                    title=section.replace("_", " ").title(),
                    content=f"No content generated or processed for {section}.",
                    key_findings=[],
                    recommendations=[]
                )

        return MarketInsights(
            report_id=llm_outputs.report_id,
            executive_summary_data=insights_data["executive_summary"],
            industry_analysis_data=insights_data["industry_analysis"],
            market_trends_data=insights_data["market_trends"],
            technology_adoption_data=insights_data["technology_adoption"],
            strategic_insights_data=insights_data["strategic_insights"],
        )


class ConcreteReportGenerationService(IReportGenerationService):
    """
    Concrete implementation of IReportGenerationService.
    This service takes structured market insights and compiles them into the final report format.
    """

    def generate_report(self, request: ReportRequest, market_insights: MarketInsights) -> GartnerReport:
        """
        Generates the final Gartner-style market research report.
        """
        logger.info(f"Generating final report document for ID: {request.report_id}")

        report_title = f"{request.industry} Market Research Report: {datetime.now().strftime('%Y-%m-%d')}"
        if request.market_segments:
            report_title += f" - Focus on {', '.join(request.market_segments)}"

        # The actual formatting logic would go here.
        # For a "Gartner-style" report, this would involve:
        # - Using a templating engine (e.g., Jinja2) for docx/pdf generation.
        # - Integrating with libraries like python-docx or ReportLab.
        # - Ensuring consistent styling, headers, footers, table of contents.
        # - Embedding charts/figures based on `charts_and_figures` placeholders.

        # For this example, we simply populate the GartnerReport model.
        # The content of each section is already structured in ReportSectionContent.

        final_report = GartnerReport(
            report_id=request.report_id,
            report_title=report_title,
            executive_summary=market_insights.executive_summary_data,
            industry_analysis=market_insights.industry_analysis_data,
            market_trends=market_insights.market_trends_data,
            technology_adoption=market_insights.technology_adoption_data,
            strategic_insights=market_insights.strategic_insights_data,
        )

        logger.info(f"Final report generated successfully: {final_report.report_title}")
        return final_report

```

#### `src/core/utils.py`

Provides utility functions, mock data, and LLM prompt templates.

```python
# src/core/utils.py
import json
import logging
from typing import Dict, Any, Callable
from src.core.models import LLMResponse

logger = logging.getLogger(__name__)

# --- Mock Data and Configurations ---

DATA_SOURCES_MOCK = [
    "industry_news_feed",
    "company_press_releases",
    "sec_filings_mock",
    "market_research_database_mock",
    "social_media_sentiment_mock",
]

# --- LLM Prompt Templates ---
# These templates guide the LLM to produce specific output for each section.
# They are designed to elicit JSON-formatted responses for easier parsing.
PROMPT_TEMPLATES: Dict[str, str] = {
    "executive_summary": """
Generate a concise executive summary for a market research report on the {industry} market, focusing on {market_segments} and considering key players like {competitors}.
Summarize the current state, key trends, and a single overarching strategic recommendation.
Provide the output as a JSON object with the following keys:
- "title": "Executive Summary"
- "content": "Comprehensive summary of key findings..."
- "key_findings": ["Finding 1", "Finding 2"]
- "recommendations": ["Overall Recommendation"]
""",
    "industry_analysis": """
Perform an industry analysis and competitive landscape mapping for the {industry} market, specifically for {market_segments}.
Detail the market size, growth drivers, and competitive dynamics among players like {competitors}.
Identify key players, their market shares (simulated if not real), and competitive advantages.
Provide the output as a JSON object with the following keys:
- "title": "Industry Analysis and Competitive Landscape"
- "content": "Detailed analysis of the industry structure..."
- "key_findings": ["Market size is X", "Competitive landscape is Y"]
- "charts_and_figures": ["Market Share Distribution Chart", "SWOT Analysis of Key Players"]
""",
    "market_trends": """
Identify and predict future market trends in the {industry} sector, with a focus on {market_segments}.
Consider emerging technologies, changing consumer behavior, and regulatory impacts.
Project short-term (1-3 years) and long-term (5+ years) trends.
Provide the output as a JSON object with the following keys:
- "title": "Market Trends and Future Predictions"
- "content": "Analysis of current and future market trends..."
- "key_findings": ["Trend 1: Description", "Trend 2: Description"]
- "recommendations": ["Recommendation related to Trend 1"]
- "charts_and_figures": ["Trend Adoption Curve", "Market Growth Projection"]
""",
    "technology_adoption": """
Analyze technology adoption within the {industry} market, particularly in {market_segments}.
Assess the maturity of key technologies (e.g., AI, IoT, Cloud) and their impact.
Provide recommendations for technology investment and implementation for businesses in this sector.
Consider the processed data summary: {processed_data_summary}.
Focus on entities like {extracted_entities} and topics like {extracted_topics}.
Provide the output as a JSON object with the following keys:
- "title": "Technology Adoption Analysis and Recommendations"
- "content": "Assessment of technology maturity and impact..."
- "key_findings": ["Technology X is mature", "Technology Y is emerging"]
- "recommendations": ["Invest in Technology X", "Pilot Technology Y"]
""",
    "strategic_insights": """
Derive strategic insights and actionable recommendations for stakeholders in the {industry} market, covering {market_segments}.
Synthesize findings from industry analysis, market trends, and technology adoption.
Suggest specific strategies for growth, competitive advantage, and risk mitigation.
Considering processed data summarized as: {processed_data_summary}.
Provide the output as a JSON object with the following keys:
- "title": "Strategic Insights and Actionable Recommendations"
- "content": "Key strategic takeaways and actionable advice..."
- "key_findings": ["Insight 1", "Insight 2"]
- "recommendations": ["Action Item 1", "Action Item 2"]
""",
}

# --- Mock LLM Client ---

def get_mock_llm_response(prompt_template_key: str, context: Dict[str, Any]) -> LLMResponse:
    """
    Simulates an LLM API call, returning a structured mock response.
    In a real application, this would use an actual LLM SDK (e.g., Google Generative AI, OpenAI).

    Args:
        prompt_template_key: The key for the prompt template to use from PROMPT_TEMPLATES.
        context: A dictionary of variables to fill into the prompt template.

    Returns:
        An LLMResponse object containing the simulated LLM output.
    """
    logger.info(f"Mock LLM: Processing request for {prompt_template_key} with context: {list(context.keys())}")
    prompt = PROMPT_TEMPLATES.get(prompt_template_key)

    if not prompt:
        raise ValueError(f"No prompt template found for key: {prompt_template_key}")

    # Fill the prompt template with context variables
    try:
        # Create a safe context for string formatting, filling missing keys with empty string
        formatted_context = {k: v if v is not None else "" for k, v in context.items()}
        filled_prompt = prompt.format(**formatted_context)
    except KeyError as e:
        logger.error(f"Missing key in context for prompt template '{prompt_template_key}': {e}")
        # Provide a fallback or raise a more specific error
        filled_prompt = prompt # Use unformatted prompt if keys are missing

    # Simulate LLM processing and generate a mock response
    # For a real LLM, you'd send 'filled_prompt' to the API
    mock_content = {
        "title": f"Mock {prompt_template_key.replace('_', ' ').title()}",
        "content": f"This is a simulated detailed analysis for the {context.get('industry', 'specified')} market regarding {prompt_template_key.replace('_', ' ')}. "
                   f"Relevant entities: {context.get('extracted_entities', 'N/A')}. "
                   f"Topics discussed: {context.get('extracted_topics', 'N/A')}. "
                   f"Data summary snippet: {context.get('processed_data_summary', 'N/A')[:50]}...",
        "key_findings": [f"Simulated finding 1 for {prompt_template_key}", f"Simulated finding 2 for {prompt_template_key}"],
        "recommendations": [f"Simulated recommendation for {prompt_template_key}"],
        "charts_and_figures": [f"Placeholder Chart for {prompt_template_key}"]
    }
    # For the executive summary, ensure single overall recommendation
    if prompt_template_key == "executive_summary" and mock_content["recommendations"]:
        mock_content["recommendations"] = [mock_content["recommendations"][0]]


    return LLMResponse(
        model_id="mock-llm-v1.0",
        content=json.dumps(mock_content, indent=2), # Simulate JSON output from LLM
        token_usage={"prompt_tokens": len(filled_prompt) // 4, "completion_tokens": len(json.dumps(mock_content)) // 4}
    )

def _parse_llm_structured_output(llm_raw_content: Any) -> Dict[str, Any]:
    """
    Helper function to parse LLM's raw content, expecting JSON.
    """
    if isinstance(llm_raw_content, str):
        try:
            # LLMs might embed JSON within markdown backticks or other text.
            # A more robust parser would use regex to extract the JSON block.
            # For simplicity, assuming the whole string is JSON here.
            return json.loads(llm_raw_content)
        except json.JSONDecodeError:
            logger.warning("LLM raw content is not valid JSON. Attempting to return as is.")
            return {"content": llm_raw_content}
    return llm_raw_content

```

### Unit Tests

#### `tests/test_main.py`

Tests the overall orchestration flow of the `ReportGenerationFramework`.

```python
# tests/test_main.py
import unittest
from unittest.mock import MagicMock, patch
from src.main import ReportGenerationFramework
from src.core.models import ReportRequest, RawData, ProcessedData, LLMOutputBundle, MarketInsights, GartnerReport
from src.core.services import (
    MockDataIngestionService,
    MockDataProcessingService,
    ConcreteLLMOrchestrationService,
    ConcreteMarketIntelligenceService,
    ConcreteReportGenerationService
)
from src.core.utils import get_mock_llm_response, DATA_SOURCES_MOCK

class TestReportGenerationFramework(unittest.TestCase):

    def setUp(self) -> None:
        # Initialize mock services. We can mock their methods if needed for specific test cases.
        self.mock_ingestion_service = MagicMock(spec=MockDataIngestionService)
        self.mock_processing_service = MagicMock(spec=MockDataProcessingService)
        self.mock_llm_orchestration_service = MagicMock(spec=ConcreteLLMOrchestrationService)
        self.mock_market_intelligence_service = MagicMock(spec=ConcreteMarketIntelligenceService)
        self.mock_report_generation_service = MagicMock(spec=ConcreteReportGenerationService)

        self.framework = ReportGenerationFramework(
            data_ingestion_service=self.mock_ingestion_service,
            data_processing_service=self.mock_processing_service,
            llm_orchestration_service=self.mock_llm_orchestration_service,
            market_intelligence_service=self.mock_market_intelligence_service,
            report_generation_service=self.mock_report_generation_service,
        )

        self.example_request = ReportRequest(
            report_id="TEST-001",
            industry="Test Industry",
            competitors=["CompA"],
            market_segments=["SegmentX"],
            data_sources=DATA_SOURCES_MOCK,
            output_format="markdown",
            personalization_data={}
        )

        # Define return values for mocked services
        self.mock_ingestion_service.ingest_data.return_value = RawData(request_id="test", data=[])
        self.mock_processing_service.process_data.return_value = ProcessedData(request_id="test", data=[])
        self.mock_llm_orchestration_service.orchestrate_analysis.return_value = LLMOutputBundle(report_id="test", sections=[])
        self.mock_market_intelligence_service.analyze_insights.return_value = MarketInsights(
            report_id="test",
            executive_summary_data=MagicMock(),
            industry_analysis_data=MagicMock(),
            market_trends_data=MagicMock(),
            technology_adoption_data=MagicMock(),
            strategic_insights_data=MagicMock(),
        )
        self.mock_report_generation_service.generate_report.return_value = GartnerReport(
            report_id="test",
            report_title="Test Report",
            executive_summary=MagicMock(),
            industry_analysis=MagicMock(),
            market_trends=MagicMock(),
            technology_adoption=MagicMock(),
            strategic_insights=MagicMock(),
        )

    def test_generate_report_success(self) -> None:
        """
        Test successful end-to-end report generation.
        """
        report = self.framework.generate_report(self.example_request)

        # Assert that each service method was called once with the correct arguments
        self.mock_ingestion_service.ingest_data.assert_called_once_with(
            sources=self.example_request.data_sources,
            industry=self.example_request.industry,
            competitors=self.example_request.competitors
        )
        self.mock_processing_service.process_data.assert_called_once() # Argument is the RawData returned by ingestion
        self.mock_llm_orchestration_service.orchestrate_analysis.assert_called_once() # Arguments are request and processed_data
        self.mock_market_intelligence_service.analyze_insights.assert_called_once() # Arguments are llm_outputs, processed_data, personalization_data
        self.mock_report_generation_service.generate_report.assert_called_once() # Arguments are request, market_insights

        self.assertIsInstance(report, GartnerReport)
        self.assertEqual(report.report_id, "test") # Based on the mock return value

    def test_generate_report_ingestion_failure(self) -> None:
        """
        Test report generation failure due to data ingestion error.
        """
        self.mock_ingestion_service.ingest_data.side_effect = Exception("Ingestion failed")

        with self.assertRaisesRegex(Exception, "Ingestion failed"):
            self.framework.generate_report(self.example_request)

        self.mock_ingestion_service.ingest_data.assert_called_once()
        self.mock_processing_service.process_data.assert_not_called() # Should not proceed past ingestion

    def test_generate_report_llm_orchestration_failure(self) -> None:
        """
        Test report generation failure due to LLM orchestration error.
        """
        self.mock_llm_orchestration_service.orchestrate_analysis.side_effect = Exception("LLM call error")

        with self.assertRaisesRegex(Exception, "LLM call error"):
            self.framework.generate_report(self.example_request)

        self.mock_ingestion_service.ingest_data.assert_called_once()
        self.mock_processing_service.process_data.assert_called_once()
        self.mock_llm_orchestration_service.orchestrate_analysis.assert_called_once()
        self.mock_market_intelligence_service.analyze_insights.assert_not_called() # Should not proceed

```

#### `tests/core/test_services.py`

Tests individual core services for their specific logic.

```python
# tests/core/test_services.py
import unittest
from unittest.mock import MagicMock, patch
import json

from src.core.services import (
    MockDataIngestionService,
    MockDataProcessingService,
    ConcreteLLMOrchestrationService,
    ConcreteMarketIntelligenceService,
    ConcreteReportGenerationService
)
from src.core.models import (
    ReportRequest, RawData, RawDataEntry,
    ProcessedData, ProcessedDataEntry,
    LLMOutputBundle, LLMOutput, LLMResponse,
    MarketInsights, GartnerReport, ReportSectionContent
)
from src.core.utils import DATA_SOURCES_MOCK, PROMPT_TEMPLATES, get_mock_llm_response

class TestCoreServices(unittest.TestCase):

    def test_mock_data_ingestion_service(self) -> None:
        """
        Test MockDataIngestionService.
        """
        service = MockDataIngestionService()
        request_id = "test_ingestion"
        industry = "Tech"
        competitors = ["Apple", "Microsoft"]
        sources = ["industry_news_feed", "company_press_releases"]

        raw_data = service.ingest_data(sources=sources, industry=industry, competitors=competitors)

        self.assertIsInstance(raw_data, RawData)
        self.assertGreater(len(raw_data.data), 0)
        self.assertEqual(len(raw_data.data), len(sources))
        self.assertIn("Simulated data from industry_news_feed for Tech market.", raw_data.data[0].content)

    def test_mock_data_processing_service(self) -> None:
        """
        Test MockDataProcessingService.
        """
        service = MockDataProcessingService()
        raw_data = RawData(
            request_id="test_processing",
            data=[
                RawDataEntry(source="test", content="Simulated data on AI and machine learning for healthcare."),
                RawDataEntry(source="test", content="Another simulated data entry with mentions of Google.")
            ]
        )

        processed_data = service.process_data(raw_data)

        self.assertIsInstance(processed_data, ProcessedData)
        self.assertEqual(len(processed_data.data), 2)
        self.assertIn("Cleaned Data on AI", processed_data.data[0].processed_content)
        self.assertIn("AI", processed_data.data[0].entities)
        self.assertIn("Google", processed_data.data[1].entities)


    def test_concrete_llm_orchestration_service(self) -> None:
        """
        Test ConcreteLLMOrchestrationService with mock LLM client.
        """
        # Use the actual mock LLM client from utils
        service = ConcreteLLMOrchestrationService(llm_client=get_mock_llm_response)

        request = ReportRequest(
            report_id="llm_test",
            industry="Energy",
            competitors=["CompX"],
            market_segments=["Solar"],
            data_sources=[],
            output_format="markdown"
        )
        processed_data = ProcessedData(
            request_id="llm_test",
            data=[ProcessedDataEntry(original_source="mock", processed_content="Solar energy is growing.", entities=["Solar"], topics=["Growth"])]
        )

        llm_output_bundle = service.orchestrate_analysis(request, processed_data)

        self.assertIsInstance(llm_output_bundle, LLMOutputBundle)
        self.assertEqual(llm_output_bundle.report_id, "llm_test")
        self.assertEqual(len(llm_output_bundle.sections), 5) # Expecting 5 sections based on implementation
        
        # Verify one of the sections has valid LLM response structure
        exec_summary_output = next((s for s in llm_output_bundle.sections if s.section_name == "executive_summary"), None)
        self.assertIsNotNone(exec_summary_output)
        self.assertIsInstance(exec_summary_output.llm_response, LLMResponse)
        self.assertIn("mock-llm-v1.0", exec_summary_output.llm_response.model_id)
        self.assertIsInstance(exec_summary_output.llm_response.content, str) # Mock returns JSON string

        # Check if the content is parsable JSON and contains expected keys
        parsed_content = json.loads(exec_summary_output.llm_response.content)
        self.assertIn("title", parsed_content)
        self.assertIn("content", parsed_content)
        self.assertIn("key_findings", parsed_content)


    def test_concrete_market_intelligence_service(self) -> None:
        """
        Test ConcreteMarketIntelligenceService with mock LLM outputs.
        """
        service = ConcreteMarketIntelligenceService()

        # Create a mock LLM output bundle that mimics what the LLM would return
        mock_llm_output_bundle = LLMOutputBundle(
            report_id="mi_test",
            sections=[
                LLMOutput(
                    section_name="executive_summary",
                    llm_response=LLMResponse(
                        model_id="mock",
                        content=json.dumps({
                            "title": "Exec Sum",
                            "content": "Overall summary.",
                            "key_findings": ["Exec Finding 1"],
                            "recommendations": ["Exec Rec 1"]
                        })
                    )
                ),
                LLMOutput(
                    section_name="industry_analysis",
                    llm_response=LLMResponse(
                        model_id="mock",
                        content=json.dumps({
                            "title": "Industry",
                            "content": "Industry data.",
                            "key_findings": ["Industry Finding 1"],
                            "charts_and_figures": ["Chart A"]
                        })
                    )
                ),
                LLMOutput( # Test personalization data integration
                    section_name="strategic_insights",
                    llm_response=LLMResponse(
                        model_id="mock",
                        content=json.dumps({
                            "title": "Strategic Insights",
                            "content": "Core strategy.",
                            "key_findings": ["Strat Insight 1"],
                            "recommendations": ["General Strat Rec"]
                        })
                    )
                )
            ]
        )
        processed_data = ProcessedData(request_id="mi_test", data=[])
        personalization_data = {"customer_id": "CUST-XYZ", "sales_region": "EU"}

        market_insights = service.analyze_insights(
            llm_outputs=mock_llm_output_bundle,
            processed_data=processed_data,
            personalization_data=personalization_data
        )

        self.assertIsInstance(market_insights, MarketInsights)
        self.assertEqual(market_insights.report_id, "mi_test")

        self.assertEqual(market_insights.executive_summary_data.title, "Exec Sum")
        self.assertIn("Exec Finding 1", market_insights.executive_summary_data.key_findings)

        self.assertEqual(market_insights.industry_analysis_data.title, "Industry")
        self.assertIn("Chart A", market_insights.industry_analysis_data.charts_and_figures)

        # Check for personalization
        self.assertIn(
            "Personalized recommendation for customer CUST-XYZ in EU based on their sales trends.",
            market_insights.strategic_insights_data.recommendations
        )
        self.assertIn("General Strat Rec", market_insights.strategic_insights_data.recommendations)

        # Ensure other sections, even if not in mock_llm_output_bundle, are present with default content
        self.assertIn("No content generated", market_insights.market_trends_data.content)
        self.assertIn("No content generated", market_insights.technology_adoption_data.content)


    def test_concrete_report_generation_service(self) -> None:
        """
        Test ConcreteReportGenerationService.
        """
        service = ConcreteReportGenerationService()
        request = ReportRequest(
            report_id="report_gen_test",
            industry="Automotive",
            market_segments=["EVs"],
            data_sources=[],
            output_format="pdf"
        )
        market_insights = MarketInsights(
            report_id="report_gen_test",
            executive_summary_data=ReportSectionContent(title="Summary", content="Key points.", key_findings=["K1"], recommendations=["R1"]),
            industry_analysis_data=ReportSectionContent(title="Industry", content="Industry details.", key_findings=["K2"]),
            market_trends_data=ReportSectionContent(title="Trends", content="Trend analysis.", recommendations=["R2"]),
            technology_adoption_data=ReportSectionContent(title="Tech", content="Tech analysis."),
            strategic_insights_data=ReportSectionContent(title="Strategy", content="Strategic recommendations.", recommendations=["R3"]),
        )

        final_report = service.generate_report(request, market_insights)

        self.assertIsInstance(final_report, GartnerReport)
        self.assertEqual(final_report.report_id, "report_gen_test")
        self.assertIn("Automotive Market Research Report", final_report.report_title)
        self.assertIn("EVs", final_report.report_title)

        self.assertEqual(final_report.executive_summary.title, "Summary")
        self.assertEqual(final_report.industry_analysis.content, "Industry details.")
        self.assertEqual(final_report.market_trends.recommendations, ["R2"])
```

### Installation and Usage Instructions

1.  **Clone the Repository (Simulated):**
    ```bash
    # In a real scenario, you would clone a Git repository.
    # For this example, manually create the project structure and files.
    mkdir -p project/src/core project/tests/core
    cd project
    ```

2.  **Create a Virtual Environment:**
    It's highly recommended to use a Python virtual environment to manage dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    Create a `requirements.txt` file in the `project/` directory:

    ```
    # requirements.txt
    pydantic==2.x.x # Use the latest stable Pydantic v2
    # Other potential future dependencies:
    # langchain
    # openai
    # google-generativeai
    # python-docx
    # reportlab
    # apache-kafka-python
    # boto3 (for S3)
    ```

    Then install:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Framework:**
    Navigate to the `project` directory and execute `main.py`:
    ```bash
    python src/main.py
    ```
    This will trigger the simulated report generation process and print a summary of the generated report to the console.

5.  **Run Tests:**
    Navigate to the `project` directory and run tests using `unittest`:
    ```bash
    python -m unittest discover tests
    ```

**Documentation Generation (Future Implementation):**

For comprehensive documentation (as per requirements for Sphinx and Read the Docs):

1.  **Install Sphinx:**
    ```bash
    pip install sphinx sphinx_rtd_theme
    ```
2.  **Initialize Sphinx:**
    In the `project` directory:
    ```bash
    sphinx-quickstart
    ```
    Follow the prompts (e.g., enable `autodoc`, `napoleon` for Google style docstrings).
3.  **Configure `conf.py`:**
    Edit `docs/conf.py` to point to your `src` directory and enable necessary extensions (`sphinx.ext.autodoc`, `sphinx.ext.napoleon`, `sphinx.ext.viewcode`).
    ```python
    import os
    import sys
    sys.path.insert(0, os.path.abspath('../src'))
    ```
4.  **Create RST Files:**
    Create `.rst` files (e.g., `modules.rst`, `index.rst`) in your `docs` directory, using `automodule` directives to pull docstrings from your Python code.
5.  **Build Documentation:**
    ```bash
    cd docs
    make html
    ```
    The generated HTML documentation will be in `_build/html`.

**Further Development Notes:**

*   **Real LLM Integration:** Replace `get_mock_llm_response` with actual API calls to OpenAI, Google Gemini, Anthropic, or self-hosted LLMs using their respective SDKs (e.g., `google-generativeai`, `openai`).
*   **Data Lake/Message Broker:** Implement actual integration with Kafka, AWS S3, etc., replacing the mock services with clients for these systems.
*   **Structured Output Parsing:** The `_parse_llm_structured_output` function is basic. A more robust solution would involve regex to extract JSON from larger LLM text, or using tools like Pydantic's `parse_raw` if LLM directly outputs valid JSON strings.
*   **Report Templating:** Integrate with libraries like `python-docx` or `ReportLab` to generate professionally formatted PDF/DOCX outputs.
*   **Continuous Monitoring & Personalization:** Develop dedicated services (as outlined in the architecture) that feed into the existing pipeline or trigger re-runs.
*   **Error Handling & Observability:** Implement comprehensive custom exceptions, structured logging (e.g., using `loguru` or `structlog`), metrics collection (Prometheus), and distributed tracing (OpenTelemetry).
*   **Security:** Integrate proper authentication (JWT, OAuth2), authorization (RBAC), and data encryption (at rest and in transit) across all service interactions and data storage.

---
*Saved by after_agent_callback on 2025-07-06 15:25:33*
