# Docker Test Script - Validates Docker setup without building
# Run this to check if everything is configured correctly

Write-Host "🧪 SignalForge Docker Configuration Test" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# Test 1: Check Dockerfile exists
Write-Host "📄 Checking Dockerfile..." -NoNewline
if (Test-Path "Dockerfile") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

# Test 2: Check docker-compose.yml exists
Write-Host "📄 Checking docker-compose.yml..." -NoNewline
if (Test-Path "docker-compose.yml") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

# Test 3: Check .dockerignore exists
Write-Host "📄 Checking .dockerignore..." -NoNewline
if (Test-Path ".dockerignore") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ⚠" -ForegroundColor Yellow
    $warnings++
}

# Test 4: Check environment template
Write-Host "📄 Checking .env.docker template..." -NoNewline
if (Test-Path ".env.docker") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

# Test 5: Check deployment scripts
Write-Host "📄 Checking deploy.ps1..." -NoNewline
if (Test-Path "deploy.ps1") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ⚠" -ForegroundColor Yellow
    $warnings++
}

Write-Host "📄 Checking deploy.sh..." -NoNewline
if (Test-Path "deploy.sh") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ⚠" -ForegroundColor Yellow
    $warnings++
}

# Test 6: Check directories
Write-Host "📁 Checking data directory..." -NoNewline
if (Test-Path "data") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ⚠ (will be created)" -ForegroundColor Yellow
    $warnings++
}

Write-Host "📁 Checking logs directory..." -NoNewline
if (Test-Path "logs") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ⚠ (will be created)" -ForegroundColor Yellow
    $warnings++
}

# Test 7: Check required files
Write-Host "📄 Checking requirements.txt..." -NoNewline
if (Test-Path "requirements.txt") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

Write-Host "📄 Checking main.py..." -NoNewline
if (Test-Path "main.py") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

Write-Host "📄 Checking config.py..." -NoNewline
if (Test-Path "config.py") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

# Test 8: Validate Dockerfile syntax
Write-Host "🔍 Validating Dockerfile syntax..." -NoNewline
$dockerfileContent = Get-Content "Dockerfile" -Raw
if ($dockerfileContent -match "FROM python" -and $dockerfileContent -match "WORKDIR" -and $dockerfileContent -match "CMD") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

# Test 9: Validate docker-compose.yml
Write-Host "🔍 Validating docker-compose.yml..." -NoNewline
$composeContent = Get-Content "docker-compose.yml" -Raw
if ($composeContent -match "services:" -and $composeContent -match "signalforge:") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

# Test 10: Check Docker availability (optional)
Write-Host "🐳 Checking Docker availability..." -NoNewline
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host " ✓ Docker installed" -ForegroundColor Green
        
        # Check if Docker is running
        Write-Host "🐳 Checking Docker daemon..." -NoNewline
        try {
            docker ps 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host " ✓ Docker running" -ForegroundColor Green
            } else {
                Write-Host " ✗ Docker not running (Start Docker Desktop)" -ForegroundColor Red
                Write-Host "   To deploy: Start Docker Desktop, then run .\deploy.ps1" -ForegroundColor Yellow
            }
        } catch {
            Write-Host " ✗ Docker not running" -ForegroundColor Red
        }
    } else {
        Write-Host " ⚠ Docker not installed" -ForegroundColor Yellow
        Write-Host "   Install from: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    }
} catch {
    Write-Host " ⚠ Docker not installed" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 Test Summary" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ready to deploy!" -ForegroundColor Green
    Write-Host "Run: .\deploy.ps1" -ForegroundColor Cyan
} elseif ($errors -eq 0) {
    Write-Host "⚠️  Tests passed with $warnings warning(s)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Configuration is valid but has minor issues." -ForegroundColor Yellow
    Write-Host "You can proceed with deployment." -ForegroundColor Yellow
} else {
    Write-Host "❌ $errors error(s) and $warnings warning(s) found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the errors before deploying." -ForegroundColor Red
}

Write-Host ""
Write-Host "📖 For detailed Docker instructions, see DOCKER.md" -ForegroundColor Cyan
Write-Host ""
