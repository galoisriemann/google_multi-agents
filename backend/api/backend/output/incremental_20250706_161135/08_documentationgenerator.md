# DocumentationGenerator Output
**Agent**: DocumentationGenerator
**Execution Order**: 8
**Timestamp**: 2025-07-06 16:16:55

---

## Complete Documentation Package

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

---
*Saved by after_agent_callback on 2025-07-06 16:16:55*
