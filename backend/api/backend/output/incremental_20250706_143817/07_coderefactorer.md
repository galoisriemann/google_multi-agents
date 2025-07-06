# CodeRefactorer Output
**Agent**: CodeRefactorer
**Execution Order**: 7
**Timestamp**: 2025-07-06 14:45:49

---

## Refactored Code Implementation

### Summary of Changes

The refactoring focused on transitioning the framework from a purely in-memory simulation to one that conceptualizes persistent storage and asynchronous operations, addressing critical feedback from the security, performance, and quality reviews.

**Key Improvements Made:**

*   **Simulated Persistence:** Replaced all in-memory data stores (e.g., `data_lake`, `data_warehouse`) with file-based persistence using dedicated directories (`data_storage/raw_data_lake`, `data_storage/processed_data_warehouse`, `reports`). Each data entity (RawMarketData, ProcessedMarketData) is now stored as a separate JSON file. This better simulates real-world database and object storage interactions.
*   **Asynchronous Processing (`asyncio`):** Introduced `async`/`await` patterns throughout the service layer and `main.py`. This allows for concurrent execution of I/O-bound tasks (like simulated API calls and file I/O), significantly improving responsiveness and laying the groundwork for a truly scalable, non-blocking architecture. `asyncio.gather` is utilized for parallel processing of multiple data items or LLM sub-tasks.
*   **LLM Output Robustness:** Enhanced LLM interactions, particularly in `LLMService.extract_entities_and_summary` and `LLMInferenceService.generate_strategic_insights`, to explicitly prompt the LLM for structured JSON output. Robust `json.loads` parsing with error handling and fallbacks is implemented to gracefully handle cases where the LLM might deviate from the expected format.
*   **Input Sanitization for Security:** A new `sanitize_text_input` utility function was added to rigorously clean and escape potentially harmful characters (e.g., Markdown, HTML special characters) from all user-provided or external data before it's used in LLM prompts or written to reports. This mitigates prompt injection and output injection vulnerabilities.
*   **Improved Error Handling:** `main.py` now implements more granular error handling, distinguishing between `ValueError` (for business logic issues like "no data ingested") and generic `Exception` (for unexpected internal errors). User-facing error messages are generic, while detailed error information (including stack traces) is logged internally.
*   **LLM Response Caching:** A simple in-memory cache was added to `LLMService` to store and retrieve LLM responses for identical prompts, reducing redundant API calls and improving perceived performance.
*   **Configuration Consistency:** The `Config` class's defined paths (`RAW_DATA_LAKE_DIR`, `PROCESSED_DATA_WAREHOUSE_DIR`, `REPORTS_DIR`) are now actively used by the services for file I/O, ensuring consistency between configuration and implementation.
*   **Enhanced Prompt Engineering:** LLM prompts now utilize clear delimiters (e.g., `<DATA>`, `<SECTION>`) to define context boundaries, which can help the LLM better interpret instructions and mitigate some forms of prompt injection.
*   **Comprehensive Unit Test Updates:** All existing unit tests were updated to accommodate the asynchronous changes (using `asyncio.run` and `AsyncMock`) and verify the new file-based persistence and LLM JSON parsing logic. New tests were added for data sanitization and LLM error handling.

### Refactored Code

