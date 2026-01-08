# AI Agent Orchestration for Grassroots Lobbying

A production-grade multi-agent AI orchestration system for grassroots lobbying campaigns, built with Python, FastAPI, LangChain, and Apache Kafka.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Dashboard UI                             │
│                     (Next.js 14 + React)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    FastAPI Gateway                               │
│              (REST + GraphQL Endpoints)                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                     Apache Kafka                                 │
│            (Event Bus / Message Broker)                          │
└───┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─┘
    │         │         │         │         │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Monitor│ │Analysis│ │Strategy│ │Tactics│ │Content│ │Distrib│ │Feedbck│
│ Agent │ │ Agent │ │ Agent │ │ Agent │ │ Agent │ │ Agent │ │ Agent │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘
```

## 🤖 Agents

| Agent | Description |
|-------|-------------|
| **Monitoring** | Scans legislative, news, and social media sources |
| **Analysis** | Fact-checks claims, generates intelligence briefs |
| **Strategy** | Stakeholder analysis, policy window detection |
| **Tactics** | Converts strategy into concrete action items |
| **Content** | Generates press releases, tweets, fact sheets |
| **Distribution** | Delivers content via email, social media |
| **Feedback** | Tracks metrics and optimizes campaigns |

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for dashboard)

### 1. Clone and Configure

```bash
cd "AI Agent Orchestration"

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
```

### 2. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Run Migrations

```bash
# Install dependencies
pip install -e .

# Run database migrations
alembic upgrade head
```

### 4. Access Services

- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000
- **Kafka UI**: http://localhost:8080

## 📁 Project Structure

```
AI Agent Orchestration/
├── agents/                 # Agent implementations
│   ├── base/              # Base agent class
│   ├── monitoring/        # Legislative & news monitoring
│   ├── analysis/          # Fact-checking & summarization
│   ├── strategy/          # Campaign planning
│   ├── tactics/           # Action item generation
│   ├── content/           # Content creation
│   ├── distribution/      # Email & social posting
│   └── feedback/          # Analytics & metrics
├── api/                   # FastAPI application
│   ├── main.py           # App entrypoint
│   └── routes/           # API endpoints
├── core/                  # Shared utilities
│   ├── config/           # Settings & configuration
│   ├── database/         # SQLAlchemy models
│   ├── messaging/        # Kafka client
│   └── llm/              # LLM client wrapper
├── integrations/          # External API integrations
│   ├── congress/         # Congress.gov API
│   ├── news/             # NewsAPI & Google News
│   └── social/           # Twitter & Reddit
├── migrations/           # Alembic migrations
├── docker/              # Dockerfiles
├── docker-compose.yml   # Infrastructure definition
├── pyproject.toml       # Python dependencies
└── .env.example         # Environment template
```

## 🔧 Configuration

All configuration is done via environment variables. Key settings:

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `CONGRESS_API_KEY` | Congress.gov API key |
| `TWITTER_BEARER_TOKEN` | Twitter API v2 token |
| `SENDGRID_API_KEY` | SendGrid for email campaigns |

## 📊 API Endpoints

### Campaigns
- `GET /api/campaigns` - List campaigns
- `POST /api/campaigns` - Create campaign
- `PUT /api/campaigns/{id}` - Update campaign

### Intelligence
- `GET /api/intelligence` - List intelligence items
- `GET /api/intelligence/stats/summary` - Get statistics

### Content
- `GET /api/content` - List content items
- `POST /api/content/{id}/approve` - Approve content
- `POST /api/content/{id}/publish` - Publish content

### Agents
- `POST /api/agents/monitoring/scan` - Trigger scan
- `POST /api/agents/analysis/brief` - Generate brief
- `POST /api/agents/content/generate` - Generate content

## 🔒 Security

- JWT-based authentication
- Role-based access control
- Audit logging for all agent actions
- Rate limiting on API endpoints
- Secrets managed via environment variables

## 📈 Monitoring

- Prometheus metrics export
- Structured JSON logging
- Agent event auditing
- Performance dashboards

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy .

# Linting
ruff check .
```

## 📄 License

MIT License - See LICENSE file for details.
