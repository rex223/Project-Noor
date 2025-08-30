# The Last Neuron - Agentic AI Companion

A personality-adaptive digital twin companion for Gen Z built with Django, leveraging reinforcement learning and NLP for dynamic personality modeling.

## 🧠 About The Last Neuron

The Last Neuron is not just a chatbot - it's an autonomous digital twin agent designed to evolve alongside its user. Built specifically for Gen Z in India, it addresses the growing mental health challenges and digital isolation through:

- **Gamified Self-Discovery**: Interactive RPG scenarios to understand personality
- **Reinforcement Learning Adaptation**: Continuously learns from user interactions
- **Mood-Aware Media Curation**: Suggests content based on real-time emotional analysis
- **Privacy-First Architecture**: Secure and anonymized user data
- **Proactive Engagement**: Initiates conversations and suggests activities

## 🏗️ Architecture

### Tech Stack
- **Backend**: Django 4.2 LTS + Django Channels + DRF
- **Real-time**: WebSockets via Django Channels + Redis
- **Database**: PostgreSQL (primary) + MongoDB (flexible schemas)
- **ML/AI**: Stable-Baselines3, scikit-learn, spaCy, Transformers
- **Frontend**: Django Templates + HTMX + Tailwind CSS
- **Tasks**: Celery + Redis
- **Security**: JWT + AES encryption + Row-level security

### Key Components
1. **Personality Engine**: Dynamic personality modeling using RL
2. **Game Engine**: RPG-style scenarios for personality assessment
3. **Chat Engine**: Real-time conversation with NLP analysis
4. **Recommendation Engine**: Mood-aware media suggestions
5. **Anti-Gaming System**: Prevents manipulation of personality model

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+** (required for virtual environment)
- PostgreSQL 15+ (optional, SQLite used by default in development)
- Redis 6+ (required for Celery and real-time features)
- Node.js (for Tailwind CSS, optional)

### Installing Dependencies

#### Option 1: Using Docker (Recommended)
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Then run Redis in Docker:
docker run -p 6379:6379 redis
```

#### Option 2: Install Redis Natively (Windows)
```powershell
# Download Redis for Windows from:
# https://github.com/tporadowski/redis/releases
# Extract and run redis-server.exe
```

#### Option 3: Using Windows Subsystem for Linux (WSL)
```bash
# Install WSL and Ubuntu, then:
sudo apt update
sudo apt install redis-server
redis-server
```

### Installation

1. **Clone and setup virtual environment**
```bash
git clone <repository-url>
cd the-last-neuron
python3.12 -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your database and Redis configurations
```

4. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Run the development server**
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A the_last_neuron worker -l info

# Terminal 3: Celery beat scheduler
celery -A the_last_neuron beat -l info
```

## 📁 Project Structure

```
the_last_neuron/
├── apps/
│   ├── accounts/          # User authentication & profiles
│   ├── personality/       # Personality modeling & assessment
│   ├── chat/             # Real-time chat system
│   ├── games/            # RPG scenarios & mini-games
│   ├── recommendations/  # Media recommendation engine
│   ├── ml/               # Machine learning models
│   └── api/              # REST API endpoints
├── config/               # Django settings
├── static/               # Static files
├── templates/            # HTML templates
├── media/                # User uploads
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Container orchestration
└── README.md
```

## 🎮 Core Features

### 1. Gamified Onboarding
- Interactive personality assessment through RPG scenarios
- Big Five + MBTI-style questionnaires
- Dynamic scenario generation based on user responses

### 2. Agentic Behavior
- Proactive conversation initiation
- Context-aware response generation
- Goal-directed interaction planning

### 3. Personality Adaptation
- Continuous learning from user interactions
- Reinforcement learning-based personality updates
- Anti-gaming mechanisms for authentic modeling

### 4. Real-time Features
- WebSocket-based chat interface
- Live personality progress visualization
- Instant mood detection and response

## 🔒 Security & Privacy

- **End-to-End Encryption**: All chat logs encrypted with AES-256
- **Data Anonymization**: Training data detached from PII
- **Secure Authentication**: JWT with brute-force protection
- **Row-Level Security**: PostgreSQL RLS for data isolation

## 📊 Success Metrics

- Personality Prediction Accuracy: >75%
- User Retention (7-day): >40%
- Game Completion Rate: >60%
- Recommendation Uptake: >50%
- Average Session Duration: >8 minutes

## 🛣️ Roadmap

- **V1**: Web-based MVP with core personality modeling
- **V2**: Voice input/output capabilities
- **V3**: Android app with Flutter
- **V4**: Multimodal interaction (text + voice + image)
- **V5**: Group interactions and social features
- **V6**: Open API for third-party developers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for Gen Z mental health awareness
- Inspired by the need for authentic digital companionship
- Powered by open-source AI/ML technologies

---

**"An AI that doesn't just talk — it understands, remembers, and grows with you."**