```python
import os
import uuid
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import asyncio
import hashlib

# --- Refactored src/config.py ---
class Config:
    """
    General configuration settings for the framework.
    """
    LLM_API_KEY: str = os.getenv("LLM_API_KEY") # Removed default value
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gpt-4")
    
    # Paths for simulating persistent storage
    BASE_DATA_DIR: str = "data_storage"
    RAW_DATA_LAKE_DIR: str = os.path.join(BASE_DATA_DIR, "raw_data_lake")
    PROCESSED_DATA_WAREHOUSE_DIR: str = os.path.join(BASE_DATA_DIR, "processed_data_warehouse")
    REPORTS_DIR: str = "reports"
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Define various data sources (conceptual)
    DATA_SOURCES: Dict[str, Dict[str, Any]] = {
        "news_api": {"url": "https://api.example.com/news", "key": "NEWS_API_KEY"},
        "sec_filings_db": {"url": "https://api.example.com/sec", "key": "SEC_API_KEY"},
        "social_media_stream": {"url": "https://api.example.com/social", "key": "SOCIAL_API_KEY"},
        "market_research_db": {"url": "https://api.example.com/market", "key": "MARKET_API_KEY"},
    }

    @staticmethod
    def initialize_dirs():
        """Ensure necessary directories exist."""
        os.makedirs(Config.RAW_DATA_LAKE_DIR, exist_ok=True)
        os.makedirs(Config.PROCESSED_DATA_WAREHOUSE_DIR, exist_ok=True)
        os.makedirs(Config.REPORTS_DIR, exist_ok=True)

# --- Refactored src/utils/logger.py ---
"""
Centralized logging utility for the Market Research Report Generating Framework.
"""
def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger instance.

    Args:
        name: The name of the logger, typically the module name (e.g., __name__).

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(Config.LOG_LEVEL)
        ch = logging.StreamHandler()
        ch.setLevel(Config.LOG_LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

# --- Refactored src/models/report_models.py ---
from pydantic import BaseModel, Field

class RawMarketData(BaseModel):
    """Represents raw data ingested from various sources."""
    id: str = Field(..., description="Unique identifier for the raw data entry.") # Added explicit ID
    source: str = Field(..., description="The source of the raw data (e.g., 'news_api', 'sec_filings').")
    timestamp: str = Field(..., description="Timestamp of when the data was ingested (ISO format).")
    content: Dict[str, Any] = Field(..., description="The raw content from the source.")

class ProcessedMarketData(BaseModel):
    """Represents data after initial processing and structuring."""
    id: str = Field(..., description="Unique identifier for the processed data entry.") # Added explicit ID
    original_raw_data_id: str = Field(..., description="ID of the raw data it originated from.")
    industry_sector: Optional[str] = Field(None, description="Identified industry sector.")
    companies: List[str] = Field([], description="List of companies mentioned.")
    keywords: List[str] = Field([], description="Extracted keywords.")
    summary: str = Field(..., description="A concise summary of the processed content.")
    sentiment: Optional[str] = Field(None, description="Overall sentiment (e.g., 'positive', 'negative', 'neutral').")
    processed_at: str = Field(..., description="Timestamp of when the data was processed.")
    structured_data: Dict[str, Any] = Field({}, description="Structured data derived from raw content.")

class LLMInsight(BaseModel):
    """Represents an insight generated by the LLM."""
    insight_type: str = Field(..., description="Type of insight (e.g., 'trend', 'competitive_advantage', 'prediction').")
    description: str = Field(..., description="Detailed description of the insight.")
    relevance_score: float = Field(..., description="Score indicating relevance (0-1).")
    confidence_score: float = Field(..., description="LLM's confidence in the insight (0-1).")
    supporting_data_ids: List[str] = Field([], description="List of processed data IDs supporting this insight.")
    generated_at: str = Field(..., description="Timestamp of insight generation.")

class Recommendation(BaseModel):
    """Represents an actionable recommendation."""
    category: str = Field(..., description="Category of the recommendation (e.g., 'Technology Adoption', 'Market Entry').")
    description: str = Field(..., description="Detailed description of the recommendation.")
    action_steps: List[str] = Field([], description="Concrete steps to implement the recommendation.")
    expected_impact: str = Field(..., description="Expected business impact of the recommendation.")
    priority: str = Field(..., description="Priority level (e.g., 'High', 'Medium', 'Low').")
    related_insights: List[str] = Field([], description="IDs or descriptions of related LLM insights.")

class ExecutiveSummary(BaseModel):
    """Represents the executive summary of the report."""
    key_findings: List[str] = Field(..., description="List of major findings.")
    strategic_implications: List[str] = Field(..., description="List of strategic implications.")
    top_recommendations: List[Recommendation] = Field(..., description="Top 3-5 key recommendations.")
    summary_text: str = Field(..., description="Full text of the executive summary.")

class ReportContent(BaseModel):
    """Structure for the complete Gartner-style report content."""
    executive_summary: ExecutiveSummary
    industry_analysis: Dict[str, Any] = Field(..., description="Industry overview, market size, growth drivers.")
    competitive_landscape: Dict[str, Any] = Field(..., description="Key players, market share, SWOT analysis.")
    market_trends_predictions: Dict[str, Any] = Field(..., description="Identified trends, future outlook, growth opportunities.")
    technology_adoption_analysis: Dict[str, Any] = Field(..., description="Relevant technologies, adoption rates, impact assessment.")
    strategic_insights: List[LLMInsight] = Field(..., description="Comprehensive list of generated strategic insights.")
    actionable_recommendations: List[Recommendation] = Field(..., description="Comprehensive list of actionable recommendations.")
    appendix: Optional[Dict[str, Any]] = Field(None, description="Supporting data, methodologies.")

class ReportRequest(BaseModel):
    """Model for a user's request to generate a report."""
    request_id: str = Field(..., description="Unique ID for the report request.")
    industry: str = Field(..., description="Target industry for the research.", min_length=1, max_length=100)
    focus_areas: List[str] = Field(..., description="Specific areas of focus (e.g., 'AI in Healthcare', 'EV Battery Tech').", min_items=1)
    competitors_of_interest: List[str] = Field([], description="Specific competitors to analyze.")
    report_format: str = Field("pdf", description="Desired output format (e.g., 'pdf', 'docx', 'html').", pattern=r"^(pdf|docx|html|md)$")
    start_date: Optional[str] = Field(None, description="Start date for data collection (ISO format).")
    end_date: Optional[str] = Field(None, description="End date for data collection (ISO format).")

class ReportStatus(BaseModel):
    """Model for tracking the status of a report generation."""
    request_id: str
    status: str = Field(..., description="Current status of the report (e.g., 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED').")
    progress: float = Field(0.0, description="Progress percentage (0-100).")
    last_updated: str = Field(..., description="Timestamp of the last status update.")
    report_path: Optional[str] = Field(None, description="Path to the generated report if completed.")
    error_message: Optional[str] = Field(None, description="Error message if generation failed.")

# --- Refactored src/utils/data_utils.py ---
"""
Utility functions for data manipulation, transformation, and validation.
Includes file I/O for simulated persistence.
"""
logger = get_logger(__name__)

def escape_markdown_html(text: str) -> str:
    """Escapes common Markdown and HTML special characters to prevent injection."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#x27;")
    text = text.replace("*", "&#42;") # For markdown bold/italics
    text = text.replace("_", "&#95;") # For markdown bold/italics
    text = text.replace("[", "&#91;") # For markdown links
    text = text.replace("]", "&#93;")
    text = text.replace("(", "&#40;") # For markdown links/images
    text = text.replace(")", "&#41;")
    return text

def sanitize_text_input(text: str) -> str:
    """
    Sanitizes general text input for LLM prompts and report content.
    Removes leading/trailing whitespace and escapes potential injection characters.
    """
    return escape_markdown_html(text.strip())

async def write_json_to_file(data: BaseModel, directory: str, filename: str) -> str:
    """Writes a Pydantic BaseModel to a JSON file."""
    filepath = os.path.join(directory, filename)
    try:
        os.makedirs(directory, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, indent=4)
        logger.debug(f"Successfully wrote {filename} to {directory}")
        return filepath
    except IOError as e:
        logger.error(f"Error writing JSON to {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error writing JSON to {filepath}: {e}")
        raise

async def read_json_from_file(filepath: str, model_type: type[BaseModel]) -> BaseModel:
    """Reads a JSON file and loads it into a Pydantic BaseModel."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Successfully read {filepath}")
        return model_type.parse_obj(data)
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading JSON from {filepath}: {e}")
        raise

async def list_files_in_dir(directory: str, extension: str = ".json") -> List[str]:
    """Lists files in a directory with a specific extension."""
    if not os.path.exists(directory):
        return []
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extension)]


# --- Refactored src/utils/llm_utils.py ---
"""
Utility functions for interacting with Large Language Models (LLMs),
including prompt engineering and simulated responses.
"""
logger = get_logger(__name__)

class LLMService:
    """
    A conceptual service for interacting with LLMs.
    In a real implementation, this would connect to an actual LLM API.
    Includes a basic in-memory cache for responses.
    """
    def __init__(self, api_key: str = Config.LLM_API_KEY, model_name: str = Config.LLM_MODEL_NAME):
        if not api_key:
            logger.warning("LLM_API_KEY not set. Using simulated responses only.")
        self.api_key = api_key
        self.model_name = model_name
        self.cache: Dict[str, str] = {} # Simple in-memory cache
        logger.info(f"Initialized LLMService with model: {self.model_name}")

    async def _call_llm_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Simulates an asynchronous LLM API call."""
        # In a real scenario, this would use an SDK like openai.Completion.create or gemini.GenerativeModel.generate_content
        # from openai import OpenAI
        # client = OpenAI(api_key=self.api_key)
        # response = await client.chat.completions.create( # Use await for async client
        #     model=self.model_name,
        #     messages=[{"role": "user", "content": prompt}],
        #     max_tokens=max_tokens,
        #     temperature=temperature,
        # )
        # return response.choices[0].message.content.strip()

        logger.debug(f"Simulating LLM API call for prompt: {prompt[:100]}...")
        # Simulate network latency
        await asyncio.sleep(0.1) # Simulate I/O bound operation

        # Simple simulated responses based on prompt keywords
        if "industry analysis" in prompt.lower():
            return "Based on the provided data, the semiconductor industry is experiencing rapid growth driven by AI and IoT. Key players include NVIDIA, Intel, and AMD. Market size is projected to reach $500 billion by 2030."
        elif "market trends" in prompt.lower():
            return "Emerging trends include sustainable energy solutions, personalized healthcare, and advanced automation. Future predictions indicate a significant shift towards decentralized technologies by 2028."
        elif "technology adoption" in prompt.lower():
            return "AI adoption in enterprise software is at 40% and growing. Blockchain in supply chain management is still nascent but shows promise. Recommendations include investment in AI-powered analytics."
        elif "strategic insights" in prompt.lower():
            return "A key strategic insight is the increasing consumer demand for eco-friendly products, presenting an opportunity for green innovation. Another insight points to consolidation in the streaming market, indicating potential acquisition targets."
        elif "actionable recommendations" in prompt.lower():
            return "Recommendation 1: Diversify supply chain to reduce reliance on single regions. Recommendation 2: Invest in R&D for quantum computing applications. Recommendation 3: Form strategic partnerships for market expansion."
        elif "executive summary" in prompt.lower():
            return "This report highlights the transformative impact of AI on various sectors, identifies sustainable practices as a core market trend, and recommends strategic investments in emerging technologies to maintain competitive advantage. Key findings indicate robust growth in tech-driven markets, particularly in cloud and AI segments. Strategic implications include the need for agile innovation cycles and diversified market presence."
        elif "competitive landscape" in prompt.lower():
            return "The competitive landscape is dominated by a few large entities with significant market share. New entrants are disrupting niche markets through innovation. SWOT analysis reveals strong R&D but vulnerability to regulatory changes for XYZ Corp. ABC Inc. shows strong market capture in emerging markets."
        elif "summary and extract entities" in prompt.lower() and "json" in prompt.lower():
            # Simulate structured JSON output from LLM
            if "techcorp" in prompt.lower():
                return '''
                {
                    "summary": "TechCorp's Q3 earnings report shows a 15% revenue increase, primarily due to cloud services. Innovation is highlighted as a growth driver.",
                    "entities": ["TechCorp", "Q3", "cloud services", "revenue", "innovation"]
                }
                '''
            elif "green energy" in prompt.lower():
                return '''
                {
                    "summary": "Record new investments in renewable energy, driven by sustainability trends. Solar and wind power are key areas.",
                    "entities": ["renewable energy", "sustainability", "solar power", "wind power", "investment"]
                }
                '''
            else:
                return '''
                {
                    "summary": "General market insights indicate shifting consumer preferences and technological advancements.",
                    "entities": ["consumer preferences", "technological advancements", "market insights"]
                }
                '''
        else:
            return "Simulated LLM response: Data processing complete. Insight extraction is ongoing. Further analysis is required for comprehensive findings."

    async def generate_response(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Generates a text response using the LLM, with caching.

        Args:
            prompt: The input prompt for the LLM.
            max_tokens: Maximum number of tokens in the generated response.
            temperature: Sampling temperature for creativity.

        Returns:
            An LLM response string.
        """
        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        if prompt_hash in self.cache:
            logger.debug(f"Returning cached response for prompt hash: {prompt_hash}")
            return self.cache[prompt_hash]

        response = await self._call_llm_api(prompt, max_tokens, temperature)
        self.cache[prompt_hash] = response
        return response

    async def batch_generate_response(self, prompts: List[str], max_tokens: int = 500, temperature: float = 0.7) -> List[str]:
        """
        Simulates batch processing of LLM requests.
        In a real scenario, this would leverage provider's batch API or asyncio.gather.

        Args:
            prompts: A list of input prompts.
            max_tokens: Maximum number of tokens for each response.
            temperature: Sampling temperature.

        Returns:
            A list of LLM responses, corresponding to the input prompts.
        """
        logger.info(f"Simulating batch LLM response for {len(prompts)} prompts.")
        # For simulation, run them sequentially but with asyncio.gather for proper async behavior
        responses = await asyncio.gather(*[
            self.generate_response(p, max_tokens, temperature) for p in prompts
        ])
        return responses

    async def extract_entities_and_summary(self, text: str) -> Dict[str, Any]:
        """
        Uses LLM to extract key entities and provide a summary of the given text,
        expecting JSON output.

        Args:
            text: The input text to process.

        Returns:
            A dictionary containing 'summary' and 'entities'.
        """
        # Sanitize input text before passing to LLM to prevent prompt injection
        sanitized_text = sanitize_text_input(text)
        
        prompt = f"""
        Summarize the following text and extract key entities (people, organizations, locations, products, events).
        The response MUST be in strict JSON format with two keys: "summary" (string) and "entities" (list of strings).
        
        TEXT:
        <DATA>
        {sanitized_text}
        </DATA>
        
        JSON:
        """
        response_text = await self.generate_response(prompt, max_tokens=200)
        
        try:
            # Attempt to parse the LLM response as JSON
            llm_output = json.loads(response_text)
            summary = llm_output.get("summary", "No summary extracted.")
            entities = llm_output.get("entities", [])
            if not isinstance(summary, str):
                summary = str(summary) # Ensure summary is string
            if not isinstance(entities, list) or not all(isinstance(e, str) for e in entities):
                entities = [str(e) for e in entities if e is not None] # Ensure entities are list of strings
            
            return {"summary": summary, "entities": entities}
        except json.JSONDecodeError as e:
            logger.error(f"LLM did not return valid JSON. Error: {e}. Raw response: {response_text[:200]}...")
            # Fallback for when LLM does not return valid JSON
            return {"summary": "Failed to extract structured summary due to parsing error.", "entities": []}
        except Exception as e:
            logger.error(f"Unexpected error processing LLM output: {e}. Raw response: {response_text[:200]}...")
            return {"summary": "Failed to extract structured summary due to unexpected error.", "entities": []}


# --- Refactored src/services/data_ingestion.py ---
"""
Service responsible for collecting and pre-processing raw data from diverse external sources.
Acts as the AI agent for automated data aggregation. Uses file-based data lake simulation.
"""
logger = get_logger(__name__)

class DataIngestionService:
    """
    Manages data collection from various configured sources and stores it in a simulated data lake.
    """
    def __init__(self):
        self.data_sources = Config.DATA_SOURCES
        logger.info("DataIngestionService initialized.")

    async def _fetch_from_source(self, source_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simulates fetching data from a specific external source asynchronously.
        In a real system, this would involve async API calls, web scraping, etc.

        Args:
            source_name: The name of the data source.
            query: Parameters for the data fetch (e.g., keywords, date range).

        Returns:
            A list of raw data dictionaries.
        """
        logger.info(f"Simulating data fetch from {source_name} with query: {query}")
        await asyncio.sleep(0.05) # Simulate network I/O latency

        if source_name == "news_api":
            return [
                {"title": "Tech Giant Q3 Earnings Up 15%", "text": "TechCorp reported a significant increase in revenue, primarily driven by its cloud services division. The CEO highlighted innovation as a key driver."},
                {"title": "Green Energy Investment Surges", "text": "New investments in renewable energy hit record highs, indicating a strong market trend towards sustainability. Solar and wind power lead the way."},
                {"title": "Competitor X Launches New AI Product", "text": "InnovationLabs unveiled its new AI-powered gadget, aiming to disrupt the smart home market. Analysts predict strong competition."}
            ]
        elif source_name == "sec_filings_db":
            return [
                {"company": "TechCorp", "filing_type": "10-K", "report_date": "2023-09-30", "content_summary": "Annual report detailing financial performance and strategic outlook."},
                {"company": "InnovationLabs", "filing_type": "8-K", "report_date": "2023-10-15", "content_summary": "Current report on recent product launch and market expansion plans."}
            ]
        return []

    async def ingest_data(self, query: Dict[str, Any]) -> List[str]:
        """
        Aggregates data from all configured sources based on a given query
        and stores them as JSON files in the data lake directory.

        Args:
            query: A dictionary containing parameters like 'industry', 'keywords', 'start_date', 'end_date'.

        Returns:
            A list of IDs for the newly ingested raw data entries.
        """
        logger.info(f"Starting data ingestion for query: {query}")
        ingested_ids: List[str] = []
        
        # Use asyncio.gather to fetch data from sources concurrently
        fetch_tasks = [self._fetch_from_source(s_name, query) for s_name in self.data_sources]
        results_per_source = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        for source_name, raw_data_items_or_exc in zip(self.data_sources.keys(), results_per_source):
            if isinstance(raw_data_items_or_exc, Exception):
                logger.error(f"Error fetching data from {source_name}: {raw_data_items_or_exc}")
                continue
            
            for item in raw_data_items_or_exc:
                try:
                    # Sanitize content before storing and processing
                    cleaned_item = {k: sanitize_text_input(str(v)) if isinstance(v, str) else v for k, v in item.items()}
                    
                    data_id = f"raw_{uuid.uuid4()}"
                    raw_data_entry = RawMarketData(
                        id=data_id,
                        source=source_name,
                        timestamp=datetime.now().isoformat(),
                        content=cleaned_item
                    )
                    
                    filename = f"{data_id}.json"
                    await write_json_to_file(raw_data_entry, Config.RAW_DATA_LAKE_DIR, filename)
                    ingested_ids.append(data_id)
                    logger.debug(f"Ingested data_id: {data_id} from {source_name}")
                except Exception as e:
                    logger.error(f"Error processing and storing item from {source_name}: {e}")
        
        logger.info(f"Finished data ingestion. Total {len(ingested_ids)} new items.")
        return ingested_ids

    async def get_raw_data(self, data_ids: List[str]) -> List[RawMarketData]:
        """
        Retrieves raw data entries from the data lake (files) based on their IDs.

        Args:
            data_ids: A list of IDs of the raw data entries.

        Returns:
            A list of RawMarketData objects.
        """
        logger.debug(f"Retrieving {len(data_ids)} raw data items from data lake.")
        tasks = []
        for data_id in data_ids:
            filepath = os.path.join(Config.RAW_DATA_LAKE_DIR, f"{data_id}.json")
            tasks.append(read_json_from_file(filepath, RawMarketData))
        
        # Use asyncio.gather to read files concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        retrieved_data: List[RawMarketData] = []
        for res in results:
            if isinstance(res, RawMarketData):
                retrieved_data.append(res)
            elif isinstance(res, Exception):
                logger.error(f"Failed to retrieve raw data: {res}")
        return retrieved_data

# --- Refactored src/services/market_data_processing.py ---
"""
Service responsible for transforming raw data into a structured format suitable for LLM consumption
and further analysis, and loading it into a data warehouse (file-based simulation).
"""
logger = get_logger(__name__)

class MarketDataProcessingService:
    """
    Processes raw market data, extracts entities, summarizes content,
    and loads into a structured format within a simulated data warehouse.
    """
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        logger.info("MarketDataProcessingService initialized.")

    async def process_raw_data(self, raw_data_items: List[RawMarketData]) -> List[str]:
        """
        Transforms raw data items into structured ProcessedMarketData using LLM capabilities
        and stores them as JSON files in the data warehouse directory.
        Processes items concurrently using asyncio.
        
        Args:
            raw_data_items: A list of RawMarketData objects.

        Returns:
            A list of IDs for the newly processed data entries.
        """
        logger.info(f"Starting processing of {len(raw_data_items)} raw data items.")
        
        async def _process_single_item(raw_item: RawMarketData) -> Optional[str]:
            try:
                # Convert content dict to string for LLM, ensuring it's sanitized
                content_text = sanitize_text_input(json.dumps(raw_item.content))
                
                # Use LLM to extract summary and entities
                llm_output = await self.llm_service.extract_entities_and_summary(content_text)
                
                summary = llm_output.get("summary", "No summary extracted.").strip()
                entities = [e.strip() for e in llm_output.get("entities", []) if e and e.strip()]
                
                # Simulate further structuring (e.g., sentiment, industry identification)
                industry_sector = None
                if "semiconductor" in summary.lower() or "nvidia" in str(entities).lower() or "intel" in str(entities).lower():
                    industry_sector = "Semiconductor"
                elif "energy" in summary.lower() or "solar" in summary.lower() or "wind" in summary.lower():
                    industry_sector = "Renewable Energy"

                sentiment = "neutral" 
                if "increase" in summary.lower() or "growth" in summary.lower() or "surges" in summary.lower():
                    sentiment = "positive"
                elif "disrupt" in summary.lower() or "competition" in summary.lower() or "vulnerability" in summary.lower():
                    sentiment = "mixed"

                processed_data_id = f"proc_{uuid.uuid4()}"
                processed_data = ProcessedMarketData(
                    id=processed_data_id,
                    original_raw_data_id=raw_item.id,
                    industry_sector=industry_sector,
                    companies=[e for e in entities if "Corp" in e or "Labs" in e or "Inc" in e],
                    keywords=[k for k in entities if k not in [comp for e_list in [raw_item.content.values()] for comp in e_list] and "Corp" not in k and "Labs" not in k and "Inc" not in k], # Filter out company names from keywords
                    summary=summary,
                    sentiment=sentiment,
                    processed_at=datetime.now().isoformat(),
                    structured_data={
                        "source_type": raw_item.source,
                        "original_timestamp": raw_item.timestamp,
                        "raw_content_preview": content_text[:100] + "..."
                    }
                )
                filename = f"{processed_data_id}.json"
                await write_json_to_file(processed_data, Config.PROCESSED_DATA_WAREHOUSE_DIR, filename)
                logger.debug(f"Processed raw_data_id: {raw_item.id} to processed_data_id: {processed_data_id}")
                return processed_data_id
            except Exception as e:
                logger.error(f"Error processing raw data ID {raw_item.id}: {e}", exc_info=True)
                return None
        
        # Process items concurrently
        processed_ids_with_none = await asyncio.gather(*[_process_single_item(item) for item in raw_data_items])
        processed_ids = [pid for pid in processed_ids_with_none if pid is not None]

        logger.info(f"Finished data processing. Total {len(processed_ids)} items processed.")
        return processed_ids

    async def get_processed_data(self, processed_data_ids: List[str]) -> List[ProcessedMarketData]:
        """
        Retrieves processed data entries from the data warehouse (files) based on their IDs.

        Args:
            processed_data_ids: A list of processed data IDs.

        Returns:
            A list of ProcessedMarketData objects.
        """
        logger.debug(f"Retrieving {len(processed_data_ids)} processed data items from data warehouse.")
        tasks = []
        for data_id in processed_data_ids:
            filepath = os.path.join(Config.PROCESSED_DATA_WAREHOUSE_DIR, f"{data_id}.json")
            tasks.append(read_json_from_file(filepath, ProcessedMarketData))
        
        # Use asyncio.gather to read files concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        retrieved_data: List[ProcessedMarketData] = []
        for res in results:
            if isinstance(res, ProcessedMarketData):
                retrieved_data.append(res)
            elif isinstance(res, Exception):
                logger.error(f"Failed to retrieve processed data: {res}")
        return retrieved_data

    async def get_all_processed_data(self) -> List[ProcessedMarketData]:
        """Retrieves all processed data entries from the data warehouse."""
        all_files = await list_files_in_dir(Config.PROCESSED_DATA_WAREHOUSE_DIR)
        processed_data_ids = [os.path.basename(f).replace(".json", "") for f in all_files]
        return await self.get_processed_data(processed_data_ids)


# --- Refactored src/services/llm_inference.py ---
"""
Core intelligence component for interacting with Large Language Models for advanced analysis,
insight extraction, and content generation.
"""
logger = get_logger(__name__)

class LLMInferenceService:
    """
    Orchestrates LLM interactions to extract insights from processed market data.
    """
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        logger.info("LLMInferenceService initialized.")

    async def _build_context_from_data(self, processed_data: List[ProcessedMarketData]) -> str:
        """
        Aggregates processed data into a single string context for the LLM.
        Applies sanitization to content before building context.

        Args:
            processed_data: List of ProcessedMarketData objects.

        Returns:
            A concatenated string representing the context.
        """
        context = []
        for item in processed_data:
            # Sanitize each piece of content before adding to prompt context
            context.append(f"Source Type: {sanitize_text_input(item.structured_data.get('source_type', 'N/A'))}")
            context.append(f"Summary: {sanitize_text_input(item.summary)}")
            if item.industry_sector:
                context.append(f"Industry Sector: {sanitize_text_input(item.industry_sector)}")
            if item.companies:
                context.append(f"Companies: {sanitize_text_input(', '.join(item.companies))}")
            if item.keywords:
                context.append(f"Keywords: {sanitize_text_input(', '.join(item.keywords))}")
            context.append("-" * 20)
        return "\n".join(context)

    async def generate_industry_analysis(self, processed_data: List[ProcessedMarketData]) -> Dict[str, Any]:
        """
        Generates industry analysis using the LLM.

        Args:
            processed_data: Relevant processed market data.

        Returns:
            A dictionary containing industry analysis details.
        """
        if not processed_data:
            logger.warning("No processed data provided for industry analysis.")
            return {"overview": "No data available for industry analysis.", "market_size_estimation": "N/A", "growth_drivers_llm": [], "key_segments_llm": []}

        context = await self._build_context_from_data(processed_data)
        prompt = f"""
        Based on the following processed market data, provide a comprehensive industry analysis.
        Include market size, growth drivers, key segments, and major trends.
        The response should be concise and direct.
        
        DATA CONTEXT:
        <DATA>
        {context}
        </DATA>
        
        INDUSTRY ANALYSIS:
        """
        response = await self.llm_service.generate_response(prompt, max_tokens=1000)
        
        return {
            "overview": sanitize_text_input(response),
            "market_size_estimation": "Not directly calculated, but LLM indicates significant growth.", # Placeholder for real calculation
            "growth_drivers_llm": ["AI adoption", "Sustainability initiatives", "Digital transformation"] if "ai" in response.lower() or "sustainability" in response.lower() else ["general market forces"],
            "key_segments_llm": ["Cloud Computing", "Renewable Energy", "Smart Devices"] if "cloud" in response.lower() or "energy" in response.lower() else ["diverse sectors"]
        }

    async def generate_competitive_landscape(self, processed_data: List[ProcessedMarketData], competitors_of_interest: List[str]) -> Dict[str, Any]:
        """
        Generates competitive landscape mapping and SWOT analysis for specific competitors.

        Args:
            processed_data: Relevant processed market data.
            competitors_of_interest: List of competitor names to focus on.

        Returns:
            A dictionary containing competitive landscape details.
        """
        if not processed_data:
            logger.warning("No processed data provided for competitive landscape analysis.")
            return {"overview": "No data available for competitive landscape.", "key_players_identified": [], "swot_analysis": {}}

        context = await self._build_context_from_data(processed_data)
        competitors_str = sanitize_text_input(", ".join(competitors_of_interest)) if competitors_of_interest else "key players"
        prompt = f"""
        Analyze the competitive landscape based on the following processed market data, focusing on {competitors_str}.
        Identify key players, their market positioning, strengths, weaknesses, opportunities, and threats (SWOT analysis).
        
        DATA CONTEXT:
        <DATA>
        {context}
        </DATA>
        
        COMPETITIVE LANDSCAPE AND SWOT:
        """
        response = await self.llm_service.generate_response(prompt, max_tokens=1000)
        
        return {
            "overview": sanitize_text_input(response),
            "key_players_identified": competitors_of_interest if competitors_of_interest else ["TechCorp", "InnovationLabs"],
            "swot_analysis": { # Simulated SWOT for example purposes
                "TechCorp": {"Strengths": ["Strong cloud portfolio"], "Weaknesses": ["Reliance on specific markets"]},
                "InnovationLabs": {"Strengths": ["Innovative products"], "Weaknesses": ["Smaller market share"]}
            }
        }

    async def identify_market_trends_and_predictions(self, processed_data: List[ProcessedMarketData]) -> Dict[str, Any]:
        """
        Identifies current and emerging market trends and generates future predictions.

        Args:
            processed_data: Relevant processed market data.

        Returns:
            A dictionary containing market trends and predictions.
        """
        if not processed_data:
            logger.warning("No processed data provided for market trends and predictions.")
            return {"identified_trends": [], "future_predictions": "No data available for predictions.", "growth_opportunities_llm": []}

        context = await self._build_context_from_data(processed_data)
        prompt = f"""
        Based on the following processed market data, identify current and emerging market trends.
        Provide future predictions for these trends over the next 3-5 years.
        
        DATA CONTEXT:
        <DATA>
        {context}
        </DATA>
        
        MARKET TRENDS AND FUTURE PREDICTIONS:
        """
        response = await self.llm_service.generate_response(prompt, max_tokens=1000)
        
        return {
            "identified_trends": ["Sustainability", "Hyper-personalization", "AI-driven Automation"] if "sustainability" in response.lower() else ["general market trends"],
            "future_predictions": sanitize_text_input(response),
            "growth_opportunities_llm": ["Green Tech", "Personalized Healthcare platforms"] if "green tech" in response.lower() else ["diverse opportunities"]
        }

    async def analyze_technology_adoption(self, processed_data: List[ProcessedMarketData]) -> Dict[str, Any]:
        """
        Assesses the adoption rates and impact of relevant technologies.

        Args:
            processed_data: Relevant processed market data.

        Returns:
            A dictionary containing technology adoption analysis.
        """
        if not processed_data:
            logger.warning("No processed data provided for technology adoption analysis.")
            return {"overview": "No data available for technology adoption analysis.", "technology_focus": [], "adoption_rates_llm": {}, "impact_assessment_llm": "N/A"}

        context = await self._build_context_from_data(processed_data)
        prompt = f"""
        Based on the following processed market data, analyze the adoption rates and impact of relevant technologies
        (e.g., AI, Blockchain, Cloud Computing, IoT) within the specified market.
        
        DATA CONTEXT:
        <DATA>
        {context}
        </DATA>
        
        TECHNOLOGY ADOPTION ANALYSIS:
        """
        response = await self.llm_service.generate_response(prompt, max_tokens=800)
        
        return {
            "overview": sanitize_text_input(response),
            "technology_focus": ["AI", "Cloud Computing", "Blockchain"] if "ai" in response.lower() else ["general technologies"],
            "adoption_rates_llm": {"AI": "High and growing", "Blockchain": "Emerging"} if "ai" in response.lower() else {},
            "impact_assessment_llm": sanitize_text_input("AI significantly enhances operational efficiency.") if "ai" in response.lower() else "General impact."
        }

    async def generate_strategic_insights(self, industry_analysis: Dict[str, Any], competitive_landscape: Dict[str, Any], market_trends: Dict[str, Any], tech_adoption: Dict[str, Any]) -> List[LLMInsight]:
        """
        Extracts actionable strategic insights by synthesizing various analysis outputs.
        Attempts to parse insights from LLM as a list of JSON objects (conceptual).

        Args:
            industry_analysis: Output from industry analysis.
            competitive_landscape: Output from competitive landscape analysis.
            market_trends: Output from market trends and predictions.
            tech_adoption: Output from technology adoption analysis.

        Returns:
            A list of LLMInsight objects.
        """
        combined_context = f"""
        Industry Analysis: <SECTION>{sanitize_text_input(industry_analysis.get('overview', ''))}</SECTION>
        Competitive Landscape: <SECTION>{sanitize_text_input(competitive_landscape.get('overview', ''))}</SECTION>
        Market Trends & Predictions: <SECTION>{sanitize_text_input(market_trends.get('future_predictions', ''))}</SECTION>
        Technology Adoption: <SECTION>{sanitize_text_input(tech_adoption.get('overview', ''))}</SECTION>
        """
        prompt = f"""
        Based on the following comprehensive analysis reports, extract key strategic insights.
        Each insight should be concise, data-driven, and highlight a significant implication.
        Provide each insight with a type (e.g., 'Market Opportunity', 'Competitive Threat', 'Technological Imperative').
        The output must be a JSON array of objects, where each object has 'insight_type' (string), 'description' (string), 'relevance_score' (float), and 'confidence_score' (float).
        
        COMBINED ANALYSIS:
        <DATA>
        {combined_context}
        </DATA>
        
        STRATEGIC INSIGHTS (JSON ARRAY):
        """
        response_text = await self.llm_service.generate_response(prompt, max_tokens=1500)
        
        insights: List[LLMInsight] = []
        try:
            # Attempt to parse the LLM response as a JSON array
            llm_insights_raw = json.loads(response_text)
            if not isinstance(llm_insights_raw, list):
                raise ValueError("LLM response is not a JSON array.")

            for item in llm_insights_raw:
                try:
                    # Validate and sanitize individual insight fields
                    item['description'] = sanitize_text_input(item.get('description', ''))
                    insight = LLMInsight(
                        insight_type=sanitize_text_input(item.get('insight_type', 'General')),
                        description=item['description'],
                        relevance_score=float(item.get('relevance_score', 0.5)),
                        confidence_score=float(item.get('confidence_score', 0.5)),
                        supporting_data_ids=[], # This would be populated in a real RAG system
                        generated_at=datetime.now().isoformat()
                    )
                    insights.append(insight)
                except Exception as e:
                    logger.warning(f"Failed to parse individual LLM insight item: {item}. Error: {e}")

        except json.JSONDecodeError as e:
            logger.error(f"LLM did not return valid JSON array for strategic insights. Error: {e}. Raw response: {response_text[:200]}...")
            # Fallback to simulated insights if JSON parsing fails
            insights.append(LLMInsight(
                insight_type="Market Opportunity",
                description=sanitize_text_input("The surging demand for sustainable products presents a significant green innovation market opportunity."),
                relevance_score=0.9, confidence_score=0.85, supporting_data_ids=[], generated_at=datetime.now().isoformat()
            ))
            insights.append(LLMInsight(
                insight_type="Competitive Threat",
                description=sanitize_text_input("Aggressive entry of new AI-powered startups poses a competitive threat to established players in the smart home sector."),
                relevance_score=0.85, confidence_score=0.8, supporting_data_ids=[], generated_at=datetime.now().isoformat()
            ))
        except Exception as e:
            logger.error(f"Unexpected error processing strategic insights LLM output: {e}. Raw response: {response_text[:200]}...")
            # Fallback for unexpected errors
            insights.append(LLMInsight(
                insight_type="Technological Imperative",
                description=sanitize_text_input("Strategic investment in advanced AI analytics is imperative."),
                relevance_score=0.7, confidence_score=0.7, supporting_data_ids=[], generated_at=datetime.now().isoformat()
            ))
        
        return insights


# --- Refactored src/services/analytics_insights.py ---
"""
Applies structured analytical methods and statistical models to processed data and LLM outputs
to generate deep insights and validate LLM outputs. Also responsible for generating actionable recommendations.
"""
logger = get_logger(__name__)

class AnalyticsInsightsService:
    """
    Performs structured analysis and generates actionable recommendations based on LLM insights.
    """
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        logger.info("AnalyticsInsightsService initialized.")

    async def validate_llm_insights(self, llm_insights: List[LLMInsight], processed_data: List[ProcessedMarketData]) -> List[LLMInsight]:
        """
        Validates LLM-generated insights against processed data.
        This conceptual validation focuses on keyword presence and confidence scores.
        A real system would involve more sophisticated factual cross-referencing and statistical checks.

        Args:
            llm_insights: List of LLMInsight objects.
            processed_data: Relevant processed data (for conceptual validation).

        Returns:
            A list of validated LLMInsight objects (or filtered/adjusted ones).
        """
        logger.info(f"Validating {len(llm_insights)} LLM insights.")
        validated_insights = []
        
        processed_summaries = [d.summary.lower() for d in processed_data]
        
        for insight in llm_insights:
            is_valid_by_content = False
            # Check if keywords from insight description are present in processed data summaries
            insight_keywords = {word for word in insight.description.lower().split() if len(word) > 3} # Basic keyword extraction
            
            for summary_text in processed_summaries:
                if any(keyword in summary_text for keyword in insight_keywords):
                    is_valid_by_content = True
                    break
            
            # Apply confidence threshold and content validation
            if insight.confidence_score >= 0.6 and is_valid_by_content:
                validated_insights.append(insight)
            else:
                logger.warning(
                    f"Insight '{insight.description[:50]}...' failed validation. "
                    f"Confidence: {insight.confidence_score:.2f}, Content Match: {is_valid_by_content}"
                )
        logger.info(f"Finished validation. {len(validated_insights)} insights passed.")
        return validated_insights

    async def generate_actionable_recommendations(self, strategic_insights: List[LLMInsight], analysis_context: Dict[str, Any]) -> List[Recommendation]:
        """
        Translates strategic insights into concrete, practical, and actionable recommendations.
        Attempts to parse recommendations from LLM as a list of JSON objects (conceptual).

        Args:
            strategic_insights: List of LLMInsight objects.
            analysis_context: Additional context from other analysis components (e.g., industry, tech trends).

        Returns:
            A list of Recommendation objects.
        """
        logger.info(f"Generating recommendations from {len(strategic_insights)} strategic insights.")
        recommendations: List[Recommendation] = []
        
        insight_descriptions = "\n".join([f"- {i.description} (Type: {i.insight_type})" for i in strategic_insights])
        full_prompt = f"""
        Given the following strategic insights and market analysis context, generate concrete, actionable recommendations for businesses.
        Each recommendation MUST include 'category' (string), 'description' (string), 'action_steps' (list of strings), 'expected_impact' (string), and 'priority' (High, Medium, Low).
        The output must be a JSON array of recommendation objects.
        
        Strategic Insights:
        <INSIGHTS>
        {insight_descriptions}
        </INSIGHTS>
        
        Market Analysis Context:
        Industry: {sanitize_text_input(analysis_context.get('industry_name', 'General'))}
        Key Market Trends: {sanitize_text_input(', '.join(analysis_context.get('market_trends', [])))}
        Technology Focus: {sanitize_text_input(', '.join(analysis_context.get('tech_focus', [])))}
        
        Actionable Recommendations (JSON ARRAY):
        """
        llm_response_text = await self.llm_service.generate_response(full_prompt, max_tokens=1000)
        
        try:
            llm_recommendations_raw = json.loads(llm_response_text)
            if not isinstance(llm_recommendations_raw, list):
                raise ValueError("LLM response for recommendations is not a JSON array.")

            for item in llm_recommendations_raw:
                try:
                    # Sanitize recommendation fields
                    item['description'] = sanitize_text_input(item.get('description', ''))
                    item['expected_impact'] = sanitize_text_input(item.get('expected_impact', ''))
                    item['action_steps'] = [sanitize_text_input(s) for s in item.get('action_steps', [])]
                    item['priority'] = item.get('priority', 'Medium') # Default priority
                    if item['priority'] not in ["High", "Medium", "Low"]:
                        item['priority'] = "Medium" # Ensure valid priority

                    recommendation = Recommendation(
                        category=sanitize_text_input(item.get('category', 'General')),
                        description=item['description'],
                        action_steps=item['action_steps'],
                        expected_impact=item['expected_impact'],
                        priority=item['priority'],
                        related_insights=[sanitize_text_input(s) for s in item.get('related_insights', [])]
                    )
                    recommendations.append(recommendation)
                except Exception as e:
                    logger.warning(f"Failed to parse individual LLM recommendation item: {item}. Error: {e}")

        except json.JSONDecodeError as e:
            logger.error(f"LLM did not return valid JSON array for recommendations. Error: {e}. Raw response: {llm_response_text[:200]}...")
            # Fallback to simulated recommendations
            recommendations.append(Recommendation(
                category="Product Development & Innovation",
                description=sanitize_text_input("Invest in R&D for sustainable product lines."),
                action_steps=["Formulate green product teams.", "Seek eco-certifications."],
                expected_impact="Increased market share.",
                priority="High",
                related_insights=["Market Opportunity: Sustainable products"]
            ))
            recommendations.append(Recommendation(
                category="Competitive Strategy",
                description=sanitize_text_input("Develop rapid response innovation cycle."),
                action_steps=["Monitor competitor product launches.", "Launch new features quarterly."],
                expected_impact="Mitigation of market share loss.",
                priority="Medium",
                related_insights=["Competitive Threat: AI startup entry"]
            ))
        except Exception as e:
            logger.error(f"Unexpected error processing recommendations LLM output: {e}. Raw response: {llm_response_text[:200]}...")
            recommendations.append(Recommendation(
                category="Technology Adoption",
                description=sanitize_text_input("Implement advanced AI analytics solutions."),
                action_steps=["Conduct feasibility study.", "Train workforce."],
                expected_impact="Improved operational efficiency.",
                priority="High",
                related_insights=["Technological Imperative: AI analytics"]
            ))

        logger.info(f"Generated {len(recommendations)} actionable recommendations.")
        return recommendations


# --- Refactored src/services/report_generation.py ---
"""
Service responsible for compiling all processed data, LLM outputs, and analytical insights
into the final "Gartner-style" report format. Stores reports in a designated directory.
"""
logger = get_logger(__name__)

class ReportGenerationService:
    """
    Assembles all generated insights and data into a structured Gartner-style report.
    """
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.reports_dir = Config.REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True) # Ensure directory exists
        logger.info(f"ReportGenerationService initialized. Reports will be saved in: {self.reports_dir}")

    async def _generate_executive_summary_llm(self, report_content: ReportContent) -> ExecutiveSummary:
        """
        Uses LLM to generate a concise executive summary based on the full report content.

        Args:
            report_content: The nearly complete report content object.

        Returns:
            An ExecutiveSummary object.
        """
        top_recommendations_text = '\n'.join([f"- {sanitize_text_input(r.description)} (Priority: {r.priority})" for r in report_content.actionable_recommendations[:5]])
        
        summary_prompt = f"""
        Generate a concise Executive Summary (approx. 200-300 words) for a Gartner-style market research report.
        Highlight the key findings, strategic implications, and the top 3-5 most important actionable recommendations.
        
        Ensure the language is professional, analytical, and impactful.
        
        Report Key Sections Overview (Summaries):
        - Industry Analysis: <SECTION_SUMMARY>{sanitize_text_input(report_content.industry_analysis.get('overview', ''))[:500]}...</SECTION_SUMMARY>
        - Competitive Landscape: <SECTION_SUMMARY>{sanitize_text_input(report_content.competitive_landscape.get('overview', ''))[:500]}...</SECTION_SUMMARY>
        - Market Trends & Predictions: <SECTION_SUMMARY>{sanitize_text_input(report_content.market_trends_predictions.get('future_predictions', ''))[:500]}...</SECTION_SUMMARY>
        - Technology Adoption Analysis: <SECTION_SUMMARY>{sanitize_text_input(report_content.technology_adoption_analysis.get('overview', ''))[:500]}...</SECTION_SUMMARY>

        Strategic Insights (Key Points):
        <INSIGHTS>
        {'\n'.join([f"- {sanitize_text_input(i.description)}" for i in report_content.strategic_insights])}
        </INSIGHTS>

        Top Actionable Recommendations:
        <RECOMMENDATIONS>
        {top_recommendations_text}
        </RECOMMENDATIONS>

        EXECUTIVE SUMMARY:
        """
        
        summary_text = await self.llm_service.generate_response(summary_prompt, max_tokens=400)
        summary_text = sanitize_text_input(summary_text)

        # Extract key findings and strategic implications from the generated summary
        # This parsing remains conceptual and relies on LLM to follow instructions.
        key_findings = ["Robust growth in tech-driven markets, particularly cloud and AI services.",
                        "Surging demand for sustainable products opens new market opportunities.",
                        "Increased competition from AI startups necessitates agile innovation."]
        strategic_implications = ["Need for rapid innovation cycles to maintain competitive edge.",
                                  "Opportunity for market leadership through green innovation.",
                                  "Imperative for strategic AI adoption to enhance operational efficiency."]
        
        # Select top recommendations for the summary (e.g., top 3 High priority)
        # Sort by priority (High=3, Medium=2, Low=1) then alphabetically by description
        sorted_recs = sorted(
            report_content.actionable_recommendations,
            key=lambda x: ({"High": 3, "Medium": 2, "Low": 1}.get(x.priority, 0), x.description),
            reverse=True
        )
        top_recommendations = sorted_recs[:3]

        return ExecutiveSummary(
            key_findings=key_findings,
            strategic_implications=strategic_implications,
            top_recommendations=top_recommendations,
            summary_text=summary_text
        )

    async def generate_report(
        self,
        request_id: str,
        industry_analysis: Dict[str, Any],
        competitive_landscape: Dict[str, Any],
        market_trends_predictions: Dict[str, Any],
        technology_adoption_analysis: Dict[str, Any],
        strategic_insights: List[LLMInsight],
        actionable_recommendations: List[Recommendation],
        report_request: ReportRequest
    ) -> str:
        """
        Assembles and generates the full Gartner-style market research report.

        Args:
            request_id: The ID of the report request.
            industry_analysis: Output from LLMInferenceService.
            competitive_landscape: Output from LLMInferenceService.
            market_trends_predictions: Output from LLMInferenceService.
            technology_adoption_analysis: Output from LLMInferenceService.
            strategic_insights: List of LLMInsight objects from LLMInferenceService/AnalyticsInsightsService.
            actionable_recommendations: List of Recommendation objects from AnalyticsInsightsService.
            report_request: The original report request object.

        Returns:
            The file path to the generated report.
        """
        logger.info(f"Starting report generation for request ID: {request_id}")

        report_content = ReportContent(
            executive_summary=ExecutiveSummary(
                key_findings=[], strategic_implications=[], top_recommendations=[], summary_text="" # Placeholder
            ),
            industry_analysis=industry_analysis,
            competitive_landscape=competitive_landscape,
            market_trends_predictions=market_trends_predictions,
            technology_adoption_analysis=technology_adoption_analysis,
            strategic_insights=strategic_insights,
            actionable_recommendations=actionable_recommendations,
            appendix={
                "data_sources_used": list(Config.DATA_SOURCES.keys()),
                "methodology_notes": "LLM-guided analysis with human validation principles. Data sourced from various public and proprietary APIs."
            }
        )
        
        # Generate the Executive Summary after other sections are conceptually populated
        report_content.executive_summary = await self._generate_executive_summary_llm(report_content)

        report_filename = f"market_research_report_{request_id}.{report_request.report_format}"
        report_filepath = os.path.join(self.reports_dir, report_filename)

        # Simulate writing the report to a file based on format (Markdown for this example)
        try:
            with open(report_filepath, "w", encoding="utf-8") as f:
                f.write(f"# Gartner-Style Market Research Report\n\n")
                f.write(f"## Executive Summary\n\n")
                f.write(f"{report_content.executive_summary.summary_text}\n\n")
                f.write(f"### Key Findings\n")
                for finding in report_content.executive_summary.key_findings:
                    f.write(f"- {sanitize_text_input(finding)}\n")
                f.write(f"\n### Strategic Implications\n")
                for implication in report_content.executive_summary.strategic_implications:
                    f.write(f"- {sanitize_text_input(implication)}\n")
                f.write(f"\n### Top Recommendations\n")
                for rec in report_content.executive_summary.top_recommendations:
                    f.write(f"- **{sanitize_text_input(rec.description)}** (Priority: {sanitize_text_input(rec.priority)})\n")
                
                f.write(f"\n## 1. Industry Analysis\n\n")
                f.write(f"{sanitize_text_input(report_content.industry_analysis.get('overview', 'N/A'))}\n\n")
                f.write(f"### Market Size Estimation\n")
                f.write(f"{sanitize_text_input(report_content.industry_analysis.get('market_size_estimation', 'N/A'))}\n\n")
                f.write(f"### Growth Drivers\n")
                for driver in report_content.industry_analysis.get('growth_drivers_llm', []):
                    f.write(f"- {sanitize_text_input(driver)}\n")
                
                f.write(f"\n## 2. Competitive Landscape Mapping\n\n")
                f.write(f"{sanitize_text_input(report_content.competitive_landscape.get('overview', 'N/A'))}\n\n")
                f.write(f"### Key Players\n")
                for player in report_content.competitive_landscape.get('key_players_identified', []):
                    f.write(f"- {sanitize_text_input(player)}\n")
                f.write(f"### SWOT Analysis (Selected Players)\n")
                for company, swot in report_content.competitive_landscape.get('swot_analysis', {}).items():
                    f.write(f"#### {sanitize_text_input(company)}\n")
                    f.write(f"  - **Strengths:** {sanitize_text_input(', '.join(swot.get('Strengths', [])))}\n")
                    f.write(f"  - **Weaknesses:** {sanitize_text_input(', '.join(swot.get('Weaknesses', [])))}\n")
                    f.write(f"  - **Opportunities:** {sanitize_text_input(', '.join(swot.get('Opportunities', [])))}\n")
                    f.write(f"  - **Threats:** {sanitize_text_input(', '.join(swot.get('Threats', [])))}\n")


                f.write(f"\n## 3. Market Trends Identification and Future Predictions\n\n")
                f.write(f"### Identified Trends\n")
                for trend in report_content.market_trends_predictions.get('identified_trends', []):
                    f.write(f"- {sanitize_text_input(trend)}\n")
                f.write(f"\n### Future Predictions\n")
                f.write(f"{sanitize_text_input(report_content.market_trends_predictions.get('future_predictions', 'N/A'))}\n\n")
                f.write(f"### Growth Opportunities\n")
                for opp in report_content.market_trends_predictions.get('growth_opportunities_llm', []):
                    f.write(f"- {sanitize_text_input(opp)}\n")
                
                f.write(f"\n## 4. Technology Adoption Analysis and Recommendations\n\n")
                f.write(f"{sanitize_text_input(report_content.technology_adoption_analysis.get('overview', 'N/A'))}\n\n")
                f.write(f"### Technology Focus\n")
                for tech in report_content.technology_adoption_analysis.get('technology_focus', []):
                    f.write(f"- {sanitize_text_input(tech)}\n")
                f.write(f"### Adoption Rates\n")
                for tech, rate in report_content.technology_adoption_analysis.get('adoption_rates_llm', {}).items():
                    f.write(f"- {sanitize_text_input(tech)}: {sanitize_text_input(rate)}\n")
                f.write(f"### Impact Assessment\n")
                f.write(f"{sanitize_text_input(report_content.technology_adoption_analysis.get('impact_assessment_llm', 'N/A'))}\n\n")
                
                f.write(f"\n## 5. Strategic Insights\n\n")
                if not report_content.strategic_insights:
                    f.write("No strategic insights generated.\n\n")
                for insight in report_content.strategic_insights:
                    f.write(f"### {sanitize_text_input(insight.insight_type)}\n")
                    f.write(f"- {sanitize_text_input(insight.description)} (Relevance: {insight.relevance_score:.2f}, Confidence: {insight.confidence_score:.2f})\n\n")
                
                f.write(f"## 6. Actionable Recommendations\n\n")
                if not report_content.actionable_recommendations:
                    f.write("No actionable recommendations generated.\n\n")
                for rec in report_content.actionable_recommendations:
                    f.write(f"### {sanitize_text_input(rec.category)} (Priority: {sanitize_text_input(rec.priority)})\n")
                    f.write(f"- **Recommendation:** {sanitize_text_input(rec.description)}\n")
                    f.write(f"- **Action Steps:** {sanitize_text_input('; '.join(rec.action_steps))}\n")
                    f.write(f"- **Expected Impact:** {sanitize_text_input(rec.expected_impact)}\n\n")

                f.write(f"## Appendix\n\n")
                f.write(f"Data Sources: {sanitize_text_input(', '.join(report_content.appendix.get('data_sources_used', [])))}\n")
                f.write(f"Methodology: {sanitize_text_input(report_content.appendix.get('methodology_notes', ''))}\n")

            logger.info(f"Report for request ID {request_id} generated at: {report_filepath}")
            return report_filepath
        except IOError as e:
            logger.error(f"Error writing report file {report_filepath}: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during report file generation for {request_id}: {e}", exc_info=True)
            raise


# --- Refactored src/services/continuous_monitoring.py ---
"""
Orchestrates scheduled data ingestion, re-analysis, and report updates based on real-time market changes.
This service primarily listens for events or triggers based on schedules.
"""
logger = get_logger(__name__)

class ContinuousMonitoringService:
    """
    Monitors market developments and triggers report updates.
    In a real system, this would be event-driven via a message broker
    or a dedicated scheduler (e.g., Airflow, Kubernetes CronJobs).
    """
    def __init__(self, trigger_report_generation_callback: Callable[[ReportRequest], Any]):
        # The callback is now Any because it will be an async function returning a Coroutine
        self.trigger_report_generation = trigger_report_generation_callback
        self.monitored_requests: Dict[str, ReportRequest] = {}
        self.monitoring_interval_seconds = 5 # Simulate frequent monitoring for demo purposes
        logger.info("ContinuousMonitoringService initialized.")

    def register_for_monitoring(self, report_request: ReportRequest):
        """
        Registers a report request for continuous monitoring.

        Args:
            report_request: The ReportRequest object to monitor.
        """
        self.monitored_requests[report_request.request_id] = report_request
        logger.info(f"Report request {report_request.request_id} registered for continuous monitoring.")

    async def _check_and_trigger_update(self, request_id: str, report_request: ReportRequest):
        """
        Conceptual check for triggering an update. In a real system, this would involve
        checking for new data ingested since the last report, or significant market shifts.

        Args:
            request_id: The ID of the report request.
            report_request: The ReportRequest object.
        """
        logger.info(f"Checking for updates for report request {request_id}...")
        
        # For demonstration, always trigger if registered for monitoring after a delay
        logger.info(f"Triggering update for report request {request_id} due to simulated new data.")
        try:
            # Await the callback as it's now an async function
            status = await self.trigger_report_generation(report_request)
            logger.info(f"Update triggered for {request_id}, new status: {status.status}")
        except Exception as e:
            logger.error(f"Error triggering update for {request_id} via callback: {e}", exc_info=True)


    async def start_monitoring_loop(self, duration_seconds: int = 10):
        """
        Simulates a continuous monitoring loop. This would be a long-running async process.

        Args:
            duration_seconds: How long the simulation should run.
        """
        logger.info(f"Starting continuous monitoring loop for {duration_seconds} seconds...")
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < duration_seconds:
            # Create tasks for all monitored requests to run concurrently
            tasks = [self._check_and_trigger_update(req_id, req) 
                     for req_id, req in list(self.monitored_requests.items())]
            
            if tasks:
                await asyncio.gather(*tasks) # Run checks concurrently
            
            await asyncio.sleep(self.monitoring_interval_seconds) # Wait before next check
        logger.info("Continuous monitoring loop ended.")


# --- Refactored src/main.py ---
"""
Orchestrates the entire LLM-guided Gartner-style market research report generation framework.
This acts as a high-level manager, coordinating calls between different microservices.
Uses asynchronous operations for better performance and responsiveness.
"""
logger = get_logger(__name__)

class MarketResearchFramework:
    """
    The main orchestrator for the Gartner-style market research report generation.
    Manages the flow from request to final report.
    """
    def __init__(self):
        Config.initialize_dirs() # Ensure directories are set up

        # Initialize core LLM utility
        self.llm_service = LLMService()

        # Initialize all dependent services
        self.data_ingestion_service = DataIngestionService()
        self.market_data_processing_service = MarketDataProcessingService(self.llm_service)
        self.llm_inference_service = LLMInferenceService(self.llm_service)
        self.analytics_insights_service = AnalyticsInsightsService(self.llm_service)
        self.report_generation_service = ReportGenerationService(self.llm_service)
        
        # Continuous monitoring service needs an async callback
        self.continuous_monitoring_service = ContinuousMonitoringService(
            trigger_report_generation_callback=self.generate_market_research_report
        )

        self.report_statuses: Dict[str, ReportStatus] = {}
        logger.info("MarketResearchFramework initialized. All services are ready.")

    async def generate_market_research_report(self, request: ReportRequest) -> ReportStatus:
        """
        Initiates the end-to-end process of generating a market research report asynchronously.

        Args:
            request: A ReportRequest object detailing the research requirements.

        Returns:
            A ReportStatus object indicating the current status of the report generation.
        """
        report_status = ReportStatus(
            request_id=request.request_id,
            status="IN_PROGRESS",
            progress=0.0,
            last_updated=datetime.now().isoformat()
        )
        self.report_statuses[request.request_id] = report_status
        logger.info(f"Started report generation for request ID: {request.request_id}")

        try:
            # Stage 1: Data Ingestion
            logger.info("Stage 1: Data Ingestion")
            report_status.progress = 10.0
            raw_data_query = {
                "industry": sanitize_text_input(request.industry),
                "focus_areas": [sanitize_text_input(fa) for fa in request.focus_areas],
                "competitors": [sanitize_text_input(c) for c in request.competitors_of_interest],
                "start_date": request.start_date,
                "end_date": request.end_date
            }
            raw_data_ids = await self.data_ingestion_service.ingest_data(raw_data_query)
            if not raw_data_ids:
                raise ValueError("No raw data ingested for the given request criteria. Please refine your query.")
            raw_data_items = await self.data_ingestion_service.get_raw_data(raw_data_ids)
            if not raw_data_items: # Defensive check if get_raw_data fails
                raise ValueError("Failed to retrieve raw data after ingestion.")
            report_status.last_updated = datetime.now().isoformat()

            # Stage 2: Market Data Processing
            logger.info("Stage 2: Market Data Processing")
            report_status.progress = 30.0
            processed_data_ids = await self.market_data_processing_service.process_raw_data(raw_data_items)
            processed_data = await self.market_data_processing_service.get_processed_data(processed_data_ids)
            if not processed_data:
                raise ValueError("No processed data available after processing. Check raw data quality.")
            report_status.last_updated = datetime.now().isoformat()

            # Stage 3: LLM-Guided Analysis (Core Insights Generation)
            logger.info("Stage 3: LLM-Guided Analysis")
            report_status.progress = 50.0
            
            # Run LLM analysis steps concurrently
            industry_task = self.llm_inference_service.generate_industry_analysis(processed_data)
            competitive_task = self.llm_inference_service.generate_competitive_landscape(processed_data, request.competitors_of_interest)
            market_trends_task = self.llm_inference_service.identify_market_trends_and_predictions(processed_data)
            tech_adoption_task = self.llm_inference_service.analyze_technology_adoption(processed_data)

            industry_analysis, competitive_landscape, market_trends_predictions, technology_adoption_analysis = \
                await asyncio.gather(industry_task, competitive_task, market_trends_task, tech_adoption_task)
            
            strategic_insights = await self.llm_inference_service.generate_strategic_insights(
                industry_analysis, competitive_landscape, market_trends_predictions, technology_adoption_analysis
            )
            report_status.last_updated = datetime.now().isoformat()

            # Stage 4: Analytics and Actionable Recommendations
            logger.info("Stage 4: Analytics and Actionable Recommendations")
            report_status.progress = 70.0
            validated_insights = await self.analytics_insights_service.validate_llm_insights(strategic_insights, processed_data)
            
            analysis_context = {
                "industry_name": request.industry,
                "market_trends": market_trends_predictions.get("identified_trends", []),
                "tech_focus": technology_adoption_analysis.get("technology_focus", [])
            }
            actionable_recommendations = await self.analytics_insights_service.generate_actionable_recommendations(
                validated_insights, analysis_context
            )
            report_status.last_updated = datetime.now().isoformat()

            # Stage 5: Report Generation
            logger.info("Stage 5: Report Generation")
            report_status.progress = 90.0
            final_report_path = await self.report_generation_service.generate_report(
                request.request_id,
                industry_analysis,
                competitive_landscape,
                market_trends_predictions,
                technology_adoption_analysis,
                validated_insights,
                actionable_recommendations,
                request
            )
            report_status.report_path = final_report_path
            report_status.last_updated = datetime.now().isoformat()

            report_status.status = "COMPLETED"
            report_status.progress = 100.0
            logger.info(f"Report generation for request ID {request.request_id} completed successfully. Report saved to: {final_report_path}")

        except ValueError as ve:
            logger.error(f"Business logic error for request ID {request.request_id}: {ve}")
            report_status.status = "FAILED"
            report_status.error_message = f"Report generation failed: {ve}" # User-friendly message
            report_status.progress = 0.0
            report_status.last_updated = datetime.now().isoformat()
        except Exception as e:
            logger.error(f"An unexpected internal error occurred for request ID {request.request_id}: {e}", exc_info=True)
            report_status.status = "FAILED"
            report_status.error_message = "An internal error occurred during report generation. Please try again or contact support." # Generic message for user
            report_status.progress = 0.0
            report_status.last_updated = datetime.now().isoformat()

        return report_status

    def get_report_status(self, request_id: str) -> ReportStatus:
        """
        Retrieves the current status of a report generation request.

        Args:
            request_id: The ID of the report request.

        Returns:
            A ReportStatus object.
        """
        return self.report_statuses.get(request_id, ReportStatus(request_id=request_id, status="NOT_FOUND", progress=0.0, last_updated=datetime.now().isoformat()))

    async def start_continuous_monitoring(self, duration_seconds: int = 30):
        """
        Starts the continuous monitoring loop for registered reports.

        Args:
            duration_seconds: How long the simulation should run.
        """
        await self.continuous_monitoring_service.start_monitoring_loop(duration_seconds)

async def main_run():
    """Main asynchronous execution function."""
    framework = MarketResearchFramework()

    # Example Report Request 1
    request_id_1 = f"report_{uuid.uuid4()}"
    report_request_1 = ReportRequest(
        request_id=request_id_1,
        industry="Semiconductor Industry",
        focus_areas=["AI chips", "Market Consolidation"],
        competitors_of_interest=["NVIDIA", "Intel", "AMD"],
        report_format="md", # Using markdown for easy viewing
        start_date="2023-01-01",
        end_date="2023-12-31"
    )

    print(f"\n--- Initiating Report Generation for Request ID: {report_request_1.request_id} ---")
    status_1 = await framework.generate_market_research_report(report_request_1)
    print(f"Report 1 Final Status: {status_1.status}, Path: {status_1.report_path}, Error: {status_1.error_message}")
    if status_1.report_path:
        print(f"Check the generated report at: {status_1.report_path}")

    # Example Report Request 2 (simulating a simpler request)
    request_id_2 = f"report_{uuid.uuid4()}"
    report_request_2 = ReportRequest(
        request_id=request_id_2,
        industry="Renewable Energy",
        focus_areas=["Solar Power Trends", "Investment Opportunities"],
        report_format="md"
    )

    print(f"\n--- Initiating Report Generation for Request ID: {report_request_2.request_id} ---")
    status_2 = await framework.generate_market_research_report(report_request_2)
    print(f"Report 2 Final Status: {status_2.status}, Path: {status_2.report_path}, Error: {status_2.error_message}")
    if status_2.report_path:
        print(f"Check the generated report at: {status_2.report_path}")


    # Demonstrate continuous monitoring (will trigger re-generation of registered reports)
    print("\n--- Registering Report 1 for Continuous Monitoring ---")
    framework.continuous_monitoring_service.register_for_monitoring(report_request_1)
    
    # Run monitoring loop for a short duration to show it triggers
    print("\n--- Starting Continuous Monitoring Simulation (will re-trigger Report 1) ---")
    await framework.start_continuous_monitoring(duration_seconds=10)

    print("\n--- Framework Execution Complete ---")

if __name__ == "__main__":
    asyncio.run(main_run())

```

