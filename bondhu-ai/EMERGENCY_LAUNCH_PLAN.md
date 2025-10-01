# 🚨 EMERGENCY LAUNCH PLAN - October 3rd, 2025

## ⏰ TIME REMAINING: 48 HOURS

---

## 🎯 MVP SCOPE (What We MUST Have)

### ✅ ALREADY WORKING (Don't Touch!)
1. ✅ Personality Assessment (Big Five test)
2. ✅ User authentication
3. ✅ Dashboard UI
4. ✅ Multi-agent backend running
5. ✅ Gemini Pro integration
6. ✅ Supabase personality profiles

### 🔥 CRITICAL PATH (Must Complete)

#### TODAY (October 1st) - 8 hours
**Priority: Get chat working with personality context**

- [ ] **Chat Backend (3 hours)**
  - [ ] Create chat_history table in Supabase
  - [ ] Create `/api/v1/chat/send` endpoint
  - [ ] Load personality context before each message
  - [ ] Send to Gemini with context
  - [ ] Return response

- [ ] **Chat Frontend (3 hours)**
  - [ ] Connect EnhancedChat to backend
  - [ ] Show personality loading state
  - [ ] Display chat responses
  - [ ] Basic error handling

- [ ] **Testing (2 hours)**
  - [ ] Test with real personality profiles
  - [ ] Verify personality context is working
  - [ ] Fix critical bugs

#### TOMORROW (October 2nd) - 8 hours
**Priority: Service connections UI + basic data collection**

- [ ] **Entertainment Hub UI (4 hours)**
  - [ ] "Connect Spotify" button with OAuth
  - [ ] "Connect YouTube" button with OAuth
  - [ ] "Connect Steam" form (just API key input)
  - [ ] Show connection status
  - [ ] **DON'T BUILD DATA COLLECTION YET**

- [ ] **OAuth Endpoints (3 hours)**
  - [ ] Spotify OAuth flow (minimal)
  - [ ] YouTube OAuth flow (minimal)
  - [ ] Steam API key storage
  - [ ] Store tokens in entertainment_connections table

- [ ] **Final Testing & Polish (1 hour)**
  - [ ] End-to-end user journey
  - [ ] Fix critical bugs
  - [ ] Basic error messages

#### LAUNCH DAY (October 3rd) - 4 hours
- [ ] **Final checks and deployment**
- [ ] **Monitor for issues**
- [ ] **Quick bug fixes if needed**

---

## ❌ POST-LAUNCH (Do AFTER October 3rd)

### Week 1 After Launch
- [ ] Background data collection (APScheduler)
- [ ] Actual data fetching from APIs
- [ ] Personality evolution engine
- [ ] Data collection status display

### Week 2+ After Launch
- [ ] Chat history persistence
- [ ] Manual data input forms
- [ ] Personality evolution visualization
- [ ] Admin monitoring dashboard

---

## 🎯 LAUNCH FEATURES

### What Users Will Experience:
1. ✅ **Sign up** → Supabase auth
2. ✅ **Take personality test** → Big Five scores stored
3. ✅ **Dashboard** → See their personality profile
4. 🔥 **Chat with Bondhu** → Personality-aware responses (NEW!)
5. 🔥 **Connect services** → OAuth flows (UI only for now) (NEW!)
6. ✅ **View settings** → Existing pages

### What's Fake/Coming Soon:
- **Data collection**: Buttons work, but data isn't collected yet
- **Personality updates**: Profile stays static post-assessment
- **Service integration**: Connected, but not used for analysis yet

### Messaging for Launch:
> "Connect your Spotify, YouTube, and Steam accounts for future personality insights! (Data collection starts next week)"

---

## 📋 DETAILED IMPLEMENTATION PLAN

### 🔥 TASK 1: Chat Backend (3 hours)

#### 1.1 Create Chat Schema (30 min)
```sql
-- bondhu-ai/database/chat-schema.sql
CREATE TABLE chat_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  response TEXT NOT NULL,
  personality_context JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policies
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat" ON chat_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat" ON chat_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Index for performance
CREATE INDEX idx_chat_history_user_created ON chat_history(user_id, created_at DESC);
```

#### 1.2 Create Chat Service (1 hour)
```python
# core/chat/gemini_service.py
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import get_config
from core.database.personality_service import get_personality_service

class GeminiChatService:
    def __init__(self):
        config = get_config()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=config.gemini.api_key
        )
        self.personality_service = get_personality_service()
    
    async def send_message(self, user_id: str, message: str) -> dict:
        # Get personality context
        personality_data = await self.personality_service.get_user_personality_context(user_id)
        
        if personality_data:
            llm_context = personality_data.get('llm_context', {})
            system_prompt = llm_context.get('system_prompt', 'You are Bondhu, an empathetic AI companion.')
        else:
            system_prompt = 'You are Bondhu, an empathetic AI companion focused on mental health support.'
        
        # Create messages
        messages = [
            ("system", system_prompt),
            ("human", message)
        ]
        
        # Get response
        response = await self.llm.ainvoke(messages)
        
        return {
            "response": response.content,
            "personality_context": llm_context if personality_data else None
        }
```

#### 1.3 Create Chat Endpoint (1 hour)
```python
# api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.chat.gemini_service import GeminiChatService
from core.database.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    has_personality_context: bool

@router.post("/send", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    try:
        chat_service = GeminiChatService()
        result = await chat_service.send_message(request.user_id, request.message)
        
        # Store in database (optional for MVP)
        # await store_chat_history(request.user_id, request.message, result['response'])
        
        return ChatResponse(
            response=result['response'],
            has_personality_context=result['personality_context'] is not None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 1.4 Register Router (10 min)
```python
# main.py - Add import and include router
from api.routes.chat import router as chat_router

