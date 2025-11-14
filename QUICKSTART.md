# Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- **OpenAI API key (REQUIRED)** - Get one from https://platform.openai.com/api-keys

## Setup Steps

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
# On Windows:
copy .env.example .env
# On macOS/Linux:
cp .env.example .env

# Edit .env and add your configuration:
# - OPENAI_API_KEY=your_key_here (REQUIRED - get from https://platform.openai.com/api-keys)
# - OPENAI_MODEL=gpt-4-turbo-preview (optional, defaults to gpt-4-turbo-preview for larger context)
# - JWT_SECRET_KEY=your-secret-key (optional, but recommended for production)
# - GITHUB_TOKEN=your_token (optional, for GitHub integration)
# - GITHUB_USERNAME=your_username (optional)
# - CORS_ORIGINS=http://localhost:3000 (optional, defaults to http://localhost:3000)

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Backend
cd backend
# Create virtual environment
python -m venv venv
# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
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

# Create .env.local file from example (optional)
# On Windows:
copy .env.local.example .env.local
# On macOS/Linux:
cp .env.local.example .env.local

# Edit .env.local if needed (defaults to http://localhost:8000):
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the development server
npm run dev

# Run the Frontend server
cd frontend
npm install
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Testing the Application

1. Open `http://localhost:3000` in your browser
2. **Register/Login**: Create an account or log in (authentication is required)
3. Enter a prompt like: "Create a todo list app with add, edit, and delete functionality"
4. Click "Generate App"
5. Watch the status page for real-time progress updates (via WebSocket)
6. Once complete, download the ZIP or view on GitHub
7. View build history at `/history` page (shows only your builds)

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

✅ **Multi-Agent System**: Spec-driven architecture with Requirements, UI, Code, and Reviewer agents
✅ **AppSpec Schema**: Structured, language-agnostic application specifications
✅ **Iterative Refinement**: Automatic code review and improvement loop (up to 3 iterations)
✅ **Persistent Storage**: SQLite database for job storage per user
✅ **Real-Time Updates**: WebSocket support for live status updates
✅ **Authentication**: User sign-up/login with JWT tokens
✅ **AI Integration**: Full OpenAI integration in all agents (REQUIRED)
✅ **Error Handling**: Comprehensive error handling with clear, actionable messages
✅ **Build History**: View and filter your previous builds with search
✅ **Toast Notifications**: User-friendly notifications for status changes
✅ **Context-Aware**: Automatically adjusts token limits based on model (gpt-4-turbo-preview recommended)

## Next Steps

- [ ] Complete GitHub API integration (currently stubbed)
- [ ] Add deployment integration (Vercel, Netlify, etc.)
- [ ] Implement Docker-based sandboxing for code execution
- [x] Authentication/authorization (✅ Implemented)

## Troubleshooting

### Backend won't start
- Make sure Python 3.10+ is installed
- Verify virtual environment is activated
  - Windows PowerShell: `.\venv\Scripts\Activate.ps1`
  - Windows CMD: `venv\Scripts\activate.bat`
  - macOS/Linux: `source venv/bin/activate`
- Check that all dependencies are installed: `pip install -r requirements.txt`
- If you get an execution policy error on Windows, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

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

**IMPORTANT**: The OpenAI API key is now **REQUIRED**. App generation will fail immediately if not configured.

- **Missing API Key**: 
  - Set `OPENAI_API_KEY` in `backend/.env` file
  - Get your key from https://platform.openai.com/api-keys
  - Restart the backend server after adding the key

- **Context Length Exceeded**:
  - Use `gpt-4-turbo-preview` model (default, 128k context) instead of `gpt-4` (8k context)
  - Set `OPENAI_MODEL=gpt-4-turbo-preview` in your `.env` file
  - Simplify your prompt or break it into smaller requests
  - The system automatically adjusts token limits based on model

- **Authentication Errors**:
  - Verify your API key is valid and has credits/quota available
  - Check the backend logs for specific error messages

- **Other API Errors**:
  - Check backend console logs for detailed error messages
  - Verify your OpenAI account has sufficient credits

### Network/Connection errors
- If you see "Server unreachable – is the backend running?", check that:
  - The backend server is running on port 8000
  - The `NEXT_PUBLIC_API_URL` in `frontend/.env.local` matches your backend URL
  - There are no firewall issues blocking the connection

### WebSocket connection issues
- The frontend automatically falls back to polling if WebSocket fails
- Check browser console for WebSocket connection errors
- Ensure the backend is accessible from the frontend
- WebSocket warnings (1005 errors) are usually transient and won't block builds

### Authentication/Login issues
- Make sure the backend database is initialized (happens automatically on first run)
- If you can't log in, try registering a new account
- Check backend logs for authentication errors
- Verify `JWT_SECRET_KEY` is set in `.env` (auto-generated if not set, but should be changed for production)