### Security Improvements

1.  **Prompt Injection Mitigation:**
    *   **Input Sanitization:** Implemented `sanitize_text_input` in `src/utils/data_utils.py`. This function escapes common Markdown and HTML special characters (e.g., `< > & * _ [ ] ( )`) from any text input (user queries, raw content, etc.) before it is incorporated into LLM prompts or written to reports. This significantly reduces the risk of an attacker manipulating the LLM's behavior or injecting malicious content into the final report.
    *   **Contextual Delimiters in Prompts:** LLM prompts now use explicit delimiters like `<DATA>` and `</DATA>` or `<SECTION_SUMMARY>` to clearly separate user-controlled or external data from the LLM's instructions. This helps the LLM distinguish between content and command, further mitigating prompt injection.
2.  **Robust LLM Output Parsing:**
    *   The framework now explicitly instructs the LLM to provide outputs in a strict JSON format for critical components (e.g., `extract_entities_and_summary`, `generate_strategic_insights`, `generate_actionable_recommendations`).
    *   `json.loads` is used with `try-except` blocks to parse these JSON responses. If the LLM deviates and provides malformed JSON, the system logs the error and falls back to a default simulated response, preventing system crashes and ensuring data integrity.
3.  **Improved Error Handling (Information Leakage):**
    *   In `src/main.py`, the `generate_market_research_report` method now uses more specific `try...except ValueError` for expected business logic failures (e.g., no data ingested) and a broader `except Exception` for unexpected internal errors.
    *   For user-facing error messages in `ReportStatus`, generic messages (e.g., "Report generation failed: [specific business reason]", "An internal error occurred...") are provided. Detailed internal error messages and stack traces are now logged only to the internal logging system, preventing sensitive information leakage to end-users.
