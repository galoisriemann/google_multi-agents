# Flexible Agent Workflow System

A production-ready, multi-agent workflow system for advanced code generation, research, and search tasks. This project leverages Google's Gemini models and provides a flexible, configurable, and extensible architecture for building sophisticated AI-powered applications.

## Features

### Multi-Agent Architecture
- **Specialized Agents**: Includes distinct agents for coding, research, and search, each with its own configuration and workflow.
- **Flexible Workflows**: Supports sequential and parallel agent execution, allowing for complex task decomposition and processing.
- **Configurable Agents**: Each agent is configured via YAML files, allowing for easy customization of models, prompts, and behavior.

### Backend
- **Python-based**: Built with Python 3.12 and Poetry for dependency management.
- **Google Gemini Integration**: Natively supports Google's Gemini models, including the latest versions.
- **RAG and Search**: The research and search agents include capabilities for Retrieval-Augmented Generation (RAG) and web search.
- **Async Support**: Asynchronous processing for improved performance.
- **Type Safe**: Full type annotations with mypy compatibility.

### Frontend
- **React and Vite**: A modern, fast, and responsive user interface built with React and Vite.
- **TypeScript**: Type-safe code for improved reliability and maintainability.
- **Tailwind CSS and Shadcn UI**: A beautiful and consistent design system based on Tailwind CSS and Shadcn UI.
- **Component-Based**: A modular and reusable component architecture.

## Project Structure

```
workflow_google/
├── backend/
│   ├── coding_agent.py
│   ├── flexible_agent.py
│   ├── rag_agent.py
│   ├── search_agent.py
│   ├── config/
│   │   ├── coding/
│   │   ├── flexible_agent/
│   │   ├── research/
│   │   └── search/
│   ├── core/
│   ├── data_model/
│   ├── llm_providers/
│   ├── prompts/
│   └── tools/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── pyproject.toml
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry
- Node.js and npm (or bun)
- Google API Key

### Installation

1.  **Clone the repository**

    ```bash
    git clone <repository-url>
    cd workflow_google
    ```

2.  **Install backend dependencies**

    ```bash
    poetry install
    ```

3.  **Install frontend dependencies**

    ```bash
    cd frontend
    npm install
    ```

4.  **Configure Google API Key**

    -   Set the `GOOGLE_API_KEY` environment variable.
    -   Alternatively, you can add your API key to the `gemini_config_*.yml` files in the `backend/config` subdirectories.

### Usage

#### Backend

-   **Run an agent**:

    ```bash
    poetry run python backend/<agent_name>.py
    ```

    Replace `<agent_name>` with `coding_agent`, `flexible_agent`, `rag_agent`, or `search_agent`.

#### Frontend

-   **Start the development server**:

    ```bash
    cd frontend
    npm run dev
    ```

## Configuration

Each agent has its own configuration files located in the `backend/config` subdirectories. These files allow you to customize the agent's behavior, including the model, prompts, and workflow steps.

-   **`workflow_*.yml`**: Defines the agent's workflow, including the sequence of steps and the tools to be used.
-   **`gemini_config_*.yml`**: Configures the Gemini model, including the API key, model name, and other parameters.

## Dependencies

### Backend

-   `google-ai-generativelanguage`
-   `google-adk`
-   `pyyaml`
-   `pydantic`
-   `python-dotenv`
-   `httpx`

### Frontend

-   `react`
-   `vite`
-   `typescript`
-   `tailwindcss`
-   `@radix-ui/react-*`
-   `shadcn-ui`
-   `react-router-dom`

## Development

### Backend

-   **Linting and formatting**: `poetry run ruff check .` and `poetry run ruff format .`
-   **Type checking**: `poetry run mypy backend/`

### Frontend

-   **Linting**: `npm run lint`

## License

MIT License
