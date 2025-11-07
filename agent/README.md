# AI Job Coach - Backend Service

> FastAPI-based Resume Optimization Service with AI-powered features

## Overview

The backend service is built with **FastAPI** following **Clean Architecture** principles. It provides intelligent resume parsing, optimization, and generation capabilities powered by Large Language Models with automatic failover support.

## Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────────┐
│           Presentation Layer                 │
│         (FastAPI Routes & Schemas)           │
└───────────────────┬─────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Application Layer                   │
│            (Use Cases)                       │
└───────────────────┬─────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│            Domain Layer                      │
│        (Models & Ports)                      │
└───────────────────┬─────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│        Infrastructure Layer                  │
│  (LLM, NLP, Storage, Cache, Vector)         │
└─────────────────────────────────────────────┘
```

### Key Design Patterns

- **Dependency Injection**: Using `wiring.py` for loose coupling
- **Repository Pattern**: Abstraction over data persistence
- **Strategy Pattern**: Interchangeable LLM providers
- **Port & Adapter Pattern**: Clean separation of concerns

## Features

### 1. Resume Parsing
- **PDF/DOCX Support**: Parse resume files in multiple formats
- **Structured Extraction**: Extract personal info, experience, education, skills
- **Section Recognition**: NLP-driven section identification
- **Storage**: Save parsed resume to database

### 2. Job Description Analysis
- **Keyword Extraction**: Extract TOP 20 keywords with weights
- **Skill Classification**: Identify required vs. preferred skills
- **Industry Detection**: Classify industry and domain
- **Verb/Noun Analysis**: Extract common action verbs and nouns

### 3. Resume Optimization
- **STAR Framework**: Convert experiences into STAR format
- **Keyword Optimization**: Embed relevant JD keywords
- **Verb Diversification**: Use 150+ categorized action verbs
- **Anti-Hallucination**: Prevent AI from fabricating information

### 4. LLM Failover System
- **Primary Provider**: OpenAI (GPT-4o-mini)
- **Fallback Provider**: Together AI (Mixtral-8x7B)
- **Automatic Switching**: Seamless failover on errors
- **Retry Logic**: Configurable attempts and delays

### 5. Knowledge Base
- **STAR Framework Guidelines**: Best practices for achievement descriptions
- **Powerful Verbs Library**: 150+ categorized action verbs
- **Anti-Hallucination Rules**: Prevent AI fabrication
- **Quantification Guidelines**: Add metrics and numbers

## Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment tool

### Installation

```bash
# Navigate to agent directory
cd agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables template
cp .env.example .env

# Edit .env and add your API keys
vim .env
```

### Environment Configuration

Create a `.env` file with the following variables:

```bash
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Together AI (Fallback)
TOGETHER_API_KEY=your-together-api-key
TOGETHER_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1

# Fallback Settings
ENABLE_FALLBACK=true
FALLBACK_PROVIDER=together
MAX_RETRIES=2
RETRY_DELAY=1

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# File Processing
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads

# Database
DATABASE_URL=sqlite+aiosqlite:///./ai_job_coach.db
DATABASE_ECHO=false
```

### Running the Service

```bash
# Initialize database
python scripts/init_database.py

# Start the service (from agent/src directory)
cd src
uvicorn agent_service.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
# Open http://localhost:8000/docs in your browser
```

## API Endpoints

### Resume Operations

#### Parse Resume
```http
POST /api/v1/parse
Content-Type: multipart/form-data

file: <resume.pdf|resume.docx>
```

**Response:**
```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  },
  "experiences": [...],
  "education": [...],
  "skills": [...]
}
```

#### Master Resume CRUD
```http
GET    /api/master-resume          # List all
GET    /api/master-resume/{id}     # Get one
POST   /api/master-resume          # Create
PUT    /api/master-resume/{id}     # Update
DELETE /api/master-resume/{id}     # Delete
```

### Job Description Operations

#### Submit Job Description
```http
POST /api/jd
Content-Type: application/json

{
  "job_title": "Software Engineer",
  "company": "Tech Corp",
  "jd_text": "Job description content..."
}
```

#### Analyze Job Description
```http
POST /api/jd-analysis
Content-Type: application/json