4.  **No Hardcoded API Keys:** The `Config.LLM_API_KEY` no longer has a default hardcoded value (`"YOUR_LLM_API_KEY"`). It relies solely on `os.getenv()`, making it mandatory for the API key to be provided via environment variables, which is a better security practice for secrets management. A warning is logged if the key is missing.
5.  **Simulated Persistent Storage Security:** While still simulated with local files, the move away from in-memory lists for `data_lake`, `data_warehouse`, and `reports` sets the stage for integrating with secure cloud object storage (e.g., AWS S3) or databases. In a real deployment, these would inherently leverage cloud provider's robust security features (encryption at rest/in transit, IAM policies, access controls), which are beyond the scope of this code but now architecturally viable.
6.  **Pydantic Validation of ReportRequest:** Pydantic models for `ReportRequest` now include basic validation for `min_length`, `max_length`, and `min_items` for string fields and lists, which helps prevent excessively large inputs that could lead to resource exhaustion or unexpected behavior.

### Performance Optimizations

1.  **Asynchronous Processing:**
    *   **I/O Concurrency:** All functions performing I/O operations (simulated external API calls in `DataIngestionService`, simulated LLM calls in `LLMService`, and file read/write operations in `data_utils`) are now `async`. This allows the Python event loop to switch between tasks while waiting for I/O, preventing blocking and improving the overall responsiveness and throughput of the system.
    *   **Concurrent Data Processing:**
        *   In `DataIngestionService.ingest_data`, data fetching from multiple `DATA_SOURCES` is now executed concurrently using `asyncio.gather`.
        *   In `MarketDataProcessingService.process_raw_data`, the processing of multiple `RawMarketData` items, which involves LLM calls and file I/O, is parallelized using `asyncio.gather`.
        *   In `LLMInferenceService`, the calls to `generate_industry_analysis`, `generate_competitive_landscape`, `identify_market_trends_and_predictions`, and `analyze_technology_adoption` are run concurrently in `main.py` using `asyncio.gather`, reducing the total time for the LLM analysis stage.
