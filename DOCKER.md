# 🐳 Docker Quick Start Guide

## Prerequisites

1. **Install Docker Desktop**
   - Windows/Mac: Download from https://www.docker.com/products/docker-desktop
   - Linux: `sudo apt-get install docker.io docker-compose`

2. **Start Docker Desktop**
   - Make sure Docker Desktop is running before deploying
   - Check status: `docker ps` should work without errors

## Deployment Methods

### Method 1: Automated Deployment (Easiest) ⭐

#### Windows:

```powershell
# Start Docker Desktop first, then run:
.\deploy.ps1
```

#### Linux/Mac:

```bash
# Start Docker daemon first, then run:
chmod +x deploy.sh
./deploy.sh
```

The script will:

- ✅ Check Docker is running
- ✅ Create required directories
- ✅ Set up environment file
- ✅ Build Docker image
- ✅ Start the application
- ✅ Open dashboard in browser

### Method 2: Docker Compose (Manual)

```bash
# 1. Ensure directories exist
mkdir -p data logs

# 2. Set up environment (optional)
cp .env.docker .env
# Edit .env if you want to configure Telegram alerts

# 3. Build and start
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Access dashboard
# Open http://localhost:8000 in browser
```

### Method 3: Plain Docker

```bash
# Build
docker build -t signalforge .

# Run
docker run -d \
  --name signalforge \
  -p 8000:8000 \
  -v ${PWD}/data:/app/data \
  -v ${PWD}/logs:/app/logs \
  -e ENABLE_ALERTS=false \
  signalforge
```

## Verification

After deployment, verify everything is working:

1. **Check container is running:**

   ```bash
   docker ps | grep signalforge
   ```

2. **Check health:**

   ```bash
   curl http://localhost:8000/health
   ```

3. **View logs:**

   ```bash
   docker-compose logs -f signalforge
   ```

4. **Access dashboard:**
   - Open http://localhost:8000
   - You should see the SignalForge dashboard

## Common Commands

```bash
# View running containers
docker-compose ps

# Stop application
docker-compose stop

# Start application
docker-compose start

# Restart application
docker-compose restart

# View logs
docker-compose logs -f

# Execute CLI commands
docker-compose exec signalforge python main.py stats
docker-compose exec signalforge python main.py collect

# Access container shell
docker-compose exec signalforge sh

# Stop and remove everything
docker-compose down

# Rebuild after code changes
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Docker not running

```
Error: failed to connect to docker API
```

**Solution:** Start Docker Desktop application

### Port already in use

```
Error: port 8000 is already allocated
```

**Solution:**

```bash
# Stop any process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml:
ports:
  - "8080:8000"  # Access via http://localhost:8080
```

### Permission denied on data/logs

```
Error: permission denied
```

**Solution:**

```bash
# Linux/Mac:
sudo chown -R $USER:$USER data logs

# Or run with sudo:
sudo docker-compose up -d
```

### Container immediately stops

**Solution:** Check logs for errors

```bash
docker-compose logs signalforge
```

Common issues:

- Missing environment variables
- Database migration needed
- Port conflicts

### Reset everything

```bash
# Stop and remove containers
docker-compose down -v

# Remove data
rm -rf data/* logs/*

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

For production, make these changes:

1. **Use PostgreSQL:**
   - Uncomment postgres service in `docker-compose.yml`
   - Update `DB_URL` in `.env`

2. **Enable alerts:**

   ```bash
   ENABLE_ALERTS=true
   TELEGRAM_TOKEN=your_real_token
   TELEGRAM_CHAT_ID=your_real_chat_id
   ```

3. **Add reverse proxy (nginx/Caddy):**

   ```yaml
   # docker-compose.yml
   nginx:
     image: nginx:alpine
     ports:
       - "80:80"
       - "443:443"
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf
   ```

4. **Set resource limits:**

   ```yaml
   deploy:
     resources:
       limits:
         cpus: "2"
         memory: 2G
   ```

5. **Configure log rotation**

6. **Set up monitoring** (Prometheus, Grafana)

## Next Steps

After successful deployment:

1. ✅ Access dashboard: http://localhost:8000
2. ✅ Trigger job collection: Click "Collect" button
3. ✅ Configure Telegram alerts (optional)
4. ✅ Set up automatic collection schedule
5. ✅ Monitor logs and performance

## Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify Docker is running: `docker ps`
3. Check environment: `docker-compose config`
4. Review documentation in README.md
5. Open an issue on GitHub

---

**Happy deploying! 🚀**
