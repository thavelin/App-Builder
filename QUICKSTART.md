# Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- OpenAI API key

## Setup Steps

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the example and add your OpenAI API key
# Windows:
copy .env.example .env
# macOS/Linux:
cp .env.example .env

# Edit .env and add:
# OPENAI_API_KEY=your_key_here (required for AI features)
# GITHUB_TOKEN=your_token (optional, for GitHub integration)
# GITHUB_USERNAME=your_username (optional)
# OPENAI_MODEL=gpt-4 (optional, defaults to gpt-4)

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

**Note**: The SQLite database (`app_builder.db`) will be automatically created on first run.

### 2. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Testing the Application

1. Open `http://localhost:3000` in your browser
2. Enter a prompt like: "Create a todo list app with add, edit, and delete functionality"
3. Click "Generate App"
4. Watch the status page for real-time progress updates (via WebSocket)
5. Once complete, download the ZIP or view on GitHub
6. View build history at `/history` page

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
App-Builder/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── routes/      # API endpoints
│   │   ├── agents/      # AI agent implementations
│   │   ├── services/    # Business logic services
│   │   ├── schemas/     # Pydantic models
│   │   ├── models.py    # Database models (SQLModel)
│   │   └── storage.py   # Async database storage
│   └── requirements.txt
│
└── frontend/            # Next.js frontend
    ├── app/             # Next.js App Router pages
    ├── components/      # React components
    └── package.json
```

## Features

✅ **Persistent Storage**: SQLite database for job storage
✅ **Real-Time Updates**: WebSocket support for live status updates
✅ **AI Integration**: Full OpenAI integration in all agents
✅ **Code Execution**: Basic subprocess-based code execution
✅ **Error Handling**: Retry logic and comprehensive error handling
✅ **Build History**: View all previous builds
✅ **Toast Notifications**: User-friendly notifications for status changes

## Next Steps

- [ ] Complete GitHub API integration (currently stubbed)
- [ ] Add deployment integration (Vercel, Netlify, etc.)
- [ ] Implement Docker-based sandboxing for code execution
- [ ] Add authentication/authorization

## Troubleshooting

### Backend won't start
- Make sure Python 3.10+ is installed
- Verify virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Frontend won't start
- Make sure Node.js 18+ is installed
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Check that port 3000 is not in use

### CORS errors
- Make sure backend is running on port 8000
- Check that CORS middleware in `backend/app/main.py` allows `http://localhost:3000`

### Database errors
- The database is automatically created on first run
- If you need to reset, delete `app_builder.db` and restart the server

### OpenAI API errors
- Verify your `OPENAI_API_KEY` is set correctly in `.env`
- Check that you have API credits/quota available
- The app will fall back to placeholder responses if OpenAI is not configured

### WebSocket connection issues
- The frontend automatically falls back to polling if WebSocket fails
- Check browser console for WebSocket connection errors
- Ensure the backend is accessible from the frontend

