# Supabase RLS Policy Fix for chat_messages

## Problem
Chat messages are not being stored because the `chat_messages` table has RLS (Row Level Security) enabled but no policies are configured.

## Solution
You need to add an RLS policy to allow authenticated users to insert their own messages.

## Steps to Fix

### Option 1: Using Supabase Dashboard (Recommended)

1. Go to your Supabase Dashboard
2. Navigate to **Authentication** → **Policies**
3. Find the `chat_messages` table
4. Click **"New Policy"**
5. Choose **"For INSERT operations"**
6. Name it: `"Users can insert their own messages"`
7. Use this policy:

```sql
-- Policy for INSERT
CREATE POLICY "Users can insert their own messages"
ON chat_messages
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Policy for SELECT (to read their own messages)
CREATE POLICY "Users can read their own messages"
ON chat_messages
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);
```

### Option 2: Using SQL Editor

Go to **SQL Editor** in Supabase Dashboard and run:

```sql
-- Enable RLS (already enabled, but just to be sure)
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Allow users to insert their own messages
CREATE POLICY "Users can insert their own messages"
ON chat_messages
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Allow users to read their own messages
CREATE POLICY "Users can read their own messages"
ON chat_messages
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Allow users to update their own messages (optional)
CREATE POLICY "Users can update their own messages"
ON chat_messages
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

### Option 3: Temporary - Disable RLS (NOT RECOMMENDED for production)

**Only use this for testing!** This makes all data publicly accessible:

```sql
ALTER TABLE chat_messages DISABLE ROW LEVEL SECURITY;
```

## After Applying the Fix

1. Restart your backend server
2. Send a test message from the frontend
3. Check the Supabase `chat_messages` table - you should see the message stored
4. Backend logs should show: `"Chat message stored with ID: <uuid>"`

## Verification

After applying the policy, you should see in your backend logs:
- ✅ `"Chat message stored with ID: ..."` (no more warnings)
- ✅ Messages appearing in your Supabase `chat_messages` table
- ✅ No more `"Failed to store chat message"` warnings

## Current Backend Status

✅ **Working:**
- Gemini chat responses
- Personality context loading (with 30-min caching)
- System prompt personalization
- REST API Supabase connection

⚠️ **Needs RLS Policy:**
- Chat message storage (blocked by RLS)
