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
# OPENAI_API_KEY=your_key_here

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

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
4. Watch the status page for progress updates
5. Once complete, download the ZIP or view on GitHub

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
│   │   └── storage.py   # Job storage (in-memory)
│   └── requirements.txt
│
└── frontend/            # Next.js frontend
    ├── app/             # Next.js App Router pages
    ├── components/      # React components
    └── package.json
```

## Next Steps

- [ ] Add your OpenAI API key to backend/.env
- [ ] Implement full OpenAI integration in agents
- [ ] Add database for persistent job storage
- [ ] Implement code execution sandbox
- [ ] Complete GitHub API integration
- [ ] Add deployment integration

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

