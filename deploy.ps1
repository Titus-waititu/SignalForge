# SignalForge Docker Deployment Script (Windows)
# PowerShell script for Windows deployment

Write-Host "🔥 SignalForge Docker Deployment" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Error: Docker is not installed" -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
$composeCmd = $null
try {
    docker-compose --version | Out-Null
    $composeCmd = "docker-compose"
} catch {
    try {
        docker compose version | Out-Null
        $composeCmd = "docker compose"
    } catch {
        Write-Host "❌ Error: Docker Compose is not installed" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✓ Docker and Docker Compose found" -ForegroundColor Green
Write-Host ""

# Create required directories
Write-Host "📁 Creating required directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  No .env file found. Creating from .env.docker template..." -ForegroundColor Yellow
    Copy-Item ".env.docker" ".env"
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Please edit .env file with your configuration:" -ForegroundColor Yellow
    Write-Host "   - Set TELEGRAM_TOKEN if using alerts" -ForegroundColor Cyan
    Write-Host "   - Set TELEGRAM_CHAT_ID if using alerts" -ForegroundColor Cyan
    Write-Host "   - Set ENABLE_ALERTS=true to enable Telegram alerts" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Continue with current .env settings? (Y/n)"
    if ($continue -eq "n" -or $continue -eq "N") {
        Write-Host "Please configure .env and run this script again" -ForegroundColor Yellow
        exit 0
    }
}

# Build the Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
if ($composeCmd -eq "docker-compose") {
    docker-compose build
} else {
    docker compose build
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Start the services
Write-Host "🚀 Starting SignalForge..." -ForegroundColor Yellow
if ($composeCmd -eq "docker-compose") {
    docker-compose up -d
} else {
    docker compose up -d
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}

# Wait for health check
Write-Host "⏳ Waiting for application to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if container is running
$container = docker ps --filter "name=signalforge-app" --format "{{.Names}}"
if ($container -eq "signalforge-app") {
    Write-Host ""
    Write-Host "✅ SignalForge is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "🌐 Dashboard:  http://localhost:8000" -ForegroundColor White
    Write-Host "📡 API Docs:   http://localhost:8000/docs" -ForegroundColor White
    Write-Host "💚 Health:     http://localhost:8000/health" -ForegroundColor White
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Useful Commands:" -ForegroundColor Yellow
    if ($composeCmd -eq "docker-compose") {
        Write-Host "   View logs:    docker-compose logs -f" -ForegroundColor Cyan
        Write-Host "   Stop:         docker-compose stop" -ForegroundColor Cyan
        Write-Host "   Restart:      docker-compose restart" -ForegroundColor Cyan
        Write-Host "   Remove:       docker-compose down" -ForegroundColor Cyan
        Write-Host "   Shell access: docker exec -it signalforge-app sh" -ForegroundColor Cyan
    } else {
        Write-Host "   View logs:    docker compose logs -f" -ForegroundColor Cyan
        Write-Host "   Stop:         docker compose stop" -ForegroundColor Cyan
        Write-Host "   Restart:      docker compose restart" -ForegroundColor Cyan
        Write-Host "   Remove:       docker compose down" -ForegroundColor Cyan
        Write-Host "   Shell access: docker exec -it signalforge-app sh" -ForegroundColor Cyan
    }
    Write-Host ""
    
    # Try to open browser
    try {
        Start-Process "http://localhost:8000"
        Write-Host "🌐 Opening dashboard in browser..." -ForegroundColor Green
    } catch {
        # Browser didn't open, that's okay
    }
} else {
    Write-Host ""
    Write-Host "❌ Failed to start SignalForge" -ForegroundColor Red
    Write-Host "Check logs with: $composeCmd logs" -ForegroundColor Yellow
    exit 1
}
