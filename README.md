# AI Job Coach

> AI-Powered Resume Optimization Platform - Craft the perfect resume and boost your job search success

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)

## Overview

**AI Job Coach** is an intelligent resume optimization platform that helps job seekers create ATS-friendly professional resumes. The system combines advanced natural language processing, knowledge base systems, and intelligent matching algorithms to provide personalized resume optimization recommendations.

### Value Proposition

- **Smart Parsing**: Automatically parse PDF/DOCX resumes and extract structured information
- **ATS Optimization**: Keyword matching and optimization against job descriptions
- **STAR Framework**: Optimize achievements using STAR (Situation, Task, Action, Result) framework
- **AI Assistant**: Real-time conversational resume improvement suggestions
- **High Availability**: LLM failover mechanism ensures service stability
- **Knowledge-Driven**: Built-in anti-hallucination rules and powerful verb library to prevent AI fabrication

## Key Features

### 1. Intelligent Resume Parsing 📄

- Support for PDF and DOCX formats
- Auto-extract personal info, work experience, education, skills
- NLP-driven section recognition
- Structured data storage

### 2. Job Description Analysis 🎯

- Extract TOP 20 keywords intelligently
- Identify required vs. preferred skills
- Industry and domain classification
- Common verbs and nouns analysis

### 3. Resume Optimization Engine ✨

- **STAR Framework**: Transform experiences into impactful achievement descriptions
- **Keyword Optimization**: Auto-embed relevant keywords based on JD
- **Powerful Verb Library**: 150+ categorized verbs to avoid repetition
- **Quantification Guidance**: Help add specific numbers and metrics
- **Anti-Hallucination**: Ensure AI doesn't fabricate facts

### 4. Tailored Resume Generation 🎨

- Select relevant experiences from master resume based on target position
- Intelligent content matching and sorting
- One-click customized resume generation

### 5. AI Chat Assistant 💬

- Real-time resume improvement suggestions
- Q&A-style interaction
- Context-aware personalized recommendations

### 6. High Availability Architecture 🔄

- **LLM Failover**: OpenAI ⇄ Together AI automatic switching
- **Retry Mechanism**: Configurable retry attempts and delays
- **Caching Layer**: Improved response speed
- **Vector Store**: Semantic search support

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (Next.js 15)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Upload  │  │ JD Input │  │ Optimize │  │   Chat   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Application Layer (Use Cases)             │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Domain Layer (Models & Ports)             │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Infrastructure Layer                    │    │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────┐          │    │
│  │  │   LLM   │  │   NLP   │  │ Storage  │          │    │
│  │  │ Manager │  │         │  │          │          │    │
│  │  │ ┌─────┐ │  │ • Parse │  │ • DB     │          │    │
│  │  │ │OpenAI│ │  │ • Optimize│ • Cache  │          │    │
│  │  │ └─────┘ │  │ • Analyze│  │ • Vector │          │    │
│  │  │ ┌─────┐ │  │         │  │          │          │    │
│  │  │ │Together│ │         │  │          │          │    │
│  │  │ │  AI  │ │  └─────────┘  └──────────┘          │    │
│  │  │ └─────┘ │                                       │    │
│  │  │(Fallback)│                                       │    │
│  │  └─────────┘                                       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
            ┌──────────────────────────────┐
            │     Knowledge Base            │
            │  • STAR Framework             │
            │  • Powerful Verbs (150+)      │
            │  • Anti-Hallucination Rules   │
            │  • Quantification Guidelines  │
            └──────────────────────────────┘
```

### Architecture Highlights

- **Clean Architecture**: Clear layered architecture, easy to maintain and extend
- **Dependency Injection**: Loosely coupled module design
- **Failover**: Dual LLM providers ensure availability
- **Async Processing**: FastAPI + async/await for high performance
- **Type Safety**: Pydantic model validation + TypeScript

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn
- OpenAI API Key (required)
- Together AI API Key (optional, for fallback)

### 5-Minute Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/ivytas0905/AI-job-coach.git
cd AI-job-coach

# 2. Start backend
cd agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add your API keys
cd src
uvicorn agent_service.main:app --reload --host 0.0.0.0 --port 8000

# 3. Start frontend (new terminal)
cd web
npm install
npm run dev

# 4. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Installation

### Backend Setup

```bash
cd agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file with your configuration
vim .env

