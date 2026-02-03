"""
SignalForge Main Entry Point
Real-time signal engine for jobs, trends, and chaotic market patterns
"""

import logging
import sys
import click
from pathlib import Path
from datetime import datetime

from config import config
from storage.db import init_db
from scheduler.tasks import start_scheduler
from api.main import app

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """SignalForge - Real-time signal engine"""
    pass


@cli.command()
def init():
    """Initialize database and configuration"""
    try:
        logger.info("Initializing SignalForge...")
        
        # Validate configuration
        config.validate()
        
        # Initialize database
        init_db()
        
        logger.info("✅ SignalForge initialized successfully!")
        logger.info(f"Database: {config.DB_URL}")
        logger.info(f"Alert threshold: {config.ALERT_THRESHOLD}")
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--mode', type=click.Choice(['scheduler', 'api', 'both']), default='both',
              help='Run mode: scheduler only, api only, or both')
def run(mode):
    """Run SignalForge application"""
    try:
        logger.info(f"🚀 Starting SignalForge in {mode} mode...")
        
        # Initialize database
        init_db()
        
        if mode == 'scheduler':
            logger.info("Starting scheduler...")
            start_scheduler()
            
        elif mode == 'api':
            logger.info("Starting API server...")
            import uvicorn
            uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
            
        elif mode == 'both':
            logger.info("Starting both scheduler and API...")
            import threading
            import uvicorn
            
            # Start scheduler in separate thread
            scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
            scheduler_thread.start()
            
            # Start API in main thread
            uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
        
    except KeyboardInterrupt:
        logger.info("⏹️  Shutting down SignalForge...")
    except Exception as e:
        logger.error(f"❌ Error running SignalForge: {e}")
        sys.exit(1)


@cli.command()
def collect():
    """Run collectors once (manual trigger)"""
    try:
        logger.info("Running collectors...")
        from scheduler.tasks import run_collectors
        run_collectors()
        logger.info("✅ Collection completed")
        
    except Exception as e:
        logger.error(f"❌ Collection failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--count', default=5, help='Number of alerts to send')
def test_alert(count):
    """Test alert system with real jobs from database"""
    try:
        logger.info("Testing alert system with real jobs...")
        from alerts.telegram import TelegramAlerter
        from storage.db import get_db
        from storage.models import Job
        import asyncio
        
        db = get_db()
        
        # Get top scoring jobs and convert to dicts inside session
        jobs_data = []
        with db.get_session() as session:
            jobs = session.query(Job).order_by(Job.score.desc()).limit(count).all()
            
            if not jobs:
                logger.warning("No jobs found in database. Run 'python main.py collect' first.")
                return
            
            # Convert to dicts while in session
            jobs_data = [job.to_dict() for job in jobs]
            logger.info(f"Found {len(jobs_data)} jobs to test alerts")
        
        alerter = TelegramAlerter()
        
        # Send alerts
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            sent_count = 0
            for job_dict in jobs_data:
                result = loop.run_until_complete(alerter.send_job_alert(job_dict))
                if result:
                    sent_count += 1
                    logger.info(f"✅ Sent alert for: {job_dict['title']} at {job_dict['company']} (Score: {job_dict['score']})")
                else:
                    logger.warning(f"⚠️  Failed to send alert for: {job_dict['title']}")
            
            logger.info(f"✅ Test completed: {sent_count}/{len(jobs_data)} alerts sent successfully")
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"❌ Test alert failed: {e}")
        sys.exit(1)


