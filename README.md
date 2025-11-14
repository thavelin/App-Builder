# AI App Builder

A multi-agent AI system that generates complete applications from natural language prompts.

## Overview

This is a monorepo containing both the backend (FastAPI) and frontend (Next.js) for an AI-powered app builder. The system uses multiple specialized AI agents to design, code, review, and deploy applications.

## Architecture

### Multi-Agent System

- **Project Manager Agent**: Orchestrates the workflow and breaks down user prompts into tasks
- **Code Agent**: Generates application code and supporting files
- **UI Agent**: Creates UI layouts and wireframe suggestions
- **Usability Agent**: Reviews UX and user flow
- **Reviewer Agent**: Scores completeness and approves/rejects results

### Tech Stack

**Backend:**
- Python 3.10+
- FastAPI
- Pydantic
- OpenAI SDK

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React 18

## Project Structure

```
.
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── agents/
│   │   ├── services/
│   │   └── schemas/
│   ├── tests/
│   └── requirements.txt
│
└── frontend/         # Next.js frontend
    ├── app/
    ├── components/
    └── package.json
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- OpenAI API key (required for AI features)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # On macOS/Linux:
   cp .env.example .env
   
   # On Windows:
   copy .env.example .env
   ```
   
   Edit `.env` and add your `OPENAI_API_KEY` (and optionally GitHub credentials).

5. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will run on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables** (optional):
   ```bash
   # On macOS/Linux:
   cp .env.local.example .env.local
   
   # On Windows:
   copy .env.local.example .env.local
   ```
   
   Edit `.env.local` if your backend is running on a different URL (defaults to `http://localhost:8000`).

4. **Run the development server:**
   ```bash
   npm run dev
   ```

   Frontend will run on `http://localhost:3000`

### Access the Application

Open [http://localhost:3000](http://localhost:3000) in your browser to access the AI App Builder.

## Usage

1. Open the frontend at `http://localhost:3000`
2. Enter a prompt describing the app you want to build
3. Click "Generate App"
4. Monitor the build progress on the status page
5. Download the generated app, view it on GitHub, or access the deployment

## API Endpoints

### POST `/api/generate`

Start app generation from a prompt.

**Request:**
```json
{
  "prompt": "Create a todo list app with add, edit, and delete functionality"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### GET `/api/status/{job_id}`

Get the status of a generation job.

**Response:**
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

## Development Status

This is an MVP scaffold with placeholder implementations. Current status:

✅ Project structure and scaffolding
✅ API endpoints with placeholder logic
✅ Multi-agent system architecture
✅ Frontend UI with status tracking
⏳ Full OpenAI integration (TODO)
⏳ Code execution sandbox (TODO)
⏳ GitHub API integration (TODO)
⏳ Deployment integration (TODO)

## Contributing

1. Follow the coding style preferences:
   - Clean, well-commented code
   - Type hints everywhere (Python)
   - TypeScript for frontend
   - Keep files focused and modular
   - Use `.env` for all secrets

## License

MIT