# Initialize database
python scripts/init_database.py

# Start service
cd src
uvicorn agent_service.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd web

# Install dependencies
npm install

# Configure environment variables
cp .env.local.example .env.local
# Edit .env.local file

# Start development server
npm run dev

# Build for production
npm run build
npm start
```

## Configuration

### Backend Environment Variables (.env)

```bash
# LLM Configuration (Primary Provider)
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Together AI Configuration (Fallback)
TOGETHER_API_KEY=your-together-api-key-here
TOGETHER_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1

# Fallback Settings
ENABLE_FALLBACK=true          # Enable failover
FALLBACK_PROVIDER=together    # Backup provider
MAX_RETRIES=2                 # Maximum retry attempts
RETRY_DELAY=1                 # Retry delay (seconds)

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000"]

# File Processing
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./ai_job_coach.db
DATABASE_ECHO=false
```

### Frontend Environment Variables (.env.local)

```bash
# API Endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-clerk-key
CLERK_SECRET_KEY=your-clerk-secret
```

## Usage Guide

### 1. Upload and Parse Resume

```bash
# Web UI
Visit: http://localhost:3000/dashboard/resume/upload
Upload PDF or DOCX resume

# API
curl -X POST "http://localhost:8000/api/v1/parse" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

### 2. Analyze Job Description

```bash
# Web UI
Visit: http://localhost:3000/dashboard/resume/jd-input
Paste job description

# API
curl -X POST "http://localhost:8000/api/jd-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "jd_text": "Job description content...",
    "job_title": "Software Engineer"
  }'
```

### 3. Optimize Resume Content

```bash
# Web UI
Visit: http://localhost:3000/dashboard/resume/optimize
Select experiences to optimize

# API
curl -X POST "http://localhost:8000/api/resume-optimization" \
  -H "Content-Type: application/json" \
  -d '{
    "bullet": "Developed an educational platform",
    "target_keywords": ["React", "AI", "EdTech"],
    "context": {
      "company": "Tech Company",
      "title": "Full Stack Engineer",
      "job_title": "Senior Frontend Engineer"
    }
  }'
```

### 4. Generate Tailored Resume

```bash
curl -X POST "http://localhost:8000/api/tailor" \
  -H "Content-Type: application/json" \
  -d '{
    "master_resume_id": "uuid",
    "jd_id": "uuid",
    "max_experiences": 5
  }'
```

### 5. AI Assistant Conversation

```bash
# Web UI
Visit: http://localhost:3000/dashboard/resume/chat

# API
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How can I make my resume more attractive?",
    "resume_id": "uuid"
  }'
```

