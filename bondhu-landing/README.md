# Bondhu Landing - Frontend

The Next.js frontend for the Bondhu AI personality analysis system. This application provides a modern, responsive interface for personality insights and entertainment recommendations.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- Access to the Bondhu AI backend (`bondhu-ai` directory)

### Installation

1. **Install dependencies**:
```bash
npm install
# or
yarn install
```

2. **Environment setup**:
```bash
# Copy environment template
cp env.local.example .env.local

# Edit .env.local with your configuration
```

3. **Required Environment Variables**:
```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Bondhu AI Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Optional: For development
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

4. **Start the development server**:
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`.

## 🔧 Backend Integration

This frontend connects to the Bondhu AI backend (`bondhu-ai` directory) which provides:

- **Multi-agent personality analysis** using LangChain/LangGraph
- **Real-time analysis orchestration** with progress tracking
- **Cross-modal validation** of personality insights
- **Entertainment recommendations** based on personality profiles

### Starting the Backend

Make sure the Bondhu AI backend is running on `http://localhost:8000`:

```bash
cd ../bondhu-ai
python main.py
```

The frontend automatically connects to this endpoint via the `NEXT_PUBLIC_API_BASE_URL` environment variable.

## 📋 Features

### Personality Analysis
- **Big Five trait assessment** with confidence scoring
- **Multi-modal data integration** (music, video, gaming)
- **Progress tracking** for long-running analyses
- **Historical tracking** of personality evolution

### Entertainment Recommendations
- **Personalized suggestions** based on personality insights
- **Interactive mini-games** for additional data collection
- **Adaptive content** that evolves with user preferences

### User Experience
- **Modern UI/UX** with dark/light mode support
- **Responsive design** for all device sizes
- **Real-time updates** during analysis processes
- **Secure authentication** via Supabase

## 🔌 API Integration

The frontend uses a comprehensive API client (`src/lib/api-client.ts`) that provides:

### Personality Analysis
```typescript
import { useBondhuAPI } from '@/hooks/use-bondhu-api'

const { analyzePersonality, isLoading, error } = useBondhuAPI()

// Trigger analysis
await analyzePersonality({
  user_id: 'user123',
  requested_agents: ['music', 'video', 'gaming'],
  include_cross_modal: true
})
```

### Real-time Progress Tracking
```typescript
// Track analysis progress
const { progress, status } = await bondhuAPI.getAnalysisStatus('analysis_id')
```

### Agent Status Monitoring
```typescript
// Check which agents are available
const agents = await bondhuAPI.getAgentStatus()
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI    │    │  API Client     │    │  FastAPI API    │
│   Components    │◄──►│  (TypeScript)   │◄──►│  (Python)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Supabase Auth  │    │  Error Handling │    │  LangGraph      │
│  User Sessions  │    │  Loading States │    │  Orchestrator   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # User dashboard
│   ├── onboarding/        # Personality setup
│   ├── personality-insights/ # Analysis results
│   └── entertainment/     # Recommendations
├── components/            # Reusable UI components
│   ├── auth/             # Authentication forms
│   ├── games/            # Interactive mini-games
│   └── ui/               # Base UI components
├── hooks/                # Custom React hooks
│   └── use-bondhu-api.ts # API integration hook
├── lib/                  # Utility libraries
│   ├── api-client.ts     # Backend HTTP client
│   ├── env-config.ts     # Environment validation
│   └── utils.ts          # Helper functions
└── types/                # TypeScript definitions
```

## 🔐 Environment Configuration

### Development Environment
- `NEXT_PUBLIC_API_BASE_URL`: Points to local backend (`http://localhost:8000`)
- Automatic environment validation with helpful error messages
- Development logging for API communication

### Production Environment
- Update `NEXT_PUBLIC_API_BASE_URL` to production backend URL
- Ensure Supabase production credentials are configured
- Enable production optimizations and error reporting

### Environment Validation
The app automatically validates environment configuration on startup:

```typescript
import { validateEnvironment } from '@/lib/env-config'

// Throws helpful errors for missing required variables
const config = validateEnvironment()
```

## 🧪 Development

### Local Development
```bash
# Start the development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Backend Connection
Ensure the Bondhu AI backend is running before starting the frontend:

1. Start backend: `cd ../bondhu-ai && python main.py`
2. Verify backend health: `curl http://localhost:8000/health`
3. Start frontend: `npm run dev`

### Debugging API Issues
Enable detailed API logging in development:

```typescript
// Check browser console for API communication logs
// Environment configuration is logged automatically
```

## 🚀 Deployment

### Vercel Deployment
1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Update `NEXT_PUBLIC_API_BASE_URL` to production backend
4. Deploy automatically on git push

### Environment Variables for Production
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_production_anon_key
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
```

## 📞 Support

### Common Issues

**"API connection failed"**
- Verify backend is running on correct port
- Check `NEXT_PUBLIC_API_BASE_URL` environment variable
- Ensure no CORS issues between frontend and backend

**"Environment validation failed"**
- Check `.env.local` file exists and has required variables
- Restart development server after environment changes
- Verify Supabase credentials are correct

**"Analysis not starting"**
- Check backend agent status: `/api/v1/agents/status`
- Verify user authentication with Supabase
- Check browser network tab for API errors

### Getting Help
- Check browser console for detailed error messages
- View API documentation at `http://localhost:8000/docs`
- Review backend logs for integration issues

---

*Built with Next.js 15, TypeScript, and Tailwind CSS*