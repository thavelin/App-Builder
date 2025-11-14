# AI App Builder - Frontend

Next.js frontend application for the AI-powered multi-agent app builder.

## Features

- **Clean, Modern UI**: Built with Tailwind CSS and Next.js App Router
- **Real-time Updates**: WebSocket-based live status and history updates
- **Authentication**: User registration, login, and protected routes
- **Robust Error Handling**: Automatic retry with exponential backoff
- **Progress Indicators**: Visual step-by-step progress display
- **Build History**: View, filter, search, and repeat previous builds
- **Build Artifacts**: Download ZIP, view GitHub repo, and access deployment links
- **Toast Notifications**: User-friendly success/error notifications
- **Mobile-friendly**: Responsive design that works on all devices

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout with providers
│   ├── providers.tsx        # Auth and Toast providers
│   ├── page.tsx             # Main page with prompt input (protected)
│   ├── login/page.tsx       # Login page
│   ├── register/page.tsx    # Registration page
│   ├── status/[id]/page.tsx # Status page for job tracking (protected)
│   ├── history/page.tsx     # Build history page (protected)
│   └── globals.css          # Global styles
├── components/
│   ├── PromptForm.tsx       # Prompt input form
│   ├── LoadingSteps.tsx     # Progress indicator component
│   ├── BuildResult.tsx      # Results display component
│   ├── Loading.tsx          # Centralized loading components
│   ├── AuthGuard.tsx        # Route protection component
│   ├── Navbar.tsx           # Navigation bar
│   └── Toast.tsx            # Toast notification component
├── hooks/
│   ├── useAuth.ts           # Authentication hook and context
│   ├── useToast.ts          # Toast notification hook
│   └── useWebSocket.ts      # WebSocket connection hook
├── utils/
│   └── fetchWithRetry.ts    # Robust fetch with retry logic
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

1. **Register/Login**: Create an account or sign in
2. **Enter a prompt**: Describe the app you want to build
3. **Configure settings**: Set review threshold and optionally attach files
4. **Generate**: Click "Generate App" to start the process
5. **Monitor progress**: Watch real-time updates on the status page
6. **View history**: Access your build history with filtering and search
7. **Repeat builds**: Use the "Repeat" button to rebuild with the same prompt

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

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/generate` - Start app generation (requires auth)
- `GET /api/status/{job_id}` - Get job status (requires auth)
- `GET /api/jobs` - List user's jobs with filtering (requires auth)
- `WebSocket /api/ws/status/{job_id}` - Real-time status updates
- `WebSocket /api/ws/jobs` - Real-time job list updates

### Error Handling

The frontend uses `fetchWithRetry` utility for all API calls, providing:

- **Automatic retries**: Exponential backoff on network/HTTP errors
- **User-friendly messages**: Clear error descriptions
- **Toast notifications**: Success/error feedback for all actions
- **Graceful degradation**: Polling fallback when WebSocket fails

### Authentication

All protected routes require authentication. Unauthenticated users are redirected to `/login`.

- JWT tokens are stored in `localStorage`
- Tokens are automatically included in API requests
- Auth state is managed via `useAuth` hook

### WebSocket Updates

- **Status page**: Real-time updates via `/api/ws/status/{job_id}`
- **History page**: Live updates via `/api/ws/jobs` when jobs are created/updated
- **Fallback**: Automatic polling if WebSocket connection fails