@cli.command()
def stats():
    """Show database statistics"""
    try:
        from storage.db import get_db
        from storage.models import Job, Signal
        from sqlalchemy import func
        
        db = get_db()
        with db.get_session() as session:
            total_jobs = session.query(Job).count()
            high_score_jobs = session.query(Job).filter(Job.score >= config.ALERT_THRESHOLD).count()
            total_signals = session.query(Signal).count()
            
            logger.info("📊 SignalForge Statistics")
            logger.info(f"Total Jobs: {total_jobs}")
            logger.info(f"High Score Jobs: {high_score_jobs}")
            logger.info(f"Total Signals: {total_signals}")
            
    except Exception as e:
        logger.error(f"❌ Stats failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--limit', default=20, help='Number of jobs to show')
@click.option('--min-score', default=0, help='Minimum score filter')
@click.option('--location', default=None, help='Location filter')
def list_jobs(limit, min_score, location):
    """List collected jobs"""
    try:
        from storage.db import get_db
        from storage.models import Job
        
        db = get_db()
        with db.get_session() as session:
            query = session.query(Job)
            
            if min_score > 0:
                query = query.filter(Job.score >= min_score)
            
            if location:
                query = query.filter(Job.location.ilike(f"%{location}%"))
            
            jobs = query.order_by(Job.score.desc()).limit(limit).all()
            
            if not jobs:
                logger.info("No jobs found")
                return
            
            logger.info(f"\n📋 Found {len(jobs)} jobs:\n")
            for job in jobs:
                logger.info(f"{'='*80}")
                logger.info(f"🏢 {job.company} - {job.title}")
                logger.info(f"📍 Location: {job.location}")
                logger.info(f"⭐ Score: {job.score}")
                logger.info(f"🔗 URL: {job.url}")
                logger.info(f"📅 Posted: {job.posted_at}")
                if job.stack:
                    logger.info(f"💻 Stack: {job.stack}")
                logger.info("")
            
    except Exception as e:
        logger.error(f"❌ List jobs failed: {e}")
        sys.exit(1)


@cli.command()
def version():
    """Show version information"""
    click.echo("SignalForge v1.0.0")
    click.echo("Real-time signal engine for jobs, trends, and market patterns")
    click.echo("\nContributors:")
    click.echo("  - Mannuel Misheen")
    click.echo("  - Andreas Tailas")


@cli.command()
def trends():
    """Analyze job market trends"""
    try:
        from storage.db import get_db
        from storage.models import Job
        from processors.trends import TrendDetector
        
        logger.info("📈 Analyzing job market trends...")
        
        db = get_db()
        with db.get_session() as session:
            # Get all jobs
            jobs = session.query(Job).all()
            jobs_data = [job.to_dict() for job in jobs]
        
        if not jobs_data:
            logger.warning("No jobs in database. Run 'python main.py collect' first.")
            return
        
        detector = TrendDetector()
        trends_data = detector.analyze_trends(jobs_data)
        anomalies = detector.detect_anomalies(jobs_data)
        
        # Display trends
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 JOB MARKET TRENDS ANALYSIS")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"📈 Total Jobs Analyzed: {trends_data.get('total_jobs_analyzed', 0)}")
        logger.info(f"🔥 Recent Jobs (3 days): {trends_data.get('recent_job_count', 0)}\n")
        
        logger.info("🔝 TOP TRENDING KEYWORDS:")
        for keyword, count in trends_data.get('trending_keywords', [])[:10]:
            logger.info(f"  {keyword}: {count} jobs")
        
        logger.info("\n💻 TOP TECHNOLOGIES:")
        for tech, count in trends_data.get('top_technologies', [])[:10]:
            logger.info(f"  {tech}: {count} mentions")
        
        logger.info("\n🏢 TOP HIRING COMPANIES:")
        for company, count in trends_data.get('top_hiring_companies', [])[:10]:
            logger.info(f"  {company}: {count} positions")
        
        logger.info("\n📍 TOP LOCATIONS:")
        for location, count in trends_data.get('top_locations', [])[:10]:
            logger.info(f"  {location}: {count} jobs")
        
        if anomalies:
            logger.info(f"\n⚠️  ANOMALIES DETECTED ({len(anomalies)}):")
            for anomaly in anomalies[:5]:
                job = anomaly['job']
                logger.info(f"  🔥 {job['title']} at {job['company']}")
                logger.info(f"     Score: {job['score']} - {anomaly['reason']}")
        
        logger.info(f"\n{'='*80}\n")
        
    except Exception as e:
        logger.error(f"❌ Trends analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
