# Workflow Execution Summary

## ✅ Final Status: WorkflowStatus.COMPLETED

## 📊 Execution Metrics
- **Success**: True
- **Execution Time**: 320.22 seconds
- **Total Agents**: 2
- **Agents Executed**: 8
- **Agents with Outputs**: 8

## 🤖 Agent Execution Order
1. **RequirementAnalyzer** - ✅ Completed
2. **ArchitecturalDesigner** - ✅ Completed
3. **CodeGenerator** - ✅ Completed
4. **PerformanceReviewer** - ✅ Completed
5. **QualityReviewer** - ✅ Completed
6. **SecurityReviewer** - ✅ Completed
7. **CodeRefactorer** - ✅ Completed
8. **DocumentationGenerator** - ✅ Completed

## 📝 Final Response
## Requirements Analysis

This report provides a requirements analysis based on the user's request for a "simple test analysis report" and the content of the provided `project_requirements.txt` file, augmented with general best practices derived from `coding_standards.docx`.

### Functional Requirements
- The core functional requirement is to process and manage simple text content, as indicated by the placeholder "this is a test file" in `project_requirements.txt`. This implies capabilities such as:
    - Storing text data.
    - Retrieving stored text data.

### Non-Functional Requirements
- **Performance requirements:**
    - The system should be responsive in storing and retrieving text content, even with moderate volumes.
    - Operations should complete within acceptable timeframes (specific metrics to be defined upon clarification of usage patterns).
- **Security requirements:**
    - The text content should be protected from unauthorized access, modification, or deletion.
    - Data integrity must be maintained.
- **Scalability requirements:**
    - The system should be designed to accommodate future growth in text volume and potentially an increased number of users without significant architectural changes.
- **Usability requirements:**
    - Any user interface for interacting with the text (e.g., input, display) should be intuitive and easy for the target users to understand and operate.
    - Documentation (e.g., user manuals, API documentation) should be clear and comprehensive, adhering to standards like PEP 257 and potentially external guides such as Google's Python style guide for maintainability.

### Technical Constraints
- **Technology stack preferences:**
    - Python is the preferred programming language for development.
    - Adherence to Python Enhancement Proposals (PEPs), including PEP 8 (Style Guide), PEP 20 (Zen of Python), and PEP 257 (Docstring Conventions), is mandatory for all code.
    - Type hinting (PEP 484) should be considered for improved code clarity and maintainability.
- **Platform constraints:**
    - Development environments should support Python and integrate with code inspection tools (e.g., PyCharm, Atom-pep8, Pylint, Flake8).
    - Source code management must utilize Git for version control.
    - Virtual environments (e.g., `venv`, `conda`) are required for dependency management and project encapsulation.
- **Integration requirements:**
    - The system should integrate with a version control system (Git).
    - Consideration for automated documentation generation tools (e.g., Sphinx, Read The Docs) is recommended for larger projects.

### Assumptions and Clarifications
- **Assumptions made:**
    - The `project_requirements.txt` file, while minimal, serves as a starting point for a typical software development project where a more detailed set of requirements would eventually be provided.
    - The "simple test analysis report" is intended to demonstrate a structured approach to requirements engineering, applying general best practices.
    - The text content is non-sensitive in this initial phase, but security measures should be considered for future expansions.
    - The project will follow good coding practices, including comprehensive documentation, consistent naming conventions, and modular organization, as outlined in `coding_standards.docx`.
- **Questions that need clarification:**
    - What are the specific use cases and business objectives for processing and managing this "text content"?
    - What is the anticipated volume and format of the text data?
    - Are there specific performance targets (e.g., response times, throughput) or security certifications/compliance requirements?
    - Who are the end-users, and what is their technical proficiency level?
    - What are the deployment environment specifics (e.g., operating system, cloud platform, on-premise)?

### Risk Assessment
- **Potential technical risks:**
    - **Ambiguous Requirements:** The current requirement "this is a test file" is highly vague, leading to potential misinterpretation, scope creep, or rework if detailed requirements are not subsequently gathered.
    - **Poor Code Quality & Maintainability:** Without strict adherence to coding standards (PEP 8, PEP 257) and documentation, the codebase could become difficult to understand, maintain, and extend, increasing future development costs.
    - **Lack of Reproducibility:** Failure to use virtual environments could lead to dependency conflicts and make it difficult to reproduce the development or deployment environment.
    - **Collaboration Challenges:** Inconsistent project organization or inadequate version control practices (e.g., not using Git effectively) could hinder team collaboration and lead to lost changes.
- **Mitigation strategies:**
    - **Requirements Elaboration:** Immediately initiate detailed requirements gathering sessions with stakeholders to define specific functionalities, data structures, and user interactions.
    - **Automated Code Quality Checks:** Integrate automated linters (Pylint, Flake8) and formatters (Python Black) into the CI/CD pipeline and developer IDEs to enforce coding standards.
    - **Mandatory Documentation:** Enforce a policy requiring comprehensive docstrings for all modules, classes, functions, and methods, along with a well-maintained `README.md` and project-level documentation.
    - **Standardized Development Environment:** Mandate the use of virtual environments for all development work and ensure `requirements.txt` is always updated.
    - **Version Control Best Practices:** Establish and enforce Git branching strategies (e.g., Git Flow) and commit message conventions, along with regular code reviews.## System Architecture Design

### High-Level Architecture

The system will adopt a **Layered Architecture** with principles of **Clean Architecture** to ensure separation of concerns, testability, and maintainability, even for a "simple" initial requirement. This approach allows for easy evolution and scaling by swapping components without impacting core business logic.

*   **Overall System Design:** A single, self-contained application service primarily focused on text content management.
*   **Architecture Pattern:** Layered Architecture adhering to Clean Architecture principles.

**Core Layers:**
1.  **Presentation/API Layer:** Handles external requests (e.g., HTTP), translates them into application commands, and returns responses. It should be thin, focusing on communication protocols.
2.  **Application Layer (Use Cases):** Contains the application-specific business rules. It orchestrates the flow of data to and from the domain entities and delegates persistence operations to the infrastructure layer. It defines *what* the application does.
3.  **Domain Layer (Entities & Business Rules):** Encapsulates the core business logic and entities. It defines *the rules of the business*. This layer is completely independent of external concerns like databases or UI.
4.  **Infrastructure Layer:** Provides implementations for interfaces defined in the Application/Domain layers. This includes data persistence (e.g., file system, database), external service integrations, and other technical details.

**Visual Representation (Conceptual):**

```
+---------------------+
| Presentation/API    |
| (e.g., FastAPI)     |
+---------------------+
          | Requests / Responses
          V
+---------------------+
| Application Layer   |
| (Use Cases, Services)|
+---------------------+
          | Data / Operations
          V
+---------------------+
| Domain Layer        |
| (Entities, Core Logic)|
+---------------------+
          | Interfaces (Ports)
          V
+---------------------+
| Infrastructure Layer|
| (Repositories, DBs, |
|  File System, External Services)
+---------------------+
```

### Component Design

**Core Components and Responsibilities:**

1.  **`main.py` (Entry Point):**
    *   Initializes the FastAPI application.
    *   Configures dependency injection.
    *   Registers API routes.

2.  **Presentation/API Layer (e.g., `app/api/`):**
    *   **`text_controller.py`:**
        *   **Responsibility:** Exposes RESTful API endpoints for text content operations (e.g., `/text/`, `/text/{id}`).
        *   **Interface:** HTTP endpoints.
        *   **Contracts:** Defines request/response models using Pydantic for data validation and serialization.
        *   **Interaction:** Receives HTTP requests, calls methods on `TextService` (Application Layer), and returns HTTP responses.

3.  **Application Layer (e.g., `app/application/`):**
    *   **`text_service.py`:**
        *   **Responsibility:** Orchestrates application-specific use cases for text content. Contains the "what" of the application's behavior.
        *   **Interface:** Methods like `create_text_content(content: str) -> Text`, `get_text_content(text_id: str) -> Text`.
        *   **Contracts:** Input/Output DTOs (Data Transfer Objects) or directly using Domain Entities.
        *   **Interaction:** Calls methods on `ITextRepository` (Domain Layer interface) to perform persistence operations, and interacts with `Text` (Domain Entity).
        *   **Dependencies:** Injects `ITextRepository`.

4.  **Domain Layer (e.g., `app/domain/`):**
    *   **`text.py`:**
        *   **Responsibility:** Represents the `Text` entity with its attributes (e.g., `id`, `content`, `created_at`, `updated_at`) and any core business rules related to text content (e.g., validation rules for content length, immutability of certain fields).
        *   **Interface:** Properties and methods defined on the `Text` class.
    *   **`interfaces.py`:**
        *   **`ITextRepository` (Interface/Abstract Base Class):**
            *   **Responsibility:** Defines the contract for data persistence operations for `Text` entities. This is a "port" in Clean Architecture.
            *   **Interface:** Abstract methods like `save(text: Text) -> Text`, `find_by_id(text_id: str) -> Optional[Text]`.
            *   **Contracts:** Operates on `Text` domain entities.

5.  **Infrastructure Layer (e.g., `app/infrastructure/`):**
    *   **`file_text_repository.py`:**
        *   **Responsibility:** Implements the `ITextRepository` interface using the file system as a storage mechanism.
        *   **Interaction:** Reads from and writes to specific files based on `Text` IDs.
        *   **Data Flow:** Transforms `Text` entities to file content (e.g., JSON, plain text) and vice-versa. Handles file I/O operations and error handling specific to file system access.
    *   **`config.py`:**
        *   **Responsibility:** Manages application configurations (e.g., storage paths).
    *   **`dependencies.py`:**
        *   **Responsibility:** Manages dependency injection, providing concrete implementations (e.g., `FileTextRepository`) for interfaces (e.g., `ITextRepository`).

**Data Flow Between Components:**

1.  **API Request:** An HTTP request (e.g., `POST /text/` with content in body) arrives at `TextController`.
2.  **Controller to Service:** `TextController` validates the request body (using Pydantic model), extracts data, and calls the appropriate method on `TextService` (e.g., `text_service.create_text_content(content)`).
3.  **Service to Domain:** `TextService` creates a `Text` domain entity instance.
4.  **Service to Repository (Interface):** `TextService` calls a method on its injected `ITextRepository` instance (e.g., `text_repository.save(text)`).
5.  **Repository (Implementation) to Storage:** The concrete `FileTextRepository` implementation handles the actual file I/O operations (e.g., writing the `Text` content to a file on disk).
6.  **Repository to Service:** The `FileTextRepository` returns the persisted `Text` entity to `TextService`.
7.  **Service to Controller:** `TextService` returns the `Text` entity to `TextController`.
8.  **Controller to API Response:** `TextController` serializes the `Text` entity into an HTTP response (e.g., JSON) and sends it back to the client.

### Technology Stack

*   **Programming Language:** Python 3.9+ (as per requirements).
*   **Web Framework:**
    *   **FastAPI:** Chosen for its high performance, automatic data validation (via Pydantic), automatic API documentation (OpenAPI/Swagger UI), and excellent support for type hinting, aligning with PEPs and modern Python best practices.
*   **Data Validation/Serialization:**
    *   **Pydantic:** Integrated with FastAPI for defining request/response models and ensuring data integrity.
*   **Dependency Injection:**
    *   FastAPI's built-in dependency injection system will be leveraged.
*   **Databases and Storage Solutions:**
    *   **Initial:** File System (for "simple text content" as indicated by `project_requirements.txt`). Text content will be stored in designated files, with filenames potentially mapping to IDs.
    *   **Future/Scalability Option:** For more complex data management or higher volume, a lightweight NoSQL document database (e.g., MongoDB, TinyDB for local development/simple cases) or a relational database (e.g., PostgreSQL with SQLAlchemy) could be easily swapped in by creating new `ITextRepository` implementations.
*   **Testing Frameworks:**
    *   **Pytest:** For unit, integration, and end-to-end testing.
    *   **HTTPX:** For testing FastAPI endpoints.
*   **Code Quality & Linters:**
    *   **Black:** Opinionated code formatter (auto-fixes PEP 8).
    *   **Flake8:** Linter to enforce coding style and detect errors.
    *   **MyPy:** Static type checker to enforce PEP 484 type hinting.
    *   **Pylint:** Comprehensive code analysis tool.
*   **Documentation:**
    *   **FastAPI's auto-generated OpenAPI/Swagger UI:** For API documentation.
    *   **Sphinx:** For comprehensive project documentation (e.g., developer guides, architecture docs).
    *   **PEP 257:** Adherence to docstring conventions for internal code documentation.
*   **Version Control:**
    *   **Git:** As mandated.
*   **Dependency Management:**
    *   **`venv` (Python Virtual Environments):** As mandated, with `requirements.txt` for explicit dependency listing.
*   **Infrastructure and Deployment Considerations:**
    *   **Docker:** For containerizing the application, ensuring consistent environments across development, testing, and production.
    *   **Cloud Platform (Optional for simple cases):** Could be deployed on platforms like AWS ECS/EKS, Google Cloud Run/GKE, or Azure Container Apps for scalability and managed services.
    *   **CI/CD:** GitHub Actions or GitLab CI/CD for automated testing, linting, and deployment.

### Design Patterns

*   **Architectural Patterns:**
    *   **Layered Architecture:** Clear separation into Presentation, Application, Domain, and Infrastructure layers.
    *   **Clean Architecture (Ports and Adapters):** Emphasizes dependency inversion, ensuring the core domain logic is independent of external frameworks or databases. `ITextRepository` serves as a "port," and `FileTextRepository` is an "adapter."
*   **Design Patterns for Implementation:**
    *   **Repository Pattern:** Abstracts the data access layer, allowing the Application layer to interact with data stores through a consistent interface (`ITextRepository`).
    *   **Dependency Injection:** Manages the creation and provision of dependencies (e.g., injecting `ITextRepository` concrete implementation into `TextService`). FastAPI's dependency injection system simplifies this.
    *   **Factory Pattern (Implicit):** When choosing between different repository implementations (e.g., `FileTextRepository` vs. `DatabaseTextRepository`), a factory or configuration-driven approach can select the appropriate one.
    *   **DTO (Data Transfer Object):** Pydantic models serve as DTOs for data ingress/egress in the API layer, separating external data representation from internal domain entities.
    *   **Strategy Pattern (Potential):** If different "analysis" strategies for text are introduced later, they could be encapsulated as strategies.

### Quality Attributes

*   **Scalability:**
    *   **Stateless Design:** The API service will be stateless, allowing for easy horizontal scaling by running multiple instances behind a load balancer.
    *   **Component Modularity:** The layered architecture and Repository pattern allow for easy swapping of the persistence layer (e.g., from file system to a distributed database like Cassandra or a managed service like DynamoDB) without changing core business logic.
    *   **Containerization:** Docker allows for efficient resource utilization and orchestration (e.g., Kubernetes) for scaling out.
    *   **Python's GIL:** Acknowledged, but for I/O-bound "simple text content" operations, it's less of a bottleneck, and multiple Python processes can still scale horizontally.
*   **Security:**
    *   **Input Validation:** Pydantic models at the API layer provide automatic schema validation, preventing malformed requests.
    *   **Data Integrity:** Validation rules can be enforced in the Domain layer for `Text` entities. The chosen storage mechanism will ensure data is written and read correctly.
    *   **Access Control (Future):** Authentication (e.g., JWT) and Authorization (e.g., Role-Based Access Control) can be implemented as middlewares or FastAPI dependencies at the Presentation layer to protect endpoints.
    *   **Least Privilege:** Ensure the application has only the necessary file system permissions for its operations.
    *   **Error Handling:** Graceful error handling to prevent information leakage through detailed error messages.
*   **Performance Optimizations:**
    *   **Lightweight Framework:** FastAPI provides high performance due to its ASGI nature and Pydantic integration.
    *   **Efficient I/O:** For file-based storage, optimized Python I/O operations will be used.
    *   **Caching (Future):** For frequently accessed text content, in-memory caching (e.g., LRU cache) or a distributed cache (e.g., Redis) can be introduced at the Application layer.
    *   **Asynchronous Operations:** FastAPI supports `async`/`await` which can be leveraged if I/O operations become significant (e.g., large files, network calls to other services).
*   **Maintainability Features:**
    *   **Clean Architecture:** Clear separation of concerns, making code easier to understand, modify, and extend. Changes in one layer have minimal impact on others.
    *   **SOLID Principles:** Adherence to Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles.
    *   **Comprehensive Documentation:** Auto-generated API docs, PEP 257 compliant docstrings, and Sphinx for project-level documentation.
    *   **Strict Code Quality Standards:** Enforcement of PEP 8 (Black), type hinting (MyPy), and linting (Flake8, Pylint) ensures consistent, readable, and less error-prone code.
    *   **High Testability:** The modular design with clear interfaces (e.g., `ITextRepository`) makes unit testing components in isolation straightforward by mocking dependencies.
    *   **Virtual Environments:** Ensures project dependencies are isolated and reproducible, simplifying onboarding and deployment.## Code Implementation

### Project Structure
```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── modules/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── text_controller.py
│       ├── application/
│       │   ├── __init__.py
│       │   └── text_service.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── text.py
│       │   └── interfaces.py
│       └── infrastructure/
│           ├── __init__.py
│           ├── config.py
│           ├── dependencies.py
│           └── file_text_repository.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── modules/
│       ├── __init__.py
│       ├── api/
│       │   └── test_text_controller.py
│       ├── application/
│       │   └── test_text_service.py
│       ├── domain/
│       │   └── test_text.py
│       └── infrastructure/
│           └── test_file_text_repository.py
├── .gitignore
├── pyproject.toml
└── requirements.txt
```

### Main Implementation
```python
# src/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.modules.api.text_controller import router as text_router
from src.modules.infrastructure.config import AppConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    config = AppConfig()
    # Create storage directory if it doesn't exist
    config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Application startup: Storage directory ensured at {config.STORAGE_DIR}")
    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title="Simple Text Analysis Report API",
    description="A basic API for managing text content, demonstrating Clean Architecture principles.",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routers
app.include_router(text_router, prefix="/api/v1")

@app.get("/health", summary="Health Check")
async def health_check() -> dict[str, str]:
    """
    Checks the health of the application.

    Returns:
        A dictionary indicating the application's status.
    """
    return {"status": "healthy", "message": "API is running smoothly!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

```

### Supporting Modules

```python
# src/modules/domain/text.py
import datetime
import uuid
from typing import Self

from pydantic import BaseModel, Field


class Text(BaseModel):
    """
    Represents a core text entity in the domain.

    Attributes:
        id (str): Unique identifier for the text.
        content (str): The actual text content.
        created_at (datetime.datetime): Timestamp when the text was created.
        updated_at (datetime.datetime): Timestamp when the text was last updated.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., min_length=1, max_length=10000)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    def update_content(self, new_content: str) -> Self:
        """
        Updates the content of the text and sets the updated_at timestamp.

        Args:
            new_content (str): The new text content.

        Returns:
            Self: The updated Text instance.
        """
        self.content = new_content
        self.updated_at = datetime.datetime.utcnow()
        return self

    class Config:
        """Pydantic model configuration."""
        json_encoders = {datetime.datetime: lambda dt: dt.isoformat()}
        populate_by_name = True # Allow population by field name for better compatibility
        from_attributes = True # New in Pydantic V2, replaces allow_population_by_field_name

```

```python
# src/modules/domain/interfaces.py
import abc
from typing import Optional

from src.modules.domain.text import Text


class ITextRepository(abc.ABC):
    """
    Abstract Base Class (ABC) defining the contract for text content persistence.
    This is a "Port" in Clean Architecture.
    """

    @abc.abstractmethod
    def save(self, text: Text) -> Text:
        """
        Saves a Text entity to the persistence layer.

        Args:
            text (Text): The Text entity to save.

        Returns:
            Text: The saved Text entity (potentially with updated attributes like ID or timestamps).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_id(self, text_id: str) -> Optional[Text]:
        """
        Retrieves a Text entity by its unique identifier.

        Args:
            text_id (str): The unique ID of the text to retrieve.

        Returns:
            Optional[Text]: The Text entity if found, otherwise None.
        """
        raise NotImplementedError

```

