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

1. **Create a virtual environment** (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Run the development server**:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

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

Get the current status of a generation job.

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

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project uses type hints throughout. Follow PEP 8 style guidelines.

## Environment Variables

- `OPENAI_API_KEY`: Required for OpenAI API calls
- `GITHUB_TOKEN`: Optional, for GitHub integration
- `GITHUB_USERNAME`: Optional, for GitHub integration
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## Next Steps

- [ ] Implement full OpenAI integration in agents
- [ ] Add database for job storage (replace in-memory dict)
- [ ] Implement actual code execution sandbox
- [ ] Complete GitHub API integration
- [ ] Add deployment integration (Vercel, Netlify, etc.)
- [ ] Add comprehensive error handling
- [ ] Implement logging
- [ ] Add authentication/authorization

