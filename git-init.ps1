# PowerShell script to initialize Git repository

Write-Host "🔧 Initializing Git repository for Organizations API..." -ForegroundColor Cyan

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    exit 1
}

# Initialize git if not already initialized
if (-not (Test-Path ".git")) {
    Write-Host "📦 Initializing Git repository..." -ForegroundColor Yellow
    git init
} else {
    Write-Host "✅ Git repository already initialized" -ForegroundColor Green
}

# Add all files
Write-Host "📝 Adding files..." -ForegroundColor Yellow
git add .

# Create commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
git commit -m "feat(api): initial implementation - Organizations REST API

Complete REST API implementation with:
- FastAPI + Pydantic v2 + SQLAlchemy 2.0
- PostgreSQL 15 + PostGIS 3.4
- Alembic migrations + seed data
- API Key authentication
- 10+ endpoints (CRUD + geo search)
- Materialized Path tree (activities, max 3 levels)
- Docker + docker-compose
- Pytest integration tests
- Swagger UI documentation

Features:
- Organizations with phones, building, activities
- Buildings with PostGIS geography (lat/lon)
- Activity tree (max depth 3)
- Geo search (radius + bounding box)
- Search by name
- Filter by building, activity (with nested)

Stack: Python 3.11, FastAPI, SQLAlchemy, PostGIS, Docker"

Write-Host ""
Write-Host "✅ Git initialized successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Repository status:" -ForegroundColor Cyan
git log --oneline -1

Write-Host ""
Write-Host "🔗 Next steps:" -ForegroundColor Yellow
Write-Host "1. Create GitHub repository: https://github.com/new" -ForegroundColor White
Write-Host "2. Add remote: git remote add origin https://github.com/Sonti22/organizations-api.git" -ForegroundColor White
Write-Host "3. Push: git push -u origin main" -ForegroundColor White