```python
# src/modules/infrastructure/config.py
import os
from pathlib import Path


class AppConfig:
    """
    Configuration settings for the application.
    """
    # Base directory for storing text files
    STORAGE_DIR: Path = Path(os.getenv("STORAGE_DIR", "./data/text_content"))

    def __init__(self) -> None:
        """Initializes AppConfig and ensures storage directory exists."""
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

```

```python
# src/modules/infrastructure/file_text_repository.py
import json
import logging
from pathlib import Path
from typing import Optional

from src.modules.domain.interfaces import ITextRepository
from src.modules.domain.text import Text
from src.modules.infrastructure.config import AppConfig

logger = logging.getLogger(__name__)


class FileTextRepository(ITextRepository):
    """
    Concrete implementation of ITextRepository using the file system for storage.
    Each Text entity is stored as a JSON file, named after its ID.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initializes the FileTextRepository.

        Args:
            config (AppConfig): Application configuration.
        """
        self.storage_dir = config.STORAGE_DIR
        logger.info(f"FileTextRepository initialized. Storage directory: {self.storage_dir}")

    def _get_file_path(self, text_id: str) -> Path:
        """
        Constructs the file path for a given text ID.

        Args:
            text_id (str): The ID of the text.

        Returns:
            Path: The full file path.
        """
        return self.storage_dir / f"{text_id}.json"

    def save(self, text: Text) -> Text:
        """
        Saves a Text entity to a JSON file.

        Args:
            text (Text): The Text entity to save.

        Returns:
            Text: The saved Text entity.
        """
        file_path = self._get_file_path(text.id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text.model_dump_json(indent=2))
            logger.info(f"Text '{text.id}' saved to {file_path}")
            return text
        except IOError as e:
            logger.error(f"Error saving text '{text.id}' to {file_path}: {e}")
            raise RuntimeError(f"Failed to save text content: {e}") from e

    def find_by_id(self, text_id: str) -> Optional[Text]:
        """
        Retrieves a Text entity by reading its corresponding JSON file.

        Args:
            text_id (str): The unique ID of the text to retrieve.

        Returns:
            Optional[Text]: The Text entity if found, otherwise None.
        """
        file_path = self._get_file_path(text_id)
        if not file_path.exists():
            logger.info(f"Text '{text_id}' not found at {file_path}")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            text = Text.model_validate(data)
            logger.info(f"Text '{text_id}' loaded from {file_path}")
            return text
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading text '{text_id}' from {file_path}: {e}")
            raise RuntimeError(f"Failed to load text content: {e}") from e

```

```python
# src/modules/application/text_service.py
import logging
from typing import Optional

from src.modules.domain.interfaces import ITextRepository
from src.modules.domain.text import Text

logger = logging.getLogger(__name__)


class TextService:
    """
    Application service for managing text content.
    Orchestrates business logic and interacts with the domain and infrastructure layers.
    """

    def __init__(self, text_repository: ITextRepository) -> None:
        """
        Initializes the TextService with a text repository.

        Args:
            text_repository (ITextRepository): The repository for Text entities.
        """
        self.text_repository = text_repository
        logger.info("TextService initialized.")

    def create_text_content(self, content: str) -> Text:
        """
        Creates a new Text entity and persists it.

        Args:
            content (str): The raw text content to be stored.

        Returns:
            Text: The newly created Text entity.
        """
        try:
            new_text = Text(content=content)
            saved_text = self.text_repository.save(new_text)
            logger.info(f"New text content created with ID: {saved_text.id}")
            return saved_text
        except Exception as e:
            logger.exception(f"Failed to create text content: {e}")
            raise

    def get_text_content(self, text_id: str) -> Optional[Text]:
        """
        Retrieves a Text entity by its ID.

        Args:
            text_id (str): The unique ID of the text to retrieve.

        Returns:
            Optional[Text]: The Text entity if found, otherwise None.
        """
        try:
            text = self.text_repository.find_by_id(text_id)
            if text:
                logger.info(f"Retrieved text content with ID: {text_id}")
            else:
                logger.info(f"Text content with ID '{text_id}' not found.")
            return text
        except Exception as e:
            logger.exception(f"Failed to retrieve text content with ID '{text_id}': {e}")
            raise

```

```python
# src/modules/infrastructure/dependencies.py
from functools import lru_cache

from src.modules.application.text_service import TextService
from src.modules.infrastructure.config import AppConfig
from src.modules.infrastructure.file_text_repository import FileTextRepository


@lru_cache()
def get_app_config() -> AppConfig:
    """
    Provides a singleton instance of the application configuration.
    """
    return AppConfig()

def get_text_repository(config: AppConfig = get_app_config()) -> FileTextRepository:
    """
    Provides a concrete instance of ITextRepository (FileTextRepository).
    """
    return FileTextRepository(config)

def get_text_service(
    text_repository: FileTextRepository = get_text_repository(),
) -> TextService:
    """
    Provides an instance of TextService, injecting its dependencies.
    """
    return TextService(text_repository)

```

```python
# src/modules/api/text_controller.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.modules.application.text_service import TextService
from src.modules.domain.text import Text
from src.modules.infrastructure.dependencies import get_text_service


class CreateTextRequest(BaseModel):
    """Request model for creating new text content."""
    content: str = Field(..., min_length=1, max_length=10000,
                         example="This is a simple test analysis report content.")


class TextResponse(BaseModel):
    """Response model for text content."""
    id: str
    content: str
    created_at: str
    updated_at: str

    model_config = { # New in Pydantic V2, replaces Config
        "json_encoders": {
            # This is handled by Text model's config, but good to have consistency
            # if we were transforming directly here
        },
        "from_attributes": True # Allow population from Text domain model attributes
    }

router = APIRouter()


@router.post(
    "/text",
    response_model=TextResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Text Content",
    description="Creates a new piece of text content and stores it.",
)
async def create_text_content_endpoint(
    request: CreateTextRequest,
    text_service: Annotated[TextService, Depends(get_text_service)],
) -> TextResponse:
    """
    Endpoint to create new text content.

    Args:
        request (CreateTextRequest): The request body containing the text content.
        text_service (TextService): Dependency-injected text service.

    Returns:
        TextResponse: The created text content with its ID and timestamps.

    Raises:
        HTTPException: If there's an internal server error during creation.
    """
    try:
        text = text_service.create_text_content(request.content)
        return TextResponse.model_validate(text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create text content: {e}",
        )


@router.get(
    "/text/{text_id}",
    response_model=TextResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Text Content by ID",
    description="Retrieves a specific piece of text content by its unique ID.",
)
async def get_text_content_endpoint(
    text_id: str,
    text_service: Annotated[TextService, Depends(get_text_service)],
) -> TextResponse:
    """
    Endpoint to retrieve text content by ID.

    Args:
        text_id (str): The unique ID of the text content to retrieve.
        text_service (TextService): Dependency-injected text service.

    Returns:
        TextResponse: The retrieved text content.

    Raises:
        HTTPException: If the text content is not found (404) or an internal error occurs (500).
    """
    try:
        text = text_service.get_text_content(text_id)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Text content with ID '{text_id}' not found.",
            )
        return TextResponse.model_validate(text)
    except HTTPException:
        # Re-raise HTTPException if it's already a 404 from above
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve text content: {e}",
        )

```

### Unit Tests

```python
# tests/test_main.py
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check() -> None:
    """
    Test the health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "API is running smoothly!"}

@patch('src.modules.infrastructure.config.AppConfig.STORAGE_DIR')
def test_lifespan_creates_directory(mock_storage_dir) -> None:
    """
    Test that the lifespan event creates the storage directory.
    """
    # Simulate a clean start
    mock_storage_dir.mkdir.reset_mock()
    with TestClient(app) as test_client:
        # Client context manager will trigger lifespan events
        response = test_client.get("/health")
        assert response.status_code == 200
    mock_storage_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)

```

```python
# tests/modules/domain/test_text.py
import datetime
import uuid

from src.modules.domain.text import Text


def test_text_creation() -> None:
    """
    Test Text entity creation with default values.
    """
    content = "Hello World!"
    text = Text(content=content)

    assert isinstance(text.id, str)
    assert len(text.id) > 0 # UUIDs are non-empty strings
    assert uuid.UUID(text.id, version=4) # Ensure it's a valid UUID
    assert text.content == content
    assert isinstance(text.created_at, datetime.datetime)
    assert isinstance(text.updated_at, datetime.datetime)
    assert text.created_at <= datetime.datetime.utcnow()
    assert text.updated_at <= datetime.datetime.utcnow()
    assert text.created_at == text.updated_at # Should be same on initial creation

def test_text_update_content() -> None:
    """
    Test updating text content.
    """
    text = Text(content="Original content")
    original_updated_at = text.updated_at

    new_content = "Updated content here."
    updated_text = text.update_content(new_content)

    assert updated_text.content == new_content
    assert updated_text.id == text.id # ID should remain unchanged
    assert updated_text.created_at == text.created_at # Created_at should remain unchanged
    assert updated_text.updated_at > original_updated_at # Updated_at should be more recent

def test_text_serialization_deserialization() -> None:
    """
    Test Text entity serialization to JSON and deserialization back.
    """
    original_text = Text(content="Some test content.")
    json_data = original_text.model_dump_json()

    loaded_text = Text.model_validate_json(json_data)

    assert loaded_text.id == original_text.id
    assert loaded_text.content == original_text.content
    assert loaded_text.created_at == original_text.created_at
    assert loaded_text.updated_at == original_text.updated_at
    assert loaded_text == original_text # Pydantic model equality check

```

```python
# tests/modules/infrastructure/test_file_text_repository.py
import json
import os
import shutil
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.modules.domain.text import Text
from src.modules.infrastructure.config import AppConfig
from src.modules.infrastructure.file_text_repository import FileTextRepository


@pytest.fixture(scope="function")
def temp_storage_dir(tmp_path: Path) -> Path:
    """
    Provides a temporary directory for file storage and ensures it's clean.
    """
    temp_dir = tmp_path / "test_storage"
    temp_dir.mkdir()
    yield temp_dir
    # Cleanup after test
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

@pytest.fixture
def mock_app_config(temp_storage_dir: Path) -> Mock:
    """
    Provides a mock AppConfig instance with a temporary storage directory.
    """
    mock_config = Mock(spec=AppConfig)
    mock_config.STORAGE_DIR = temp_storage_dir
    return mock_config

@pytest.fixture
def file_repo(mock_app_config: Mock) -> FileTextRepository:
    """
    Provides an instance of FileTextRepository with the mock config.
    """
    return FileTextRepository(mock_app_config)

def test_save_text(file_repo: FileTextRepository, temp_storage_dir: Path) -> None:
    """
    Test saving a Text entity to a file.
    """
    test_text = Text(content="This is content to save.")
    saved_text = file_repo.save(test_text)

    assert saved_text == test_text # Ensure the returned text is the same
    file_path = temp_storage_dir / f"{test_text.id}.json"
    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["id"] == test_text.id
    assert data["content"] == test_text.content

def test_find_by_id_found(file_repo: FileTextRepository, temp_storage_dir: Path) -> None:
    """
    Test finding an existing Text entity by ID.
    """
    test_text = Text(content="Content for retrieval.")
    # Manually save the file to simulate existing data
    file_path = temp_storage_dir / f"{test_text.id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(test_text.model_dump_json(indent=2))

    found_text = file_repo.find_by_id(test_text.id)
    assert found_text == test_text

def test_find_by_id_not_found(file_repo: FileTextRepository) -> None:
    """
    Test finding a non-existent Text entity by ID.
    """
    non_existent_id = "non_existent_id"
    found_text = file_repo.find_by_id(non_existent_id)
    assert found_text is None

def test_save_io_error(file_repo: FileTextRepository, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test error handling during save due to IOError.
    """
    # Simulate an IOError during file writing
    def mock_open_fail(*args, **kwargs):
        raise IOError("Simulated disk full error")

    monkeypatch.setattr("builtins.open", mock_open_fail)

    with pytest.raises(RuntimeError, match="Failed to save text content"):
        file_repo.save(Text(content="Will fail"))

def test_find_by_id_json_decode_error(file_repo: FileTextRepository, temp_storage_dir: Path) -> None:
    """
    Test error handling during find_by_id due to invalid JSON.
    """
    bad_json_text = Text(content="Invalid JSON content")
    file_path = temp_storage_dir / f"{bad_json_text.id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("this is not valid json {") # Write invalid JSON

    with pytest.raises(RuntimeError, match="Failed to load text content"):
        file_repo.find_by_id(bad_json_text.id)

```

```python
# tests/modules/application/test_text_service.py
from unittest.mock import Mock

import pytest

from src.modules.application.text_service import TextService
from src.modules.domain.interfaces import ITextRepository
from src.modules.domain.text import Text


@pytest.fixture
def mock_text_repository() -> Mock:
    """
    Provides a mock ITextRepository instance.
    """
    return Mock(spec=ITextRepository)

@pytest.fixture
def text_service(mock_text_repository: Mock) -> TextService:
    """
    Provides an instance of TextService with the mock repository.
    """
    return TextService(mock_text_repository)

def test_create_text_content_success(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test successful creation of text content.
    """
    mock_text_repository.save.return_value = Text(id="test-id", content="Some content")

    content = "New report data."
    created_text = text_service.create_text_content(content)

    mock_text_repository.save.assert_called_once()
    # Check that save was called with an instance of Text with the correct content
    args, kwargs = mock_text_repository.save.call_args
    assert isinstance(args[0], Text)
    assert args[0].content == content

    assert created_text.id == "test-id"
    assert created_text.content == "Some content"

def test_create_text_content_failure(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test failure during text content creation.
    """
    mock_text_repository.save.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError, match="DB error"):
        text_service.create_text_content("Content that will fail.")

def test_get_text_content_found(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test successful retrieval of text content by ID.
    """
    expected_text = Text(id="existing-id", content="Found content.")
    mock_text_repository.find_by_id.return_value = expected_text

    found_text = text_service.get_text_content("existing-id")

    mock_text_repository.find_by_id.assert_called_once_with("existing-id")
    assert found_text == expected_text

def test_get_text_content_not_found(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test retrieval of non-existent text content.
    """
    mock_text_repository.find_by_id.return_value = None

    found_text = text_service.get_text_content("non-existent-id")

    mock_text_repository.find_by_id.assert_called_once_with("non-existent-id")
    assert found_text is None

def test_get_text_content_failure(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test failure during text content retrieval.
    """
    mock_text_repository.find_by_id.side_effect = Exception("Network error")

    with pytest.raises(Exception, match="Network error"):
        text_service.get_text_content("some-id")

```

```python
# tests/modules/api/test_text_controller.py
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.application.text_service import TextService
from src.modules.domain.text import Text

client = TestClient(app)


@pytest.fixture
def mock_text_service() -> Mock:
    """
    Provides a mock TextService instance.
    """
    return Mock(spec=TextService)

@pytest.fixture(autouse=True)
def override_get_text_service(mock_text_service: Mock) -> None:
    """
    Overrides the get_text_service dependency for testing.
    """
    app.dependency_overrides[
        TextService
    ] = lambda: mock_text_service # Fastapi 0.100+ requires passing the class

    # If using earlier versions where get_text_service is directly overridden:
    # from src.modules.infrastructure.dependencies import get_text_service
    # app.dependency_overrides[get_text_service] = lambda: mock_text_service

    yield
    # Clean up overrides after test
    app.dependency_overrides = {}


def test_create_text_content_success(mock_text_service: Mock) -> None:
    """
    Test successful creation of text content via API.
    """
    test_content = "API test content."
    expected_text = Text(id="new-api-id", content=test_content)
    mock_text_service.create_text_content.return_value = expected_text

    response = client.post(
        "/api/v1/text",
        json={"content": test_content}
    )

    assert response.status_code == 201
    assert response.json()["id"] == "new-api-id"
    assert response.json()["content"] == test_content
    mock_text_service.create_text_content.assert_called_once_with(test_content)


def test_create_text_content_invalid_input() -> None:
    """
    Test API input validation for creating text content (empty content).
    """
    response = client.post(
        "/api/v1/text",
        json={"content": ""}
    )
    assert response.status_code == 422 # Unprocessable Entity for validation error
    assert "field_validation_error" in response.json()["detail"][0]["type"]

def test_create_text_content_internal_error(mock_text_service: Mock) -> None:
    """
    Test internal server error during text content creation.
    """
    mock_text_service.create_text_content.side_effect = RuntimeError("Something went wrong in service")

    response = client.post(
        "/api/v1/text",
        json={"content": "Content causing error"}
    )
    assert response.status_code == 500
    assert "Failed to create text content" in response.json()["detail"]


def test_get_text_content_success(mock_text_service: Mock) -> None:
    """
    Test successful retrieval of text content by ID via API.
    """
    text_id = "some-existing-id"
    expected_text = Text(id=text_id, content="Retrieved content.")
    mock_text_service.get_text_content.return_value = expected_text

    response = client.get(f"/api/v1/text/{text_id}")

    assert response.status_code == 200
    assert response.json()["id"] == text_id
    assert response.json()["content"] == "Retrieved content."
    mock_text_service.get_text_content.assert_called_once_with(text_id)

def test_get_text_content_not_found(mock_text_service: Mock) -> None:
    """
    Test retrieval of non-existent text content by ID via API.
    """
    text_id = "non-existent-id"
    mock_text_service.get_text_content.return_value = None

    response = client.get(f"/api/v1/text/{text_id}")

    assert response.status_code == 404
    assert "Text content with ID 'non-existent-id' not found." in response.json()["detail"]
    mock_text_service.get_text_content.assert_called_once_with(text_id)

def test_get_text_content_internal_error(mock_text_service: Mock) -> None:
    """
    Test internal server error during text content retrieval.
    """
    text_id = "error-id"
    mock_text_service.get_text_content.side_effect = Exception("Service layer error")

    response = client.get(f"/api/v1/text/{text_id}")

    assert response.status_code == 500
    assert "Failed to retrieve text content" in response.json()["detail"]
    mock_text_service.get_text_content.assert_called_once_with(text_id)

```

### Installation and Usage Instructions

```bash
# 1. Clone the repository (if applicable, assuming this is the project root)
# git clone <your-repo-url>
# cd <your-project-directory>

# 2. Create a Python Virtual Environment
python3 -m venv .venv

# 3. Activate the Virtual Environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 4. Install Dependencies
pip install -r requirements.txt

# 5. Define dependencies in requirements.txt
echo "fastapi==0.111.0" > requirements.txt
echo "uvicorn==0.30.1" >> requirements.txt
echo "pydantic==2.7.4" >> requirements.txt
echo "pydantic-settings==2.3.3" >> requirements.txt # For potential future config management
echo "python-dotenv==1.0.1" >> requirements.txt # For potential future .env support
echo "pytest==8.2.2" >> requirements.txt
echo "httpx==0.27.0" >> requirements.txt
echo "pytest-mock==3.14.0" >> requirements.txt

# 6. Run the Application
# The application will run on http://0.0.0.0:8000
# The API documentation will be available at http://0.0.0.0:8000/docs
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 7. Usage Examples (using curl)

# Health Check
curl http://localhost:8000/health

# Create a new text content
curl -X POST "http://localhost:8000/api/v1/text" \
     -H "Content-Type: application/json" \
     -d '{"content": "This is a simple analysis report for test case XYZ. All checks passed."}'

# Example Output (copy the "id" from the response for the next step):
# {"id": "your-generated-uuid", "content": "...", "created_at": "...", "updated_at": "..."}

# Get text content by ID (replace YOUR_TEXT_ID with the actual ID from the create response)
curl http://localhost:8000/api/v1/text/YOUR_TEXT_ID

# Get text content by a non-existent ID (will return 404)
curl http://localhost:8000/api/v1/text/non-existent-uuid

# 8. Run Tests
pytest
```## Performance Review Report