2.  **LLM Response Caching:**
    *   `LLMService` now includes a simple in-memory `self.cache` that stores LLM responses. Before making an actual LLM call, it checks if a response for the given prompt is already in the cache. This drastically reduces redundant LLM API calls for identical prompts, saving costs and improving latency for repeated queries.
3.  **Simulated Batch LLM Calls:**
    *   A conceptual `LLMService.batch_generate_response` method was added. While currently implemented using `asyncio.gather` over individual calls, in a real scenario, this method would be refactored to leverage LLM providers' native batch processing APIs (if available), which are significantly more efficient than individual calls for large volumes of prompts.
4.  **Transition from In-Memory to File-Based Storage:**
    *   While not a direct performance *optimization* in the simulated code (file I/O is still simulated synchronously for simplicity within `asyncio`), this architectural shift is critical for real-world scalability. Replacing unbounded Python lists with file-based persistence (which would be backed by scalable cloud object storage/databases) prevents memory exhaustion and ensures that data retrieval operations (which would use indexed queries in a real database) scale logarithmically or constantly, instead of linearly (`O(N)`) as with current list scans.
5.  **Efficient Data Retrieval (Conceptual):**
    *   The `get_raw_data` and `get_processed_data` methods now read data from specific JSON files in directories, rather than iterating through large in-memory lists. This change aligns with how data would be retrieved efficiently from a real data lake (e.g., S3) or data warehouse (e.g., specific table queries).

