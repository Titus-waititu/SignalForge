"""
RemoteOK Jobs Collector
Collects remote job postings from RemoteOK
"""

from datetime import datetime
from typing import List, Dict, Any
import requests
import time
import logging

logger = logging.getLogger(__name__)


class RemoteOKCollector:
    """Collect jobs from RemoteOK API"""
    
    def __init__(self):
        self.name = "remoteok"
        self.base_url = "https://remoteok.com/api"
        self.headers = {
            "User-Agent": "SignalForge/1.0 (Job Aggregator)"
        }
        logger.info(f"Initialized {self.name} collector")
    
    def collect(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        Collect jobs from RemoteOK
        
        Args:
            keywords: List of keywords to filter (optional)
            
        Returns:
            List of raw job data
        """
        jobs = []
        
        try:
            logger.info(f"Collecting jobs from {self.name}")
            
            # RemoteOK API returns all jobs
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # First item is metadata, skip it
                jobs_data = data[1:] if len(data) > 1 else []
                
                logger.info(f"Retrieved {len(jobs_data)} jobs from {self.name}")
                
                # Parse each job
                for job_raw in jobs_data:
                    parsed = self._parse_job(job_raw)
                    if parsed:
                        jobs.append(parsed)
                
                # Rate limiting - be nice to the API
                time.sleep(1)
                
            else:
                logger.error(f"{self.name} API returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error collecting from {self.name}: {e}")
        except Exception as e:
            logger.error(f"Error collecting from {self.name}: {e}")
        
        return jobs
    
    def _parse_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw job data into standard format"""
        try:
            # Extract tech stack
            tags = raw_job.get("tags", [])
            stack = ",".join(tags) if tags else ""
            
            # Parse date
            posted_date = raw_job.get("date")
            if posted_date:
                try:
                    # Try parsing as timestamp first
                    if isinstance(posted_date, (int, float)):
                        posted_at = datetime.fromtimestamp(posted_date)
                    elif isinstance(posted_date, str):
                        # Try ISO format
                        try:
                            posted_at = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                        except:
                            # Try as timestamp string
                            posted_at = datetime.fromtimestamp(int(posted_date))
                    else:
                        posted_at = datetime.now()
                except:
                    posted_at = datetime.now()
            else:
                posted_at = datetime.now()
            
            return {
                "id": str(raw_job.get("id", "")),
                "title": raw_job.get("position", ""),
                "company": raw_job.get("company", ""),
                "location": raw_job.get("location", "Remote"),
                "url": raw_job.get("url", ""),
                "posted_at": posted_at.isoformat(),
                "stack": stack,
                "description": raw_job.get("description", ""),
                "source": self.name
            }
        except Exception as e:
            logger.error(f"Error parsing job from {self.name}: {e}")
            return {}


class MockJobCollector:
    """Mock collector for testing purposes"""
    
    def __init__(self):
        self.name = "mock"
        logger.info(f"Initialized {self.name} collector")
    
    def collect(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Return mock job data for testing"""
        return [
            {
                "id": "mock-001",
                "title": "Senior Python Backend Engineer",
                "company": "TechCorp",
                "location": "Remote",
                "url": "https://example.com/job/001",
                "posted_at": datetime.utcnow().isoformat(),
                "stack": "python,django,postgresql,docker",
                "description": "We're looking for a senior backend engineer with Python expertise",
                "source": self.name
            },
            {
                "id": "mock-002",
                "title": "AI/ML Engineer",
                "company": "DataCo",
                "location": "Kenya",
                "url": "https://example.com/job/002",
                "posted_at": datetime.utcnow().isoformat(),
                "stack": "python,tensorflow,pytorch,aws",
                "description": "Join our AI team building cutting-edge ML models",
                "source": self.name
            },
            {
                "id": "mock-003",
                "title": "Full Stack Developer",
                "company": "StartupXYZ",
                "location": "Nairobi",
                "url": "https://example.com/job/003",
                "posted_at": datetime.utcnow().isoformat(),
                "stack": "javascript,react,nodejs,mongodb",
                "description": "Build modern web applications with our team",
                "source": self.name
            }
        ]
