# Bondhu Landing Page Setup Guide

## Prerequisites
- Node.js 18+ and npm
- A Supabase account
- Git

## Quick Start

### 1. Clone and Install
```bash
git clone <repository-url>
cd Project-Noor/bondhu-landing
npm install
```

### 2. Supabase Setup
1. Create a new project at [supabase.com](https://supabase.com)
2. Go to Settings → API to get your keys
3. Copy `env.local.example` to `.env.local`
4. Fill in your Supabase credentials:
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Database Setup
1. Go to Supabase Dashboard → SQL Editor
2. Run the complete schema from `database/schema.sql`
3. Or copy-paste this SQL:

```sql
-- Create user profiles table with all required columns
CREATE TABLE IF NOT EXISTS profiles (
  id uuid references auth.users on delete cascade not null primary key,
  updated_at timestamp with time zone DEFAULT now(),
  full_name text,
  avatar_url text,
  onboarding_completed boolean default false,
  personality_traits jsonb default '{}'::jsonb,
  personality_data jsonb default '{}'::jsonb,
  created_at timestamp with time zone default now()
);

-- Add missing columns if they don't exist (for existing tables)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'onboarding_completed') THEN
        ALTER TABLE profiles ADD COLUMN onboarding_completed boolean default false;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'personality_data') THEN
        ALTER TABLE profiles ADD COLUMN personality_data jsonb default '{}'::jsonb;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'onboarding_complete') THEN
        ALTER TABLE profiles RENAME COLUMN onboarding_complete TO onboarding_completed;
    END IF;
END $$;

-- Set up Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update their own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert their own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Create function to automatically create profiles
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, avatar_url, onboarding_completed, personality_data, created_at, updated_at)
  VALUES (
    NEW.id, 
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    NEW.raw_user_meta_data->>'avatar_url',
    FALSE,
    '{}'::jsonb,
    NOW(),
    NOW()
  )
  ON CONFLICT (id) DO UPDATE SET
    full_name = COALESCE(EXCLUDED.full_name, profiles.full_name),
    avatar_url = COALESCE(EXCLUDED.avatar_url, profiles.avatar_url),
    updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Grant permissions
GRANT ALL ON profiles TO authenticated;
GRANT ALL ON profiles TO service_role;
```

### 4. Run the Application
```bash
npm run dev
```

Visit http://localhost:3000

## Features Working
✅ Landing page with all sections
✅ Sign up / Sign in functionality
✅ Personality questionnaire 
✅ Dashboard with:
  - Chat interface
  - Music recommendations
  - Video recommendations  
  - RPG-style games
✅ Authentication flow
✅ Database integration

## Troubleshooting

### Error: "Could not find the 'onboarding_completed' column"
- Make sure you ran the database setup SQL above
- Check your Supabase project has the profiles table

### Error: "Profile creation error: {}"
- Verify your .env.local has correct Supabase credentials
- Check Row Level Security policies are set up

### Debug Tools
- Visit `/debug` to test database connection
- Check browser console for detailed error logs

## Project Structure
```
bondhu-landing/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── sign-up/        # Registration page
│   │   ├── sign-in/        # Login page  
│   │   ├── onboarding/     # Personality questionnaire
│   │   ├── dashboard/      # Main dashboard
│   │   └── debug/          # Database testing
│   ├── components/         # Reusable UI components
│   └── lib/               # Utilities and Supabase client
├── database/              # Database schema
└── public/               # Static assets
```

That's it! The app should work out of the box once Supabase is configured.