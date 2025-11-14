# AI App Builder - Backend

FastAPI-based backend for the AI-powered multi-agent app builder application.

## Architecture

The backend uses a **spec-driven, multi-agent system** to generate applications from natural language prompts:

### Multi-Agent Workflow

1. **Requirements Agent**: Extracts structured `AppSpec` from natural language prompts
   - Handles complexity assessment and scope adjustment
   - Creates a single source of truth for what the app should be

2. **UI Agent**: Generates UX plan from `AppSpec`
   - Creates concrete layouts, component lists, and navigation flow
   - Provides actionable guidance for implementation

3. **Code Agent**: Generates complete, runnable code
   - Uses `AppSpec` and UX plan as inputs
   - Implements all core features (no TODOs for main flows)
   - Supports iterative refinement with repair briefs

4. **Reviewer Agent**: Evaluates code against `AppSpec`
   - Structured evaluation with multiple score dimensions
   - Identifies red flags and missing features
   - Determines if app is ready for users

5. **Project Manager Agent**: Orchestrates the entire workflow
   - Coordinates all agents using `AppSpec` as single source of truth
   - Manages iteration loop with repair briefs
   - Ensures quality through structured review process

### AppSpec Schema

The `AppSpec` is a generic, language-agnostic specification that represents what an app should be:

- **goal**: Short summary of what the user wants
- **user_type**: Who the app is for
- **core_features**: High-level features the app must have
- **entities**: Data entities with fields
- **views**: Views/pages/screens needed
- **stack_preferences**: Technology hints from user
- **non_functional_requirements**: Mobile-first, dark mode, etc.
- **constraints**: No external DB, static site, etc.
- **complexity_level**: tiny/small/medium/ambitious
- **scope_notes**: Notes about scope adjustments

### Iteration Loop

The system uses a robust iteration loop:

1. Extract `AppSpec` from prompt
2. Generate UX plan from `AppSpec`
3. Generate code from `AppSpec` + UX plan
4. Review code against `AppSpec`
5. If not approved, create repair brief and iterate (up to 3 times)
6. Return best available version with review notes

### Telemetry

Generation runs are logged to `logs/generation_runs.jsonl` for analysis:
- Input: prompt, AppSpec summary
- Output: reviewer scores, approval status, iteration count

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── routes/
│   │   ├── generate.py      # Generation API endpoints
│   │   ├── auth.py          # Authentication endpoints
│   │   └── websockets.py    # WebSocket endpoints
│   ├── agents/
│   │   ├── project_manager.py
│   │   ├── requirements_agent.py  # Extracts AppSpec from prompts
│   │   ├── code_agent.py
│   │   ├── ui_agent.py
│   │   ├── usability_agent.py
│   │   └── reviewer_agent.py
│   ├── schemas/
│   │   ├── app_spec.py      # AppSpec schema definition
│   │   ├── request.py       # Pydantic request schemas
│   │   └── response.py      # Pydantic response schemas
│   ├── auth.py              # Authentication utilities (JWT, password hashing)
│   ├── services/
│   │   ├── orchestrator.py  # Multi-agent workflow controller
│   │   ├── execution.py     # Sandbox/runner integration
│   │   ├── github.py        # GitHub API integration
│   │   └── telemetry.py     # Run logging and analytics
│   ├── models.py            # Database models (Job, User)
│   └── storage.py           # Database operations
├── tests/
├── requirements.txt
└── README.md
```

## Authentication

The API requires authentication for most endpoints. Users must register and login to:
- Create new builds
- View their build history
- Access job status

### Authentication Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user information

### JWT Tokens

After login, clients receive a JWT token that must be included in the `Authorization` header:
```
Authorization: Bearer <token>
```

### Environment Variables

Add to your `.env` file:
```env
JWT_SECRET_KEY=your-secret-key-change-in-production-use-random-string
```

## WebSocket Endpoints

Real-time updates are available via WebSocket:

- `/api/ws/status/{job_id}` - Real-time status updates for a specific job
- `/api/ws/jobs` - Real-time job list updates (new jobs, status changes)

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

## Entry Point Detection

The execution service uses recursive entry point detection to find runnable files in generated projects.

### Entry Point Candidates

The system searches for the following entry point files (in order of priority):
- `app.py` - Python application entry point
- `main.py` - Python main entry point
- `index.js` - Node.js/JavaScript entry point

### Detection Process

1. **Recursive Search**: The system uses `Path.rglob()` to recursively search the entire project directory tree for entry point files.
2. **First Match**: The first matching file found is used as the entry point.
3. **Execution**: The execution method is determined by the file extension:
   - `.py` files are executed using Python
   - `.js` files are executed using Node.js (with npm install if package.json exists)

### Requirements for Generated Projects

**All generated projects must include at least one entry point file at the root level** (app.py, main.py, or index.js). This requirement is:
- Enforced during validation before packaging
- Communicated to the AI code generator in prompts
- Checked recursively to support nested project structures

### Example Project Structure

A valid project might look like:
```
project/
├── main.py          # Root entry point (required)
├── app.py           # Application code
├── backend/
│   └── app.py       # Alternative entry point (will be found recursively)
├── requirements.txt
└── README.md
```

The system will find and use `main.py` as the entry point, but can also detect `backend/app.py` if no root entry point exists.

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
✅ Automatic timeout for stuck jobs (15 minutes)
✅ Comprehensive error logging with stack traces

## Troubleshooting

### Backend Not Starting

1. **Check that uvicorn is running on the correct port:**
   ```bash
   # Default port is 8000
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   If port 8000 is in use, change it in the command and update `CORS_ORIGINS` in `.env` accordingly.

