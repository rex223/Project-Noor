# Supabase Authentication Setup Guide for Bondhu

This guide will help you set up Supabase authentication for the Bondhu AI Mental Health Companion landing page.

## 🚀 Quick Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create an account
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `bondhu-ai-companion`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your users
5. Click "Create new project"

### 2. Environment Variables

1. Copy `env.local.example` to `.env.local`
2. In your Supabase dashboard, go to **Settings > API**
3. Copy the following values:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **Anon public key** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`

```env
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### 3. Database Setup

1. Go to **SQL Editor** in your Supabase dashboard
2. Copy and paste the contents of `database/schema.sql`
3. Click "Run" to execute the SQL

This will create:
- `profiles` table with RLS policies
- Automatic trigger to create profiles on user signup
- Proper permissions and security

### 4. Authentication Providers

#### Email/Password (Default)
- Already enabled by default

#### Google OAuth (Optional)
1. Go to **Authentication > Providers**
2. Click on **Google**
3. Enable the provider
4. Add your Google OAuth credentials:
   - **Client ID**: From Google Cloud Console
   - **Client Secret**: From Google Cloud Console
5. Add redirect URL: `https://your-project-id.supabase.co/auth/v1/callback`

### 5. URL Configuration

1. Go to **Authentication > URL Configuration**
2. Add your site URL: `http://localhost:3000` (development)
3. For production, add: `https://your-domain.com`
4. Add redirect URLs:
   - `http://localhost:3000/auth/callback`
   - `https://your-domain.com/auth/callback`

## 🔧 Development Setup

### Install Dependencies
```bash
npm install @supabase/ssr @supabase/supabase-js react-hook-form @hookform/resolvers zod
```

### Run Development Server
```bash
npm run dev
```

## 📱 User Flow Testing

### New User Journey
1. Visit `/sign-up`
2. Fill out registration form
3. Verify email (if email confirmation enabled)
4. Redirected to `/onboarding/personality`
5. Complete personality questionnaire
6. Redirected to `/dashboard`

### Returning User Journey
1. Visit `/sign-in`
2. Enter credentials
3. Automatic redirect based on onboarding status:
   - If incomplete → `/onboarding/personality`
   - If complete → `/dashboard`

## 🛠️ Database Schema

### Profiles Table
```sql
profiles (
  id UUID PRIMARY KEY (references auth.users),
  full_name TEXT,
  avatar_url TEXT,
  onboarding_completed BOOLEAN DEFAULT FALSE,
  personality_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)
```

### Row Level Security (RLS)
- Users can only access their own profile data
- Automatic profile creation on user signup
- Secure by default

## 🔐 Security Features

- **RLS Policies**: Users can only access their own data
- **Password Requirements**: Minimum 8 characters with complexity
- **Email Validation**: Built-in email verification
- **Session Management**: Automatic refresh and secure cookies
- **Route Protection**: Middleware-based authentication checks

## 📋 Routes Overview

### Public Routes
- `/` - Landing page
- `/sign-in` - Authentication
- `/sign-up` - Registration

### Protected Routes
- `/dashboard` - Main user dashboard
- `/chat` - Chat interface (when implemented)
- `/profile` - User profile management

### Conditional Routes
- `/onboarding/personality` - Only accessible if onboarding incomplete

## 🎨 UI Features

### Split-Screen Auth Design
- Left: Animated gradient background with testimonials
- Right: Clean form with error handling
- Responsive design for all screen sizes
- Dark/light theme support

### Form Validation
- Real-time validation with Zod schemas
- Supportive error messages (mental health appropriate)
- Loading states and disabled inputs
- Remember me functionality

### Accessibility
- WCAG 2.1 AA compliant
- Proper ARIA labels
- Keyboard navigation
- Screen reader support

## 🚨 Troubleshooting

### Common Issues

#### "Invalid login credentials"
- Check email/password combination
- Verify user exists in Supabase Auth dashboard
- Check if email confirmation is required

#### Redirect loops
- Verify RLS policies are correctly set
- Check middleware configuration
- Ensure profile table exists

#### OAuth not working
- Verify redirect URLs in provider settings
- Check client ID/secret configuration
- Ensure provider is enabled

### Debug Mode
Add to your `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_DEBUG=true
```

## 📚 Additional Resources

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Next.js SSR Guide](https://supabase.com/docs/guides/auth/server-side/nextjs)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

## 🔄 Development Workflow

1. Make changes to auth components
2. Test locally with `npm run dev`
3. Check browser console for errors
4. Verify database changes in Supabase dashboard
5. Test user flows thoroughly

## 📊 Monitoring

### Supabase Dashboard
- **Auth**: Monitor user signups and logins
- **Database**: Check profile creation and updates
- **Logs**: Debug authentication issues

### Key Metrics to Watch
- User registration rate
- Email verification completion
- Onboarding completion rate
- Sign-in success rate

---

**Need Help?** Check the Supabase documentation or reach out to the development team.

**Made with ❤️ for Gen Z mental health**
