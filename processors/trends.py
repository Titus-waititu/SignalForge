"""
Trend Detector Module
Tracks emerging tech trends and patterns in job postings
"""

from typing import Dict, List, Any
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TrendDetector:
    """Detect emerging trends from job data"""
    
    def __init__(self):
        self.tech_keywords = [
            "ai", "ml", "machine learning", "artificial intelligence",
            "python", "javascript", "typescript", "go", "rust",
            "react", "vue", "angular", "nextjs",
            "aws", "azure", "gcp", "kubernetes", "docker",
            "blockchain", "web3", "crypto",
            "data science", "data engineering", "devops"
        ]
        logger.info("TrendDetector initialized")
    
    def analyze_trends(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze jobs for emerging trends
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            # Stack frequency
            stack_counter = Counter()
            keyword_counter = Counter()
            company_counter = Counter()
            location_counter = Counter()
            
            # Time-based analysis
            recent_cutoff = datetime.now() - timedelta(days=3)
            recent_jobs = []
            
            for job in jobs:
                # Count technologies
                stack = job.get("stack", "")
                if stack:
                    techs = [t.strip().lower() for t in stack.split(",")]
                    stack_counter.update(techs)
                
                # Count keywords in title
                title = job.get("title", "").lower()
                for keyword in self.tech_keywords:
                    if keyword in title:
                        keyword_counter[keyword] += 1
                
                # Count companies and locations
                company_counter[job.get("company", "Unknown")] += 1
                location_counter[job.get("location", "Unknown")] += 1
                
                # Track recent jobs
                posted_at = job.get("posted_at")
                if posted_at:
                    try:
                        if isinstance(posted_at, str):
                            posted_date = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                        else:
                            posted_date = posted_at
                        
                        if posted_date >= recent_cutoff:
                            recent_jobs.append(job)
                    except:
                        pass
            
            trends = {
                "top_technologies": stack_counter.most_common(10),
                "trending_keywords": keyword_counter.most_common(10),
                "top_hiring_companies": company_counter.most_common(10),
                "top_locations": location_counter.most_common(10),
                "recent_job_count": len(recent_jobs),
                "total_jobs_analyzed": len(jobs),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Trend analysis complete: {len(jobs)} jobs analyzed")
            return trends
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {}
    
    def detect_spikes(self, current_count: int, historical_avg: float, threshold: float = 1.5) -> bool:
        """
        Detect sudden spikes in job postings
        
        Args:
            current_count: Current number of jobs
            historical_avg: Historical average
            threshold: Multiplier for spike detection (default 1.5x)
            
        Returns:
            True if spike detected
        """
        if historical_avg == 0:
            return False
        
        ratio = current_count / historical_avg
        is_spike = ratio >= threshold
        
        if is_spike:
            logger.warning(f"SPIKE DETECTED: Current={current_count}, Avg={historical_avg:.1f}, Ratio={ratio:.2f}x")
        
        return is_spike
    
    def detect_anomalies(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalous job postings (unusually high score, rare stack, etc.)
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of anomalous jobs
        """
        anomalies = []
        
        try:
            if not jobs:
                return anomalies
            
            # Calculate score statistics
            scores = [job.get("score", 0) for job in jobs]
            avg_score = sum(scores) / len(scores)
            
            # Detect high-value anomalies (2x average score)
            for job in jobs:
                score = job.get("score", 0)
                if score >= avg_score * 2 and score > 60:
                    anomalies.append({
                        "type": "high_value",
                        "job": job,
                        "reason": f"Score {score} is {score/avg_score:.1f}x average",
                        "detected_at": datetime.now().isoformat()
                    })
            
            logger.info(f"Detected {len(anomalies)} anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
