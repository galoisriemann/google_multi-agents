# Flexible Agent Workflow API

FastAPI backend for the Flexible Agent Workflow system. This API provides REST endpoints for executing and managing flexible agent workflows through a web interface.

## Features

- **Workflow Execution**: Execute flexible agent workflows with custom requests
- **Real-time Status**: Monitor workflow progress and status in real-time
- **Configuration Management**: Load and view workflow configurations
- **Tool Registry**: Access available tools and their descriptions
- **Background Processing**: Non-blocking workflow execution with status polling
- **Error Handling**: Comprehensive error reporting and recovery
- **CORS Support**: Configured for frontend integration

## API Endpoints

### Core Endpoints

- `GET /` - API information and endpoint listing
- `GET /api/v1/health` - Health check and status
- `GET /api/v1/workflow/config` - Get current workflow configuration
- `GET /api/v1/tools` - List available tools

### Workflow Management

- `POST /api/v1/workflow/execute` - Execute a new workflow
- `GET /api/v1/workflow/status/{workflow_id}` - Get workflow status
- `GET /api/v1/workflow/result/{workflow_id}` - Get workflow result
- `DELETE /api/v1/workflow/{workflow_id}` - Cancel workflow
- `GET /api/v1/workflows` - List all workflows

## Quick Start

### 1. Start the API Server

```bash
# From the backend directory
cd backend/api
python start_server.py
```

The server will start on `http://localhost:8000`

### 2. API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

## Example Usage

### Execute a Workflow

```bash
curl -X POST "http://localhost:8000/api/v1/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Create a comprehensive market research report"
  }'
```

Response:
```json
{
  "id": "workflow-uuid",
  "status": "running",
  "metadata": {
    "start_time": "2024-01-01T12:00:00",
    "user_request": "Create a comprehensive market research report"
  }
}
```

### Check Status

```bash
curl http://localhost:8000/api/v1/workflow/status/workflow-uuid
```

Response:
```json
{
  "id": "workflow-uuid",
  "status": "running",
  "progress": 45.0,
  "current_agent": "RequirementAnalyzer",
  "executed_agents": ["RequirementAnalyzer"],
  "start_time": "2024-01-01T12:00:00"
}
```

### Get Results

```bash
curl http://localhost:8000/api/v1/workflow/result/workflow-uuid
```

## Configuration

The API automatically loads configuration from:
- `backend/config/flexible_agent/workflow_flexible.yml`
- `backend/config/flexible_agent/gemini_config_flexible.yml`
- `backend/prompts/flexible_agent/prompts_flexible.yml`

## Integration with Frontend

The API is designed to work with the React frontend. Key features:

1. **CORS Configuration**: Allows requests from frontend development servers
2. **Real-time Updates**: Status polling for live progress updates
3. **Error Handling**: Structured error responses for UI display
4. **Background Processing**: Non-blocking execution for better UX

## Error Handling

The API provides structured error responses:

```json
{
  "detail": "Error description",
  "status_code": 500
}
```

Common error codes:
- `400`: Bad request (invalid input)
- `404`: Workflow not found
- `500`: Internal server error
- `503`: Service unavailable (workflow manager not initialized)

## Development

### Running in Development Mode

```bash
python start_server.py
```

This starts the server with:
- Auto-reload on code changes
- Debug logging
- CORS enabled for local development

### Testing

```bash
# Test the health endpoint
curl http://localhost:8000/api/v1/health

# Test workflow configuration
curl http://localhost:8000/api/v1/workflow/config
```

## Architecture

The API is built with:
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization
- **Background Tasks**: Async workflow execution
- **In-memory Storage**: Workflow state tracking (Redis/DB recommended for production)

## Production Deployment

For production deployment:

1. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
2. Configure proper CORS origins
3. Use Redis or database for workflow state storage
4. Set up proper logging and monitoring
5. Configure environment-specific settings

Example production startup:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.api.main:app
``` 