# SignalForge 🔥

**A real-time signal engine for jobs, trends, and chaotic market patterns.**

SignalForge watches the internet, scores what matters, and alerts you before everyone else.

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd SignalForge

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Add your Telegram bot token and chat ID
```

### 3. Initialize Database

```bash
python main.py init
```

### 4. Run the Application

```bash
# Run both scheduler and API
python main.py run

# Or run separately
python main.py run --mode scheduler
python main.py run --mode api
```

---

## 🎯 Features

- ✅ **Job Collection**: Automatically scrapes job listings from multiple sources
- ✅ **Smart Scoring**: ML-powered scoring based on keywords, stack, location, and freshness
- ✅ **Real-time Alerts**: Telegram notifications for high-value opportunities
- ✅ **REST API**: Query jobs and signals via FastAPI endpoints
- ✅ **Extensible**: Easy to add new collectors and signal types

---

## 📦 Architecture

```
signalforge/
├── alerts/          # Notification channels (Telegram)
├── api/             # FastAPI REST service
├── collectors/      # Data fetchers (GitHub Jobs, RemoteOK)
├── processors/      # Intelligence layer (scoring, NLP)
├── rules/           # Business logic (YAML configs)
├── scheduler/       # Task runners (APScheduler)
├── storage/         # Database models and ORM
├── config.py        # Application configuration
├── main.py          # CLI entrypoint
└── requirements.txt # Dependencies
```

---

## 🔁 Data Flow

```
Scheduler → Collector → Normalizer → Scorer → Database → Alert Engine
```

1. **Scheduler** triggers collectors on interval
2. **Collectors** fetch raw data from sources
3. **Normalizer** standardizes data format
4. **Scorer** evaluates based on rules
5. **Database** persists results
6. **Alert Engine** notifies on high scores

---

## 📊 Job Signal Model

| Field     | Type        | Description         |
| --------- | ----------- | ------------------- |
| id        | string      | Unique identifier   |
| title     | string      | Job title           |
| company   | string      | Company name        |
| location  | string      | Job location        |
| stack     | string[]    | Tech stack          |
| url       | string      | Application URL     |
| posted_at | datetime    | When job was posted |
| score     | int (0-100) | Relevance score     |
| source    | string      | Data source         |
| alerted   | boolean     | Alert sent flag     |

---

## 🧮 Scoring Algorithm v1

| Rule                | Weight | Description                   |
| ------------------- | ------ | ----------------------------- |
| Freshness (<7 days) | 30     | How recent the job posting is |
| Keyword match       | 40     | Match with target keywords    |
| Stack match         | 20     | Tech stack relevance          |
| Location relevance  | 10     | Preferred location match      |

**Alert Threshold:** score >= 70

---

## 📜 Configuration

Edit `rules/job_rules.yaml`:

```yaml
keywords:
  - python
  - backend
  - ai
min_score: 70
max_age_days: 7
locations:
  - remote
  - kenya
```

Edit `.env`:

```bash
DATABASE_URL=sqlite:///signalforge.db
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
ALERT_THRESHOLD=70
```

---

## 🔔 Setting Up Telegram Alerts

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Copy the bot token
3. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
4. Add both to `.env` file

Test alerts:

```bash
python main.py test-alert
```

---

## 📡 API Endpoints

| Method | Endpoint              | Description      |
| ------ | --------------------- | ---------------- |
| GET    | `/`                   | API info         |
| GET    | `/health`             | Health check     |
| GET    | `/jobs`               | List all jobs    |
| GET    | `/jobs/{id}`          | Get specific job |
| GET    | `/jobs/stats/summary` | Job statistics   |
| GET    | `/signals`            | List signals     |
| DELETE | `/jobs/{id}`          | Delete job       |

**Example:**

```bash
# Get high-score jobs
curl http://localhost:8000/jobs?min_score=80

# Get remote jobs
curl http://localhost:8000/jobs?location=remote

# Get stats
curl http://localhost:8000/jobs/stats/summary
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t signalforge .

# Run container
docker run -d -p 8000:8000 --env-file .env signalforge

# Or use docker-compose
docker-compose up -d
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## 🛠️ CLI Commands

```bash
# Initialize database
python main.py init

# Run application
python main.py run

# Run collectors once
python main.py collect

# Test alerts
python main.py test-alert

# View statistics
python main.py stats

# Show version
python main.py version
```

---

## 🗺️ Roadmap

### Phase 1 ✅ (Complete)

- [x] Job collectors (GitHub Jobs, RemoteOK)
- [x] Rules engine + scoring
- [x] Telegram alerts
- [x] REST API
- [x] Docker deployment

### Phase 2 🚧 (In Progress)

- [ ] Trends engine
- [ ] Advanced NLP patterns
- [ ] Dashboard UI
- [ ] Multiple notification channels

### Phase 3 📋 (Planned)

- [ ] Chaos detection (anomalies, spikes)
- [ ] AI-powered scoring
- [ ] Multi-user support
- [ ] SaaS mode

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👥 Contributors

- **Mannuel Misheen** - Lead Developer
- **Andreas Tailas** - Contributor

---

## 🔗 Links

- Documentation: [Coming Soon]
- Issues: [GitHub Issues]
- Discussions: [GitHub Discussions]

---

**SignalForge** — _Build once, watch everything._ 🔥
