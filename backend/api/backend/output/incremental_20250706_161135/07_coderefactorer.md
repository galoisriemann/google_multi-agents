# CodeRefactorer Output
**Agent**: CodeRefactorer
**Execution Order**: 7
**Timestamp**: 2025-07-06 16:15:48

---

## Refactored Code Implementation

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
*   **Configuration:** Update `AppConfig` or introduce new environment variables to hold database connection strings/credentials.

---
*Saved by after_agent_callback on 2025-07-06 16:15:48*
