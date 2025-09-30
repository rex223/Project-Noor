# 🚀 **BONDHU AI - COMPLETE API KEYS & DATABASE SETUP GUIDE**

## 📋 **Required API Keys - Priority Order**

### **🔴 CRITICAL (Required for basic functionality):**

1. **Google Gemini API Key** (Primary LLM)
   - Get from: https://makersuite.google.com/app/apikey
   - Required for: Personality analysis, agent reasoning
   - Free tier: 60 requests per minute
   - Variable: `GEMINI_API_KEY`

2. **Supabase Keys** (Database & Auth)
   - Get from: Your Supabase project dashboard
   - Required for: User data, personality storage, recommendations
   - Variables: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

### **🟡 HIGH PRIORITY (Entertainment features):**

3. **Spotify API Keys** (Music recommendations)
   - Get from: https://developer.spotify.com/dashboard
   - Required for: Music recommendation agent
   - Variables: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`

4. **YouTube Data API Key** (Video recommendations)  
   - Get from: https://console.developers.google.com/
   - Required for: Video recommendation agent
   - Free tier: 10,000 units/day
   - Variable: `YOUTUBE_API_KEY`

### **🟢 OPTIONAL (Enhanced features):**

5. **Steam Web API Key** (Gaming recommendations)
   - Get from: https://steamcommunity.com/dev/apikey
   - Required for: Gaming recommendation agent
   - Variable: `STEAM_API_KEY`

6. **OpenAI API Key** (Backup LLM)
   - Get from: https://platform.openai.com/api-keys
   - Optional: Fallback for Gemini
   - Variable: `OPENAI_API_KEY`

7. **Anthropic API Key** (Backup LLM)
   - Get from: https://console.anthropic.com/
   - Optional: Additional LLM option
   - Variable: `ANTHROPIC_API_KEY`

---

## 🗄️ **Complete Database Schema Setup**

### **Step 1: Run your existing base schema**
```sql
-- Run your optimized_database_schema.sql first
-- This creates all the core tables (profiles, personality_traits, etc.)
```

### **Step 2: Add entertainment system tables**
```sql
-- Run the new entertainment_database_schema.sql
-- This adds tables for recommendations, interactions, and analytics
```

### **Step 3: Verify all tables exist**
After running both schemas, you should have these tables:

**Core Tables:**
- ✅ `profiles` - User profiles with personality data
- ✅ `onboarding_answers` - Personality questionnaire responses  
- ✅ `personality_traits` - Big Five personality scores
- ✅ `chat_messages` - AI conversation history
- ✅ `recommendations` - General content recommendations
- ✅ `activity_history` - User activity tracking

**Entertainment Tables:**
- ✅ `entertainment_recommendations` - AI-generated entertainment suggestions
- ✅ `entertainment_interactions` - User engagement tracking
- ✅ `entertainment_sessions` - Entertainment session management
- ✅ `entertainment_preferences` - Learned user preferences
- ✅ `entertainment_analytics` - Advanced analytics and insights

---

## ⚙️ **Environment Setup Instructions**

### **Backend Setup (bondhu-ai/):**

1. **Copy environment file:**
   ```bash
   cd bondhu-ai
   cp .env.example .env
   ```

2. **Fill in your actual API keys in `.env`:**
   ```bash
   # REQUIRED
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key_here
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
   GEMINI_API_KEY=your_gemini_api_key_here

   # ENTERTAINMENT APIS
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   YOUTUBE_API_KEY=your_youtube_api_key
   STEAM_API_KEY=your_steam_api_key

   # OPTIONAL
   OPENAI_API_KEY=your_openai_key_if_needed
   SECRET_KEY=generate_a_long_random_string_here
   ```

### **Frontend Setup (bondhu-landing/):**

1. **Copy environment file:**
   ```bash
   cd bondhu-landing  
   cp env.local.example .env.local
   ```

2. **Fill in your Supabase details:**
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

---

## 🔗 **API Key Setup Instructions**

### **1. Google Gemini API:**
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key to `GEMINI_API_KEY`

### **2. Supabase Setup:**
1. Visit https://supabase.com/dashboard
2. Create new project or use existing
3. Go to Settings → API
4. Copy "Project URL" → `SUPABASE_URL`
5. Copy "anon public" key → `SUPABASE_KEY`
6. Copy "service_role" key → `SUPABASE_SERVICE_ROLE_KEY`

### **3. Spotify API:**
1. Visit https://developer.spotify.com/dashboard
2. Create new app
3. Set redirect URI: `http://localhost:8000/api/v1/auth/spotify/callback`
4. Copy Client ID and Secret

### **4. YouTube Data API:**
1. Visit https://console.developers.google.com/
2. Create project or select existing
3. Enable "YouTube Data API v3"
4. Create credentials → API Key
5. Copy the API key

### **5. Steam Web API:**
1. Visit https://steamcommunity.com/dev/apikey
2. Enter domain: `localhost`
3. Copy the generated key

---

## 🧪 **Testing Your Setup**

### **1. Test Backend:**
```bash
cd bondhu-ai
python -m pip install -r requirements.txt
python main.py
```
- Should start on http://localhost:8000
- Visit http://localhost:8000/docs for API documentation

### **2. Test Frontend:**
```bash
cd bondhu-landing
npm install
npm run dev
```
- Should start on http://localhost:3000
- Test signup/login functionality

### **3. Test Entertainment System:**
1. Complete personality onboarding
2. Visit entertainment page
3. Verify recommendations load
4. Test interaction tracking

---

## 🎯 **Feature Availability by API Keys**

| Feature | Required Keys | Status |
|---------|---------------|--------|
| **User Authentication** | Supabase | ✅ Core |
| **Personality Analysis** | Gemini + Supabase | ✅ Core |  
| **Music Recommendations** | Spotify + Gemini | 🎵 Entertainment |
| **Video Recommendations** | YouTube + Gemini | 📺 Entertainment |
| **Game Recommendations** | Steam + Gemini | 🎮 Entertainment |
| **Chat System** | Gemini + Supabase | 💬 Core |
| **Progress Tracking** | Supabase | 📊 Core |

---

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"Gemini API key not found"**
   - Ensure `GEMINI_API_KEY` is set in backend `.env`
   - Verify API key is valid and not expired

2. **"Supabase connection error"**
   - Check URL format: `https://your-project.supabase.co`
   - Verify both anon and service role keys

3. **"Entertainment recommendations not loading"**
   - Ensure entertainment database schema is applied
   - Check Spotify/YouTube API keys are valid

4. **"Frontend can't connect to backend"**
   - Verify backend is running on port 8000
   - Check `NEXT_PUBLIC_API_BASE_URL` in frontend

### **Test Commands:**
```bash
# Test backend API
curl http://localhost:8000/health

# Test database connection
cd bondhu-ai && python -c "from core.database.supabase_client import get_supabase_client; print('DB Connected!')"

# Test Gemini API
cd bondhu-ai && python -c "from core.config.settings import config; print(f'Gemini configured: {bool(config.gemini.api_key)}')"
```

---

## 🎉 **Success Indicators**

When everything is working correctly:

✅ Backend starts without errors on port 8000
✅ Frontend starts without errors on port 3000  
✅ User can sign up and complete onboarding
✅ Personality analysis completes successfully
✅ Entertainment recommendations appear in dashboard
✅ User interactions are tracked in database
✅ Progress tracking shows real-time updates

**Your Bondhu AI system is now fully operational! 🚀**