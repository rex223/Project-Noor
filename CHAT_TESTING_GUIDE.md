# 🧪 Chat Integration Testing Guide

## ✅ What We Just Built

### Backend (`bondhu-ai/`)
- ✅ Chat schema in Supabase
- ✅ Gemini chat service with personality context
- ✅ Chat API endpoints (`/api/v1/chat/send`)
- ✅ Automatic personality loading per user

### Frontend (`bondhu-landing/`)
- ✅ Chat API client (`src/lib/api/chat.ts`)
- ✅ Updated EnhancedChat component
- ✅ Real-time chat with backend
- ✅ Personality context indicators
- ✅ Error handling

---

## 🚀 Testing Steps

### Step 1: Run Database Migration

1. **Open Supabase SQL Editor**
   - Go to your Supabase dashboard
   - Navigate to SQL Editor

2. **Copy and run this SQL:**
   ```sql
   -- Copy contents from: bondhu-ai/database/chat-schema.sql
   ```

3. **Verify tables created:**
   - Check that `chat_history` table exists
   - Verify RLS policies are active

---

### Step 2: Start Backend Server

```bash
cd bondhu-ai

# Make sure venv is activated
# (venv) should show in your terminal

# Start the server
python main.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000
```

**Verify chat endpoint:**
Open browser to: http://localhost:8000/docs
- Look for `/api/v1/chat/send` endpoint
- Look for `/api/v1/chat/health` endpoint

---

### Step 3: Configure Frontend

1. **Create `.env.local` file in `bondhu-landing/`:**
   ```bash
   cd bondhu-landing
   cp env.local.example .env.local
   ```

2. **Edit `.env.local` with your values:**
   ```env
   # Supabase Configuration
   NEXT_PUBLIC_SUPABASE_URL=https://eilvtjkqmvmhkfzocrzs.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   # Bondhu AI Backend API
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # Optional: For development
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

---

### Step 4: Start Frontend

```bash
cd bondhu-landing

# Install dependencies if needed
npm install

# Start development server
npm run dev
```

**Expected output:**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Ready in X.Xs
```

---

### Step 5: Test Complete Flow

1. **Open browser to:** http://localhost:3000

2. **Sign in with your test account**
   - Use existing account or create new one

3. **Go to Dashboard** (or wherever EnhancedChat is)

4. **Test Chat:**
   
   **Test 1: Basic Message**
   - Type: "Hi Bondhu, how are you?"
   - Press Send
   - ✅ Should see your message
   - ✅ Should see typing indicator
   - ✅ Should receive response from Gemini

   **Test 2: With Personality Context**
   - If you completed personality assessment:
   - ✅ Should see "Personality-aware mode active" badge
   - ✅ Response should be personalized

   **Test 3: Without Personality Context**
   - If no assessment completed:
   - ✅ Should see warning: "Complete personality assessment..."
   - ✅ Response should still work (default context)

   **Test 4: Error Handling**
   - Stop backend server
   - Try sending message
   - ✅ Should see error message
   - ✅ Should get friendly error response

---

## 🔍 Debugging Checklist

### Backend Issues

**Problem: Server won't start**
```bash
# Check if port 8000 is already in use
netstat -ano | findstr :8000

# Kill process if needed (Windows)
taskkill /PID <process_id> /F

# Try starting again
python main.py
```

**Problem: Import errors**
```bash
# Make sure venv is activated
# (venv) should show in terminal

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: "Module 'core.chat' not found"**
```bash
# Check file exists
ls core/chat/gemini_service.py
ls core/chat/__init__.py

# Restart server
```

### Frontend Issues

**Problem: "Cannot connect to backend"**
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Verify backend is running on http://localhost:8000
- Check browser console for CORS errors

**Problem: "User not authenticated"**
- Make sure user is signed in
- Check Supabase auth is working
- Open browser dev tools → Application → Cookies
- Look for Supabase session cookie

**Problem: Chat API errors in console**
- Open browser dev tools → Network tab
- Look for failed requests to `/api/v1/chat/send`
- Check request/response details

---

## 📊 Success Criteria

### ✅ Backend Healthy:
- [ ] Server starts without errors
- [ ] `/docs` page loads at http://localhost:8000/docs
- [ ] Chat endpoints visible in Swagger UI
- [ ] `/api/v1/chat/health` returns `{"status": "healthy"}`

### ✅ Frontend Connected:
- [ ] App loads without errors
- [ ] User can sign in
- [ ] Chat interface appears
- [ ] Messages can be typed

### ✅ Chat Working:
- [ ] User message appears immediately
- [ ] Typing indicator shows
- [ ] AI response appears
- [ ] Responses are conversational and relevant

### ✅ Personality Integration:
- [ ] Users with personality profiles see "Personality-aware mode"
- [ ] Responses feel personalized
- [ ] Users without profiles see helpful warning
- [ ] Chat still works without personality data

---

## 🎯 Manual Test Conversation

Try this conversation to test personality awareness:

**User:** "Hi Bondhu, I've been feeling stressed lately."

**Expected (with personality):** 
Response should acknowledge their specific personality traits.
Example: "Given your high conscientiousness, I understand stress about responsibilities can weigh heavily..."

**Expected (without personality):**
Generic but supportive response.
Example: "I hear you. Stress can be challenging..."

---

## 📝 Test Results Template

```
Date: ___________
Tester: ___________

Backend Status:
[ ] Server started successfully
[ ] Chat endpoints accessible
[ ] Health check passes

Frontend Status:
[ ] App loads correctly
[ ] Authentication working
[ ] Chat UI renders

Chat Functionality:
[ ] Messages send successfully
[ ] Responses received
[ ] Typing indicator works
[ ] Error handling works

Personality Integration:
[ ] Context indicator shows (if applicable)
[ ] Responses feel personalized
[ ] Warning shows (if no profile)

Issues Found:
1. ___________________________
2. ___________________________
3. ___________________________

Overall: ✅ PASS / ❌ FAIL
```

---

## 🚨 Common Issues & Solutions

### Issue: "Gemini API Error"
**Solution:** Check `GEMINI_API_KEY` in `bondhu-ai/.env`

### Issue: "Database connection failed"
**Solution:** Verify `SUPABASE_URL` and `SUPABASE_KEY` in `bondhu-ai/.env`

### Issue: "CORS error in browser"
**Solution:** Backend CORS already configured for `localhost:3000`, but check `main.py`:
```python
allow_origins=["http://localhost:3000", ...]
```

### Issue: "Chat loads forever"
**Solution:** 
1. Check backend logs for errors
2. Check Network tab for failed API calls
3. Verify backend is actually running

---

## 📞 Need Help?

1. **Check backend logs:** Terminal where `python main.py` is running
2. **Check frontend logs:** Browser dev tools console
3. **Check network requests:** Browser dev tools → Network tab
4. **Test backend directly:** Use Swagger UI at http://localhost:8000/docs

---

**Ready to test? Start with Step 1! 🚀**