### Performance Score: 6/10

The system exhibits good architectural choices (FastAPI, Clean Architecture, Pydantic, async I/O support) for its API layer, which contribute positively to performance. However, the use of the file system as the primary persistence layer is a significant bottleneck that severely limits its performance under anything beyond very light load or for larger text volumes.

### Critical Performance Issues
- **File System Persistence Bottleneck:** The `FileTextRepository` performs direct disk I/O for every `save` and `find_by_id` operation.
    -   **High Latency:** Each request to create or retrieve text involves opening a file, reading/writing its content, and closing it. This is inherently slow compared to in-memory operations or optimized database access.
    -   **I/O Contention:** Under concurrent load, multiple requests trying to access or modify files simultaneously will lead to disk I/O contention, causing increased wait times and reduced throughput.
    -   **Lack of Concurrency Control:** While Python's `asyncio` handles I/O concurrency well at the application level, the underlying file system does not provide sophisticated concurrency control or transactional capabilities, which can lead to data corruption or race conditions if not carefully managed (though not explicitly present in the simple save/read).
    -   **Scalability Limit:** This approach does not scale well horizontally. If multiple instances of the application run, they would need access to a shared file system (e.g., NFS, EFS), which introduces its own latency, complexity, and potential for single points of failure.

### Optimization Opportunities
-   **Database Migration:** Transition from file system storage to a proper database (e.g., SQLite for simplicity, PostgreSQL/MongoDB for scalability). This would provide:
    -   Optimized I/O operations with connection pooling.
    -   Indexing for faster lookups (not directly applicable for primary key lookups but useful for future query patterns).
    -   Concurrency control, transactions, and robust error handling.
    -   Better horizontal scalability by connecting to a shared database cluster.
-   **Caching:** For frequently accessed text content, implement an in-memory cache (e.g., using `functools.lru_cache` for `get_text_content` in `TextService` or a dedicated caching layer like Redis for larger deployments). This would reduce repetitive disk I/O.
-   **Batch Operations (Future consideration):** If there are scenarios for saving/retrieving multiple texts at once, batching these operations could reduce the overhead per item.
-   **Asynchronous File I/O (Minor):** While FastAPI/Uvicorn already handle async for network I/O, explicit `aiofiles` could be considered for disk I/O within the repository if very large files were to be handled and blocking disk operations became a measurable bottleneck, though less impactful than changing the storage mechanism entirely.

### Algorithmic Analysis
-   **`Text` Entity (Domain Model):**
    -   `uuid.uuid4()` generation: O(1) time complexity.
    -   Pydantic model validation/serialization: O(L) where L is the length of the text content. Generally very efficient for typical string lengths.
-   **`FileTextRepository` (Persistence):**
    -   `save(text: Text)`: Time complexity is dominated by file writing and JSON serialization. O(L) where L is the length of `text.content`. This involves disk write operations.
    -   `find_by_id(text_id: str)`: Time complexity is dominated by file reading and JSON deserialization. O(L) where L is the length of `text.content`. This involves disk read operations.
    -   **Space Complexity:** O(L) for storing each text entity on disk, and O(L) in memory when loaded.
-   **Overall Application Logic:**
    -   The application service (`TextService`) and API controller (`TextController`) mostly perform delegation. Their algorithmic complexity is O(1) in terms of the number of calls, plus the complexity of the underlying repository operations.

**Conclusion:** The algorithms themselves (UUID generation, Pydantic, direct file access) are efficient for their specific tasks. The bottleneck is not in the algorithm choice for text manipulation, but in the inherent performance characteristics of file system operations for persistence in a concurrent API context.

### Resource Utilization
-   **Memory Usage:** Low. Given the `max_length=10000` characters for text content (approx. 10KB per file), each `Text` object loaded into memory is very small. Even with many concurrent requests, the memory footprint from text content itself should be manageable. Python's overhead per process will be higher than the data itself.
-   **CPU Utilization:** Low. Text content is small, and JSON serialization/deserialization for 10KB is a trivial CPU load. The application is I/O-bound.
-   **I/O Operation Efficiency:** Poor for a high-throughput API. Each `save` and `find_by_id` operation translates directly to a disk read or write. This will become the primary performance bottleneck under load, causing requests to queue while waiting for disk operations to complete. The use of `asyncio` in FastAPI will help by allowing the server to switch to other requests while waiting for disk I/O, but it doesn't make the I/O itself faster.

### Scalability Assessment
-   **Vertical Scaling:** Limited by disk I/O capabilities of a single machine. Upgrading disk speed (e.g., SSD to NVMe) will help, but there's a ceiling.
-   **Horizontal Scaling:** Very challenging with the current file system persistence.
    -   If multiple instances of the FastAPI application are deployed, they would all need access to the same storage directory. This typically requires a Network File System (NFS) or a cloud-managed file system (e.g., AWS EFS, Azure Files). These shared file systems introduce network latency and have their own scaling limitations and performance characteristics, often becoming a bottleneck themselves for high-throughput, small-file access patterns.
    -   Ensuring data consistency and preventing race conditions (e.g., two instances trying to write to the same file simultaneously) becomes complex without explicit locking mechanisms provided by a proper database.
    -   The current design ensures stateless API services, which is excellent for horizontal scaling of the compute layer, but the shared storage layer undermines this benefit.

**Overall:** The architecture is designed for scalability in terms of the application's stateless nature and modularity. However, the choice of the file system for persistence prevents it from truly scaling beyond a single instance with very low concurrent load.

### Recommendations
1.  **Prioritize Database Migration (Critical):**
    *   **Action:** Replace `FileTextRepository` with a database-backed repository (`SQLAlchemyTextRepository` or `MongoTextRepository`).
    *   **Recommendation:** For initial simplicity and local development, consider `SQLite` if data volume is truly small and single-file, but for any production scenario or future growth, `PostgreSQL` (relational) or `MongoDB` (document-oriented, well-suited for JSON-like data) would be much more robust choices.
    *   **Tools:** `SQLAlchemy` (ORM for relational databases), `Pymongo` (for MongoDB), `Alembic` (for database migrations).
2.  **Implement Caching (High Impact):**
    *   **Action:** For `get_text_content`, add an in-memory cache in `TextService` (e.g., using `functools.lru_cache`).
    *   **Benefit:** Reduces repetitive disk I/O for frequently accessed items.
    *   **Tools:** `functools.lru_cache` for simple cases, `Redis` or `Memcached` for distributed caching.
3.  **Monitor Key Performance Indicators (KPIs):**
    *   **Action:** Set up monitoring for:
        *   **Request Latency:** Measure response times for `create` and `get` endpoints.
        *   **Throughput:** Requests per second.
        *   **Error Rates:** Track 5xx errors.
        *   **Disk I/O Metrics:** Monitor read/write operations per second, I/O wait times on the underlying server.
    *   **Tools:** Prometheus + Grafana, Datadog, New Relic, or custom logging with ELK stack.
4.  **Load Testing:**
    *   **Action:** Conduct load tests to simulate anticipated user concurrency and data volumes.
    *   **Purpose:** Identify actual breakpoints and bottlenecks under load.
    *   **Tools:** `Locust`, `JMeter`, `K6`.
5.  **Consider Object Storage for Large Files (Future):**
    *   **Action:** If text content could become very large (MBs to GBs), consider using object storage (e.g., AWS S3, Google Cloud Storage, Azure Blob Storage) instead of direct file system or even relational databases. Store only metadata in the database and the actual content in object storage.
    *   **Benefit:** Highly scalable, cost-effective for large binaries.
    *   **Tools:** `boto3` (AWS S3), respective cloud SDKs.
6.  **Review `AppConfig` Initialization:** The `AppConfig` `mkdir` is called on `__init__`, and `get_app_config` is `lru_cache`d. This means `mkdir` is called only once per process. The `lifespan` event also calls `mkdir`. This is redundant but harmless due to `exist_ok=True`. It can be simplified by removing `mkdir` from `AppConfig.__init__` as the `lifespan` event handles it appropriately for a FastAPI application lifecycle.## Code Quality Review Report

### Quality Score: 9/10

### Strengths
*   **Excellent Adherence to Architecture:** The codebase strictly follows the Clean Architecture (Layered Architecture with Ports & Adapters) outlined in the design. This results in clear separation of concerns, high modularity, and strong testability across all layers (Domain, Application, Infrastructure, API).
*   **Robust Test Suite:** The project boasts comprehensive unit and integration tests covering each layer.
    *   **Isolation:** Tests effectively use mocking (`unittest.mock.Mock`, `pytest-mock`) to isolate units (e.g., `TextService` is tested with a mocked `ITextRepository`, `TextController` with a mocked `TextService`).
    *   **Edge Cases:** Error handling paths (e.g., `IOError`, `JSONDecodeError`, service failures, not found scenarios) are explicitly tested, demonstrating a focus on robustness.
    *   **Fixtures:** Effective use of `pytest` fixtures (`temp_storage_dir`, `mock_app_config`, `mock_text_service`) ensures clean setup and teardown for tests.
*   **Clear and Consistent Naming Conventions:** All modules, classes, methods, and variables follow Python's PEP 8 guidelines (e.g., PascalCase for classes, snake_case for functions/variables).
*   **Good Documentation and Docstrings:**
    *   Every module, class, and method has a well-formed docstring (PEP 257 compliant) explaining its purpose, arguments, returns, and potential raises.
    *   FastAPI's automatic OpenAPI/Swagger UI generation will be highly effective due to the detailed endpoint docstrings and Pydantic models.
*   **Effective Error Handling:**
    *   Errors in the `infrastructure` layer (file I/O, JSON decoding) are caught and re-raised as `RuntimeError`s, providing a consistent error type for the layer.
    *   The `api` layer gracefully handles exceptions from the `application` layer, converting them into appropriate HTTP status codes (404 for Not Found, 500 for internal errors) and informative `HTTPException` details.
    *   Logging is used effectively to record information, warnings, and exceptions across different layers.
*   **Strong Type Hinting:** Consistent use of type hints throughout the codebase (PEP 484) significantly improves readability, maintainability, and allows for static analysis.
*   **Modern Python Practices:** Leverages Pydantic V2 features (`model_config`, `model_dump_json`, `model_validate`, `from_attributes`), FastAPI's `async/await` and dependency injection system, and `pathlib` for file operations.
*   **Maintainable Design:** The modular structure, clear interfaces, and rigorous testing make the codebase easy to understand, modify, and extend (e.g., swapping out the `FileTextRepository` for a database repository would require minimal changes to `TextService`).

### Areas for Improvement
*   **Redundant Directory Creation in `AppConfig`:** The `AppConfig.__init__` method includes `self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)`. This `mkdir` call is redundant because the `main.py`'s `lifespan` context manager already performs this operation reliably once at application startup. While `exist_ok=True` prevents errors, removing it from `AppConfig.__init__` would avoid unnecessary calls and align better with the single responsibility principle for configuration classes.
*   **Generic Exception Handling in `TextService`:** In `TextService`, `create_text_content` and `get_text_content` methods catch a generic `Exception`. While `logger.exception` is good for debugging, it's generally a better practice to catch more specific exceptions (e.g., `RuntimeError` if coming from the repository layer) and potentially wrap them in a more application-specific exception (e.g., `TextServiceError`) before re-raising. This provides callers with more granular control over error handling and prevents unintended catching of unrelated errors. For this simple application, it's not a critical flaw, but worth noting for larger systems.
*   **Pydantic `json_encoders` in `TextResponse`:** The `TextResponse` model includes `json_encoders` in its `model_config`. This configuration is already present and handled within the `Text` domain model itself. Since `TextResponse` is populated from a `Text` instance via `model_validate(text)`, the configuration in `Text` is sufficient, making this a minor redundancy in `TextResponse`.
*   **Dependency Management File (`requirements.txt` vs `pyproject.toml`):** While `requirements.txt` is functional and commonly used, for new Python projects, adopting a more modern approach like `pyproject.toml` with tools like Poetry or PDM for dependency management offers better developer experience, dependency resolution, and project metadata management. The current instruction to `echo` dependencies into `requirements.txt` is unusual; typically, it's generated via `pip freeze` or managed by a tool.

### Code Structure
*   **Organization and Modularity:** Exemplary. The `project/src/modules` directory is perfectly structured to represent the layers of Clean Architecture:
    *   `domain/`: Core business entities (`Text`) and interfaces (`ITextRepository`).
    *   `application/`: Application-specific business rules/use cases (`TextService`).
    *   `infrastructure/`: External concerns, concrete implementations (`FileTextRepository`, `AppConfig`, `dependencies`).
    *   `api/`: Presentation layer, handles HTTP requests/responses (`text_controller`).
    *   This strict separation ensures that the core domain logic remains untainted by external frameworks or persistence mechanisms, making it highly flexible and maintainable.
*   **Design Pattern Usage:**
    *   **Layered Architecture/Clean Architecture (Ports and Adapters):** Dominant pattern, clearly implemented through module organization and interface definitions. `ITextRepository` serves as a "port," and `FileTextRepository` is its "adapter."
    *   **Repository Pattern:** Abstracted data access via `ITextRepository`, allowing data storage mechanisms to be swapped without affecting the application or domain layers.
    *   **Dependency Injection:** Effectively used via FastAPI's `Depends` and dedicated `dependencies.py` module, ensuring components receive their required collaborators (e.g., `TextService` gets `ITextRepository`).
    *   **DTO (Data Transfer Object):** Pydantic models (`CreateTextRequest`, `TextResponse`) act as DTOs for data ingress/egress at the API boundary, separating external data representation from internal domain entities.

### Documentation
*   **Quality of Comments and Docstrings:** Very high. All public classes, methods, and functions have comprehensive docstrings explaining their purpose, arguments, and return values. This significantly aids understanding and onboarding.
*   **README and Inline Documentation:** While a dedicated `README.md` file wasn't provided, the "Installation and Usage Instructions" section effectively serves as a basic README, covering setup, running, and usage examples. Inline comments are used sparingly and effectively where complex logic might require additional explanation.

### Testing
*   **Test Coverage Analysis:** Excellent. Every core component and layer has dedicated unit or integration tests:
    *   `test_main.py`: Tests application startup (`lifespan`) and health check.
    *   `test_text.py`: Covers `Text` entity creation, updates, and Pydantic serialization.
    *   `test_file_text_repository.py`: Tests file-based persistence, including success, not-found, and error scenarios (IO errors, malformed JSON).
    *   `test_text_service.py`: Tests application-level business logic, mocking the repository.
    *   `test_text_controller.py`: Tests API endpoints, mocking the application service layer.
    *   This comprehensive coverage ensures high confidence in the codebase's functionality and robustness.
*   **Test Quality and Comprehensiveness:** High quality. Tests are well-structured, use appropriate assertions, and demonstrate a good understanding of mocking to achieve unit isolation. The use of `pytest` fixtures for setup and teardown is exemplary. Error paths and edge cases are explicitly tested.

### Maintainability
*   **Ease of Modification and Extension:** Exceptionally easy. The Clean Architecture ensures that:
    *   Changes in the persistence layer (e.g., switching from file system to a database) would only require a new implementation of `ITextRepository` and an update in `dependencies.py`, leaving the `domain`, `application`, and `api` layers untouched.
    *   Adding new business logic or use cases would primarily involve the `application` layer and potentially new domain entities, with minimal impact on other layers.
    *   The modularity allows developers to understand and work on specific parts of the system without needing to grasp the entire codebase at once.
*   **Technical Debt Assessment:** Very low. The code adheres to strong best practices, is well-structured, thoroughly tested, and clearly documented. The few "areas for improvement" are minor nits rather than significant technical debt.

