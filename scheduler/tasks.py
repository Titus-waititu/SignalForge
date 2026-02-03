"""
Task Scheduler Module
Orchestrates data collection, processing, and alerting
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from collectors.jobs.remote_ok import RemoteOKCollector, MockJobCollector
from processors.normalize import normalize_job
from processors.scoring import score_job
from storage.db import get_db
from storage.models import Job
from alerts.telegram import TelegramAlerter
from config import config

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Main task orchestrator"""
    
    def __init__(self, use_mock: bool = False, use_background: bool = False):
        """
        Initialize task scheduler
        
        Args:
            use_mock: Use mock collector for testing
            use_background: Use background scheduler instead of async (for threading)
        """
        if use_background:
            self.scheduler = BackgroundScheduler()
        else:
            self.scheduler = AsyncIOScheduler()
        
        self.use_background = use_background
        self.db = get_db()
        self.alerter = TelegramAlerter()
        
        # Initialize collectors
        if use_mock:
            self.collectors = [MockJobCollector()]
        else:
            self.collectors = [
                RemoteOKCollector(),
            ]
            
            # Try importing LinkedIn collector
            try:
                from collectors.jobs.linkedin_scraper import LinkedInJobsCollector
                self.collectors.append(LinkedInJobsCollector())
            except Exception as e:
                logger.warning(f"Could not load LinkedIn collector: {e}")
        
        logger.info(f"TaskScheduler initialized with {len(self.collectors)} collectors")
    
    def start(self):
        """Start the scheduler"""
        
        if self.use_background:
            # For background scheduler, wrap async function
            def sync_collect():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.collect_and_process_jobs())
                finally:
                    loop.close()
            
            self.scheduler.add_job(
                sync_collect,
                trigger=IntervalTrigger(minutes=config.COLLECTOR_INTERVAL_MINUTES),
                id="job_collection",
                name="Collect and process jobs",
                replace_existing=True
            )
            
            # Run immediately on start
            self.scheduler.add_job(
                sync_collect,
                id="job_collection_startup",
                name="Initial job collection"
            )
        else:
            # For async scheduler
            self.scheduler.add_job(
                self.collect_and_process_jobs,
                trigger=IntervalTrigger(minutes=config.COLLECTOR_INTERVAL_MINUTES),
                id="job_collection",
                name="Collect and process jobs",
                replace_existing=True
            )
            
            # Run immediately on start
            self.scheduler.add_job(
                self.collect_and_process_jobs,
                id="job_collection_startup",
                name="Initial job collection"
            )
        
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def collect_and_process_jobs(self):
        """Main pipeline: collect → normalize → score → store → alert → trends"""
        logger.info("=== Starting job collection pipeline ===")
        
        try:
            # Step 1: Collect jobs from all sources
            all_jobs = []
            for collector in self.collectors:
                try:
                    jobs = collector.collect()
                    all_jobs.extend(jobs)
                    logger.info(f"Collected {len(jobs)} jobs from {collector.name}")
                except Exception as e:
                    logger.error(f"Error in collector {collector.name}: {e}")
            
            logger.info(f"Total jobs collected: {len(all_jobs)}")
            
            if not all_jobs:
                logger.warning("No jobs collected")
                return
            
            # Step 2 & 3: Normalize and score jobs
            processed_jobs = []
            for raw_job in all_jobs:
                try:
                    # Normalize
                    normalized = normalize_job(raw_job)
                    
                    # Score
                    normalized["score"] = score_job(normalized)
                    
                    processed_jobs.append(normalized)
                    
                except Exception as e:
                    logger.error(f"Error processing job: {e}")
            
            logger.info(f"Processed {len(processed_jobs)} jobs")
            
            # Step 3.5: Trend Analysis
            try:
                from processors.trends import TrendDetector
                trend_detector = TrendDetector()
                trends = trend_detector.analyze_trends(processed_jobs)
                anomalies = trend_detector.detect_anomalies(processed_jobs)
                
                if trends:
                    logger.info(f"📈 Top trending tech: {trends.get('trending_keywords', [])[:3]}")
                
                if anomalies:
                    logger.warning(f"⚠️ Detected {len(anomalies)} anomalies")
                    for anomaly in anomalies[:3]:  # Log top 3
                        job = anomaly.get('job', {})
                        logger.warning(f"  - {job.get('title')} at {job.get('company')} (Score: {job.get('score')})")
            except Exception as e:
                logger.error(f"Error in trend analysis: {e}")
            
            # Step 4: Store in database
            high_score_jobs = []
            with self.db.get_session() as session:
                for job_data in processed_jobs:
                    try:
                        # Check if job already exists
                        existing = session.query(Job).filter(Job.id == job_data["id"]).first()
                        
                        if existing:
                            # Update score if changed
                            if existing.score != job_data["score"]:
                                existing.score = job_data["score"]
                                logger.debug(f"Updated job {job_data['id']} score to {job_data['score']}")
                        else:
                            # Create new job
                            job = Job(
                                id=job_data["id"],
                                title=job_data["title"],
                                company=job_data["company"],
                                location=job_data["location"],
                                stack=job_data["stack"],
                                url=job_data["url"],
                                posted_at=job_data["posted_at"],
                                score=job_data["score"],
                                source=job_data.get("source"),
                                raw_data=job_data.get("raw_data")
                            )
                            session.add(job)
                            logger.debug(f"Saved new job {job_data['id']} with score {job_data['score']}")
                            
                            # Check if alert threshold is met
                            if job_data["score"] >= config.ALERT_THRESHOLD:
                                high_score_jobs.append(job_data)
                    
                    except Exception as e:
                        logger.error(f"Error saving job to database: {e}")
                
                session.commit()
            
            logger.info(f"Saved {len(processed_jobs)} jobs to database")
            
            # Step 5: Send alerts for high-scoring jobs
            if high_score_jobs:
                logger.info(f"Found {len(high_score_jobs)} jobs above threshold ({config.ALERT_THRESHOLD})")
                sent_count = await self.alerter.send_bulk_alerts(high_score_jobs)
                
                # Mark jobs as alerted
                with self.db.get_session() as session:
                    for job_data in high_score_jobs:
                        job = session.query(Job).filter(Job.id == job_data["id"]).first()
                        if job:
                            job.alerted = 1
                    session.commit()
                
                logger.info(f"Sent {sent_count} alerts")
            else:
                logger.info("No jobs above alert threshold")
            
            logger.info("=== Job collection pipeline completed ===")
            
        except Exception as e:
            logger.error(f"Error in job collection pipeline: {e}", exc_info=True)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            with self.db.get_session() as session:
                total_jobs = session.query(Job).count()
                high_score_jobs = session.query(Job).filter(Job.score >= config.ALERT_THRESHOLD).count()
                alerted_jobs = session.query(Job).filter(Job.alerted == 1).count()
                
                return {
                    "total_jobs": total_jobs,
                    "high_score_jobs": high_score_jobs,
                    "alerted_jobs": alerted_jobs,
                    "alert_threshold": config.ALERT_THRESHOLD,
                    "collectors": len(self.collectors),
                    "status": "running" if self.scheduler.running else "stopped"
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


def run_scheduler(use_mock: bool = False):
    """Run the scheduler in async mode"""
    scheduler = TaskScheduler(use_mock=use_mock)
    scheduler.start()
    
    logger.info("SignalForge scheduler is running. Press Ctrl+C to stop.")
    
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Keep running
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.stop()


def start_scheduler(use_mock: bool = False):
    """Start the scheduler (blocking call) - for threaded use"""
    scheduler = TaskScheduler(use_mock=use_mock, use_background=True)
    scheduler.start()
    
    logger.info("SignalForge background scheduler is running.")
    
    # Keep thread alive
    try:
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down background scheduler...")
        scheduler.stop()


def run_collectors():
    """Run collectors once (synchronous)"""
    logger.info("Running collectors once...")
    scheduler = TaskScheduler()
    
    # Run collection in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(scheduler.collect_and_process_jobs())
    finally:
        loop.close()
    
    logger.info("Collection completed")