app.include_router(chat_router)
```

---

### 🔥 TASK 2: Chat Frontend (3 hours)

#### 2.1 Create Chat API Client (30 min)
```typescript
// bondhu-landing/src/lib/api/chat.ts
import { apiClient } from './client';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatResponse {
  response: string;
  has_personality_context: boolean;
}

export const chatApi = {
  sendMessage: async (userId: string, message: string): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/api/v1/chat/send', {
      message,
      user_id: userId
    });
    return response.data;
  }
};
```

#### 2.2 Update EnhancedChat Component (2 hours)
```typescript
// bondhu-landing/src/components/ui/enhanced-chat.tsx
// Add real API integration

const [messages, setMessages] = useState<ChatMessage[]>([]);
const [isLoading, setIsLoading] = useState(false);
const { user } = useAuth(); // Get from auth context

const handleSendMessage = async (message: string) => {
  if (!user?.id) {
    toast.error("Please sign in to chat");
    return;
  }

  // Add user message
  const userMessage: ChatMessage = {
    role: 'user',
    content: message,
    timestamp: new Date()
  };
  setMessages(prev => [...prev, userMessage]);
  setIsLoading(true);

  try {
    const response = await chatApi.sendMessage(user.id, message);
    
    // Add assistant response
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: response.response,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, assistantMessage]);
    
    if (!response.has_personality_context) {
      toast.warning("Complete personality assessment for better responses!");
    }
  } catch (error) {
    toast.error("Failed to send message");
  } finally {
    setIsLoading(false);
  }
};
```

---

### 🔥 TASK 3: Entertainment Connections (4 hours)

#### 3.1 Create OAuth Endpoints (2 hours)
```python
# api/routes/auth/spotify.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import os

router = APIRouter(prefix="/api/v1/auth/spotify", tags=["auth"])

@router.get("/connect")
async def spotify_connect(user_id: str):
    """Redirect to Spotify OAuth"""
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    redirect_uri = "http://localhost:8000/api/v1/auth/spotify/callback"
    scope = "user-read-recently-played user-top-read user-library-read"
    
    auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}&state={user_id}"
    
    return {"spotify_auth_url": auth_url}

@router.get("/callback")
async def spotify_callback(code: str, state: str):
    """Handle Spotify OAuth callback"""
    try:
        # Exchange code for token (simplified for MVP)
        # Store token in database
        # For now, just redirect to success page
        return RedirectResponse(url=f"http://localhost:3000/entertainment?connected=spotify")
    except Exception as e:
        return RedirectResponse(url=f"http://localhost:3000/entertainment?error=spotify")
```

Similar for YouTube and Steam (simplified versions)

#### 3.2 Create Connection UI (2 hours)
```typescript
// bondhu-landing/src/components/entertainment/ServiceConnections.tsx

export function ServiceConnections() {
  const { user } = useAuth();
  const [connecting, setConnecting] = useState<string | null>(null);

  const connectSpotify = async () => {
    setConnecting('spotify');
    try {
      const response = await fetch(`http://localhost:8000/api/v1/auth/spotify/connect?user_id=${user.id}`);
      const data = await response.json();
      window.location.href = data.spotify_auth_url;
    } catch (error) {
      toast.error("Failed to connect Spotify");
      setConnecting(null);
    }
  };

  return (
    <div className="space-y-4">
      <Button onClick={connectSpotify} disabled={connecting === 'spotify'}>
        {connecting === 'spotify' ? 'Connecting...' : 'Connect Spotify'}
      </Button>
      {/* Similar for YouTube and Steam */}
    </div>
  );
}
```

---

## 🚀 DEPLOYMENT CHECKLIST (October 3rd)

### Pre-Launch
- [ ] Run all migrations on production Supabase
- [ ] Update environment variables
- [ ] Test personality assessment flow
- [ ] Test chat with personality context
- [ ] Test service OAuth flows

### Launch
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway/Render
- [ ] Update CORS settings
- [ ] Monitor error logs
- [ ] Be ready for hot fixes

### Post-Launch Message
```
🎉 Bondhu AI is LIVE!

Current Features:
✅ Personality Assessment (Big Five)
✅ AI Chat with personality-aware responses
✅ Connect Spotify/YouTube/Steam (OAuth)

Coming Soon:
🔜 Automated data collection (next week)
🔜 Evolving personality profiles
🔜 Deeper entertainment insights

We're in beta - your feedback shapes Bondhu! 💙
```

---

## ⚠️ KNOWN LIMITATIONS (For Launch)

1. **Service connections don't collect data yet** - OAuth works, but we don't fetch/analyze data
2. **No chat history** - Each session is fresh (can add later)
3. **Static personality** - Profile doesn't evolve until we add data collection
4. **No background jobs** - Manual triggers only (if needed)

---

## 📞 EMERGENCY CONTACTS

If something breaks:
1. Check Supabase logs
2. Check FastAPI logs (uvicorn)
3. Check browser console
4. Check Vercel deployment logs

---

## 💡 SUCCESS METRICS (First Week)

- [ ] 50+ users complete personality assessment
- [ ] 100+ chat messages sent
- [ ] 20+ users connect at least one service
- [ ] <5 critical bugs reported
- [ ] 80%+ positive feedback

---

**LET'S DO THIS! 🚀**

**Next: Start with Task 1 (Chat Backend) RIGHT NOW!**
