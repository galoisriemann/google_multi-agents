# CodeGenerator Output
**Agent**: CodeGenerator
**Execution Order**: 3
**Timestamp**: 2025-07-06 16:12:59

---

## Code Implementation

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
```

---
*Saved by after_agent_callback on 2025-07-06 16:12:59*
