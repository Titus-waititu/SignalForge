"""
SignalForge REST API
FastAPI service for accessing jobs and signals
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging

from storage.db import get_db
from storage.models import Job, Signal
from config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup paths
BASE_DIR = Path(__file__).parent.parent
WEB_DIR = BASE_DIR / "web"
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

# Initialize FastAPI app
app = FastAPI(
    title="SignalForge API",
    description="Real-time signal engine for jobs, trends, and market patterns",
    version="1.0.0"
)

# Mount static files if directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR)) if TEMPLATES_DIR.exists() else None

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting SignalForge API...")
    db = get_db()
    db.create_tables()
    logger.info("Database tables initialized")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - serve dashboard"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse(content="<h1>SignalForge API - Dashboard not available</h1>")


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "name": "SignalForge API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/jobs")
async def list_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    location: Optional[str] = None,
    company: Optional[str] = None,
    source: Optional[str] = None,
    posted_after: Optional[str] = None
):
    """
    List jobs with optional filters
    
    Args:
        limit: Maximum number of jobs to return
        offset: Number of jobs to skip
        min_score: Minimum score filter
        location: Location filter
        company: Company filter
        source: Job source filter (remoteok, linkedin, etc.)
        posted_after: Posted after date (ISO format)
    """
    db = get_db()
    
    with db.get_session() as session:
        query = session.query(Job)
        
        # Apply filters
        if min_score is not None:
            query = query.filter(Job.score >= min_score)
        
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        
        if company:
            query = query.filter(Job.company.ilike(f"%{company}%"))
        
        if source:
            query = query.filter(Job.source == source)
        
        if posted_after:
            try:
                date_filter = datetime.fromisoformat(posted_after)
                query = query.filter(Job.posted_at >= date_filter)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")
        
        # Order by score descending
        query = query.order_by(Job.score.desc(), Job.posted_at.desc())
        
        # Apply pagination
        jobs = query.offset(offset).limit(limit).all()
        
        # Convert to dict and return with metadata
        return {
            "jobs": [job.to_dict() for job in jobs],
            "count": len(jobs),
            "limit": limit,
            "offset": offset
        }


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """
    Get a specific job by ID
    
    Args:
        job_id: Job ID
    """
    db = get_db()
    
    with db.get_session() as session:
        job = session.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job.to_dict()


@app.get("/api/jobs/stats/summary")
async def get_jobs_stats():
    """Get job statistics"""
    db = get_db()
    
    with db.get_session() as session:
        from sqlalchemy import func
        
        total_jobs = session.query(Job).count()
        high_score_jobs = session.query(Job).filter(Job.score >= config.ALERT_THRESHOLD).count()
        alerted_jobs = session.query(Job).filter(Job.alerted == 1).count()
        
        # Calculate average score
        avg_score = session.query(func.avg(Job.score)).scalar() or 0
        
        # Recent jobs (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_jobs = session.query(Job).filter(Job.posted_at >= seven_days_ago).count()
        
        # Count remote jobs
        remote_jobs = session.query(Job).filter(
            Job.location.ilike('%remote%')
        ).count()
        
        # Top companies
        top_companies = session.query(
            Job.company,
            func.count(Job.id).label('count')
        ).group_by(Job.company).order_by(func.count(Job.id).desc()).limit(10).all()
        
        # Top locations
        top_locations = session.query(
            Job.location,
            func.count(Job.id).label('count')
        ).group_by(Job.location).order_by(func.count(Job.id).desc()).limit(10).all()
        
        return {
            "total_jobs": total_jobs,
            "high_score_count": high_score_jobs,
            "alerted_jobs": alerted_jobs,
            "recent_jobs": recent_jobs,
            "average_score": float(avg_score),
            "remote_jobs": remote_jobs,
            "top_companies": [{"company": c, "count": cnt} for c, cnt in top_companies],
            "top_locations": [{"location": l, "count": cnt} for l, cnt in top_locations]
        }


@app.get("/api/signals")
async def list_signals(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    signal_type: Optional[str] = None,
    min_score: Optional[int] = Query(None, ge=0, le=100)
):
    """
    List signals with optional filters
    
    Args:
        limit: Maximum number of signals to return
        offset: Number of signals to skip
        signal_type: Signal type filter (trend, anomaly, spike)
        min_score: Minimum score filter
    """
    db = get_db()
    
    with db.get_session() as session:
        query = session.query(Signal)
        
        if signal_type:
            query = query.filter(Signal.signal_type == signal_type)
        
        if min_score is not None:
            query = query.filter(Signal.score >= min_score)
        
        query = query.order_by(Signal.detected_at.desc())
        signals = query.offset(offset).limit(limit).all()
        
        return [signal.to_dict() for signal in signals]


@app.get("/api/signals/{signal_id}")
async def get_signal(signal_id: str):
    """Get a specific signal by ID"""
    db = get_db()
    
    with db.get_session() as session:
        signal = session.query(Signal).filter(Signal.id == signal_id).first()
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        return signal.to_dict()


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job by ID"""
    db = get_db()
    
    with db.get_session() as session:
        job = session.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        session.delete(job)
        session.commit()
        
        return {"message": "Job deleted successfully", "id": job_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