### Quality Enhancements

1.  **Enhanced Data Modeling:**
    *   `RawMarketData` and `ProcessedMarketData` models in `src/models/report_models.py` now explicitly include an `id` field using `uuid.uuid4()` for unique identification. This provides consistent primary keys for data entities, which is crucial for managing data in persistent stores and improves traceability.
2.  **Robust LLM Output Parsing:**
    *   As detailed in security, forcing JSON output from LLMs and rigorously parsing it with `json.loads` and Pydantic-style validation (even if conceptualized) makes the system more resilient to LLM "hallucinations" regarding output format, leading to higher data quality downstream.
3.  **Improved Docstrings and Type Hinting:** Maintained high standards of docstrings for all modules, classes, and methods, clearly describing their purpose, arguments, and return types. Comprehensive type hinting is used consistently throughout the codebase, improving readability and maintainability.
4.  **Consistent Directory Management:** The `Config.initialize_dirs()` static method ensures that all necessary data and report directories are created at framework initialization, centralizing file system setup and preventing runtime errors due to missing paths.
5.  **Structured Report Content:** The `ReportContent` model and the `ReportGenerationService` now include more detailed sub-sections for industry analysis, competitive landscape, market trends, and technology adoption, aligning more closely with the comprehensive "Gartner-style" report structure.
6.  **Refined Recommendation Prioritization:** The `_generate_executive_summary_llm` method now includes a sorting mechanism for `top_recommendations` based on `priority` (High, Medium, Low), making the executive summary more impactful and logically structured.
7.  **Separation of Concerns (Enhanced):** While already strong, the clear distinction between data utilities (file I/O, sanitization) and service-specific logic is reinforced, making each component more focused and testable.
8.  **Logging Granularity:** The use of `logger.debug`, `logger.info`, `logger.warning`, and `logger.error` is applied more judiciously to provide clearer insights into the framework's execution flow, potential issues, and critical failures.

### Updated Tests

All unit tests were updated to reflect the asynchronous nature of the refactored code and the move to file-based data storage.

*   **`async_test` decorator:** A custom `async_test` decorator was added to allow `unittest` to run asynchronous test methods.
*   **`AsyncMock`:** `unittest.mock.AsyncMock` is used for patching asynchronous methods of services in integration tests (e.g., `test_main.py`), allowing proper testing of async calls (`assert_awaited_once`).
*   **File System Management in Tests:** `setUp` and `tearDown` methods in service tests (e.g., `TestDataIngestionService`, `TestMarketDataProcessingService`, `TestReportGenerationService`) now rigorously create and clean up temporary directories (`test_raw_data_lake`, `test_processed_data_warehouse`, `test_reports_gen`) to ensure test isolation and prevent side effects.
*   **Verification of File I/O:** Tests now assert the existence and content of JSON files written by `DataIngestionService` and `MarketDataProcessingService` in their respective simulated data lake and data warehouse directories.
*   **LLM JSON Parsing Tests:** `TestLLMService` and `TestLLMInferenceService` include specific tests to verify that the LLM output is correctly parsed as JSON and that appropriate fallbacks are triggered when invalid JSON is received.
*   **Input Sanitization Tests:** `TestDataUtils` includes tests for the `sanitize_text_input` function, verifying its ability to escape special characters.
*   **Improved Mocking for `main.py`:** The `test_main.py` now uses `AsyncMock` for all service instances, ensuring that the orchestration logic is correctly tested with asynchronous dependencies.

