# Bondhu - AI Mental Health Companion

<div align="center">
  
![Bondhu Logo](https://ik.imagekit.io/nqxbbkkms/bg%20removed%20dark.png?updatedAt=1758793039828)

**An AI companion that adapts to your personality, grows with your journey, and becomes the friend you've always needed.**

[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?logo=typescript)](https://typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Backend-green?logo=supabase)](https://supabase.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![shadcn/ui](https://img.shields.io/badge/shadcn%2Fui-Components-black)](https://ui.shadcn.com/)

[🚀 Live Demo](https://bondhu-ai.vercel.app) • [📖 Documentation](#documentation) • [🤝 Contributing](#contributing) • [📧 Support](mailto:support@bondhu.ai)

</div>

## 📖 Table of Contents

- [About Bondhu](#about-bondhu)
- [✨ Key Features](#key-features)
- [🛠️ Technology Stack](#technology-stack)
- [🏗️ Architecture](#architecture)
- [🚀 Quick Start](#quick-start)
- [🔧 Installation & Setup](#installation--setup)
- [🎯 Usage Guide](#usage-guide)
- [🧠 AI & Personality System](#ai--personality-system)
- [🎮 Entertainment Learning](#entertainment-learning)
- [📱 Screenshots](#screenshots)
- [🔐 Privacy & Security](#privacy--security)
- [🤝 Contributing](#contributing)
- [📄 License](#license)
- [👥 Team](#team)

## About Bondhu

**Bondhu** (meaning "friend" in Bengali) is a next-generation AI mental health companion that goes beyond traditional chatbots. Built with cutting-edge personality analysis and multi-modal learning, Bondhu creates a unique, adaptive relationship with each user.

### 🎯 Mission
To democratize mental health support by providing personalized, accessible, and judgment-free AI companionship that evolves with each user's unique personality and needs.

### 🌟 What Makes Bondhu Different
- **Personality-Driven AI**: Uses Big Five personality analysis to adapt conversation style
- **Multi-Modal Learning**: Learns from games, music, videos, and conversations
- **Progressive Understanding**: Gets smarter about you over time
- **Mental Health Focused**: Designed specifically for emotional well-being and support

## ✨ Key Features

### 🧠 Advanced Personality Analysis
- **Big Five (OCEAN) Assessment**: Comprehensive personality profiling
- **RPG-Style Questionnaire**: Engaging 15-question personality discovery
- **Dynamic UI Adaptation**: Interface changes based on personality traits
- **Personality Evolution Tracking**: Monitor how your traits develop over time

### 💬 Intelligent Conversation System
- **Adaptive Communication**: AI adjusts tone, topics, and approach to your personality
- **Contextual Memory**: Remembers past conversations and personal growth
- **Emotional Intelligence**: Recognizes and responds to emotional states
- **Crisis Support Integration**: Seamless access to professional help when needed

### 🎮 Entertainment-Based Learning
- **Interactive Games**: Puzzle games, creative challenges, and strategic thinking tasks
- **Music Analysis**: Learns from your musical preferences and mood correlations
- **Video Content**: Curated mental health and educational content
- **Cross-Modal Insights**: Connects entertainment choices to personality understanding

### 📊 Comprehensive Analytics
- **Personality Dashboard**: Visual insights into your traits and growth
- **Progress Tracking**: Wellness scores, conversation metrics, and achievement systems
- **Entertainment Insights**: How your entertainment choices reflect your personality
- **Growth Opportunities**: Personalized suggestions for personal development

### 🔒 Privacy-First Design
- **End-to-End Encryption**: All conversations and data are fully encrypted
- **User Control**: Granular privacy settings and data management
- **Transparent AI**: Clear explanation of how AI learns and adapts
- **Professional Standards**: HIPAA-compliant data handling practices

## 🛠️ Technology Stack

### Frontend
```
{
  "framework": "Next.js 15 (App Router)",
  "language": "TypeScript 5.0",
  "styling": "Tailwind CSS 3.4",
  "components": "shadcn/ui",
  "animations": "Framer Motion",
  "icons": "Lucide React",
  "charts": "Recharts"
}
```

### Backend & Database
```
{
  "database": "Supabase (PostgreSQL)",
  "auth": "Supabase Auth",
  "realtime": "Supabase Realtime",
  "storage": "Supabase Storage",
  "security": "Row Level Security (RLS)"
}
```

### AI & Analytics
```
{
  "personality_analysis": "Big Five (OCEAN) Model",
  "conversation_ai": "Large Language Model Integration",
  "recommendation_engine": "Cross-modal preference learning",
  "analytics": "Custom personality scoring algorithms"
}
```

### Entertainment Integration
```
{
  "games": "HTML5 Canvas + React",
  "music": "Spotify/YouTube Music API",
  "video": "Custom HTML5 player",
  "data_tracking": "Real-time user behavior analytics"
}
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │   Database      │
│   (Next.js 15) │────│   (Supabase)     │────│   (PostgreSQL)  │
│                 │    │                  │    │                 │
│ -  Landing Page  │    │ -  Authentication │    │ -  User Profiles │
│ -  Dashboard     │    │ -  Chat System    │    │ -  Conversations │
│ -  Profile       │    │ -  Personality    │    │ -  Personality   │
│ -  Entertainment │    │ -  Entertainment  │    │ -  Entertainment │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │   AI Services    │
                    │                  │
                    │ -  LLM Integration│
                    │ -  Personality AI │
                    │ -  Recommendation │
                    │ -  Content Curation│
                    └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Supabase account
- Git

### 1-Minute Setup
```
# Clone the repository
git clone https://github.com/yourusername/bondhu-ai.git
cd bondhu-ai

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Add your Supabase keys

# Run the development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to see Bondhu in action! 🎉

## 🔧 Installation & Setup

### Environment Variables
Create a `.env.local` file in the root directory:

```
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Authentication
NEXTAUTH_SECRET=your_nextauth_secret
NEXTAUTH_URL=http://localhost:3000

# AI Integration (Optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Entertainment APIs (Optional)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
YOUTUBE_API_KEY=your_youtube_api_key
```

### Database Setup
1. Create a new Supabase project
2. Run the database migrations:
```
-- Run these SQL commands in your Supabase SQL editor
-- (Detailed schema available in /database/schema.sql)

-- Create profiles table
CREATE TABLE profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  full_name TEXT,
  avatar_url TEXT,
  personality_openness INTEGER DEFAULT 50,
  personality_conscientiousness INTEGER DEFAULT 50,
  personality_extraversion INTEGER DEFAULT 50,
  personality_agreeableness INTEGER DEFAULT 50,
  personality_neuroticism INTEGER DEFAULT 50,
  onboarding_completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Users can view own profile" 
ON profiles FOR ALL USING (auth.uid() = id);
```

3. Enable Row Level Security (RLS) on all tables
4. Set up authentication providers in Supabase Dashboard

### Development Commands
```
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run type checking
npm run type-check

# Run linting
npm run lint

# Run tests
npm run test
```

## 🎯 Usage Guide

### For Users

#### 1. Getting Started
1. **Sign up** with email or Google OAuth
2. Complete the **personality assessment** (15 engaging questions)
3. Start your first **conversation with Bondhu**
4. Explore **entertainment features** to help Bondhu learn more about you

#### 2. Dashboard Navigation
- **Chat**: Main conversation interface with your AI companion
- **Entertainment**: Games, music, and videos that help Bondhu understand you
- **Profile**: Comprehensive personality analytics and insights
- **Settings**: Privacy controls and preferences

#### 3. Building Your Relationship with Bondhu
- **Daily Conversations**: Regular chats help Bondhu understand your communication style
- **Entertainment Engagement**: Play games and consume content to provide personality data
- **Profile Review**: Check your personality insights and growth tracking

### For Developers

#### Project Structure
```
src/
├── app/                    # Next.js 15 App Router
│   ├── (auth)/            # Authentication pages
│   ├── dashboard/         # Main dashboard
│   ├── entertainment/     # Entertainment hub
│   ├── profile/           # User profile & analytics
│   └── api/               # API routes
├── components/            # React components
│   ├── ui/                # shadcn/ui components
│   ├── dashboard/         # Dashboard-specific components
│   ├── entertainment/     # Entertainment components
│   └── auth/              # Authentication components
├── lib/                   # Utility libraries
│   ├── supabase.ts        # Supabase client
│   ├── personality.ts     # Personality analysis
│   └── utils.ts           # General utilities
├── types/                 # TypeScript type definitions
└── styles/                # Global styles
```

#### Key Components
- **ChatInterface**: Main conversation component with real-time messaging
- **PersonalityRadar**: Interactive personality visualization
- **EntertainmentHub**: Games and content discovery interface
- **PersonalityAssessment**: Big Five questionnaire implementation

## 🧠 AI & Personality System

### Big Five (OCEAN) Implementation

Bondhu uses the scientifically-validated Big Five personality model to understand and adapt to each user:

#### Personality Traits
- **Openness**: Creativity, curiosity, openness to experience
- **Conscientiousness**: Organization, discipline, goal-orientation  
- **Extraversion**: Social energy, assertiveness, enthusiasm
- **Agreeableness**: Empathy, cooperation, trust
- **Neuroticism**: Emotional stability, anxiety management

#### AI Adaptation Examples
```
// High Openness User
{
  conversationStyle: "Engage with abstract concepts, encourage creative thinking",
  topicPreferences: ["Philosophy", "Arts", "Innovation", "What-if scenarios"],
  languageStyle: "Metaphorical, imaginative, intellectually curious"
}

// High Conscientiousness User  
{
  conversationStyle: "Structured approach, goal-setting, accountability",
  supportApproach: "Create systems, track progress, celebrate milestones",
  languageStyle: "Organized, methodical, achievement-oriented"
}
```

### Learning Algorithm
1. **Initial Assessment**: Big Five questionnaire provides baseline personality profile
2. **Multi-Modal Learning**: Entertainment choices refine understanding
3. **Conversation Analysis**: Chat patterns reveal communication preferences
4. **Continuous Adaptation**: AI responses become increasingly personalized

## 🎮 Entertainment Learning

### Gaming Analytics
- **Puzzle Games**: Problem-solving style, patience, analytical thinking
- **Creative Games**: Artistic expression, aesthetic preferences
- **Strategy Games**: Planning approach, risk tolerance, decision-making
- **Social Games**: Interaction style, competitive vs cooperative nature

### Music Intelligence
- **Genre Preferences**: Cultural openness, complexity tolerance
- **Mood Regulation**: How music is used for emotional management
- **Discovery Patterns**: Openness to new experiences
- **Listening Habits**: Social vs solo preferences

### Video Content Analysis
- **Content Categories**: Educational vs entertainment preferences
- **Attention Patterns**: Focus capabilities and interests
- **Emotional Responses**: What content resonates emotionally
- **Learning Style**: Visual, auditory, or kinesthetic preferences

## 📱 Screenshots

<div align="center">

### Landing Page
![Landing Page](./docs/screenshots/landing.png)
*Clean, professional landing page with personality-focused messaging*

### Personality Assessment  
![Personality Test](./docs/screenshots/personality-test.png)
*RPG-style questionnaire making personality assessment engaging*

### Dashboard
![Dashboard](./docs/screenshots/dashboard.png)
*Comprehensive dashboard with chat, entertainment, and progress tracking*

### Entertainment Hub
![Entertainment](./docs/screenshots/entertainment.png)
*Interactive games and content that help AI learn user preferences*

### Profile Analytics
![Profile](./docs/screenshots/profile.png)
*Detailed personality insights and growth tracking*

</div>

## 🔐 Privacy & Security

### Data Protection
- **Encryption**: All data encrypted in transit and at rest
- **Minimal Collection**: Only collect data that enhances user experience
- **User Control**: Granular privacy settings and data deletion options
- **Transparency**: Clear explanation of data usage and AI learning

### Compliance
- **GDPR Compliant**: Full European data protection compliance
- **CCPA Compliant**: California Consumer Privacy Act compliance
- **HIPAA-Level Security**: Medical-grade data protection standards
- **SOC 2 Type II**: Enterprise security standards

### User Rights
- **Data Portability**: Export all personal data
- **Right to Deletion**: Permanently delete account and data
- **Access Rights**: View all stored personal data
- **Correction Rights**: Update or correct personal information

## 🤝 Contributing

We welcome contributions from developers, designers, mental health professionals, and anyone passionate about improving mental health accessibility!

### Getting Started
1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/yourusername/bondhu-ai.git`
3. **Create a branch**: `git checkout -b feature/amazing-feature`
4. **Make changes** and commit: `git commit -m 'Add amazing feature'`
5. **Push** to your fork: `git push origin feature/amazing-feature`
6. **Submit a Pull Request**

### Contribution Guidelines
- **Code Quality**: Follow TypeScript and React best practices
- **Testing**: Add tests for new features
- **Documentation**: Update README and docs for changes
- **Mental Health Sensitivity**: Ensure all contributions support user well-being

### Areas for Contribution
- 🧠 **AI/ML**: Improve personality analysis and conversation AI
- 🎮 **Entertainment**: Add new games and learning algorithms  
- 🎨 **Design**: Enhance UI/UX and accessibility
- 📱 **Mobile**: React Native mobile app development
- 🔐 **Security**: Security audits and improvements
- 📖 **Content**: Mental health resources and educational content

### Development Setup for Contributors
```
# Install dependencies
npm install

# Set up pre-commit hooks
npm run prepare

# Run tests
npm test

# Check code formatting
npm run lint
npm run format
```

## 📊 Project Status

- ✅ **MVP Completed**: Core chat and personality features
- ✅ **Entertainment Learning**: Games and content integration  
- 🔄 **Advanced AI**: Improving conversation quality and personalization
- 🔄 **Mobile App**: React Native development in progress
- 📋 **Professional Integration**: Healthcare provider dashboard planned

### Roadmap 2025
- **Q1**: Mobile app beta release
- **Q2**: Advanced crisis detection and support
- **Q3**: Integration with healthcare providers
- **Q4**: Multi-language support and global expansion

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Open Source Commitment
Bondhu is committed to being open-source to ensure:
- **Transparency** in AI decision-making
- **Community-driven** improvements
- **Accessibility** for developers worldwide
- **Trust** through open development

## 👥 Team

### Core Team
- **[Your Name]** - *Founder & Lead Developer* - [GitHub](https://github.com/yourusername) | [LinkedIn](https://linkedin.com/in/yourprofile)
- **Mental Health Advisory Board** - Licensed therapists and counselors providing guidance

### Contributors
Thanks to all our amazing contributors! See the full list [here](CONTRIBUTORS.md).

### Acknowledgments
- **Big Five Research**: Based on decades of personality psychology research
- **Mental Health Community**: Feedback and guidance from mental health professionals
- **Open Source Community**: Built with amazing open-source tools and libraries

## 📞 Support & Contact

### Get Help
- **Documentation**: [docs.bondhu.ai](https://docs.bondhu.ai)
- **Community Discord**: [discord.gg/bondhu](https://discord.gg/bondhu)
- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/bondhu-ai/issues)
- **Email Support**: [support@bondhu.ai](mailto:support@bondhu.ai)

### Emergency Resources
If you're in crisis, please reach out for immediate help:
- **National Suicide Prevention Lifeline**: 988 (US)
- **Crisis Text Line**: Text HOME to 741741
- **International**: [findahelpline.com](https://findahelpline.com)

---

<div align="center">

**Made with ❤️ for mental health and human connection**

[⭐ Star this repo](https://github.com/yourusername/bondhu-ai) | [🐦 Follow updates](https://twitter.com/bondhu_ai) | [🌐 Visit website](https://bondhu.ai)

*Bondhu: Because everyone deserves a friend who truly understands them.*

</div>