2. **Verify environment variables are set:**
   - Check that `.env` file exists in the `backend/` directory
   - Ensure `OPENAI_API_KEY` is set (if you want AI features)
   - Missing `OPENAI_API_KEY` will trigger fallback behavior but should not block progress
   - Verify `CORS_ORIGINS` matches your frontend URL

3. **Database issues:**
   - The database (`app_builder.db`) is automatically created on first run
   - If you encounter database errors, try deleting `app_builder.db` and restarting
   - Ensure you have write permissions in the backend directory

### Job Failures

1. **Check console for tracebacks:**
   - All errors are now logged with full stack traces to stdout/stderr
   - Errors are also reflected in the `error` field returned by `/api/status/{job_id}`
   - Look for messages like "Error in [phase] for job [job_id]"

2. **Common failure reasons:**
   - **Timeout**: Jobs stuck in `in_progress` for more than 15 minutes are automatically marked as failed
   - **Validation errors**: Check that generated code has an entry point (app.py, main.py, or index.js)
   - **OpenAI errors**: If OpenAI API key is invalid or quota exceeded, check console logs
   - **Network errors**: Check that all external API calls (OpenAI, GitHub) are reachable

3. **Job status not updating:**
   - Check WebSocket connection status in frontend
   - Verify backend is running and accessible
   - Check browser console for connection errors
   - Frontend automatically falls back to polling if WebSocket fails

### Missing OpenAI API Key

- The app will work without `OPENAI_API_KEY` but with limited functionality
- Code generation will use placeholder responses
- Reviewer will approve by default on first iteration with a warning
- Check console for messages like "OpenAI not configured"

### Debugging Tips

1. **Enable verbose logging:**
   - All errors include full stack traces in console output
   - Check both stdout and stderr for error messages

2. **Test endpoints directly:**
   - Visit `http://localhost:8000/docs` for interactive API documentation
   - Test `/api/status/{job_id}` endpoint directly to see job status

3. **Check job history:**
   - Use `/api/jobs` endpoint to see all jobs
   - Check `created_at` and `updated_at` timestamps to identify stuck jobs

## Next Steps

- [ ] Complete GitHub API integration (currently stubbed)
- [ ] Add deployment integration (Vercel, Netlify, etc.)
- [ ] Implement proper Docker-based sandboxing for code execution
- [ ] Add comprehensive logging
- [ ] Add authentication/authorization
- [ ] Add rate limiting
- [ ] Migrate to PostgreSQL for production