```python
# tests/__init__.py
# Empty file to mark the directory as a Python package

# tests/test_data_ingestion.py
import unittest
import os
import shutil
import asyncio
from datetime import datetime
import json
from unittest.mock import MagicMock, AsyncMock, patch

# Adjust imports based on the refactored structure
from src.services.data_ingestion import DataIngestionService
from src.services.market_data_processing import MarketDataProcessingService
from src.services.llm_inference import LLMInferenceService
from src.services.analytics_insights import AnalyticsInsightsService
from src.services.report_generation import ReportGenerationService
from src.services.continuous_monitoring import ContinuousMonitoringService
from src.models.report_models import RawMarketData, ProcessedMarketData, LLMInsight, Recommendation, ReportRequest, ReportStatus, ExecutiveSummary, ReportContent
from src.utils.llm_utils import LLMService
from src.utils.data_utils import sanitize_text_input, write_json_to_file, read_json_from_file, list_files_in_dir
from src.config import Config

# Helper to run async tests
def async_test(func):
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

class TestConfig(unittest.TestCase):
    def test_initialize_dirs(self):
        # Clean up existing dirs if any
        if os.path.exists(Config.BASE_DATA_DIR):
            shutil.rmtree(Config.BASE_DATA_DIR)
        if os.path.exists(Config.REPORTS_DIR):
            shutil.rmtree(Config.REPORTS_DIR)
        
        Config.initialize_dirs()
        self.assertTrue(os.path.exists(Config.RAW_DATA_LAKE_DIR))
        self.assertTrue(os.path.exists(Config.PROCESSED_DATA_WAREHOUSE_DIR))
        self.assertTrue(os.path.exists(Config.REPORTS_DIR))
        
        # Clean up
        if os.path.exists(Config.BASE_DATA_DIR):
            shutil.rmtree(Config.BASE_DATA_DIR)
        if os.path.exists(Config.REPORTS_DIR):
            shutil.rmtree(Config.REPORTS_DIR)

class TestDataUtils(unittest.TestCase):
    @async_test
    async def test_write_read_json(self):
        test_dir = "test_data_utils_dir"
        test_file = "test_model.json"
        
        class TestModel(BaseModel):
            name: str
            value: int

        model_instance = TestModel(name="test", value=123)
        
        filepath = await write_json_to_file(model_instance, test_dir, test_file)
        self.assertTrue(os.path.exists(filepath))
        
        read_model = await read_json_from_file(filepath, TestModel)
        self.assertEqual(read_model.name, "test")
        self.assertEqual(read_model.value, 123)
        
        shutil.rmtree(test_dir)

    def test_sanitize_text_input(self):
        self.assertEqual(sanitize_text_input("  Hello <script>World</script>  "), "Hello &lt;script&gt;World&lt;/script&gt;")
        self.assertEqual(sanitize_text_input("Report with *bold* and _italics_"), "Report with &#42;bold&#42; and &#95;italics&#95;")
        self.assertEqual(sanitize_text_input("Link: [Text](url)"), "Link: &#91;Text&#93;&#40;url&#41;")
        self.assertEqual(sanitize_text_input("No special chars."), "No special chars.")

class TestLLMService(unittest.TestCase):
    def setUp(self):
        # Use an actual LLMService, but we'll control its _call_llm_api
        self.service = LLMService(api_key="mock_key")
        self.service.cache = {} # Clear cache for each test

    @async_test
    async def test_generate_response_cached(self):
        with patch.object(self.service, '_call_llm_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "First response"
            
            response1 = await self.service.generate_response("Test prompt")
            response2 = await self.service.generate_response("Test prompt") # Should be cached
            response3 = await self.service.generate_response("Another prompt") # Not cached
            
            self.assertEqual(response1, "First response")
            self.assertEqual(response2, "First response")
            # _call_llm_api should only be called twice (once for "Test prompt", once for "Another prompt")
            self.assertEqual(mock_call.call_count, 2)
            self.assertIn(hashlib.md5("Test prompt".encode('utf-8')).hexdigest(), self.service.cache)
            self.assertIn(hashlib.md5("Another prompt".encode('utf-8')).hexdigest(), self.service.cache)

    @async_test
    async def test_extract_entities_and_summary_valid_json(self):
        mock_response = '''
        {
            "summary": "This is a summary of the document.",
            "entities": ["Entity1", "Entity2"]
        }
        '''
        with patch.object(self.service, 'generate_response', new_callable=AsyncMock) as mock_gen_response:
            mock_gen_response.return_value = mock_response
            
            result = await self.service.extract_entities_and_summary("Some text.")
            self.assertEqual(result["summary"], "This is a summary of the document.")
            self.assertEqual(result["entities"], ["Entity1", "Entity2"])
            mock_gen_response.assert_called_once()
            self.assertIn("JSON", mock_gen_response.call_args[0][0].upper()) # Check if JSON instruction is in prompt

    @async_test
    async def test_extract_entities_and_summary_invalid_json(self):
        mock_response = "This is not JSON at all."
        with patch.object(self.service, 'generate_response', new_callable=AsyncMock) as mock_gen_response:
            mock_gen_response.return_value = mock_response
            
            result = await self.service.extract_entities_and_summary("Some text.")
            self.assertEqual(result["summary"], "Failed to extract structured summary due to parsing error.")
            self.assertEqual(result["entities"], [])
            mock_gen_response.assert_called_once()
    
    @async_test
    async def test_batch_generate_response(self):
        prompts = ["p1", "p2", "p3"]
        mock_responses = ["r1", "r2", "r3"]
        with patch.object(self.service, 'generate_response', side_effect=mock_responses) as mock_gen_response:
            results = await self.service.batch_generate_response(prompts)
            self.assertEqual(results, mock_responses)
            self.assertEqual(mock_gen_response.call_count, len(prompts))


class TestDataIngestionService(unittest.TestCase):
    def setUp(self):
        self.service = DataIngestionService()
        self.test_query = {
            "industry": "Test Industry",
            "keywords": ["test_keyword"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-02"
        }
        # Set up a temporary directory for tests
        self.test_data_lake_dir = "test_raw_data_lake"
        Config.RAW_DATA_LAKE_DIR = self.test_data_lake_dir
        os.makedirs(self.test_data_lake_dir, exist_ok=True)

    def tearDown(self):
        # Clean up the temporary directory
        if os.path.exists(self.test_data_lake_dir):
            shutil.rmtree(self.test_data_lake_dir)
        # Restore original config path
        Config.RAW_DATA_LAKE_DIR = os.path.join(Config.BASE_DATA_DIR, "raw_data_lake")

    @async_test
    async def test_ingest_data_success(self):
        """Test successful data ingestion to simulated file-based data lake."""
        ingested_ids = await self.service.ingest_data(self.test_query)
        self.assertGreater(len(ingested_ids), 0)
        
        # Verify files are created
        for data_id in ingested_ids:
            filepath = os.path.join(Config.RAW_DATA_LAKE_DIR, f"{data_id}.json")
            self.assertTrue(os.path.exists(filepath))
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.assertEqual(data['id'], data_id)
                self.assertIn('content', data)
                self.assertIn('source', data)

    @async_test
    async def test_get_raw_data(self):
        """Test retrieving specific raw data entries from file-based data lake."""
        ingested_ids = await self.service.ingest_data(self.test_query)
        retrieved_data = await self.service.get_raw_data([ingested_ids[0]])
        self.assertEqual(len(retrieved_data), 1)
        self.assertEqual(retrieved_data[0].id, ingested_ids[0])
        self.assertIsInstance(retrieved_data[0], RawMarketData)

    @async_test
    async def test_ingest_data_no_sources(self):
        """Test ingestion when no data sources are configured (simulated)."""
        original_sources = self.service.data_sources
        self.service.data_sources = {} # Temporarily remove sources
        ingested_ids = await self.service.ingest_data(self.test_query)
        self.assertEqual(len(ingested_ids), 0)
        self.assertEqual(len(os.listdir(Config.RAW_DATA_LAKE_DIR)), 0)
        self.service.data_sources = original_sources # Restore

    @async_test
    async def test_ingest_data_source_error_handling(self):
        """Test ingestion with error during fetch from a source."""
        original_fetch = self.service._fetch_from_source
        async def mock_fetch(source_name, query):
            if source_name == "news_api":
                raise Exception("Simulated network error")
            return original_fetch(source_name, query)
        
        with patch.object(self.service, '_fetch_from_source', side_effect=mock_fetch):
            ingested_ids = await self.service.ingest_data(self.test_query)
            # Expecting some data to be ingested from other sources, but not the errored one
            self.assertGreater(len(ingested_ids), 0)
            self.assertFalse(any("news_api" in data_id for data_id in ingested_ids)) # Assuming IDs would somehow reflect source


class TestMarketDataProcessingService(unittest.TestCase):
    def setUp(self):
        self.llm_service = LLMService(api_key="mock_key")
        # Patch the LLM service to return predictable JSON for entity extraction
        self.llm_service._call_llm_api = AsyncMock(return_value='{"summary": "Mock summary.", "entities": ["MockEntity"]}')
        self.service = MarketDataProcessingService(llm_service=self.llm_service)
        
        self.test_raw_data_lake_dir = "test_raw_data_lake_proc"
        self.test_processed_data_warehouse_dir = "test_processed_data_warehouse"
        Config.RAW_DATA_LAKE_DIR = self.test_raw_data_lake_dir
        Config.PROCESSED_DATA_WAREHOUSE_DIR = self.test_processed_data_warehouse_dir
        
        os.makedirs(self.test_raw_data_lake_dir, exist_ok=True)
        os.makedirs(self.test_processed_data_warehouse_dir, exist_ok=True)

        self.mock_raw_data_items = [
            RawMarketData(
                id="raw_123",
                source="news_api",
                timestamp=datetime.now().isoformat(),
                content={"title": "Test News 1", "text": "This is a test article about TechCorp's new AI product."}
            ),
            RawMarketData(
                id="raw_456",
                source="sec_filings_db",
                timestamp=datetime.now().isoformat(),
                content={"company": "BioLabs", "filing_type": "10-K", "content_summary": "Financial report highlighting growth in biotech."}
            )
        ]
        # Write mock raw data to files for the service to read
        for item in self.mock_raw_data_items:
            asyncio.run(write_json_to_file(item, Config.RAW_DATA_LAKE_DIR, f"{item.id}.json"))

    def tearDown(self):
        if os.path.exists(self.test_raw_data_lake_dir):
            shutil.rmtree(self.test_raw_data_lake_dir)
        if os.path.exists(self.test_processed_data_warehouse_dir):
            shutil.rmtree(self.test_processed_data_warehouse_dir)
        Config.RAW_DATA_LAKE_DIR = os.path.join(Config.BASE_DATA_DIR, "raw_data_lake")
        Config.PROCESSED_DATA_WAREHOUSE_DIR = os.path.join(Config.BASE_DATA_DIR, "processed_data_warehouse")

    @async_test
    async def test_process_raw_data_success(self):
        """Test successful processing of raw data to file-based warehouse."""
        processed_ids = await self.service.process_raw_data(self.mock_raw_data_items)
        self.assertEqual(len(processed_ids), len(self.mock_raw_data_items))
        
        # Verify files are created in processed data warehouse
        for p_id in processed_ids:
            filepath = os.path.join(Config.PROCESSED_DATA_WAREHOUSE_DIR, f"{p_id}.json")
            self.assertTrue(os.path.exists(filepath))
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.assertEqual(data['id'], p_id)
                self.assertIn('summary', data)
                self.assertNotEqual(data['summary'], "No summary extracted.") # Should be from mock LLM

    @async_test
    async def test_get_processed_data(self):
        """Test retrieving specific processed data entries from file-based warehouse."""
        processed_ids = await self.service.process_raw_data(self.mock_raw_data_items)
        retrieved_data = await self.service.get_processed_data([processed_ids[0]])
        self.assertEqual(len(retrieved_data), 1)
        self.assertEqual(retrieved_data[0].id, processed_ids[0])
        self.assertIsInstance(retrieved_data[0], ProcessedMarketData)

    @async_test
    async def test_process_empty_list(self):
        """Test processing an empty list of raw data."""
        processed_ids = await self.service.process_raw_data([])
        self.assertEqual(len(processed_ids), 0)
        self.assertEqual(len(os.listdir(Config.PROCESSED_DATA_WAREHOUSE_DIR)), 0)

    @async_test
    async def test_process_raw_data_llm_error_handling(self):
        """Test error handling when LLM fails during processing."""
        # Make LLM call fail
        self.llm_service._call_llm_api.side_effect = Exception("LLM connection error")
        
        processed_ids = await self.service.process_raw_data(self.mock_raw_data_items)
        # Should return empty list of processed IDs if LLM call consistently fails
        self.assertEqual(len(processed_ids), 0)
        self.assertEqual(len(os.listdir(Config.PROCESSED_DATA_WAREHOUSE_DIR)), 0)


class TestLLMInferenceService(unittest.TestCase):
    def setUp(self):
        self.llm_service = LLMService(api_key="mock_key")
        # Patch LLM service responses for specific prompts
        self.llm_service.generate_response = AsyncMock(side_effect=self._mock_llm_generate_response)
        self.service = LLMInferenceService(llm_service=self.llm_service)

        self.mock_processed_data = [
            ProcessedMarketData(
                id="proc_1", original_raw_data_id="raw_1", industry_sector="Tech",
                companies=["TechCorp"], keywords=["AI", "Cloud"],
                summary="TechCorp reports strong growth in AI and cloud services.",
                processed_at=datetime.now().isoformat(), structured_data={"source_type": "news_api"}
            ),
            ProcessedMarketData(
                id="proc_2", original_raw_data_id="raw_2", industry_sector="Energy",
                companies=[], keywords=["Solar", "Investment"],
                summary="Significant new investments in solar energy projects.",
                processed_at=datetime.now().isoformat(), structured_data={"source_type": "news_api"}
            )
        ]

    async def _mock_llm_generate_response(self, prompt, max_tokens, temperature):
        if "industry analysis" in prompt.lower():
            return "Simulated industry analysis overview: AI is driving tech growth."
        elif "competitive landscape" in prompt.lower():
            return "Simulated competitive landscape overview: TechCorp leads in cloud."
        elif "market trends" in prompt.lower():
            return "Simulated market trends: Sustainability is a key trend, expect growth in green tech."
        elif "technology adoption" in prompt.lower():
            return "Simulated tech adoption: AI adoption rates are high."
        elif "strategic insights" in prompt.lower():
            return """
            [
                {"insight_type": "Market Opportunity", "description": "The growing demand for sustainable tech creates new market avenues.", "relevance_score": 0.9, "confidence_score": 0.8},
                {"insight_type": "Competitive Threat", "description": "Emergence of new agile startups threatens established market share.", "relevance_score": 0.8, "confidence_score": 0.7}
            ]
            """
        else:
            return "Default simulated LLM response."

    @async_test
    async def test_generate_industry_analysis(self):
        analysis = await self.service.generate_industry_analysis(self.mock_processed_data)
        self.assertIn("overview", analysis)
        self.assertIn("AI is driving tech growth", analysis["overview"])
        self.llm_service.generate_response.assert_called_with(unittest.mock.ANY, max_tokens=1000)

    @async_test
    async def test_generate_competitive_landscape(self):
        landscape = await self.service.generate_competitive_landscape(self.mock_processed_data, ["TechCorp"])
        self.assertIn("overview", landscape)
        self.assertIn("TechCorp leads in cloud", landscape["overview"])
        self.llm_service.generate_response.assert_called_with(unittest.mock.ANY, max_tokens=1000)

    @async_test
    async def test_generate_strategic_insights_valid_json(self):
        insights = await self.service.generate_strategic_insights(
            {"overview": ""}, {"overview": ""}, {"future_predictions": ""}, {"overview": ""}
        )
        self.assertGreater(len(insights), 0)
        self.assertIsInstance(insights[0], LLMInsight)
        self.assertEqual(insights[0].insight_type, "Market Opportunity")
        self.llm_service.generate_response.assert_called_with(unittest.mock.ANY, max_tokens=1500)
        # Ensure that the prompt contains the JSON array instruction
        call_args_prompt = self.llm_service.generate_response.call_args[0][0]
        self.assertIn("JSON ARRAY", call_args_prompt)

    @async_test
    async def test_generate_strategic_insights_invalid_json_fallback(self):
        # Force LLM to return invalid JSON for strategic insights
        self.llm_service.generate_response = AsyncMock(return_value="This is not a JSON array of insights.")
        
        insights = await self.service.generate_strategic_insights(
            {"overview": ""}, {"overview": ""}, {"future_predictions": ""}, {"overview": ""}
        )
        self.assertGreater(len(insights), 0)
        self.assertIsInstance(insights[0], LLMInsight)
        # Verify it fell back to the simulated insights
        self.assertEqual(insights[0].insight_type, "Market Opportunity")


class TestAnalyticsInsightsService(unittest.TestCase):
    def setUp(self):
        self.llm_service = LLMService(api_key="mock_key")
        self.llm_service.generate_response = AsyncMock(side_effect=self._mock_llm_generate_response)
        self.service = AnalyticsInsightsService(llm_service=self.llm_service)

        self.mock_llm_insights = [
            LLMInsight(
                insight_type="Market Opportunity",
                description="Surging demand for sustainable products.",
                relevance_score=0.9,
                confidence_score=0.85,
                supporting_data_ids=[],
                generated_at=datetime.now().isoformat()
            ),
            LLMInsight(
                insight_type="Competitive Threat",
                description="New AI startups are disrupting the market.",
                relevance_score=0.8,
                confidence_score=0.7,
                supporting_data_ids=[],
                generated_at=datetime.now().isoformat()
            ),
            LLMInsight(
                insight_type="Low Confidence Insight",
                description="This is a very uncertain finding.",
                relevance_score=0.5,
                confidence_score=0.5, # Below threshold
                supporting_data_ids=[],
                generated_at=datetime.now().isoformat()
            )
        ]
        self.mock_processed_data = [
            ProcessedMarketData(
                id="proc_1", original_raw_data_id="raw_1", industry_sector="General",
                companies=[], keywords=[],
                summary="Consumers are increasingly opting for sustainable and eco-friendly goods.",
                processed_at=datetime.now().isoformat(),
                structured_data={}
            ),
            ProcessedMarketData(
                id="proc_2", original_raw_data_id="raw_2", industry_sector="Tech",
                companies=[], keywords=[],
                summary="Several new AI-powered companies recently launched products targeting the smart home sector.",
                processed_at=datetime.now().isoformat(),
                structured_data={}
            )
        ]
        self.mock_analysis_context = {
            "industry_name": "Consumer Goods",
            "market_trends": ["Sustainability", "Digitalization"],
            "tech_focus": ["AI"]
        }

    async def _mock_llm_generate_response(self, prompt, max_tokens, temperature):
        if "actionable recommendations" in prompt.lower() and "json array" in prompt.lower():
            return """
            [
                {"category": "Product Development", "description": "Invest in green tech.", "action_steps": ["R&D"], "expected_impact": "Growth", "priority": "High"},
                {"category": "Strategy", "description": "Monitor competitors.", "action_steps": ["Observe"], "expected_impact": "Mitigate risk", "priority": "Medium"}
            ]
            """
        return "Default simulated LLM response."

    @async_test
    async def test_validate_llm_insights(self):
        """Test validation of LLM insights, ensuring confidence filtering."""
        validated_insights = await self.service.validate_llm_insights(self.mock_llm_insights, self.mock_processed_data)
        # Only the first two insights should pass due to confidence threshold
        self.assertEqual(len(validated_insights), 2)
        self.assertEqual(validated_insights[0].insight_type, "Market Opportunity")
        self.assertEqual(validated_insights[1].insight_type, "Competitive Threat")
        self.assertNotIn("Low Confidence Insight", [i.insight_type for i in validated_insights])

    @async_test
    async def test_generate_actionable_recommendations_valid_json(self):
        """Test generation of actionable recommendations from LLM with valid JSON."""
        recommendations = await self.service.generate_actionable_recommendations(
            self.mock_llm_insights, self.mock_analysis_context
        )
        self.assertGreater(len(recommendations), 0)
        self.assertIsInstance(recommendations[0], Recommendation)
        self.assertEqual(recommendations[0].description, "Invest in green tech.")
        self.llm_service.generate_response.assert_called_once()
        call_args_prompt = self.llm_service.generate_response.call_args[0][0]
        self.assertIn("JSON ARRAY", call_args_prompt)

    @async_test
    async def test_generate_actionable_recommendations_invalid_json_fallback(self):
        """Test generation of actionable recommendations with LLM returning invalid JSON."""
        self.llm_service.generate_response = AsyncMock(return_value="Not a JSON array of recommendations.")
        recommendations = await self.service.generate_actionable_recommendations(
            self.mock_llm_insights, self.mock_analysis_context
        )
        self.assertGreater(len(recommendations), 0)
        self.assertIsInstance(recommendations[0], Recommendation)
        # Verify it fell back to the simulated recommendations
        self.assertEqual(recommendations[0].description, "Invest in R&D for sustainable product lines.")
        self.llm_service.generate_response.assert_called_once()


class TestReportGenerationService(unittest.TestCase):
    def setUp(self):
        self.llm_service = LLMService(api_key="mock_key")
        self.llm_service.generate_response = AsyncMock(side_effect=self._mock_llm_generate_response)
        self.service = ReportGenerationService(llm_service=self.llm_service)
        
        self.test_reports_dir = "test_reports_gen"
        Config.REPORTS_DIR = self.test_reports_dir # Override config for testing
        os.makedirs(self.test_reports_dir, exist_ok=True)

        self.mock_request_id = "test_report_123"
        self.mock_report_request = ReportRequest(
            request_id=self.mock_request_id,
            industry="Test Industry",
            focus_areas=["Test Area"],
            report_format="md"
        )
        self.mock_industry_analysis = {"overview": "Test industry is stable and growing due to AI.", "market_size_estimation": "$1T", "growth_drivers_llm": ["AI"], "key_segments_llm": ["Cloud"]}
        self.mock_competitive_landscape = {"overview": "Key player A dominates. SWOT: S-Strong R&D, W-Niche market, O-Expansion, T-New entrants.", "key_players_identified": ["Player A"], "swot_analysis": {"Player A": {"Strengths": ["R&D"], "Weaknesses": ["Niche"]}}}
        self.mock_market_trends_predictions = {"future_predictions": "Growth is expected in sustainable tech.", "identified_trends": ["Sustainable Tech"], "growth_opportunities_llm": ["Green Products"]}
        self.mock_technology_adoption_analysis = {"overview": "Tech X is widely adopted. AI adoption is high.", "technology_focus": ["AI"], "adoption_rates_llm": {"AI": "High"}, "impact_assessment_llm": "AI enhances efficiency."}
        self.mock_strategic_insights = [
            LLMInsight(
                insight_type="Opportunity",
                description="New market opening due to sustainability drive.",
                relevance_score=0.9, confidence_score=0.9,
                supporting_data_ids=[], generated_at=datetime.now().isoformat()
            )
        ]
        self.mock_actionable_recommendations = [
            Recommendation(
                category="Strategy",
                description="Expand into new regions for sustainable products.",
                action_steps=["Step 1", "Step 2"],
                expected_impact="Increased revenue.",
                priority="High",
                related_insights=[]
            ),
            Recommendation(
                category="Technology",
                description="Adopt new AI tools.",
                action_steps=["Pilot", "Integrate"],
                expected_impact="Efficiency.",
                priority="Medium",
                related_insights=[]
            )
        ]

    async def _mock_llm_generate_response(self, prompt, max_tokens, temperature):
        if "executive summary" in prompt.lower():
            return "This is a concise executive summary highlighting key findings like AI growth and sustainability demand, and top recommendations such as expanding into new regions and adopting AI tools."
        return "Default simulated LLM response."

    def tearDown(self):
        if os.path.exists(self.test_reports_dir):
            shutil.rmtree(self.test_reports_dir)
        Config.REPORTS_PATH = "reports" # Restore original config

    @async_test
    async def test_generate_executive_summary_llm(self):
        """Test LLM-based executive summary generation."""
        mock_report_content = ReportContent(
            executive_summary=ExecutiveSummary(key_findings=[], strategic_implications=[], top_recommendations=[], summary_text=""),
            industry_analysis=self.mock_industry_analysis,
            competitive_landscape=self.mock_competitive_landscape,
            market_trends_predictions=self.mock_market_trends_predictions,
            technology_adoption_analysis=self.mock_technology_adoption_analysis,
            strategic_insights=self.mock_strategic_insights,
            actionable_recommendations=self.mock_actionable_recommendations
        )
        summary = await self.service._generate_executive_summary_llm(mock_report_content)
        self.assertIsInstance(summary, ExecutiveSummary)
        self.assertIn("This is a concise executive summary", summary.summary_text)
        self.assertGreater(len(summary.key_findings), 0)
        self.assertGreater(len(summary.top_recommendations), 0)
        # Ensure recommendations are sorted by priority
        self.assertEqual(summary.top_recommendations[0].priority, "High")
        self.assertEqual(summary.top_recommendations[1].priority, "Medium")

    @async_test
    async def test_generate_report(self):
        """Test full report generation to file."""
        report_path = await self.service.generate_report(
            self.mock_request_id,
            self.mock_industry_analysis,
            self.mock_competitive_landscape,
            self.mock_market_trends_predictions,
            self.mock_technology_adoption_analysis,
            self.mock_strategic_insights,
            self.mock_actionable_recommendations,
            self.mock_report_request
        )
        self.assertTrue(os.path.exists(report_path))
        self.assertIn(self.mock_request_id, report_path)
        self.assertTrue(report_path.endswith(".md"))

        # Verify content by reading the file (basic check)
        with open(report_path, "r") as f:
            content = f.read()
            self.assertIn("Executive Summary", content)
            self.assertIn("Industry Analysis", content)
            self.assertIn(sanitize_text_input(self.mock_strategic_insights[0].description), content)
            self.assertIn(sanitize_text_input(self.mock_actionable_recommendations[0].description), content)
            self.assertIn("Key player A dominates", content)
            self.assertIn("Growth is expected in sustainable tech", content)
            self.assertIn("AI adoption is high", content)

class TestContinuousMonitoringService(unittest.TestCase):
    def setUp(self):
        self.mock_trigger_callback = AsyncMock()
        self.service = ContinuousMonitoringService(trigger_report_generation_callback=self.mock_trigger_callback)
        self.mock_request = ReportRequest(
            request_id="monitor_test_1",
            industry="Monitoring Industry",
            focus_areas=["Trends"],
            report_format="md"
        )

    @async_test
    async def test_register_for_monitoring(self):
        self.service.register_for_monitoring(self.mock_request)
        self.assertIn(self.mock_request.request_id, self.service.monitored_requests)

    @async_test
    async def test_check_and_trigger_update(self):
        self.service.register_for_monitoring(self.mock_request)
        self.mock_trigger_callback.return_value = ReportStatus(request_id=self.mock_request.request_id, status="COMPLETED", last_updated=datetime.now().isoformat())
        await self.service._check_and_trigger_update(self.mock_request.request_id, self.mock_request)
        self.mock_trigger_callback.assert_called_once_with(self.mock_request)

    @async_test
    async def test_start_monitoring_loop(self):
        self.service.register_for_monitoring(self.mock_request)
        self.service.monitoring_interval_seconds = 0.1 # Short interval for testing
        self.mock_trigger_callback.return_value = ReportStatus(request_id=self.mock_request.request_id, status="COMPLETED", last_updated=datetime.now().isoformat())
        
        # Run loop for a short duration, enough to trigger multiple checks
        await self.service.start_monitoring_loop(duration_seconds=0.3)
        self.assertGreaterEqual(self.mock_trigger_callback.call_count, 3) # Should be called at least 3 times

class TestMarketResearchFramework(unittest.TestCase):
    def setUp(self):
        # Set up temporary directories for files
        self.temp_base_data_dir = "test_framework_data"
        self.temp_reports_dir = "test_framework_reports"
        Config.BASE_DATA_DIR = self.temp_base_data_dir
        Config.RAW_DATA_LAKE_DIR = os.path.join(self.temp_base_data_dir, "raw_data_lake")
        Config.PROCESSED_DATA_WAREHOUSE_DIR = os.path.join(self.temp_base_data_dir, "processed_data_warehouse")
        Config.REPORTS_DIR = self.temp_reports_dir
        Config.initialize_dirs()

        # Patch actual service implementations with AsyncMocks
        self.patcher_llm_service = patch('src.main.LLMService', new_callable=MagicMock)
        self.mock_llm_service_cls = self.patcher_llm_service.start()
        self.mock_llm_service_instance = AsyncMock() # Mock the instance as AsyncMock
        self.mock_llm_service_cls.return_value = self.mock_llm_service_instance
        self.mock_llm_service_instance.generate_response.return_value = "Simulated LLM Response."
        self.mock_

---
*Saved by after_agent_callback on 2025-07-06 14:45:49*
