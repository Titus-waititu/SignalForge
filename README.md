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

SignalForge is fully containerized and production-ready with Docker!

### Quick Deploy (Automated)

#### Windows

```powershell
# One-command deployment
.\deploy.ps1
```

#### Linux/Mac

```bash
# One-command deployment
chmod +x deploy.sh
./deploy.sh
```

### Manual Docker Deployment

#### Option 1: Docker Compose (Recommended)

```bash
# 1. Create required directories
mkdir -p data logs

# 2. Configure environment
cp .env.docker .env
# Edit .env with your settings (Telegram tokens, etc.)

# 3. Start services
docker-compose up -d

# 4. View logs
docker-compose logs -f signalforge

# 5. Check status
docker-compose ps

# Access dashboard at http://localhost:8000
```

#### Option 2: Plain Docker

```bash
# Build image
docker build -t signalforge:latest .

# Run container
docker run -d \
  --name signalforge \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  signalforge:latest

# View logs
docker logs -f signalforge

# Access dashboard at http://localhost:8000
```

### Container Management

```bash
# View running containers
docker ps

# Stop SignalForge
docker-compose stop

# Restart SignalForge
docker-compose restart

# Update to latest code
git pull
docker-compose build
docker-compose up -d

# Remove containers and volumes
docker-compose down -v

# Access container shell
docker exec -it signalforge-app sh

# Run CLI commands inside container
docker exec signalforge-app python main.py stats
docker exec signalforge-app python main.py collect
```

### Production Deployment

For production, consider these enhancements:

1. **Use PostgreSQL** instead of SQLite:

   ```yaml
   # Uncomment postgres service in docker-compose.yml
   # Update DB_URL in .env:
   DB_URL=postgresql://signalforge:password@postgres:5432/signalforge
   ```

2. **Enable HTTPS** with a reverse proxy (nginx/traefik)

3. **Set resource limits** in docker-compose.yml:

   ```yaml
   deploy:
     resources:
       limits:
         cpus: "1.0"
         memory: 1G
   ```

4. **Configure log rotation** for production logs

5. **Set up monitoring** with health checks and alerts

### Docker Architecture

```
┌─────────────────────────────────────┐
│   SignalForge Container             │
│                                     │
│  ┌────────────┐  ┌──────────────┐  │
│  │ Scheduler  │  │   FastAPI    │  │
│  │ (Cron)     │  │   (Web UI)   │  │
│  └────────────┘  └──────────────┘  │
│         │                │          │
│  ┌──────▼────────────────▼───────┐ │
│  │   SQLite Database (Volume)    │ │
│  └───────────────────────────────┘ │
│                                     │
│  Volumes:                           │
│  - /app/data  (database)           │
│  - /app/logs  (logs)               │
└─────────────────────────────────────┘
        │
        └──── Port 8000 → localhost:8000
```

### Environment Variables

Key environment variables for Docker:

```bash
# Database
DB_URL=sqlite:////app/data/signalforge.db

# Telegram Alerts (Optional)
ENABLE_ALERTS=false
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Alert Configuration
ALERT_THRESHOLD=70

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/signalforge.log

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Scheduler
COLLECTION_INTERVAL=3600
```

### Troubleshooting

**Container won't start:**

```bash
# Check logs
docker-compose logs signalforge

# Check if port is in use
netstat -an | grep 8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

**Database permission issues:**

```bash
# Fix permissions
sudo chown -R 1000:1000 data logs
```

**Reset everything:**

```bash
docker-compose down -v
rm -rf data/* logs/*
docker-compose up -d
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