## API Documentation

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/parse` | POST | Parse uploaded resume |
| `/api/master-resume` | GET/POST/PUT/DELETE | Master resume CRUD |
| `/api/jd` | POST | Submit job description |
| `/api/jd-analysis` | POST | Analyze job description |
| `/api/resume-optimization` | POST | Optimize resume bullets |
| `/api/tailor` | POST | Generate tailored resume |
| `/api/chat` | POST | AI assistant conversation |

Full API Documentation: Visit http://localhost:8000/docs after starting the backend service

## Project Structure

```
AI-job-coach/
├── agent/                          # Backend Service (Python/FastAPI)
│   ├── src/
│   │   └── agent_service/
│   │       ├── api/               # API Layer
│   │       │   ├── routes/        # Route endpoints
│   │       │   └── schemas/       # Pydantic models
│   │       ├── application/       # Application Layer
│   │       │   └── use_cases/     # Business logic use cases
│   │       ├── domain/            # Domain Layer
│   │       │   ├── models.py      # Domain models
│   │       │   └── ports.py       # Port interfaces
│   │       ├── infra/             # Infrastructure Layer
│   │       │   ├── llm/           # LLM Integration
│   │       │   │   ├── llm_manager.py     # Failover management
│   │       │   │   ├── openai_provider.py
│   │       │   │   └── together_provider.py
│   │       │   ├── nlp/           # NLP Processing
│   │       │   ├── storage/       # Data persistence
│   │       │   ├── cache/         # Cache service
│   │       │   ├── vector/        # Vector store
│   │       │   ├── knowledge/     # Knowledge base
│   │       │   └── matching/      # Matching algorithms
│   │       ├── config.py          # Configuration management
│   │       ├── wiring.py          # Dependency injection
│   │       └── main.py            # Application entry
│   ├── knowledge_base/            # Knowledge base resources
│   │   ├── star_framework.md
│   │   ├── powerful_verbs.json
│   │   ├── anti_hallucination_rules.json
│   │   └── quantification_guidelines.md
│   ├── scripts/                   # Utility scripts
│   │   └── init_database.py
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment variables example
│   └── README.md                  # Backend documentation
│
├── web/                           # Frontend Application (Next.js 15)
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   │   └── resume/
│   │   │   │       ├── upload/   # Upload page
│   │   │   │       ├── jd-input/ # JD input
│   │   │   │       ├── optimize/ # Optimization page
│   │   │   │       └── chat/     # Chat assistant
│   │   │   └── api/              # API routes
│   │   ├── components/           # React components
│   │   ├── lib/                  # Utility functions
│   │   └── types/                # TypeScript types
│   ├── package.json              # Node dependencies
│   └── README.md                 # Frontend documentation
│
├── .github/                      # GitHub configuration
├── KNOWLEDGE_BASE_IMPLEMENTATION.md
└── README.md                     # This file
```

## Development

### Adding New Features

1. **Backend API**
   ```bash
   # 1. Create new route in agent/src/agent_service/api/routes/
   # 2. Define schemas in agent/src/agent_service/api/schemas/
   # 3. Implement business logic in agent/src/agent_service/application/use_cases/
   # 4. Register route in main.py
   ```

2. **Frontend Pages**
   ```bash
   # 1. Create new page under web/src/app/
   # 2. Define types in web/src/types/
   # 3. Use SWR for data fetching
   ```

### Running Tests

```bash
# Backend tests
cd agent
pytest

# Frontend tests
cd web
npm test

# LLM failover test
cd agent
python test_fallback.py
```

### Code Standards

- **Python**: Follow PEP 8, use black for formatting
- **TypeScript**: Follow Airbnb style guide
- **Commits**: Use Conventional Commits format
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation update
  - `refactor:` Refactoring
  - `test:` Testing

## Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
lsof -i:8000
```

### Frontend Can't Connect to Backend

```bash
# Check if backend is running
curl http://localhost:8000/docs

# Check CORS configuration
# Ensure agent/.env CORS_ORIGINS includes frontend address

# Check frontend environment variables
cat web/.env.local
```

### LLM API Errors

```bash
# Check API Key
echo $OPENAI_API_KEY

# Test failover
# Set ENABLE_FALLBACK=true in .env
# System will automatically switch to Together AI

# View logs
tail -f agent/logs/app.log
```

### File Upload Failures

```bash
# Check file size limit
# MAX_FILE_SIZE in .env (default 10MB)

# Check upload directory permissions
ls -la agent/uploads/

# Create upload directory
mkdir -p agent/uploads
chmod 755 agent/uploads
```

## Tech Stack

### Backend

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic 2.5.0
- **LLM**: OpenAI 1.3.7, Together AI
- **File Processing**: PyPDF2, python-docx
- **ML/NLP**: NumPy, scikit-learn
- **Database**: SQLAlchemy (async), SQLite
- **Testing**: pytest

### Frontend

- **Framework**: Next.js 15.5.3 (App Router + Turbopack)
- **UI**: React 19.1.0
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **Authentication**: Clerk
- **Data Fetching**: SWR
- **State Management**: React Hooks

### Infrastructure

- **Cache**: In-memory cache
- **Vector Store**: Custom simple vector store
- **Database**: SQLite (switchable to PostgreSQL)

## Contributing

We welcome all forms of contributions!

### How to Contribute

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'feat: add some amazing feature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Branches

- `main`: Production stable version
- `feature/*`: New feature development
- `bugfix/*`: Bug fixes
- `hotfix/*`: Emergency fixes

### Recent Feature Branches

- `feature/llm-fallback`: LLM failover mechanism
- `feature/knowledge-base-system`: Knowledge base system
- `feature/backend-infrastructure`: Backend infrastructure
- `feature/api-routes-and-frontend`: API and frontend integration

## License

MIT License

Copyright (c) 2024 AI Job Coach

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**Made with ❤️ for job seekers worldwide**

For questions or suggestions, please submit an [Issue](https://github.com/ivytas0905/AI-job-coach/issues)