### Recommendations
*   **Minor Refactoring (AppConfig `mkdir`):** Remove the `self.STORAGE_DIR.mkdir(...)` line from `src/modules/infrastructure/config.py`'s `__init__` method. The `main.py` `lifespan` handler is the appropriate place for directory creation during application startup.
*   **Refine Exception Handling in `TextService`:** Consider catching specific `RuntimeError`s from the `FileTextRepository` and re-raising them as more semantically meaningful application-level exceptions (e.g., `TextStorageError`) if fine-grained error types are desired at the service layer. For this simple project, the current re-raise is acceptable, but a more explicit error domain could be beneficial in larger applications.
*   **Adopt `pyproject.toml` for Dependency Management:** For future projects, or as an enhancement for this one, consider migrating from `requirements.txt` to `pyproject.toml` with a tool like [Poetry](https://python-poetry.org/) or [PDM](https://pdm.fming.dev/). This provides more robust dependency management, simplifies environment setup, and better integrates with modern Python tooling.
*   **Consider a more sophisticated Logging Setup:** For larger applications, explore `logging.config.dictConfig` or `fileConfig` to manage logging settings (e.g., log levels, handlers, formatters) more dynamically and robustly, rather than `basicConfig`.
*   **Future Enhancements (Quality Attributes):** As the project grows, explicitly consider implementing:
    *   **Authentication and Authorization:** If exposing to multiple users, securing API endpoints with JWT or similar methods.
    *   **Caching:** For frequently accessed text, introduce a caching mechanism (e.g., Redis, or an in-memory LRU cache) at the Application layer to improve performance.
    *   **Database Migration:** Prepare for switching the persistence layer from file system to a proper database (e.g., PostgreSQL, MongoDB) by ensuring the `ITextRepository` interface remains stable.## Security Review Report

### Security Score: 6/10

The application demonstrates good foundational development practices, including a clean architecture, Pydantic for input validation, and proper logging. However, it fundamentally lacks crucial security layers for any non-trivial application, primarily authentication and authorization, and exhibits potential risks related to file system interactions and information leakage in error handling.

### Critical Issues (High Priority)

*   **A01:2021-Broken Access Control (Missing Authentication and Authorization):**
    The most significant security vulnerability is the complete absence of authentication and authorization mechanisms. All API endpoints (`/api/v1/text` for creation and `/api/v1/text/{text_id}` for retrieval) are publicly accessible.
    *   **Impact:** Anyone with network access to the API can create new text content, retrieve any existing text content by guessing or enumerating IDs, or potentially exhaust resources. This is a critical flaw for any application designed for anything other than a fully public, anonymous, and unmanaged service.
    *   **Risk:** Data exposure, data manipulation (creation), resource exhaustion, denial of service.

### Medium Priority Issues

*   **A03:2021-Injection (Potential Path Traversal Risk with File System Storage):**
    The `FileTextRepository` constructs file paths by directly concatenating the `text_id` (e.g., `f"{text_id}.json"`). While the application generates `text_id` using `uuid.uuid4()` and FastAPI's router generally sanitizes path parameters against `../` or null bytes, relying solely on these mitigations can be risky. If the ID generation method were ever changed, or if a very advanced attacker found a way to inject path manipulation characters, it could lead to:
    *   **Impact:** Arbitrary file creation/overwrite outside the intended storage directory, or access to files outside the intended directory.
    *   **Risk:** Data leakage, system compromise, denial of service.
*   **A04:2021-Insecure Design (Information Leakage in Error Messages):**
    Error messages returned by the API (e.g., in `text_controller.py`) can expose internal details: `detail=f"Failed to create text content: {e}"` or `detail=f"Failed to retrieve text content: {e}"`.
    *   **Impact:** Detailed error messages (`IOError`, `json.JSONDecodeError`, service layer exceptions) can provide valuable information to an attacker about the application's internal structure, dependencies, and potential vulnerabilities, aiding further exploitation.
    *   **Risk:** Reconnaissance aid for attackers.
*   **A05:2021-Security Misconfiguration (Default Storage Location and Permissions):**
    The `STORAGE_DIR` defaults to `./data/text_content`.
    *   **Impact:** If the application is deployed without explicit configuration, files might be stored in an insecure or easily discoverable location. File permissions are inherited from the process's umask, which might not be strict enough, potentially allowing other users on the system to read or modify data.
    *   **Risk:** Data exposure, data tampering, compliance issues.
*   **Data at Rest Security (Lack of Encryption):**
    Text content is stored as plain JSON files on the file system.
    *   **Impact:** While the requirements state "simple text content" (implying non-sensitive), if the nature of the data ever changes to include sensitive information, it would be vulnerable to direct access from the underlying file system.
    *   **Risk:** Data leakage if the file system is compromised or accessed directly.
*   **Lack of Rate Limiting:**
    There are no mechanisms implemented to limit the number of requests a single client can make within a certain timeframe.
    *   **Impact:** The API is vulnerable to Denial of Service (DoS) attacks, where an attacker floods the service with requests, consuming resources and making it unavailable to legitimate users.
    *   **Risk:** Service unavailability.
*   **No Data Deletion/Lifecycle Management:**
    The current implementation only allows creation and retrieval of text content. There is no functionality to delete or manage the lifecycle of stored data.
    *   **Impact:** Uncontrolled data accumulation over time. If sensitive data were ever introduced (even temporarily), its indefinite retention increases the attack surface and potential for long-term exposure. This also presents compliance challenges (e.g., "right to be forgotten" under GDPR).
    *   **Risk:** Data remnants, increased attack surface, compliance violations.

### Low Priority Issues

*   **Development Mode Settings in Production:**
    The `uvicorn.run` command in `src/main.py` uses `reload=True` and `host="0.0.0.0"`. `reload=True` is a development-only feature that consumes more resources and can be a security risk in production. `host="0.0.0.0"` makes the application listen on all available network interfaces, which is fine for containerized deployments but can be a misconfiguration if the application is directly exposed to the internet without a proper firewall.
*   **Lack of Strict ID Validation in API:**
    While UUIDs are generated internally, the `text_id` path parameter in `text_controller.py` is simply typed as `str`. Adding an explicit regex validation for the UUID format (e.g., using `fastapi.Path(..., regex="^[0-9a-fA-F-]{36}$")`) would provide an extra layer of defense against malformed IDs before they reach the repository, though FastAPI's routing generally handles this well.
*   **Logging Verbosity:**
    While logging is generally good, `logger.exception` captures full stack traces. If logs are not properly secured, rotated, and monitored, verbose logs can also contribute to information leakage.

### Security Best Practices Followed

*   **Pydantic for Input Validation:** The use of Pydantic models (`CreateTextRequest`, `Text`) with `min_length` and `max_length` constraints, and automatic schema validation, effectively prevents many common injection attacks and ensures data integrity at the API boundary.
*   **Clean Architecture / Layered Design:** The clear separation of concerns (Presentation, Application, Domain, Infrastructure) makes the codebase more modular, testable, and easier to apply security controls at specific layers. It also allows for easier replacement of components (e.g., storage) with more secure alternatives.
*   **UUIDs for IDs:** Using `uuid.uuid4()` for generating unique identifiers makes IDs unpredictable, significantly reducing the risk of ID enumeration (though without authorization, this doesn't fully mitigate data access).
*   **Dependency Injection:** Facilitates testing and allows for the easy integration of security-related components or secure alternatives (e.g., different repository implementations).
*   **Graceful Error Handling (API Level):** The API uses `HTTPException` to catch exceptions from lower layers and return appropriate HTTP status codes (`404`, `500`), preventing raw stack traces from being directly exposed to clients (though the error `detail` is too verbose).
*   **Centralized Configuration (`AppConfig`):** Promotes better management of settings, including environment-specific secure paths.
*   **Use of `pathlib`:** For robust and OS-agnostic file path manipulation, which inherently handles some path edge cases better than string concatenation.
*   **Structured Logging:** Utilizes Python's standard `logging` module, which is good for auditing and debugging.

### Recommendations

1.  **Implement Authentication and Authorization (Immediate Priority):**
    *   **Authentication:** Integrate an authentication mechanism, such as JWT (JSON Web Tokens) or OAuth 2.0. FastAPI has excellent support for security dependencies.
    *   **Authorization:** Once users are authenticated, implement authorization (e.g., Role-Based Access Control) to define what actions specific users or roles can perform on `Text` resources. Apply FastAPI `Depends` on routes to enforce access control.
2.  **Harden File System Storage:**
    *   **Explicit Path Validation:** For any user-provided input used in file paths, strictly validate the input (e.g., using a regex for UUIDs in path parameters, or sanitizing/hashing filenames) to explicitly prevent path traversal.
    *   **Secure File Permissions:** Ensure the `STORAGE_DIR` and created files have the most restrictive permissions possible, readable and writable only by the application's dedicated user account. Consider using `os.umask` or `os.chmod` explicitly.
    *   **Dedicated Storage Volume:** In production, use a dedicated, isolated storage volume for application data, not within the application's root directory.
3.  **Refine Error Handling:**
    *   **Generic Production Errors:** Implement a custom exception handler in FastAPI to catch all unhandled exceptions and return generic error messages (e.g., "An unexpected error occurred.") to the client in production, while logging detailed information internally.
    *   **Custom Exception Types:** Define specific exception types in your domain/application layer (e.g., `TextNotFoundException`, `StorageWriteError`) and map them to appropriate HTTP status codes and non-revealing messages at the API layer.
4.  **Implement Data Encryption at Rest:**
    *   If the text content is or becomes sensitive, encrypt it before saving it to the file system. Consider using a library like `cryptography` for symmetric encryption, with keys managed securely (e.g., environment variables, a secrets manager, or a hardware security module).
5.  **Add Rate Limiting:**
    *   Integrate a rate-limiting middleware or library (e.g., `fastapi-limiter`) to protect against brute-force attacks and DoS attempts.
6.  **Implement Data Deletion and Retention:**
    *   Add API endpoints and corresponding service/repository methods to allow for the deletion of text content.
    *   Establish and enforce data retention policies, including automatic purging of old data, to minimize data footprint and comply with privacy regulations.
7.  **Secure Deployment Practices:**
    *   **Separate Environments:** Maintain distinct configurations for development, staging, and production environments. Disable `reload=True` and ensure appropriate logging levels for production.
    *   **Container Security:** If using Docker, build minimal images, scan them for vulnerabilities (e.g., with Trivy), and run containers with least privilege (`--user`, read-only file systems where possible).
    *   **Secrets Management:** Use environment variables for sensitive configurations (`STORAGE_DIR` is a good start), and for highly sensitive data (e.g., database credentials, API keys), leverage a dedicated secrets management solution (e.g., HashiCorp Vault, AWS Secrets Manager).

**Security Tools and Libraries to Consider:**

*   **SAST (Static Application Security Testing):**
    *   **Bandit:** Python security linter to detect common vulnerabilities.
    *   **Semgrep:** For writing custom security rules and finding vulnerabilities.
*   **DAST (Dynamic Application Security Testing):**
    *   **OWASP ZAP / Burp Suite:** For testing the running application for vulnerabilities.
*   **Dependency Scanning:**
    *   **Dependabot (GitHub) / Snyk / Trivy:** To automate the detection of known vulnerabilities in project dependencies.
*   **FastAPI Security Extensions:**
    *   `fastapi-users`: For comprehensive user authentication and management.
    *   `fastapi-limiter`: For adding rate limiting to endpoints.
*   **Container Security Tools:**
    *   **Hadolint:** For linting Dockerfiles to ensure best practices.
    *   **Trivy:** For scanning container images for vulnerabilities.

### Compliance Notes

*   **OWASP Top 10 (2021):**
    *   **A01:2021-Broken Access Control:** This is the most critical area to address immediately by implementing robust authentication and authorization.
    *   **A03:2021-Injection:** The current code mitigates direct path traversal due to UUIDs and FastAPI, but the underlying pattern of constructing file paths from user input needs constant vigilance and explicit validation.
    *   **A04:2021-Insecure Design:** The verbose error messages and lack of explicit security features like data at rest encryption and rate limiting fall under this category.
    *   **A05:2021-Security Misconfiguration:** Default storage paths, file permissions, and development-mode settings in production are key concerns.
    *   **A07:2021-Identification and Authentication Failures:** Directly applicable due to the absence of authentication.
    *   **A08:2021-Software and Data Integrity Failures:** Data at rest integrity is not explicitly ensured (e.g., no checksums or hashes for stored files).

*   **Industry Standard Compliance:**
    For any future expansion involving sensitive data or broader user bases, the application would need to consider stringent compliance standards like **GDPR, CCPA, HIPAA, SOC 2, or ISO 27001**. This would necessitate comprehensive data protection (encryption in transit and at rest), audit logging, access controls, data retention policies, and robust incident response plans, which are currently outside the scope of this "simple test analysis report" system.## Refactored Code Implementation

### Summary of Changes
This refactoring addresses key feedback points from performance, quality, and security reviews while maintaining all existing functionality and adhering to Clean Architecture principles.

**Key improvements made:**
*   **Data Deletion:** Implemented `DELETE` functionality for text content across all layers (Domain, Infrastructure, Application, API), allowing for data lifecycle management.
*   **Caching for Reads:** Integrated `functools.lru_cache` into `TextService` to optimize retrieval of frequently accessed text content, reducing repetitive file I/O.
*   **Enhanced Error Handling:** Refined exception handling in `TextService` to catch more specific `RuntimeError`s originating from the repository, and improved API-level error messages in `TextController` to be more generic for external clients, preventing information leakage while still logging details internally.
*   **Improved Input Validation:** Added UUID regex validation for `text_id` path parameters in `TextController` to enforce stricter input format, mitigating potential path traversal risks.
*   **Configuration Alignment:** Removed redundant directory creation logic from `AppConfig.__init__`, ensuring the FastAPI `lifespan` event is the single source of truth for storage directory setup.
*   **Pydantic Configuration Cleanup:** Eliminated redundant `json_encoders` configuration in `TextResponse` as it's correctly handled by the `Text` domain model.
*   **Production Readiness:** Modified the `uvicorn.run` command in `main.py` to disable `reload=True` for better production environment behavior.
*   **Comprehensive Testing:** Updated and added unit tests to cover the new `DELETE` functionality, cache invalidation, refined error handling, and the `AppConfig` change.

### Refactored Code

```python
# src/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.modules.api.text_controller import router as text_router
from src.modules.infrastructure.config import AppConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    Ensures necessary directories are created.
    """
    config = AppConfig()
    # Create storage directory if it doesn't exist
    config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Application startup: Storage directory ensured at {config.STORAGE_DIR}")
    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title="Simple Text Analysis Report API",
    description="A basic API for managing text content, demonstrating Clean Architecture principles.",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routers
app.include_router(text_router, prefix="/api/v1")

@app.get("/health", summary="Health Check")
async def health_check() -> dict[str, str]:
    """
    Checks the health of the application.

    Returns:
        A dictionary indicating the application's status.
    """
    return {"status": "healthy", "message": "API is running smoothly!"}

if __name__ == "__main__":
    import uvicorn
    # In a production environment, 'reload=True' should be removed.
    # The host '0.0.0.0' is suitable for containerized deployments.
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)

```

```python
# src/modules/domain/text.py
import datetime
import uuid
from typing import Self

from pydantic import BaseModel, Field


class Text(BaseModel):
    """
    Represents a core text entity in the domain.

    Attributes:
        id (str): Unique identifier for the text.
        content (str): The actual text content.
        created_at (datetime.datetime): Timestamp when the text was created.
        updated_at (datetime.datetime): Timestamp when the text was last updated.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., min_length=1, max_length=10000)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    def update_content(self, new_content: str) -> Self:
        """
        Updates the content of the text and sets the updated_at timestamp.

        Args:
            new_content (str): The new text content.

        Returns:
            Self: The updated Text instance.
        """
        self.content = new_content
        self.updated_at = datetime.datetime.utcnow()
        return self

    class Config:
        """Pydantic model configuration."""
        json_encoders = {datetime.datetime: lambda dt: dt.isoformat()}
        populate_by_name = True # Allow population by field name for better compatibility
        from_attributes = True # New in Pydantic V2, replaces allow_population_by_field_name

```

```python
# src/modules/domain/interfaces.py
import abc
from typing import Optional

from src.modules.domain.text import Text


class ITextRepository(abc.ABC):
    """
    Abstract Base Class (ABC) defining the contract for text content persistence.
    This is a "Port" in Clean Architecture.
    """

    @abc.abstractmethod
    def save(self, text: Text) -> Text:
        """
        Saves a Text entity to the persistence layer.

        Args:
            text (Text): The Text entity to save.

        Returns:
            Text: The saved Text entity (potentially with updated attributes like ID or timestamps).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_id(self, text_id: str) -> Optional[Text]:
        """
        Retrieves a Text entity by its unique identifier.

        Args:
            text_id (str): The unique ID of the text to retrieve.

        Returns:
            Optional[Text]: The Text entity if found, otherwise None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_by_id(self, text_id: str) -> bool:
        """
        Deletes a Text entity by its unique identifier.

        Args:
            text_id (str): The unique ID of the text to delete.

        Returns:
            bool: True if the text was deleted, False otherwise.
        """
        raise NotImplementedError
```

```python
# src/modules/infrastructure/config.py
import os
from pathlib import Path


class AppConfig:
    """
    Configuration settings for the application.
    """
    # Base directory for storing text files
    STORAGE_DIR: Path = Path(os.getenv("STORAGE_DIR", "./data/text_content"))

    def __init__(self) -> None:
        """
        Initializes AppConfig. The storage directory creation is handled by the
        FastAPI lifespan event to ensure it's done once at application startup.
        """
        pass # Removed mkdir call, as it's handled in main.py lifespan

```

```python
# src/modules/infrastructure/file_text_repository.py
import json
import logging
import os # Import os for os.remove
from pathlib import Path
from typing import Optional

from src.modules.domain.interfaces import ITextRepository
from src.modules.domain.text import Text
from src.modules.infrastructure.config import AppConfig

logger = logging.getLogger(__name__)


class FileTextRepository(ITextRepository):
    """
    Concrete implementation of ITextRepository using the file system for storage.
    Each Text entity is stored as a JSON file, named after its ID.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initializes the FileTextRepository.

        Args:
            config (AppConfig): Application configuration.
        """
        self.storage_dir = config.STORAGE_DIR
        logger.info(f"FileTextRepository initialized. Storage directory: {self.storage_dir}")

    def _get_file_path(self, text_id: str) -> Path:
        """
        Constructs the file path for a given text ID.

        Args:
            text_id (str): The ID of the text.

        Returns:
            Path: The full file path.
        """
        return self.storage_dir / f"{text_id}.json"

    def save(self, text: Text) -> Text:
        """
        Saves a Text entity to a JSON file.

        Args:
            text (Text): The Text entity to save.

        Returns:
            Text: The saved Text entity.
        """
        file_path = self._get_file_path(text.id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text.model_dump_json(indent=2))
            logger.info(f"Text '{text.id}' saved to {file_path}")
            return text
        except IOError as e:
            logger.error(f"Error saving text '{text.id}' to {file_path}: {e}")
            raise RuntimeError(f"Failed to save text content: {e}") from e

    def find_by_id(self, text_id: str) -> Optional[Text]:
        """
        Retrieves a Text entity by reading its corresponding JSON file.

        Args:
            text_id (str): The unique ID of the text to retrieve.

        Returns:
            Optional[Text]: The Text entity if found, otherwise None.
        """
        file_path = self._get_file_path(text_id)
        if not file_path.exists():
            logger.info(f"Text '{text_id}' not found at {file_path}")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            text = Text.model_validate(data)
            logger.info(f"Text '{text_id}' loaded from {file_path}")
            return text
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading text '{text_id}' from {file_path}: {e}")
            raise RuntimeError(f"Failed to load text content: {e}") from e

    def delete_by_id(self, text_id: str) -> bool:
        """
        Deletes a Text entity by deleting its corresponding JSON file.

        Args:
            text_id (str): The unique ID of the text to delete.

        Returns:
            bool: True if the text was deleted, False otherwise.
        """
        file_path = self._get_file_path(text_id)
        if not file_path.exists():
            logger.info(f"Attempted to delete non-existent text '{text_id}' at {file_path}")
            return False
        try:
            os.remove(file_path)
            logger.info(f"Text '{text_id}' deleted from {file_path}")
            return True
        except OSError as e: # Catch OSError for file system operations
            logger.error(f"Error deleting text '{text_id}' from {file_path}: {e}")
            raise RuntimeError(f"Failed to delete text content: {e}") from e
```

```python
# src/modules/application/text_service.py
import logging
from functools import lru_cache # Import lru_cache
from typing import Optional

from src.modules.domain.interfaces import ITextRepository
from src.modules.domain.text import Text

logger = logging.getLogger(__name__)


class TextService:
    """
    Application service for managing text content.
    Orchestrates business logic and interacts with the domain and infrastructure layers.
    """

    def __init__(self, text_repository: ITextRepository) -> None:
        """
        Initializes the TextService with a text repository.

        Args:
            text_repository (ITextRepository): The repository for Text entities.
        """
        self.text_repository = text_repository
        logger.info("TextService initialized.")

    def create_text_content(self, content: str) -> Text:
        """
        Creates a new Text entity and persists it.

        Args:
            content (str): The raw text content to be stored.

        Returns:
            Text: The newly created Text entity.
        """
        try:
            new_text = Text(content=content)
            saved_text = self.text_repository.save(new_text)
            logger.info(f"New text content created with ID: {saved_text.id}")
            # Invalidate cache for this ID if it was in cache (though unlikely for new item)
            self.get_text_content.cache_clear() # Clear cache on creation to ensure consistency
            return saved_text
        except RuntimeError as e: # Catch specific RuntimeError from repository
            logger.error(f"Failed to create text content due to repository error: {e}")
            raise # Re-raise for API layer to handle
        except Exception as e:
            logger.exception(f"An unexpected error occurred while creating text content: {e}")
            raise

    @lru_cache(maxsize=128) # Apply LRU cache for performance
    def get_text_content(self, text_id: str) -> Optional[Text]:
        """
        Retrieves a Text entity by its ID.
        Results are cached using LRU cache for performance.

        Args:
            text_id (str): The unique ID of the text to retrieve.

        Returns:
            Optional[Text]: The Text entity if found, otherwise None.
        """
        try:
            text = self.text_repository.find_by_id(text_id)
            if text:
                logger.info(f"Retrieved text content with ID: {text_id}")
            else:
                logger.info(f"Text content with ID '{text_id}' not found.")
            return text
        except RuntimeError as e: # Catch specific RuntimeError from repository
            logger.error(f"Failed to retrieve text content with ID '{text_id}' due to repository error: {e}")
            raise # Re-raise for API layer to handle
        except Exception as e:
            logger.exception(f"An unexpected error occurred while retrieving text content with ID '{text_id}': {e}")
            raise

    def delete_text_content(self, text_id: str) -> bool:
        """
        Deletes a Text entity by its ID.

        Args:
            text_id (str): The unique ID of the text to delete.

        Returns:
            bool: True if the text was deleted, False otherwise.
        """
        try:
            deleted = self.text_repository.delete_by_id(text_id)
            if deleted:
                logger.info(f"Text content with ID '{text_id}' successfully deleted.")
                self.get_text_content.cache_clear() # Invalidate cache if item is deleted
            else:
                logger.info(f"Text content with ID '{text_id}' not found for deletion.")
            return deleted
        except RuntimeError as e: # Catch specific RuntimeError from repository
            logger.error(f"Failed to delete text content with ID '{text_id}' due to repository error: {e}")
            raise # Re-raise for API layer to handle
        except Exception as e:
            logger.exception(f"An unexpected error occurred while deleting text content with ID '{text_id}': {e}")
            raise
```

```python
# src/modules/infrastructure/dependencies.py
from functools import lru_cache

from src.modules.application.text_service import TextService
from src.modules.infrastructure.config import AppConfig
from src.modules.infrastructure.file_text_repository import FileTextRepository


@lru_cache()
def get_app_config() -> AppConfig:
    """
    Provides a singleton instance of the application configuration.
    """
    return AppConfig()

def get_text_repository(config: AppConfig = get_app_config()) -> FileTextRepository:
    """
    Provides a concrete instance of ITextRepository (FileTextRepository).
    """
    return FileTextRepository(config)

def get_text_service(
    text_repository: FileTextRepository = get_text_repository(),
) -> TextService:
    """
    Provides an instance of TextService, injecting its dependencies.
    """
    return TextService(text_repository)

```

```python
# src/modules/api/text_controller.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status # Import Path
from pydantic import BaseModel, Field

from src.modules.application.text_service import TextService
from src.modules.domain.text import Text
from src.modules.infrastructure.dependencies import get_text_service

# Regex for UUID validation (standard UUID v4 format)
UUID_REGEX = "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"


class CreateTextRequest(BaseModel):
    """Request model for creating new text content."""
    content: str = Field(..., min_length=1, max_length=10000,
                         example="This is a simple test analysis report content.")


class TextResponse(BaseModel):
    """Response model for text content."""
    id: str
    content: str
    created_at: str # Use str for ISO format for API response consistency
    updated_at: str # Use str for ISO format for API response consistency

    model_config = {
        "from_attributes": True # Allow population from Text domain model attributes
        # Removed json_encoders here as it's handled by Text domain model
    }

router = APIRouter()


@router.post(
    "/text",
    response_model=TextResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Text Content",
    description="Creates a new piece of text content and stores it.",
)
async def create_text_content_endpoint(
    request: CreateTextRequest,
    text_service: Annotated[TextService, Depends(get_text_service)],
) -> TextResponse:
    """
    Endpoint to create new text content.

    Args:
        request (CreateTextRequest): The request body containing the text content.
        text_service (TextService): Dependency-injected text service.

    Returns:
        TextResponse: The created text content with its ID and timestamps.

    Raises:
        HTTPException: If there's an internal server error during creation.
    """
    try:
        text = text_service.create_text_content(request.content)
        return TextResponse.model_validate(text)
    except Exception: # Catch generic exception for logging, return generic message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while creating text content. Please try again later.",
        )


@router.get(
    "/text/{text_id}",
    response_model=TextResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Text Content by ID",
    description="Retrieves a specific piece of text content by its unique ID.",
)
async def get_text_content_endpoint(
    text_id: Annotated[str, Path(regex=UUID_REGEX)], # Add regex validation
    text_service: Annotated[TextService, Depends(get_text_service)],
) -> TextResponse:
    """
    Endpoint to retrieve text content by ID.

    Args:
        text_id (str): The unique ID of the text content to retrieve.
        text_service (TextService): Dependency-injected text service.

    Returns:
        TextResponse: The retrieved text content.

    Raises:
        HTTPException: If the text content is not found (404) or an internal error occurs (500).
    """
    try:
        text = text_service.get_text_content(text_id)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Text content with ID '{text_id}' not found.",
            )
        return TextResponse.model_validate(text)
    except HTTPException:
        # Re-raise HTTPException if it's already a 404 from above
        raise
    except Exception: # Catch generic exception for logging, return generic message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while retrieving text content. Please try again later.",
        )


@router.delete(
    "/text/{text_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Text Content by ID",
    description="Deletes a specific piece of text content by its unique ID.",
)
async def delete_text_content_endpoint(
    text_id: Annotated[str, Path(regex=UUID_REGEX)], # Add regex validation
    text_service: Annotated[TextService, Depends(get_text_service)],
) -> None:
    """
    Endpoint to delete text content by ID.

    Args:
        text_id (str): The unique ID of the text content to delete.
        text_service (TextService): Dependency-injected text service.

    Raises:
        HTTPException: If the text content is not found (404) or an internal error occurs (500).
    """
    try:
        deleted = text_service.delete_text_content(text_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Text content with ID '{text_id}' not found.",
            )
        # Return 204 No Content if successful
    except HTTPException:
        raise
    except Exception: # Catch generic exception for logging, return generic message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while deleting text content. Please try again later.",
        )

```

### Security Improvements
*   **Input Validation:** Stricter validation for `text_id` path parameters using a UUID regex (`UUID_REGEX`) in `src/modules/api/text_controller.py` reduces the risk of path traversal attacks by ensuring that the input confirms to an expected safe format.
*   **Information Leakage Prevention:** Modified API error responses in `src/modules/api/text_controller.py` to provide generic messages (e.g., "An internal server error occurred...") instead of exposing internal exception details. Detailed error information is still logged internally for debugging.
*   **Data Deletion Capability:** The introduction of a `DELETE` endpoint and corresponding logic in `src/modules/application/text_service.py` and `src/modules/infrastructure/file_text_repository.py` allows for better data lifecycle management, reducing data retention risks, especially if sensitive data were ever introduced.
*   **Production Configuration:** `uvicorn.run` in `src/main.py` now explicitly sets `reload=False`, which is crucial for secure and efficient production deployments by preventing unnecessary resource consumption and potential security bypasses associated with hot-reloading.

**Future Security Enhancements (Recommended):**
*   **Authentication and Authorization (Critical):** The most significant missing security layer is authentication and authorization. For any non-public usage, implement robust mechanisms (e.g., JWT, OAuth2.0 with scopes, RBAC) to ensure only authorized users can access and manipulate data. This would typically involve FastAPI security dependencies and custom middleware/decorators.
*   **Data at Rest Encryption:** If sensitive text content is to be stored, implement encryption before writing to disk (e.g., using a library like `cryptography`) to protect data in case of file system compromise.
*   **Secure File Permissions & Dedicated Storage:** In production, ensure the `STORAGE_DIR` has the most restrictive file system permissions possible, and ideally, resides on a dedicated, isolated storage volume outside the application's deployment root.
*   **Rate Limiting:** Implement rate limiting (e.g., using `fastapi-limiter`) to prevent brute-force attacks and Denial of Service (DoS) attacks.

### Performance Optimizations
*   **Caching for Read Operations:** Implemented `functools.lru_cache(maxsize=128)` on the `get_text_content` method in `src/modules/application/text_service.py`. This significantly improves the performance of repeated read requests for the same text content by serving them from an in-memory cache, reducing the number of costly disk I/O operations.
*   **Cache Invalidation:** The cache is automatically cleared (via `cache_clear()`) whenever text content is created (`create_text_content`) or deleted (`delete_text_content`) to ensure data consistency between the cache and the underlying file system.

**Further Performance Optimizations (Recommended):**
*   **Database Migration (Critical):** The most impactful performance improvement would be to migrate from file system storage to a proper database (e.g., PostgreSQL, MongoDB). This would provide native indexing, optimized I/O, concurrency control, and better horizontal scalability. (See Migration Guide below).
*   **Asynchronous File I/O:** While `lru_cache` mitigates many read bottlenecks, for extremely large files or very high concurrent writes, consider `aiofiles` in the `FileTextRepository` to explicitly make file operations non-blocking, though this is less critical than database migration.

### Quality Enhancements
*   **Improved Error Handling:**
    *   In `src/modules/application/text_service.py`, exception handling for repository interactions is more specific, catching `RuntimeError` (re-raised by the repository for I/O issues) rather than a generic `Exception`. This allows for more targeted error handling and clearer propagation of issues.
    *   In `src/modules/api/text_controller.py`, the `HTTPException` details for internal server errors are now generic messages to the client, preventing exposure of internal technical details (e.g., stack traces, specific file system errors), which is good for security and user experience.
*   **Code Clarity and Consistency:**
    *   Removed `self.STORAGE_DIR.mkdir()` from `AppConfig.__init__` in `src/modules/infrastructure/config.py`. This removes redundancy, as the directory creation is correctly handled once at application startup via FastAPI's `lifespan` event in `src/main.py`.
    *   Removed the redundant `json_encoders` configuration from `TextResponse.model_config` in `src/modules/api/text_controller.py`. The `Text` domain model already handles datetime serialization for Pydantic.
*   **Maintainability:** The addition of a `delete` operation maintains the Clean Architecture pattern, with changes isolated to the respective layers (interface, infrastructure, application service, API endpoint), demonstrating the maintainability benefits of the design.

### Updated Tests

```python
# tests/test_main.py
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check() -> None:
    """
    Test the health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "API is running smoothly!"}

@patch('src.modules.infrastructure.config.AppConfig.STORAGE_DIR')
def test_lifespan_creates_directory(mock_storage_dir) -> None:
    """
    Test that the lifespan event creates the storage directory.
    """
    # Simulate a clean start
    mock_storage_dir.mkdir.reset_mock()
    with TestClient(app) as test_client:
        # Client context manager will trigger lifespan events
        response = test_client.get("/health")
        assert response.status_code == 200
    mock_storage_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)

```

```python
# tests/modules/domain/test_text.py
import datetime
import uuid

from src.modules.domain.text import Text


def test_text_creation() -> None:
    """
    Test Text entity creation with default values.
    """
    content = "Hello World!"
    text = Text(content=content)

    assert isinstance(text.id, str)
    assert len(text.id) > 0 # UUIDs are non-empty strings
    assert uuid.UUID(text.id, version=4) # Ensure it's a valid UUID
    assert text.content == content
    assert isinstance(text.created_at, datetime.datetime)
    assert isinstance(text.updated_at, datetime.datetime)
    assert text.created_at <= datetime.datetime.utcnow()
    assert text.updated_at <= datetime.datetime.utcnow()
    assert text.created_at == text.updated_at # Should be same on initial creation

def test_text_update_content() -> None:
    """
    Test updating text content.
    """
    text = Text(content="Original content")
    original_updated_at = text.updated_at

    new_content = "Updated content here."
    updated_text = text.update_content(new_content)

    assert updated_text.content == new_content
    assert updated_text.id == text.id # ID should remain unchanged
    assert updated_text.created_at == text.created_at # Created_at should remain unchanged
    assert updated_text.updated_at > original_updated_at # Updated_at should be more recent

def test_text_serialization_deserialization() -> None:
    """
    Test Text entity serialization to JSON and deserialization back.
    """
    original_text = Text(content="Some test content.")
    json_data = original_text.model_dump_json()

    loaded_text = Text.model_validate_json(json_data)

    assert loaded_text.id == original_text.id
    assert loaded_text.content == original_text.content
    assert loaded_text.created_at == original_text.created_at
    assert loaded_text.updated_at == original_text.updated_at
    assert loaded_text == original_text # Pydantic model equality check

```

```python
# tests/modules/infrastructure/test_file_text_repository.py
import json
import os
import shutil
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.modules.domain.text import Text
from src.modules.infrastructure.config import AppConfig
from src.modules.infrastructure.file_text_repository import FileTextRepository


@pytest.fixture(scope="function")
def temp_storage_dir(tmp_path: Path) -> Path:
    """
    Provides a temporary directory for file storage and ensures it's clean.
    """
    temp_dir = tmp_path / "test_storage"
    temp_dir.mkdir()
    yield temp_dir
    # Cleanup after test
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

@pytest.fixture
def mock_app_config(temp_storage_dir: Path) -> Mock:
    """
    Provides a mock AppConfig instance with a temporary storage directory.
    """
    mock_config = Mock(spec=AppConfig)
    mock_config.STORAGE_DIR = temp_storage_dir
    return mock_config

@pytest.fixture
def file_repo(mock_app_config: Mock) -> FileTextRepository:
    """
    Provides an instance of FileTextRepository with the mock config.
    """
    return FileTextRepository(mock_app_config)

def test_save_text(file_repo: FileTextRepository, temp_storage_dir: Path) -> None:
    """
    Test saving a Text entity to a file.
    """
    test_text = Text(content="This is content to save.")
    saved_text = file_repo.save(test_text)

    assert saved_text == test_text # Ensure the returned text is the same
    file_path = temp_storage_dir / f"{test_text.id}.json"
    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["id"] == test_text.id
    assert data["content"] == test_text.content

def test_find_by_id_found(file_repo: FileTextRepository, temp_storage_dir: Path) -> None:
    """
    Test finding an existing Text entity by ID.
    """
    test_text = Text(content="Content for retrieval.")
    # Manually save the file to simulate existing data
    file_path = temp_storage_dir / f"{test_text.id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(test_text.model_dump_json(indent=2))

    found_text = file_repo.find_by_id(test_text.id)
    assert found_text == test_text

def test_find_by_id_not_found(file_repo: FileTextRepository) -> None:
    """
    Test finding a non-existent Text entity by ID.
    """
    non_existent_id = "non_existent_id"
    found_text = file_repo.find_by_id(non_existent_id)
    assert found_text is None

def test_delete_by_id_success(file_repo: FileTextRepository, temp_storage_dir: Path) -> None:
    """
    Test successful deletion of a Text entity by ID.
    """
    test_text = Text(content="Content to be deleted.")
    file_path = temp_storage_dir / f"{test_text.id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(test_text.model_dump_json(indent=2))
    assert file_path.exists()

    deleted = file_repo.delete_by_id(test_text.id)
    assert deleted is True
    assert not file_path.exists()

def test_delete_by_id_not_found(file_repo: FileTextRepository) -> None:
    """
    Test deleting a non-existent Text entity by ID.
    """
    non_existent_id = "non_existent_id_for_delete"
    deleted = file_repo.delete_by_id(non_existent_id)
    assert deleted is False

def test_save_io_error(file_repo: FileTextRepository, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test error handling during save due to IOError.
    """
    # Simulate an IOError during file writing
    def mock_open_fail(*args, **kwargs):
        raise IOError("Simulated disk full error")

    monkeypatch.setattr("builtins.open", mock_open_fail)

    with pytest.raises(RuntimeError, match="Failed to save text content"):
        file_repo.save(Text(content="Will fail"))

def test_find_by_id_json_decode_error(file_repo: FileTextRepository, temp_storage_dir: Path) -> None:
    """
    Test error handling during find_by_id due to invalid JSON.
    """
    bad_json_text = Text(content="Invalid JSON content")
    file_path = temp_storage_dir / f"{bad_json_text.id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("this is not valid json {") # Write invalid JSON

    with pytest.raises(RuntimeError, match="Failed to load text content"):
        file_repo.find_by_id(bad_json_text.id)

def test_delete_by_id_os_error(file_repo: FileTextRepository, temp_storage_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test error handling during delete due to OSError.
    """
    test_text = Text(content="Content to be deleted but will fail.")
    file_path = temp_storage_dir / f"{test_text.id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(test_text.model_dump_json(indent=2))
    assert file_path.exists()

    def mock_os_remove_fail(*args, **kwargs):
        raise OSError("Simulated permission denied error")

    monkeypatch.setattr(os, "remove", mock_os_remove_fail)

    with pytest.raises(RuntimeError, match="Failed to delete text content"):
        file_repo.delete_by_id(test_text.id)
```

```python
# tests/modules/application/test_text_service.py
from unittest.mock import Mock, patch # Import patch for cache clear test

import pytest

from src.modules.application.text_service import TextService
from src.modules.domain.interfaces import ITextRepository
from src.modules.domain.text import Text


@pytest.fixture
def mock_text_repository() -> Mock:
    """
    Provides a mock ITextRepository instance.
    """
    return Mock(spec=ITextRepository)

@pytest.fixture
def text_service(mock_text_repository: Mock) -> TextService:
    """
    Provides an instance of TextService with the mock repository.
    """
    # Clear the LRU cache before each test to ensure test isolation
    TextService.get_text_content.cache_clear()
    return TextService(mock_text_repository)

def test_create_text_content_success(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test successful creation of text content.
    """
    mock_text_repository.save.return_value = Text(id="test-id", content="Some content")

    content = "New report data."
    created_text = text_service.create_text_content(content)

    mock_text_repository.save.assert_called_once()
    # Check that save was called with an instance of Text with the correct content
    args, kwargs = mock_text_repository.save.call_args
    assert isinstance(args[0], Text)
    assert args[0].content == content

    assert created_text.id == "test-id"
    assert created_text.content == "Some content"

def test_create_text_content_failure(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test failure during text content creation.
    """
    mock_text_repository.save.side_effect = RuntimeError("Repository save error")

    with pytest.raises(RuntimeError, match="Repository save error"):
        text_service.create_text_content("Content that will fail.")

def test_get_text_content_found(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test successful retrieval of text content by ID.
    """
    expected_text = Text(id="existing-id", content="Found content.")
    mock_text_repository.find_by_id.return_value = expected_text

    found_text = text_service.get_text_content("existing-id")

    mock_text_repository.find_by_id.assert_called_once_with("existing-id")
    assert found_text == expected_text

    # Test cache hit
    mock_text_repository.find_by_id.reset_mock() # Reset mock to check if called again
    found_text_cached = text_service.get_text_content("existing-id")
    mock_text_repository.find_by_id.assert_not_called() # Should not call repository again
    assert found_text_cached == expected_text

def test_get_text_content_not_found(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test retrieval of non-existent text content.
    """
    mock_text_repository.find_by_id.return_value = None

    found_text = text_service.get_text_content("non-existent-id")

    mock_text_repository.find_by_id.assert_called_once_with("non-existent-id")
    assert found_text is None

def test_get_text_content_failure(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test failure during text content retrieval.
    """
    mock_text_repository.find_by_id.side_effect = RuntimeError("Repository read error")

    with pytest.raises(RuntimeError, match="Repository read error"):
        text_service.get_text_content("some-id")

def test_delete_text_content_success(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test successful deletion of text content.
    """
    mock_text_repository.delete_by_id.return_value = True
    test_id = "text-to-delete"

    deleted = text_service.delete_text_content(test_id)

    mock_text_repository.delete_by_id.assert_called_once_with(test_id)
    assert deleted is True

def test_delete_text_content_not_found(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test deletion of non-existent text content.
    """
    mock_text_repository.delete_by_id.return_value = False
    test_id = "non-existent-delete-id"

    deleted = text_service.delete_text_content(test_id)

    mock_text_repository.delete_by_id.assert_called_once_with(test_id)
    assert deleted is False

def test_delete_text_content_failure(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test failure during text content deletion.
    """
    mock_text_repository.delete_by_id.side_effect = RuntimeError("Repository delete error")
    test_id = "error-delete-id"

    with pytest.raises(RuntimeError, match="Repository delete error"):
        text_service.delete_text_content(test_id)

def test_cache_invalidation_on_create_delete(mock_text_repository: Mock, text_service: TextService) -> None:
    """
    Test that cache is cleared on create and delete operations.
    """
    # Prime the cache
    cached_text = Text(id="cached-id", content="cached-content")
    mock_text_repository.find_by_id.return_value = cached_text
    text_service.get_text_content("cached-id")
    mock_text_repository.find_by_id.assert_called_once()
    mock_text_repository.find_by_id.reset_mock()

    # Test cache clear on create
    mock_text_repository.save.return_value = Text(id="new-id", content="new-content")
    text_service.create_text_content("some new content")
    text_service.get_text_content.cache_clear.assert_called_once() # Verify cache_clear was called
    text_service.get_text_content.cache_clear.reset_mock() # Reset mock for next check

    # Verify cache is indeed clear (next get should hit repo)
    text_service.get_text_content("cached-id")
    mock_text_repository.find_by_id.assert_called_once_with("cached-id")
    mock_text_repository.find_by_id.reset_mock()

    # Test cache clear on delete
    mock_text_repository.delete_by_id.return_value = True
    text_service.delete_text_content("some-id-to-delete")
    text_service.get_text_content.cache_clear.assert_called_once() # Verify cache_clear was called

    # Verify cache is indeed clear (next get should hit repo)
    text_service.get_text_content("cached-id")
    mock_text_repository.find_by_id.assert_called_once_with("cached-id")

```

```python
# tests/modules/api/test_text_controller.py
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.application.text_service import TextService
from src.modules.domain.text import Text
from src.modules.api.text_controller import UUID_REGEX # Import UUID_REGEX

client = TestClient(app)


@pytest.fixture
def mock_text_service() -> Mock:
    """
    Provides a mock TextService instance.
    """
    return Mock(spec=TextService)

@pytest.fixture(autouse=True)
def override_get_text_service(mock_text_service: Mock) -> None:
    """
    Overrides the get_text_service dependency for testing.
    """
    app.dependency_overrides[
        TextService
    ] = lambda: mock_text_service # Fastapi 0.100+ requires passing the class

    yield
    # Clean up overrides after test
    app.dependency_overrides = {}


def test_create_text_content_success(mock_text_service: Mock) -> None:
    """
    Test successful creation of text content via API.
    """
    test_content = "API test content."
    expected_text = Text(id="new-api-id", content=test_content)
    mock_text_service.create_text_content.return_value = expected_text

    response = client.post(
        "/api/v1/text",
        json={"content": test_content}
    )

    assert response.status_code == 201
    assert response.json()["id"] == "new-api-id"
    assert response.json()["content"] == test_content
    mock_text_service.create_text_content.assert_called_once_with(test_content)


def test_create_text_content_invalid_input() -> None:
    """
    Test API input validation for creating text content (empty content).
    """
    response = client.post(
        "/api/v1/text",
        json={"content": ""}
    )
    assert response.status_code == 422 # Unprocessable Entity for validation error
    # Pydantic V2 error detail format changed slightly
    assert response.json()["detail"][0]["type"] == "string_too_short"
    assert response.json()["detail"][0]["loc"] == ("body", "content")


def test_create_text_content_internal_error(mock_text_service: Mock) -> None:
    """
    Test internal server error during text content creation.
    """
    mock_text_service.create_text_content.side_effect = RuntimeError("Something went wrong in service")

    response = client.post(
        "/api/v1/text",
        json={"content": "Content causing error"}
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "An internal server error occurred while creating text content. Please try again later."


def test_get_text_content_success(mock_text_service: Mock) -> None:
    """
    Test successful retrieval of text content by ID via API.
    """
    text_id = "a" * 8 + "-" + "b" * 4 + "-" + "c" * 4 + "-" + "d" * 4 + "-" + "e" * 12 # Valid UUID-like string
    expected_text = Text(id=text_id, content="Retrieved content.")
    mock_text_service.get_text_content.return_value = expected_text

    response = client.get(f"/api/v1/text/{text_id}")

    assert response.status_code == 200
    assert response.json()["id"] == text_id
    assert response.json()["content"] == "Retrieved content."
    mock_text_service.get_text_content.assert_called_once_with(text_id)

def test_get_text_content_invalid_uuid_input() -> None:
    """
    Test API input validation for text_id parameter (invalid UUID format).
    """
    response = client.get("/api/v1/text/invalid-uuid-format")
    assert response.status_code == 422 # Unprocessable Entity for validation error
    assert "value_error" in response.json()["detail"][0]["type"]
    assert "UUID_REGEX" in response.json()["detail"][0]["msg"]


def test_get_text_content_not_found(mock_text_service: Mock) -> None:
    """
    Test retrieval of non-existent text content by ID via API.
    """
    text_id = "1" * 8 + "-" + "2" * 4 + "-" + "3" * 4 + "-" + "4" * 4 + "-" + "5" * 12 # Valid UUID-like string
    mock_text_service.get_text_content.return_value = None

    response = client.get(f"/api/v1/text/{text_id}")

    assert response.status_code == 404
    assert f"Text content with ID '{text_id}' not found." in response.json()["detail"]
    mock_text_service.get_text_content.assert_called_once_with(text_id)

def test_get_text_content_internal_error(mock_text_service: Mock) -> None:
    """
    Test internal server error during text content retrieval.
    """
    text_id = "6" * 8 + "-" + "7" * 4 + "-" + "8" * 4 + "-" + "9" * 4 + "-" + "a" * 12 # Valid UUID-like string
    mock_text_service.get_text_content.side_effect = Exception("Service layer error")

    response = client.get(f"/api/v1/text/{text_id}")

    assert response.status_code == 500
    assert response.json()["detail"] == "An internal server error occurred while retrieving text content. Please try again later."
    mock_text_service.get_text_content.assert_called_once_with(text_id)

def test_delete_text_content_success(mock_text_service: Mock) -> None:
    """
    Test successful deletion of text content via API.
    """
    text_id = "f" * 8 + "-" + "e" * 4 + "-" + "d" * 4 + "-" + "c" * 4 + "-" + "b" * 12 # Valid UUID-like string
    mock_text_service.delete_text_content.return_value = True

    response = client.delete(f"/api/v1/text/{text_id}")

    assert response.status_code == 204
    assert response.content == b"" # 204 No Content should have empty body
    mock_text_service.delete_text_content.assert_called_once_with(text_id)

def test_delete_text_content_invalid_uuid_input() -> None:
    """
    Test API input validation for delete text_id parameter (invalid UUID format).
    """
    response = client.delete("/api/v1/text/invalid-uuid-delete")
    assert response.status_code == 422
    assert "value_error" in response.json()["detail"][0]["type"]
    assert "UUID_REGEX" in response.json()["detail"][0]["msg"]

def test_delete_text_content_not_found(mock_text_service: Mock) -> None:
    """
    Test deletion of non-existent text content via API.
    """
    text_id = "a" * 8 + "-" + "b" * 4 + "-" + "a" * 4 + "-" + "b" * 4 + "-" + "a" * 12 # Valid UUID-like string
    mock_text_service.delete_text_content.return_value = False

    response = client.delete(f"/api/v1/text/{text_id}")

    assert response.status_code == 404
    assert f"Text content with ID '{text_id}' not found." in response.json()["detail"]
    mock_text_service.delete_text_content.assert_called_once_with(text_id)

def test_delete_text_content_internal_error(mock_text_service: Mock) -> None:
    """
    Test internal server error during text content deletion.
    """
    text_id = "c" * 8 + "-" + "d" * 4 + "-" + "e" * 4 + "-" + "f" * 4 + "-" + "0" * 12 # Valid UUID-like string
    mock_text_service.delete_text_content.side_effect = Exception("Service delete error")

    response = client.delete(f"/api/v1/text/{text_id}")

    assert response.status_code == 500
    assert response.json()["detail"] == "An internal server error occurred while deleting text content. Please try again later."
    mock_text_service.delete_text_content.assert_called_once_with(text_id)
```

### Migration Guide

This section outlines how to migrate from the previous implementation to the refactored code.

**Backward Compatibility:**
The core API endpoints (`POST /api/v1/text` and `GET /api/v1/text/{text_id}`) remain backward compatible in terms of their request/response schemas and behavior for success cases. The main changes are under the hood (caching, error handling).

**Breaking Changes:**
*   **Error Message Format:** The `detail` message for `HTTP 500 Internal Server Error` responses has changed from containing specific exception details (e.g., `Failed to create text content: <exception_details>`) to a more generic, client-safe message (e.g., `An internal server error occurred while creating text content. Please try again later.`). Clients that parsed or relied on the specific error messages from the previous implementation will need to adjust.
*   **New `DELETE` Endpoint:** A new `DELETE /api/v1/text/{text_id}` endpoint has been introduced. This is an additive change and does not break existing functionality.

**Migration Steps:**

1.  **Update Codebase:** Replace your existing `src/` directory content with the new refactored code. Ensure all files (`main.py`, `modules/api/text_controller.py`, `modules/application/text_service.py`, `modules/domain/text.py`, `modules/domain/interfaces.py`, `modules/infrastructure/config.py`, `modules/infrastructure/dependencies.py`, `modules/infrastructure/file_text_repository.py`) are updated.
2.  **Update Tests:** Replace your existing `tests/` directory content with the new updated tests. This ensures that the new features are tested and existing functionality is still correctly verified.
3.  **Dependency Review:** The core dependencies (FastAPI, Uvicorn, Pydantic, Pytest, Httpx) remain the same. No new external libraries are introduced in this refactoring for runtime, but `os` module is now explicitly imported in `FileTextRepository`.
4.  **Configuration (Minor):** The `AppConfig.__init__` no longer performs directory creation. This change is internal and handled gracefully by the FastAPI `lifespan` event. No direct action is required unless you had custom logic relying on `AppConfig.__init__` for directory creation outside of the FastAPI app startup.
5.  **Deployment Environment:** If running in a production environment, ensure that the `uvicorn.run` command (or your deployment method) does not enable `reload=True`, as it's now explicitly set to `reload=False` in `src/main.py`. This ensures better resource utilization and security.

**Future Migration (Database Integration):**
The architecture is designed to make a transition to a proper database relatively straightforward.
*   **New Repository Implementation:** Create a new module (e.g., `src/modules/infrastructure/sql_text_repository.py`) that implements the `ITextRepository` interface (e.g., using `SQLAlchemy` for a relational database or `Pymongo` for MongoDB).
*   **Update Dependencies:** Modify `src/modules/infrastructure/dependencies.py` to return an instance of your new database-backed repository instead of `FileTextRepository`. This change would be localized to this single file, leaving the `Application` and `API` layers completely untouched, showcasing the power of Clean Architecture and the Repository pattern.
*   **Data Migration (if necessary):** If you have existing data in the file system, you would need a one-time script to migrate that data into the new database.
*   **Configuration:** Update `AppConfig` or introduce new environment variables to hold database connection strings/credentials.## Complete Documentation Package

### README.md
```markdown
# Simple Text Analysis Report API

## Overview
The Simple Text Analysis Report API is a basic web service designed for managing simple text content. It allows users to create, retrieve, and delete text entries, each uniquely identified by a UUID. The API is built with FastAPI, adhering to Clean Architecture principles to ensure clear separation of concerns, testability, and maintainability.

**Key Features:**
*   **Text Content Management:** Create, retrieve, and delete text entries.
*   **Unique Identification:** Each text entry is assigned a unique UUID.
*   **File System Storage:** Utilizes the local file system for persistent storage of text content (easily extensible to databases).
*   **FastAPI Framework:** Leverages FastAPI for high performance, automatic data validation, and interactive API documentation.
*   **Clean Architecture:** Structured with distinct layers (Presentation, Application, Domain, Infrastructure) for modularity and scalability.
*   **In-memory Caching:** Employs LRU caching for `GET` operations to improve performance on frequently accessed items.

## Installation

Follow these steps to set up and run the application locally.

1.  **Clone the repository:**
    ```bash
    # git clone <your-repo-url>
    # cd <your-project-directory>
    ```

2.  **Create a Python Virtual Environment:**
    ```bash
    python3 -m venv .venv
    ```

3.  **Activate the Virtual Environment:**
    *   **On macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```
    *   **On Windows (Command Prompt):**
        ```bash
        .venv\Scripts\activate.bat
        ```
    *   **On Windows (PowerShell):**
        ```bash
        .venv\Scripts\Activate.ps1
        ```

4.  **Install Dependencies:**
    First, ensure `requirements.txt` is populated with the necessary packages.
    ```bash
    echo "fastapi==0.111.0" > requirements.txt
    echo "uvicorn==0.30.1" >> requirements.txt
    echo "pydantic==2.7.4" >> requirements.txt
    echo "pydantic-settings==2.3.3" >> requirements.txt
    echo "python-dotenv==1.0.1" >> requirements.txt
    echo "pytest==8.2.2" >> requirements.txt
    echo "httpx==0.27.0" >> requirements.txt
    echo "pytest-mock==3.14.0" >> requirements.txt
    ```
    Then install:
    ```bash
    pip install -r requirements.txt
    ```

## Quick Start

Once installed, you can run the application and interact with its API.

1.  **Run the Application:**
    The application will run on `http://0.0.0.0:8000`. The interactive API documentation will be available at `http://0.0.0.0:8000/docs`.
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload=False
    ```

2.  **Usage Examples (using `curl`):**

    *   **Health Check:**
        ```bash
        curl http://localhost:8000/health
        ```
        Expected Output:
        ```json
        {"status": "healthy", "message": "API is running smoothly!"}
        ```

    *   **Create a new text content:**
        ```bash
        curl -X POST "http://localhost:8000/api/v1/text" \
             -H "Content-Type: application/json" \
             -d '{"content": "This is a simple analysis report for test case XYZ. All checks passed."}'
        ```
        Example Output (note the `id` for subsequent steps):
        ```json
        {"id": "your-generated-uuid", "content": "This is a simple analysis report for test case XYZ. All checks passed.", "created_at": "YYYY-MM-DDTHH:MM:SS.sssZ", "updated_at": "YYYY-MM-DDTHH:MM:SS.sssZ"}
        ```

    *   **Get text content by ID (replace `YOUR_TEXT_ID` with the actual ID from the create response):**
        ```bash
        curl http://localhost:8000/api/v1/text/YOUR_TEXT_ID
        ```
        Example Output:
        ```json
        {"id": "YOUR_TEXT_ID", "content": "This is a simple analysis report for test case XYZ. All checks passed.", "created_at": "YYYY-MM-DDTHH:MM:SS.sssZ", "updated_at": "YYYY-MM-DDTHH:MM:SS.sssZ"}
        ```

    *   **Get text content by a non-existent ID (will return 404):**
        ```bash
        curl http://localhost:8000/api/v1/text/non-existent-uuid
        ```
        Expected Output:
        ```json
        {"detail":"Text content with ID 'non-existent-uuid' not found."}
        ```

    *   **Delete text content by ID (replace `YOUR_TEXT_ID` with the actual ID):**
        ```bash
        curl -X DELETE "http://localhost:8000/api/v1/text/YOUR_TEXT_ID"
        ```
        Expected Output (successful deletion returns 204 No Content):
        ```
        # (empty response body)
        ```
        Then, if you try to `GET` the deleted ID, it will return 404 Not Found.

## Features

### Core Features
*   **Text Entity Management:**
    *   **Create Text (`POST /api/v1/text`):** Accepts a JSON payload with a `content` field (string, min 1, max 10000 characters) and stores it. Returns the created text object including its unique `id` and timestamps.
    *   **Retrieve Text (`GET /api/v1/text/{text_id}`):** Fetches a specific text entry using its `id`. Returns the text object or a 404 if not found.
    *   **Delete Text (`DELETE /api/v1/text/{text_id}`):** Removes a text entry by its `id`. Returns 204 No Content on successful deletion or 404 if not found.
*   **Health Check (`GET /health`):** A simple endpoint to verify that the API is running and responsive.

### Technical Features
*   **Clean Architecture Adherence:** Strict separation of Domain, Application, Infrastructure, and API layers ensures modularity and maintainability.
*   **Repository Pattern:** Abstracts data persistence logic (`ITextRepository` interface) from business logic, allowing easy swapping of storage mechanisms (e.g., file system to database).
*   **FastAPI & Pydantic:** Leverages FastAPI for its performance and modern API features, and Pydantic for robust data validation and serialization.
*   **Dependency Injection:** Uses FastAPI's built-in dependency injection for managing component dependencies and testability.
*   **In-Memory LRU Caching:** `functools.lru_cache` is applied to `get_text_content` in the `TextService` to reduce redundant I/O operations for frequently accessed text entries.
*   **Robust Error Handling:** API endpoints provide generic, client-safe error messages for internal server errors while logging detailed exceptions internally. Specific 404 messages are provided for not-found resources.
*   **UUID-based Identifiers:** Uses `uuid.uuid4()` for generating unique, unpredictable text IDs, and validates these IDs in API path parameters using regex.
```

### API Documentation
```markdown
# API Reference

This documentation details the RESTful API endpoints for managing text content. For an interactive exploration of the API, please visit the Swagger UI at `/docs` when the application is running.

## Classes and Methods

### `POST /api/v1/text`
*   **Summary:** Create Text Content
*   **Description:** Creates a new piece of text content and stores it.
*   **Request Model (`CreateTextRequest`):**
    ```python
    class CreateTextRequest(BaseModel):
        content: str = Field(..., min_length=1, max_length=10000,
                             example="This is a simple test analysis report content.")
    ```
    *   `content` (string, **required**): The actual text content to be stored. Must be between 1 and 10,000 characters.
*   **Response Model (`TextResponse`):**
    ```python
    class TextResponse(BaseModel):
        id: str
        content: str
        created_at: str # ISO 8601 format
        updated_at: str # ISO 8601 format
    ```
    *   `id` (string): Unique identifier for the text.
    *   `content` (string): The actual text content.
    *   `created_at` (string): Timestamp when the text was created (ISO 8601 format).
    *   `updated_at` (string): Timestamp when the text was last updated (ISO 8601 format).
*   **Status Codes:**
    *   `201 Created`: Successfully created the text content.
    *   `422 Unprocessable Entity`: Invalid input (e.g., `content` missing or outside length constraints).
    *   `500 Internal Server Error`: An unexpected server-side error occurred.

### `GET /api/v1/text/{text_id}`
*   **Summary:** Get Text Content by ID
*   **Description:** Retrieves a specific piece of text content by its unique ID.
*   **Path Parameters:**
    *   `text_id` (string, **required**): The unique ID of the text content to retrieve. Must conform to UUID v4 format.
*   **Response Model (`TextResponse`):** (Same as for `POST /api/v1/text`)
*   **Status Codes:**
    *   `200 OK`: Successfully retrieved the text content.
    *   `404 Not Found`: Text content with the given ID was not found.
    *   `422 Unprocessable Entity`: Invalid UUID format for `text_id`.
    *   `500 Internal Server Error`: An unexpected server-side error occurred.

### `DELETE /api/v1/text/{text_id}`
*   **Summary:** Delete Text Content by ID
*   **Description:** Deletes a specific piece of text content by its unique ID.
*   **Path Parameters:**
    *   `text_id` (string, **required**): The unique ID of the text content to delete. Must conform to UUID v4 format.
*   **Response:** No content is returned on success.
*   **Status Codes:**
    *   `204 No Content`: Successfully deleted the text content.
    *   `404 Not Found`: Text content with the given ID was not found.
    *   `422 Unprocessable Entity`: Invalid UUID format for `text_id`.
    *   `500 Internal Server Error`: An unexpected server-side error occurred.

### `GET /health`
*   **Summary:** Health Check
*   **Description:** Checks the health of the application.
*   **Response Model:**
    ```json
    {"status": "healthy", "message": "API is running smoothly!"}
    ```
*   **Status Codes:**
    *   `200 OK`: The API is running and healthy.

## Examples

For comprehensive usage examples, refer to the [Quick Start](#quick-start) section in the `README.md`.
```

### User Guide
```markdown
# User Guide

This guide provides instructions on how to interact with the Simple Text Analysis Report API, from getting started to understanding its behavior.

## Getting Started

To begin using the API, you first need to set up the development environment and run the application.

1.  **Prerequisites:**
    *   Python 3.9+ installed on your system.
    *   `git` installed (if cloning from a repository).

2.  **Setup and Run:**
    Please follow the detailed steps in the [Installation](#installation) and [Quick Start](#quick-start) sections of the `README.md` file. This includes creating a virtual environment, installing dependencies, and running the `uvicorn` server.

3.  **Accessing API Documentation:**
    Once the application is running (typically at `http://localhost:8000`), you can access the interactive API documentation (Swagger UI) by navigating to `http://localhost:8000/docs` in your web browser. This interface allows you to send requests directly from your browser and view responses.

## Basic Usage

The API provides three main operations for text content: creating, retrieving, and deleting.

*   **Creating Text Content:**
    Use the `POST /api/v1/text` endpoint. You need to provide the text content in the request body as JSON.
    *   **Example:**
        ```json
        {
            "content": "This is my first test report entry."
        }
        ```
    The response will include the unique `id` generated for your text, which you will use for retrieval and deletion.

*   **Retrieving Text Content:**
    Use the `GET /api/v1/text/{text_id}` endpoint. Replace `{text_id}` with the actual ID you received when creating the text.
    *   **Example:** If your ID is `a1b2c3d4-e5f6-7890-1234-567890abcdef`, the URL would be `http://localhost:8000/api/v1/text/a1b2c3d4-e5f6-7890-1234-567890abcdef`.
    The response will be the full text object, including content and timestamps. If the ID does not exist, you will receive a 404 Not Found error.

*   **Deleting Text Content:**
    Use the `DELETE /api/v1/text/{text_id}` endpoint. Similar to retrieval, replace `{text_id}` with the ID of the text you wish to remove.
    *   **Example:** `http://localhost:8000/api/v1/text/a1b2c3d4-e5f6-7890-1234-567890abcdef`.
    A successful deletion will return a `204 No Content` status, indicating that the operation was successful and there is no information to return. If the ID does not exist, a 404 Not Found error is returned.

## Advanced Usage

While this is a "simple" API, here are a few considerations for advanced usage:

*   **Content Length:** The `content` field has a maximum length of 10,000 characters. Ensure your input adheres to this limit to avoid `422 Unprocessable Entity` errors.
*   **UUID Format:** All `text_id` parameters are expected to be valid UUID (v4) strings. Providing an incorrectly formatted ID will result in a `422 Unprocessable Entity` error.
*   **Caching Behavior:** The API utilizes an in-memory LRU cache for `GET` requests (`get_text_content` method). This means that if you repeatedly request the same text ID, subsequent requests might be served faster from the cache. The cache is automatically cleared when new text is created or existing text is deleted to ensure data consistency.

## Best Practices

*   **Validate Inputs:** Always validate the format and content of your requests to ensure they meet the API's requirements (e.g., content length, UUID format).
*   **Handle Errors Gracefully:** Implement logic in your client applications to correctly handle different HTTP status codes (201, 200, 204, 404, 422, 500) and their associated error messages.
*   **Monitor Health:** Periodically check the `/health` endpoint to ensure the API is operational.
*   **Secure your Environment:** For any non-development deployment, ensure proper network security, firewall rules, and access controls are in place.

## Troubleshooting

Here are some common issues and their solutions:

*   **Application Fails to Start:**
    *   **"Address already in use" error:** Another process might be using port 8000. Change the port in `uvicorn.run` (e.g., `uvicorn src.main:app --port 8001`).
    *   **Missing Dependencies:** Ensure you have activated your virtual environment and run `pip install -r requirements.txt`.
    *   **File System Permissions:** Verify that the user running the application has read/write permissions to the `./data/text_content` directory (or wherever `STORAGE_DIR` is configured).

*   **`404 Not Found`:**
    *   **For `GET /api/v1/text/{text_id}` or `DELETE /api/v1/text/{text_id}`:** The `text_id` you provided does not exist in the system. Double-check the ID or try creating new content.
    *   **For other endpoints:** You might be using an incorrect URL path. Refer to the API Documentation or Swagger UI for correct paths.

*   **`422 Unprocessable Entity`:**
    *   **For `POST /api/v1/text`:** The `content` field is likely missing, empty, or exceeds the maximum length of 10,000 characters.
    *   **For `GET /api/v1/text/{text_id}` or `DELETE /api/v1/text/{text_id}`:** The `text_id` provided is not a valid UUID format.

*   **`500 Internal Server Error`:**
    *   This indicates an unexpected server-side error. The API will return a generic message ("An internal server error occurred...").
    *   **Action:** Check the application logs (where you ran `uvicorn`) for detailed stack traces and error messages. These logs will provide insights into what went wrong internally (e.g., file system issues, JSON parsing errors).
    *   **Example log message to look for:** `ERROR - src.modules.infrastructure.file_text_repository - Error saving text...`, `ERROR - src.modules.application.text_service - Failed to create text content...`

*   **Data not persisting / files not appearing:**
    *   Verify the `STORAGE_DIR` path configured in `src/modules/infrastructure/config.py` (defaults to `./data/text_content`).
    *   Ensure the `lifespan` event in `src/main.py` successfully creates this directory upon startup (check startup logs).
    *   Check file system permissions for the `STORAGE_DIR`.

```

### Developer Guide
```markdown
# Developer Guide

This guide provides an in-depth look into the architecture, development practices, and deployment considerations for the Simple Text Analysis Report API.

## Architecture Overview

The system adopts a **Layered Architecture** with strong adherence to **Clean Architecture** (also known as Ports and Adapters). This design pattern ensures clear separation of concerns, testability, and flexibility for future evolution.

**Core Layers:**

1.  **Presentation/API Layer (`src/modules/api`):**
    *   **Responsibility:** Handles external HTTP requests, validates input, calls the application layer, and formats responses. This layer is thin and framework-specific (FastAPI).
    *   **Components:** `text_controller.py` (FastAPI router and endpoints), Pydantic models for request/response schemas.

2.  **Application Layer (`src/modules/application`):**
    *   **Responsibility:** Contains application-specific business rules and orchestrates the flow of data. It defines *what* the application does in terms of use cases. It interacts with domain entities and delegates persistence to the infrastructure layer.
    *   **Components:** `text_service.py` (implements use cases like `create_text_content`, `get_text_content`, `delete_text_content`). It uses `functools.lru_cache` for read optimization.

3.  **Domain Layer (`src/modules/domain`):**
    *   **Responsibility:** Encapsulates the core business logic and entities, independent of any external frameworks, databases, or UI. It defines *the rules of the business*. This is the "core" of the application.
    *   **Components:**
        *   `text.py`: Defines the `Text` entity (Pydantic `BaseModel`) with its attributes and internal behaviors (e.g., `update_content`).
        *   `interfaces.py`: Defines abstract interfaces (Ports) for external concerns, specifically `ITextRepository`, which is the contract for data persistence.

4.  **Infrastructure Layer (`src/modules/infrastructure`):**
    *   **Responsibility:** Provides concrete implementations (Adapters) for the interfaces defined in the Domain and Application layers. This layer handles external details like data storage, configuration, and dependency injection.
    *   **Components:**
        *   `file_text_repository.py`: Implements `ITextRepository` using the local file system for storage (each text is a JSON file).
        *   `config.py`: Manages application configuration settings (`AppConfig`).
        *   `dependencies.py`: Configures and provides dependency-injected instances (e.g., `TextService`, `FileTextRepository`) using FastAPI's `Depends` system.

**Data Flow Example (Create Text):**

1.  An HTTP `POST` request arrives at `src/modules/api/text_controller.py`.
2.  `text_controller` validates the request body (`CreateTextRequest`) and calls `text_service.create_text_content()`.
3.  `text_service` creates a `Text` domain entity and then calls `text_repository.save()` (an `ITextRepository` method).
4.  The concrete `FileTextRepository` (from `src/modules/infrastructure/file_text_repository.py`) saves the `Text` entity as a JSON file to disk.
5.  The saved `Text` entity is returned up the call stack to `text_controller`, which then serializes it into an HTTP `201 Created` response.

## Contributing Guidelines

We welcome contributions to this project! To ensure code quality and consistency, please follow these guidelines:

*   **Code Style:** Adhere strictly to [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code style. Use a formatter like [Black](https://github.com/psf/black) to automatically format your code.
*   **Type Hinting:** Use [PEP 484](https://www.python.org/dev/peps/pep-0484/) compliant type hints for all function arguments, return values, and variable assignments. Use [MyPy](http://mypy-lang.org/) for static type checking.
*   **Docstrings:** All modules, classes, and public methods/functions must have comprehensive docstrings following [PEP 257](https://www.python.org/dev/peps/pep-0257/) conventions. Explain purpose, arguments, returns, and any exceptions raised.
*   **Testing:**
    *   Write unit tests for all new features and bug fixes.
    *   Ensure good test coverage.
    *   Use `pytest` for testing and `unittest.mock` or `pytest-mock` for mocking dependencies.
    *   Run tests locally before submitting pull requests.
*   **Clean Architecture:** Ensure any new features or modifications strictly adhere to the layered architecture. Changes should be localized to the appropriate layer.
*   **Git Workflow:**
    *   Branch from `main` for new features or bug fixes.
    *   Use clear and concise commit messages.
    *   Submit Pull Requests (PRs) for review.

## Testing Instructions

The project includes a comprehensive suite of tests covering all layers of the application.

1.  **Activate Virtual Environment:**
    ```bash
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    .venv\Scripts\activate.bat
    ```

2.  **Run Tests:**
    Navigate to the project root directory and execute `pytest`:
    ```bash
    pytest
    ```
    This command will discover and run all tests in the `tests/` directory.

### Test Suite Structure

The `tests/` directory mirrors the `src/modules/` structure, ensuring that tests for each component are co-located with their respective logical layers:

*   `tests/test_main.py`: Tests the main application entry point, health check, and lifespan events.
*   `tests/modules/domain/test_text.py`: Unit tests for the `Text` domain entity, covering creation, updates, and serialization.
*   `tests/modules/infrastructure/test_file_text_repository.py`: Unit and integration tests for the `FileTextRepository`, covering save, find, delete operations, and error handling with mocked file system interactions. Uses `pytest` fixtures for temporary storage.
*   `tests/modules/application/test_text_service.py`: Unit tests for the `TextService` (application layer), mocking the `ITextRepository` to test business logic in isolation, including cache behavior.
*   `tests/modules/api/test_text_controller.py`: Integration tests for the FastAPI API endpoints, using `TestClient` and mocking the `TextService` to verify request/response handling, validation, and error scenarios.

## Deployment Guide

This section provides basic guidance for deploying the application.

*   **Production Command:**
    When deploying, ensure `reload=False` is set in your `uvicorn` command for optimal performance and security:
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 # Example with workers
    ```
    The `0.0.0.0` host is suitable for containerized deployments where the container port is mapped to a host port.

*   **Containerization (Recommended):**
    For consistent environments and easier scaling, consider containerizing the application using Docker. A `Dockerfile` would typically:
    *   Use a Python base image.
    *   Copy `requirements.txt` and install dependencies.
    *   Copy the `src/` directory.
    *   Define the `CMD` to run `uvicorn`.

    Example (conceptual `Dockerfile`):
    ```dockerfile
    # FROM python:3.9-slim-buster
    # WORKDIR /app
    # COPY requirements.txt .
    # RUN pip install --no-cache-dir -r requirements.txt
    # COPY src/ ./src
    # EXPOSE 8000
    # CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

*   **Cloud Deployment:**
    The application can be deployed to various cloud platforms that support Python applications or Docker containers, such as:
    *   AWS ECS/EKS (Elastic Container Service/Kubernetes Service)
    *   Google Cloud Run/GKE (Kubernetes Engine)
    *   Azure Container Apps/AKS (Kubernetes Service)
    *   Heroku, Render, etc.

*   **Environment Variables:**
    The `STORAGE_DIR` for file storage can be configured via the `STORAGE_DIR` environment variable. In production, it is highly recommended to set this to a secure, dedicated path (e.g., `/var/data/app_text_content`) outside of the application's deployable artifact.

*   **Reverse Proxy:**
    In production, it's common practice to place a reverse proxy (e.g., Nginx, Caddy) in front of the FastAPI application. This handles SSL termination, load balancing, and serves static files (if any), enhancing security and performance.

*   **Logging:**
    Ensure your deployment environment captures logs from `uvicorn` and the application (`src/main.py` configures basic logging). For production, integrate with a centralized logging system (e.g., ELK stack, Splunk, cloud logging services) for monitoring and debugging.
```

### Quality and Security Notes
```markdown
# Quality and Security Report

This report summarizes the quality and security posture of the Simple Text Analysis Report API, based on thorough reviews.

## Code Quality Summary

**Score: 9/10**

**Strengths:**
*   **Excellent Architecture Adherence:** Strictly follows Clean Architecture (Layered Architecture with Ports & Adapters), leading to high modularity, clear separation of concerns, and easy maintainability.
*   **Robust Test Suite:** Comprehensive unit and integration tests for all layers, with strong isolation via mocking, covering success paths and edge cases (including error handling).
*   **Clear Naming & Docstrings:** Consistent PEP 8 naming and comprehensive PEP 257 docstrings for all modules, classes, and methods, greatly enhancing readability and understanding.
*   **Effective Error Handling:** Graceful exception handling across layers, converting internal errors to appropriate HTTP status codes and returning generic, client-safe messages at the API boundary, while logging detailed information internally.
*   **Strong Type Hinting:** Consistent use of PEP 484 type hints improves code clarity, maintainability, and enables static analysis.
*   **Modern Python Practices:** Leverages Pydantic V2, FastAPI's async/await and dependency injection, and `pathlib` for robust file operations.
*   **Maintainable Design:** Modular structure and clear interfaces allow for easy modification and extension (e.g., swapping storage mechanisms with minimal impact).

**Areas for Improvement (Minor):**
*   **Generic Exception Handling in Service Layer:** While functional, catching a generic `Exception` in `TextService` could be refined to catch more specific `RuntimeError`s from the repository, potentially wrapping them in custom application-specific exceptions for finer-grained control in larger systems.
*   **Dependency Management Tooling:** For future projects, consider migrating from `requirements.txt` to `pyproject.toml` with tools like Poetry or PDM for more robust dependency management.

## Security Assessment

**Score: 6/10**

**Strengths:**
*   **Pydantic for Input Validation:** Effectively prevents many common injection attacks and ensures data integrity at the API boundary with schema validation and length constraints.
*   **Clean Architecture:** Modularity makes it easier to apply security controls at specific layers and swap components with more secure alternatives.
*   **UUIDs for IDs:** Using unpredictable UUIDs for identifiers mitigates ID enumeration risks (though not a substitute for authorization).
*   **Dependency Injection:** Facilitates testing and allows for integration of security components.
*   **Refined Error Handling:** API returns generic `500 Internal Server Error` messages, preventing information leakage to external clients.
*   **Centralized Configuration:** `AppConfig` promotes better management of sensitive settings.
*   **`pathlib` Usage:** For robust and OS-agnostic file path manipulation.

**Critical Issues (High Priority - Immediate Address):**
*   **Missing Authentication and Authorization:** This is the most significant vulnerability. All API endpoints are publicly accessible, allowing anyone to create, retrieve, or delete text content. This is a critical flaw for any non-trivial application.

**Medium Priority Issues (Address Soon):**
*   **Potential Path Traversal Risk:** While UUIDs generated internally prevent immediate risk, the pattern of constructing file paths from user-provided IDs (`text_id.json`) needs vigilance. Stricter validation (UUID regex is implemented) and secure file operations are key.
*   **Default Storage Location and Permissions:** The default `./data/text_content` might be insecure in production. File permissions inherited from the process's umask may not be restrictive enough.
*   **Data at Rest Security (Lack of Encryption):** Text content is stored as plain JSON files. If sensitive data were ever stored, it would be vulnerable to direct file system access.
*   **Lack of Rate Limiting:** No mechanism to limit requests per client, making the API vulnerable to DoS attacks.
*   **No Data Deletion/Lifecycle Management (Addressed in Refactoring):** The refactored code now includes deletion functionality, which mitigates concerns about uncontrolled data accumulation.

**Low Priority Issues:**
*   **Development Mode Settings in Production:** `reload=True` in `uvicorn.run` (addressed in refactoring to `reload=False`) is a development-only feature that should not be used in production.
*   **Logging Verbosity:** If logs are not secured, verbose `logger.exception` calls could expose internal details.

**Recommendations:**
1.  **Implement Authentication and Authorization (Immediate Priority):** Integrate JWT or OAuth 2.0 for authentication and RBAC for authorization.
2.  **Harden File System Storage:** Explicitly set secure file permissions (most restrictive possible), and use a dedicated, isolated storage volume in production.
3.  **Implement Data Encryption at Rest:** Encrypt sensitive text content before writing to disk.
4.  **Add Rate Limiting:** Integrate a rate-limiting middleware (e.g., `fastapi-limiter`).
5.  **Secure Deployment Practices:** Maintain separate configurations for environments, use container security best practices, and leverage secrets management solutions.

## Performance Characteristics

**Score: 6/10** (Improved from initial implementation due to caching, but file system remains a bottleneck)

**Overall:** The API layer (FastAPI, Pydantic, async I/O support) provides good architectural choices for performance. However, the use of the file system for persistence is a significant bottleneck for anything beyond very light load or for larger text volumes.

**Critical Performance Bottlenecks:**
*   **File System Persistence:** Direct disk I/O for every `save` and `find_by_id` operation in `FileTextRepository` leads to high latency and I/O contention under concurrent load. This limits horizontal scalability.

**Optimization Opportunities (Implemented in Refactoring):**
*   **Caching (`functools.lru_cache`):** Implemented on `get_text_content` in `TextService` to reduce repetitive disk I/O for reads. Cache is invalidated on create/delete.

**Further Optimization Opportunities (Recommended):**
*   **Database Migration (Critical):** Transition from file system storage to a proper database (e.g., PostgreSQL/MongoDB) for optimized I/O, indexing, concurrency control, and true horizontal scalability.
*   **Monitoring:** Set up monitoring for request latency, throughput, error rates, and disk I/O metrics.
*   **Load Testing:** Conduct load tests to identify actual breakpoints and bottlenecks under anticipated load.

**Algorithmic Analysis:**
*   **`Text` Entity:** Operations like UUID generation, Pydantic validation/serialization are efficient (O(1) or O(L) where L is content length).
*   **`FileTextRepository`:** `save` and `find_by_id` are dominated by file I/O (O(L)).
*   **Overall Logic:** Application and API layers primarily delegate, adding minimal algorithmic overhead (O(1) per call).
The bottleneck is the inherent performance of file system operations in a concurrent API context, not the algorithms themselves.

**Resource Utilization:**
*   **Memory:** Low, as text content (max 10KB) is small.
*   **CPU:** Low, as text processing is minimal. The application is I/O-bound.
*   **I/O Efficiency:** Poor for high-throughput due to direct disk reads/writes. `asyncio` helps prevent blocking the server, but doesn't speed up the disk I/O itself.

**Scalability Assessment:**
*   **Vertical Scaling:** Limited by single machine disk I/O.
*   **Horizontal Scaling:** Very challenging with file system persistence without introducing complex shared file systems (NFS, EFS) which become new bottlenecks and consistency challenges. The stateless nature of the API layer is good for horizontal scaling *of the compute*, but the storage layer undermines this.

## Known Limitations

*   **Scalability for Persistence:** The current file system-based persistence (`FileTextRepository`) is a significant limitation for high-volume or highly concurrent usage. It is not designed for distributed environments or large datasets.
*   **Security (Authentication/Authorization):** The API currently has no authentication or authorization. All operations are publicly accessible, which is a major security limitation for any real-world application with restricted access requirements.
*   **No Data Update Functionality (API):** While the `Text` domain model has an `update_content` method, there is no corresponding API endpoint exposed to update existing text content after creation.
*   **Limited Error Detail for Clients:** For internal server errors (HTTP 500), the API returns generic messages to prevent information leakage. While good for security, this means clients will not receive specific technical reasons for the failure. Detailed errors are only available in server logs.
```

### Changelog
```markdown
# Changelog

## Version History

*   **Version 1.0.0 (Current)**
    *   **Features:**
        *   Initial release with core text management functionalities (create, retrieve, delete).
        *   FastAPI-based RESTful API.
        *   Clean Architecture implementation.
        *   File system-based persistence.
        *   In-memory LRU caching for read operations.
        *   UUID-based text identifiers with input validation.
    *   **Improvements:**
        *   Enhanced error handling in API responses (generic messages for 500s).
        *   Stricter input validation for `text_id` parameters (UUID regex).
        *   Production readiness: `uvicorn` runs with `reload=False`.
        *   Code quality improvements, including `AppConfig` initialization.
        *   Comprehensive unit and integration tests.

## Breaking Changes

*   **API Error Messages:** The `detail` message for `HTTP 500 Internal Server Error` responses has changed from containing specific internal exception details to a more generic, client-safe message (e.g., "An internal server error occurred..."). Clients that parsed or relied on the specific error messages from previous, unrefactored implementations will need to adjust.

## Migration Guides

### Migrating to Version 1.0.0 (from initial implementation)

This guide outlines the necessary steps to migrate to the refactored and improved codebase of version 1.0.0.

**Backward Compatibility:**
*   The `POST /api/v1/text` and `GET /api/v1/text/{text_id}` endpoints remain backward compatible in terms of their request/response schemas and behavior for successful operations.
*   The new `DELETE /api/v1/text/{text_id}` endpoint is an additive change and does not affect existing functionality.

**Breaking Changes to Note:**
*   As noted above, `HTTP 500` error `detail` messages are now generic. Update any client-side error parsing logic accordingly.

**Migration Steps:**

1.  **Update Codebase:** Replace your entire `src/` directory content with the new refactored code provided. Ensure all files (especially `main.py`, all files under `src/modules/`, and the new `delete_by_id` method in `src/modules/domain/interfaces.py` and `src/modules/infrastructure/file_text_repository.py`) are updated.
2.  **Update Tests:** Replace your existing `tests/` directory content with the new updated tests. This ensures that new features are tested and existing functionality is verified.
3.  **Dependency Review:** The core Python package dependencies remain the same. Ensure your `requirements.txt` matches the one provided in the [Installation](#installation) section of the `README.md`.
4.  **Configuration (`AppConfig`):** The `AppConfig.__init__` method no longer performs the directory creation (`mkdir`) itself. This is now solely handled by the FastAPI `lifespan` event in `src/main.py` at application startup. No direct action is required unless you had custom code that specifically relied on `AppConfig.__init__` for directory creation outside the FastAPI application context.
5.  **Deployment Environment:** If running in a production environment, verify that your `uvicorn` command (or equivalent deployment setup) sets `reload=False`. This is now explicitly handled in `src/main.py` for direct execution but is good practice to confirm in your deployment scripts.

### Future Migration (Database Integration)

The current architecture is specifically designed to facilitate an easy transition from file system storage to a more robust database solution (e.g., PostgreSQL, MongoDB).

**Steps for Database Migration:**

1.  **Choose a Database and ORM/Client:** Select your desired database (e.g., PostgreSQL) and a suitable Python library (e.g., `SQLAlchemy` for ORM, `psycopg2` or `asyncpg` for direct client).
2.  **Create New Repository Implementation:**
    *   Create a new module within `src/modules/infrastructure/` (e.g., `sql_text_repository.py` or `mongo_text_repository.py`).
    *   This new class **must** implement the `ITextRepository` interface (`save`, `find_by_id`, `delete_by_id`) defined in `src/modules/domain/interfaces.py`.
    *   All database-specific logic (connection, queries, ORM mapping) will reside solely within this new repository.
3.  **Update Dependency Injection:**
    *   Modify `src/modules/infrastructure/dependencies.py`.
    *   Change the `get_text_repository` function to return an instance of your *new* database-backed repository instead of `FileTextRepository`. This is the only file outside the new repository implementation that needs modification to switch storage.
    *   Example:
        ```python
        # src/modules/infrastructure/dependencies.py (Conceptual change)
        # ... imports ...
        # from src.modules.infrastructure.sql_text_repository import SQLTextRepository # New import

        def get_text_repository(config: AppConfig = get_app_config()) -> ITextRepository: # Return interface type
            # return FileTextRepository(config) # Comment out or remove
            # return SQLTextRepository(config.DATABASE_URL) # Use your new repository
            pass
        ```
4.  **Database Configuration:**
    *   Update `src/modules/infrastructure/config.py` to include database connection strings or credentials (e.g., `DATABASE_URL`). Use environment variables for sensitive information.
5.  **Data Migration (if needed):**
    *   If you have existing data stored in the file system from the current implementation, write a one-time script to read data from the file system and insert it into your new database.
6.  **Testing:**
    *   Write new unit tests for your database-backed repository.
    *   Run integration tests to ensure the entire application works correctly with the new persistence layer.

This modular approach ensures that the core business logic (in `TextService` and `Text` domain model) remains completely untouched during a database migration, highlighting the benefits of Clean Architecture.
```
```python
# The final code to be documented. This is a merge of initial and refactored code.
# The user already provided the refactored code as "Final Code", so I'll just
# make sure to use that for the documentation.
refactored_code = """
# src/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.modules.api.text_controller import router as text_router
from src.modules.infrastructure.config import AppConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"
    Handles startup and shutdown events for the application.
    Ensures necessary directories are created.
    \"\"\"
    config = AppConfig()
    # Create storage directory if it doesn't exist
    config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Application startup: Storage directory ensured at {config.STORAGE_DIR}")
    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title="Simple Text Analysis Report API",
    description="A basic API for managing text content, demonstrating Clean Architecture principles.",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routers
app.include_router(text_router, prefix="/api/v1")

@app.get("/health", summary="Health Check")
async def health_check() -> dict[str, str]:
    \"\"\"
    Checks the health of the application.

    Returns:
        A dictionary indicating the application's status.
    \"\"\"
    return {"status": "healthy", "message": "API is running smoothly!"}

if __name__ == "__main__":
    import uvicorn
    # In a production environment, 'reload=True' should be removed.
    # The host '0.0.0.0' is suitable for containerized deployments.
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)

# src/modules/domain/text.py
import datetime
import uuid
from typing import Self

from pydantic import BaseModel, Field


class Text(BaseModel):
    \"\"\"
    Represents a core text entity in the domain.

    Attributes:
        id (str): Unique identifier for the text.
        content (str): The actual text content.
        created_at (datetime.datetime): Timestamp when the text was created.
        updated_at (datetime.datetime): Timestamp when the text was last updated.
    \"\"\"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., min_length=1, max_length=10000)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    def update_content(self, new_content: str) -> Self:
        \"\"\"
        Updates the content of the text and sets the updated_at timestamp.

        Args:
            new_content (str): The new text content.

        Returns:
            Self: The updated Text instance.
        \"\"\"
        self.content = new_content
        self.updated_at = datetime.datetime.utcnow()
        return self

    class Config:
        \"\"\"Pydantic model configuration.\"\"\"
        json_encoders = {datetime.datetime: lambda dt: dt.isoformat()}
        populate_by_name = True # Allow population by field name for better compatibility
        from_attributes = True # New in Pydantic V2, replaces allow_population_by_field_name

# src/modules/domain/interfaces.py
import abc
from typing import Optional

from src.modules.domain.text import Text


class ITextRepository(abc.ABC):
    \"\"\"
    Abstract Base Class (ABC) defining the contract for text content persistence.
    This is a "Port" in Clean Architecture.
    \"\"\"

    @abc.abstractmethod
    def save(self, text: Text) -> Text:
        \"\"\"
        Saves a Text entity to the persistence layer.

        Args:
            text (Text): The Text entity to save.

        Returns:
            Text: The saved Text entity (potentially with updated attributes like ID or timestamps).
        \"\"\"
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_id(self, text_id: str) -> Optional[Text]:
        \"\"\"
        Retrieves a Text entity by its unique identifier.

        Args:
            text_id (str): The unique ID of the text to retrieve.

        Returns:
            Optional[Text]: The Text entity if found, otherwise None.
        \"\"\"
        raise NotImplementedError

    @abc.abstractmethod
    def delete_by_id(self, text_id: str) -> bool:
        \"\"\"
        Deletes a Text entity by its unique identifier.

        Args:
            text_id (str): The unique ID of the text to delete.

        Returns:
            bool: True if the text was deleted, False otherwise.
        \"\"\"
        raise NotImplementedError

# src/modules/infrastructure/config.py
import os
from pathlib import Path


class AppConfig:
    \"\"\"
    Configuration settings for the application.
    \"\"\"
    # Base directory for storing text files
    STORAGE_DIR: Path = Path(os.getenv("STORAGE_DIR", "./data/text_content"))

    def __init__(self) -> None:
        \"\"\"
        Initializes AppConfig. The storage directory creation is handled by the
        FastAPI lifespan event to ensure it's done once at application startup.
        \"\"\"
        pass # Removed mkdir call, as it's handled in main.py lifespan

# src/modules/infrastructure/file_text_repository.py
import json
import logging
import os # Import os for os.remove
from pathlib import Path
from typing import Optional

from src.modules.domain.interfaces import ITextRepository
from src.modules.domain.text import Text
from src.modules.infrastructure.config import AppConfig

logger = logging.getLogger(__name__)


class FileTextRepository(ITextRepository):
    \"\"\"
    Concrete implementation of ITextRepository using the file system for storage.
    Each Text entity is stored as a JSON file, named after its ID.
    \"\"\"

    def __init__(self, config: AppConfig) -> None:
        \"\"\"
        Initializes the FileTextRepository.

        Args:
            config (AppConfig): Application configuration.
        \"\"\"
        self.storage_dir = config.STORAGE_DIR
        logger.info(f"FileTextRepository initialized. Storage directory: {self.storage_dir}")

    def _get_file_path(self, text_id: str) -> Path:
        \"\"\"
        Constructs the file path for a given text ID.

        Args:
            text_id (str): The ID of the text.

        Returns:
            Path: The full file path.
        \"\"\"
        return self.storage_dir / f"{text_id}.json"

    def save(self, text: Text) -> Text:
        \"\"\"
        Saves a Text entity to a JSON file.

        Args:
            text (Text): The Text entity to save.

        Returns:
            Text: The saved Text entity.
        \"\"\"
        file_path = self._get_file_path(text.id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text.model_dump_json(indent=2))
            logger.info(f"Text '{text.id}' saved to {file_path}")
            return text
        except IOError as e:
            logger.error(f"Error saving text '{text.id}' to {file_path}: {e}")
            raise RuntimeError(f"Failed to save text content: {e}") from e

    def find_by_id(self, text_id: str) -> Optional[Text]:
        \"\"\"
        Retrieves a Text entity by reading its corresponding JSON file.

        Args:
            text_id (str): The unique ID of the text to retrieve.

        Returns:
            Optional[Text]: The Text entity if found, otherwise None.
        \"\"\"
        file_path = self._get_file_path(text_id)
        if not file_path.exists():
            logger.info(f"Text '{text_id}' not found at {file_path}")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            text = Text.model_validate(data)
            logger.info(f"Text '{text_id}' loaded from {file_path}")
            return text
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading text '{text_id}' from {file_path}: {e}")
            raise RuntimeError(f"Failed to load text content: {e}") from e

    def delete_by_id(self, text_id: str) -> bool:
        \"\"\"
        Deletes a Text entity by deleting its corresponding JSON file.

        Args:
            text_id (str): The unique ID of the text to delete.

        Returns:
            bool: True if the text was deleted, False otherwise.
        \"\"\"
        file_path = self._get_file_path(text_id)
        if not file_path.exists():
            logger.info(f"Attempted to delete non-existent text '{text_id}' at {file_path}")
            return False
        try:
            os.remove(file_path)
            logger.info(f"Text '{text_id}' deleted from {file_path}")
            return True
        except OSError as e: # Catch OSError for file system operations
            logger.error(f"Error deleting text '{text_id}' from {file_path}: {e}")
            raise RuntimeError(f"Failed to delete text content: {e}") from e

# src/modules/application/text_service.py
import logging
from functools import lru_cache # Import lru_cache
from typing import Optional

from src.modules.domain.interfaces import ITextRepository
from src.modules.domain.text import Text

logger = logging.getLogger(__name__)


class TextService:
    \"\"\"
    Application service for managing text content.
    Orchestrates business logic and interacts with the domain and infrastructure layers.
    \"\"\"

    def __init__(self, text_repository: ITextRepository) -> None:
        \"\"\"
        Initializes the TextService with a text repository.

        Args:
            text_repository (ITextRepository): The repository for Text entities.
        \"\"\"
        self.text_repository = text_repository
        logger.info("TextService initialized.")

    def create_text_content(self, content: str) -> Text:
        \"\"\"
        Creates a new Text entity and persists it.

        Args:
            content (str): The raw text content to be stored.

        Returns:
            Text: The newly created Text entity.
        \"\"\"
        try:
            new_text = Text(content=content)
            saved_text = self.text_repository.save(new_text)
            logger.info(f"New text content created with ID: {saved_text.id}")
            # Invalidate cache for this ID if it was in cache (though unlikely for new item)
            self.get_text_content.cache_clear() # Clear cache on creation to ensure consistency
            return saved_text
        except RuntimeError as e: # Catch specific RuntimeError from repository
            logger.error(f"Failed to create text content due to repository error: {e}")
            raise # Re-raise for API layer to handle
        except Exception as e:
            logger.exception(f"An unexpected error occurred while creating text content: {e}")
            raise

    @lru_cache(maxsize=128) # Apply LRU cache for performance
    def get_text_content(self, text_id: str) -> Optional[Text]:
        \"\"\"
        Retrieves a Text entity by its ID.
        Results are cached using LRU cache for performance.

        Args:
            text_id (str): The unique ID of the text to retrieve.

        Returns:
            Optional[Text]: The Text entity if found, otherwise None.
        \"\"\"
        try:
            text = self.text_repository.find_by_id(text_id)
            if text:
                logger.info(f"Retrieved text content with ID: {text_id}")
            else:
                logger.info(f"Text content with ID '{text_id}' not found.")
            return text
        except RuntimeError as e: # Catch specific RuntimeError from repository
            logger.error(f"Failed to retrieve text content with ID '{text_id}' due to repository error: {e}")
            raise # Re-raise for API layer to handle
        except Exception as e:
            logger.exception(f"An unexpected error occurred while retrieving text content with ID '{text_id}': {e}")
            raise

    def delete_text_content(self, text_id: str) -> bool:
        \"\"\"
        Deletes a Text entity by its ID.

        Args:
            text_id (str): The unique ID of the text to delete.

        Returns:
            bool: True if the text was deleted, False otherwise.
        \"\"\"
        try:
            deleted = self.text_repository.delete_by_id(text_id)
            if deleted:
                logger.info(f"Text content with ID '{text_id}' successfully deleted.")
                self.get_text_content.cache_clear() # Invalidate cache if item is deleted
            else:
                logger.info(f"Text content with ID '{text_id}' not found for deletion.")
            return deleted
        except RuntimeError as e: # Catch specific RuntimeError from repository
            logger.error(f"Failed to delete text content with ID '{text_id}' due to repository error: {e}")
            raise # Re-raise for API layer to handle
        except Exception as e:
            logger.exception(f"An unexpected error occurred while deleting text content with ID '{text_id}': {e}")
            raise

# src/modules/infrastructure/dependencies.py
from functools import lru_cache

from src.modules.application.text_service import TextService
from src.modules.infrastructure.config import AppConfig
from src.modules.infrastructure.file_text_repository import FileTextRepository


@lru_cache()
def get_app_config() -> AppConfig:
    \"\"\"
    Provides a singleton instance of the application configuration.
    \"\"\"
    return AppConfig()

def get_text_repository(config: AppConfig = get_app_config()) -> FileTextRepository:
    \"\"\"
    Provides a concrete instance of ITextRepository (FileTextRepository).
    \"\"\"
    return FileTextRepository(config)

def get_text_service(
    text_repository: FileTextRepository = get_text_repository(),
) -> TextService:
    \"\"\"
    Provides an instance of TextService, injecting its dependencies.
    \"\"\"
    return TextService(text_repository)

# src/modules/api/text_controller.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status # Import Path
from pydantic import BaseModel, Field

from src.modules.application.text_service import TextService
from src.modules.domain.text import Text
from src.modules.infrastructure.dependencies import get_text_service

# Regex for UUID validation (standard UUID v4 format)
UUID_REGEX = "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"


class CreateTextRequest(BaseModel):
    \"\"\"Request model for creating new text content.\"\"\"
    content: str = Field(..., min_length=1, max_length=10000,
                         example="This is a simple test analysis report content.")


class TextResponse(BaseModel):
    \"\"\"Response model for text content.\"\"\"
    id: str
    content: str
    created_at: str # Use str for ISO format for API response consistency
    updated_at: str # Use str for ISO format for API response consistency

    model_config = {
        "from_attributes": True # Allow population from Text domain model attributes
        # Removed json_encoders here as it's handled by Text domain model
    }

router = APIRouter()


@router.post(
    "/text",
    response_model=TextResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Text Content",
    description="Creates a new piece of text content and stores it.",
)
async def create_text_content_endpoint(
    request: CreateTextRequest,
    text_service: Annotated[TextService, Depends(get_text_service)],
) -> TextResponse:
    \"\"\"
    Endpoint to create new text content.

    Args:
        request (CreateTextRequest): The request body containing the text content.
        text_service (TextService): Dependency-injected text service.

    Returns:
        TextResponse: The created text content with its ID and timestamps.

    Raises:
        HTTPException: If there's an internal server error during creation.
    \"\"\"
    try:
        text = text_service.create_text_content(request.content)
        return TextResponse.model_validate(text)
    except Exception: # Catch generic exception for logging, return generic message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while creating text content. Please try again later.",
        )


@router.get(
    "/text/{text_id}",
    response_model=TextResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Text Content by ID",
    description="Retrieves a specific piece of text content by its unique ID.",
)
async def get_text_content_endpoint(
    text_id: Annotated[str, Path(regex=UUID_REGEX)], # Add regex validation
    text_service: Annotated[TextService, Depends(get_text_service)],
) -> TextResponse:
    \"\"\"
    Endpoint to retrieve text content by ID.

    Args:
        text_id (str): The unique ID of the text content to retrieve.
        text_service (TextService): Dependency-injected text service.

    Returns:
        TextResponse: The retrieved text content.

    Raises:
        HTTPException: If the text content is not found (404) or an internal error occurs (500).
    \"\"\"
    try:
        text = text_service.get_text_content(text_id)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Text content with ID '{text_id}' not found.",
            )
        return TextResponse.model_validate(text)
    except HTTPException:
        # Re-raise HTTPException if it's already a 404 from above
        raise
    except Exception: # Catch generic exception for logging, return generic message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while retrieving text content. Please try again later.",
        )


@router.delete(
    "/text/{text_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Text Content by ID",
    description="Deletes a specific piece of text content by its unique ID.",
)
async def delete_text_content_endpoint(
    text_id: Annotated[str, Path(regex=UUID_REGEX)], # Add regex validation
    text_service: Annotated[TextService, Depends(get_text_service)],
) -> None:
    \"\"\"
    Endpoint to delete text content by ID.

    Args:
        text_id (str): The unique ID of the text content to delete.
        text_service (TextService): Dependency-injected text service.

    Raises:
        HTTPException: If the text content is not found (404) or an internal error occurs (500).
    \"\"\"
    try:
        deleted = text_service.delete_text_content(text_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Text content with ID '{text_id}' not found.",
            )
        # Return 204 No Content if successful
    except HTTPException:
        raise
    except Exception: # Catch generic exception for logging, return generic message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while deleting text content. Please try again later.",
        )
"""
```

## 📁 Generated Files
- `00_workflow_metadata.md`
- `01_requirementanalyzer.md`
- `02_architecturaldesigner.md`
- `03_codegenerator.md`
- `04_performancereviewer.md`
- `05_qualityreviewer.md`
- `06_securityreviewer.md`
- `07_coderefactorer.md`
- `08_documentationgenerator.md`

## 🎯 Workflow Performance
- **Average time per agent**: 40.03s
- **Success rate**: 100.0%

---
*Workflow completed at 2025-07-06 16:16:55*
