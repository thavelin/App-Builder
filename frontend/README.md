# AI App Builder - Frontend

Next.js frontend application for the AI-powered multi-agent app builder.

## Features

- **Clean, Modern UI**: Built with Tailwind CSS and Next.js App Router
- **Real-time Status Updates**: Polls backend for build status
- **Progress Indicators**: Visual step-by-step progress display
- **Build Artifacts**: Download ZIP, view GitHub repo, and access deployment links
- **Mobile-friendly**: Responsive design that works on all devices

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Main page with prompt input
│   ├── status/[id]/page.tsx # Status page for job tracking
│   └── globals.css          # Global styles
├── components/
│   ├── PromptForm.tsx       # Prompt input form
│   ├── LoadingSteps.tsx     # Progress indicator component
│   └── BuildResult.tsx      # Results display component
├── package.json
└── README.md
```

## Installation

### 1. Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 2. Set Up Environment Variables

Copy the example environment file and fill in your values:

```bash
# On macOS/Linux:
cp .env.local.example .env.local

# On Windows:
copy .env.local.example .env.local
```

Edit `.env.local` and set the backend API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note:** If you don't create `.env.local`, the app will default to `http://localhost:8000`.

### 3. Run the Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

**Important:** Make sure the backend server is running on port 8000 before starting the frontend.

## Usage

1. Enter a natural language prompt describing the app you want to build
2. Click "Generate App" to start the generation process
3. You'll be redirected to a status page that shows real-time progress
4. Once complete, download the ZIP file, view the GitHub repository, or access the deployed app

## Development

### Building for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## Styling

This project uses:
- **Tailwind CSS** for utility-first styling
- **Dark mode** support via CSS variables
- **Responsive design** with mobile-first approach

## API Integration

The frontend communicates with the backend API at `http://localhost:8000` by default. Make sure the backend is running before starting the frontend.

### Endpoints Used

- `POST /api/generate` - Start app generation
- `GET /api/status/{job_id}` - Get job status (polled every 2 seconds)
- `WebSocket /api/ws/status/{job_id}` - Real-time status updates

### Error Handling

The frontend provides user-friendly error messages for common issues:

- **Missing Entry Point**: If a generated app is missing a runnable file (app.py, main.py, or index.js), a helpful alert is displayed suggesting the user try again or refine their prompt.
- **Network Errors**: If the backend is unreachable, a clear message is shown asking the user to check if the backend is running.
- **Build Failures**: All build errors are displayed with clear, actionable messages.

## Next Steps

- [ ] Add error handling and retry logic
- [ ] Implement WebSocket for real-time updates (instead of polling)
- [ ] Add authentication
- [ ] Add build history/previous builds page
- [ ] Improve loading states and animations
- [ ] Add toast notifications