{
  "jd_text": "Job description content...",
  "job_title": "Software Engineer"
}
```

**Response:**
```json
{
  "top_keywords": [
    {"keyword": "Python", "weight": 0.95, "type": "technical_skill"},
    {"keyword": "Machine Learning", "weight": 0.90, "type": "technical_skill"}
  ],
  "required_skills": ["Python", "SQL", "Git"],
  "preferred_skills": ["Docker", "AWS"],
  "common_verbs": ["develop", "implement", "design"],
  "industry": "technology"
}
```

### Optimization Operations

#### Optimize Resume Bullet
```http
POST /api/resume-optimization
Content-Type: application/json

{
  "bullet": "Built a teaching platform",
  "target_keywords": ["React", "AI", "EdTech"],
  "context": {
    "company": "Tech Company",
    "title": "Full Stack Engineer",
    "job_title": "Senior Frontend Engineer"
  },
  "used_verbs": ["built", "developed"]
}
```

**Response:**
```json
{
  "optimized_bullet": "Engineered AI-powered EdTech platform using React, serving 500+ students with personalized learning paths",
  "verb_used": "Engineered",
  "keywords_embedded": ["React", "AI", "EdTech"]
}
```

#### Generate Tailored Resume
```http
POST /api/tailor
Content-Type: application/json

{
  "master_resume_id": "uuid",
  "jd_id": "uuid",
  "max_experiences": 5
}
```

### Chat Operations

#### AI Assistant
```http
POST /api/chat
Content-Type: application/json

{
  "message": "How can I improve my resume?",
  "resume_id": "uuid",
  "chat_history": []
}
```

## Project Structure

```
agent/
├── src/
│   └── agent_service/
│       ├── api/                    # Presentation Layer
│       │   ├── routes/
│       │   │   ├── parse.py        # Resume parsing endpoint
│       │   │   ├── master.py       # Master resume CRUD
│       │   │   ├── jd.py           # Job description endpoints
│       │   │   ├── jd_analysis.py  # JD analysis endpoint
│       │   │   ├── resume_optimization.py
│       │   │   ├── tailor.py       # Tailored resume generation
│       │   │   └── chat_assistant.py
│       │   └── schemas/
│       │       ├── resume.py       # Resume models
│       │       ├── job_description.py
│       │       ├── optimization_schemas.py
│       │       └── ...
│       │
│       ├── application/            # Application Layer
│       │   └── use_cases/
│       │       ├── analyze_jd.py
│       │       ├── jd_analysis_enhanced.py
│       │       ├── resume_optimization_enhanced.py
│       │       ├── tailor_resume.py
│       │       └── chat_assistant.py
│       │
│       ├── domain/                 # Domain Layer
│       │   ├── models.py           # Domain entities
│       │   └── ports.py            # Port interfaces
│       │
│       ├── infra/                  # Infrastructure Layer
│       │   ├── llm/                # LLM Integration
│       │   │   ├── llm_manager.py  # Failover management
│       │   │   ├── openai_provider.py
│       │   │   ├── together_provider.py
│       │   │   └── enhanced_llm.py
│       │   │
│       │   ├── nlp/                # NLP Processing
│       │   │   ├── section_extractor.py
│       │   │   ├── bullet_optimizer.py
│       │   │   └── jd_analyzer.py
│       │   │
│       │   ├── storage/            # Data Persistence
│       │   │   ├── database.py     # Database manager
│       │   │   ├── models.py       # SQLAlchemy models
│       │   │   └── files.py        # File storage
│       │   │
│       │   ├── cache/              # Caching
│       │   │   └── memory_cache.py
│       │   │
│       │   ├── vector/             # Vector Store
│       │   │   └── simple_vector_store.py
│       │   │
│       │   ├── knowledge/          # Knowledge Base
│       │   │   └── knowledge_base.py
│       │   │
│       │   ├── matching/           # Matching Algorithms
│       │   │   └── content_selector.py
│       │   │
│       │   └── parsing/            # File Parsing
│       │       ├── pdf_parser.py
│       │       └── docx_parser.py
│       │
│       ├── config.py               # Configuration
│       ├── wiring.py               # Dependency Injection
│       └── main.py                 # Application Entry
│
├── knowledge_base/                 # Knowledge Resources
│   ├── star_framework.md
│   ├── powerful_verbs.json
│   ├── anti_hallucination_rules.json
│   └── quantification_guidelines.md
│
├── scripts/                        # Utility Scripts
│   └── init_database.py
│
├── tests/                          # Tests
│   ├── unit/
│   └── integration/
│
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
└── README.md                       # This file
```

## Infrastructure Modules

### LLM Manager

**Location**: `infra/llm/llm_manager.py`

Manages LLM provider failover:

```python
from agent_service.infra.llm import LLMManager

