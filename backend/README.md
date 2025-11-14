# AI App Builder - Backend

FastAPI-based backend for the AI-powered multi-agent app builder application.

## Architecture

The backend uses a multi-agent system to generate applications from natural language prompts:

- **Project Manager Agent**: Orchestrates the workflow and breaks down tasks
- **Code Agent**: Generates application code and supporting files
- **UI Agent**: Creates UI layouts and wireframe suggestions
- **Usability Agent**: Reviews UX and user flow
- **Reviewer Agent**: Scores completeness and approves/rejects results

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── routes/
│   │   └── generate.py      # API endpoints
│   ├── agents/
│   │   ├── project_manager.py
│   │   ├── code_agent.py
│   │   ├── ui_agent.py
│   │   ├── usability_agent.py
│   │   └── reviewer_agent.py
│   ├── services/
│   │   ├── orchestrator.py  # Multi-agent workflow controller
│   │   ├── execution.py     # Sandbox/runner integration
│   │   └── github.py        # GitHub API integration
│   └── schemas/
│       ├── request.py       # Pydantic request schemas
│       └── response.py      # Pydantic response schemas
├── tests/
├── requirements.txt
└── README.md
```

## Installation

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

**Activate the virtual environment:**

- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

- On Windows:
  ```bash
  venv\Scripts\activate
  ```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the example environment file and fill in your values:

```bash
# On macOS/Linux:
cp .env.example .env

# On Windows:
copy .env.example .env
```

Edit `.env` and add your configuration:

- **OPENAI_API_KEY** (required for AI features): Your OpenAI API key
- **OPENAI_MODEL** (optional, defaults to `gpt-4`): The OpenAI model to use
- **GITHUB_TOKEN** (optional): GitHub personal access token for repository creation
- **GITHUB_USERNAME** (optional): Your GitHub username
- **CORS_ORIGINS** (optional, defaults to `http://localhost:3000`): Comma-separated list of allowed origins

Example `.env` file:
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
GITHUB_TOKEN=ghp_your-token-here
GITHUB_USERNAME=your-username
CORS_ORIGINS=http://localhost:3000
```

### 4. Database Setup

The database (SQLite) will be automatically created on first run. The database file `app_builder.db` will be created in the backend directory.

### 5. Run the Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- API Documentation (Swagger UI): `http://localhost:8000/docs`
- API Documentation (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

### POST `/api/generate`

Trigger app generation from a natural language prompt.

**Request Body**:
```json
{
  "prompt": "Create a todo list app with add, edit, and delete functionality"
}
```

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### GET `/api/status/{job_id}`

Get the current status of a generation job (polling endpoint).

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "step": "coding",
  "download_url": null,
  "github_url": null,
  "deployment_url": null,
  "error": null
}
```

### WebSocket `/api/ws/status/{job_id}`

Real-time status updates via WebSocket. Connects to a specific job and streams status changes.

**Message Format**:
```json
{
  "type": "status_update",
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "in_progress",
    "step": "coding",
    "download_url": null,
    "github_url": null,
    "deployment_url": null,
    "error": null
  }
}
```

### GET `/api/jobs`

List all jobs with pagination.

**Query Parameters**:
- `limit` (optional, default: 50): Maximum number of jobs to return
- `offset` (optional, default: 0): Number of jobs to skip

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "prompt": "Create a todo list app",
    "status": "complete",
    "step": "complete",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:05:00"
  }
]
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project uses type hints throughout. Follow PEP 8 style guidelines.

## Database

The application uses SQLite with SQLModel for persistent job storage. The database is automatically initialized on startup.

**Database File**: `app_builder.db` (created in the backend directory)

**Job Model Fields**:
- `id`: UUID string (primary key)
- `prompt`: User's original prompt
- `status`: Job status (pending, in_progress, complete, failed)
- `step`: Current step in generation process
- `download_url`: URL to download ZIP file
- `github_url`: URL to GitHub repository
- `deployment_url`: URL to deployed application
- `error`: Error message if failed
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Real-Time Updates

The backend supports real-time status updates via WebSocket connections. The frontend automatically connects to the WebSocket endpoint and receives updates as jobs progress. If WebSocket connection fails, the frontend falls back to polling.

## Environment Variables

- `OPENAI_API_KEY`: **Required** for OpenAI API calls (AI agent functionality)
- `OPENAI_MODEL`: Optional, OpenAI model to use (default: `gpt-4`)
- `GITHUB_TOKEN`: Optional, for GitHub integration
- `GITHUB_USERNAME`: Optional, for GitHub integration
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app tests/
```

## Features Implemented

✅ Persistent job storage with SQLite
✅ Real-time WebSocket updates
✅ OpenAI integration in all agents
✅ Code execution with subprocess (basic sandboxing)
✅ Error handling and retry logic
✅ Job history endpoint
✅ Type hints throughout
✅ Unit tests for storage and WebSocket

## Next Steps

- [ ] Complete GitHub API integration (currently stubbed)
- [ ] Add deployment integration (Vercel, Netlify, etc.)
- [ ] Implement proper Docker-based sandboxing for code execution
- [ ] Add comprehensive logging
- [ ] Add authentication/authorization
- [ ] Add rate limiting
- [ ] Migrate to PostgreSQL for production