# Initialize
llm_manager = LLMManager()

# Generate text (automatic failover)
response = await llm_manager.generate_text(
    prompt="Optimize this bullet point",
    system_prompt="You are a resume expert",
    temperature=0.7
)

# Current provider
print(llm_manager.get_current_provider())  # "openai" or "together"
```

### Knowledge Base

**Location**: `infra/knowledge/knowledge_base.py`

Access knowledge resources:

```python
from agent_service.infra.knowledge import get_knowledge_base

kb = get_knowledge_base()

# Get powerful verbs by category
leadership_verbs = kb.get_verbs_by_category("leadership")

# Get anti-hallucination rules
rules = kb.get_anti_hallucination_principles()

# Get STAR framework guidelines
star_guidelines = kb.get_star_framework()
```

### Vector Store

**Location**: `infra/vector/simple_vector_store.py`

Semantic search for resume experiences:

```python
from agent_service.infra.vector import SimpleVectorStore

vector_store = SimpleVectorStore()

# Add experience
await vector_store.add(
    id="exp1",
    text="Built React application...",
    metadata={"company": "Tech Corp"}
)

# Semantic search
results = await vector_store.search(
    query="frontend development experience",
    top_k=5
)
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=agent_service
```

### Test LLM Failover

```bash
python test_fallback.py
```

## Development

### Adding a New API Endpoint

1. **Define Schema** (`api/schemas/`)
```python
from pydantic import BaseModel

class MyRequest(BaseModel):
    field1: str
    field2: int

class MyResponse(BaseModel):
    result: str
```

2. **Create Use Case** (`application/use_cases/`)
```python
class MyUseCase:
    def __init__(self, dependency):
        self.dependency = dependency

    async def execute(self, request):
        # Business logic here
        return result
```

3. **Create Route** (`api/routes/`)
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/my-endpoint", response_model=MyResponse)
async def my_endpoint(request: MyRequest):
    use_case = MyUseCase()
    result = await use_case.execute(request)
    return result
```

4. **Register Route** (`main.py`)
```python
from agent_service.api.routes import my_route

app.include_router(my_route.router, prefix="/api", tags=["my-feature"])
```

### Code Quality

```bash
# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

## Troubleshooting

### Database Issues

```bash
# Reset database
rm ai_job_coach.db
python scripts/init_database.py

# Check database
sqlite3 ai_job_coach.db ".tables"
```

### LLM API Errors

```bash
# Test OpenAI connection
python -c "from openai import OpenAI; client = OpenAI(); print(client.models.list())"

# Enable verbose logging
# Set LOG_LEVEL=DEBUG in .env
```

### Import Errors

```bash
# Ensure you're running from src/ directory
cd src
python -m agent_service.main

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

## Performance Optimization

### Caching

The system uses in-memory caching for:
- Frequently accessed resumes
- Job description analyses
- Keyword extractions

Configure cache settings in `.env`:
```bash
CACHE_TTL=3600  # seconds
CACHE_MAX_SIZE=1000  # items
```

### Database Optimization

For production, switch to PostgreSQL:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_job_coach
```

### Async Processing

All I/O operations use async/await for optimal performance:
- Database queries
- LLM API calls
- File operations

## Deployment

### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY knowledge_base/ ./knowledge_base/

CMD ["uvicorn", "agent_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/ai_job_coach
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ai_job_coach
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## License

MIT License - See [LICENSE](../LICENSE) for details

---

For frontend documentation, see [../web/README.md](../web/README.md)

For project overview, see [../README.md](../README.md)
