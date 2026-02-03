"""
We Work Remotely Jobs Collector
Scrapes job postings from We Work Remotely
"""

from datetime import datetime
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import logging
import hashlib

logger = logging.getLogger(__name__)


class WeWorkRemotelyCollector:
    """Collect jobs from We Work Remotely"""
    
    def __init__(self):
        self.name = "weworkremotely"
        self.base_url = "https://weworkremotely.com/remote-jobs.rss"
        self.headers = {
            "User-Agent": "SignalForge/1.0 (Job Aggregator)"
        }
        logger.info(f"Initialized {self.name} collector")
    
    def collect(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        Collect jobs from We Work Remotely RSS feed
        
        Returns:
            List of raw job data
        """
        jobs = []
        
        try:
            logger.info(f"Collecting jobs from {self.name}")
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                
                logger.info(f"Retrieved {len(items)} jobs from {self.name}")
                
                for item in items:
                    parsed = self._parse_job(item)
                    if parsed:
                        jobs.append(parsed)
            else:
                logger.error(f"{self.name} returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error collecting from {self.name}: {e}")
        
        return jobs
    
    def _parse_job(self, item) -> Dict[str, Any]:
        """Parse RSS item into standard format"""
        try:
            title = item.find('title').text if item.find('title') else ""
            link = item.find('link').text if item.find('link') else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') else ""
            
            # Parse company from title (format: "Company: Job Title")
            parts = title.split(":", 1)
            company = parts[0].strip() if len(parts) > 1 else "Unknown"
            job_title = parts[1].strip() if len(parts) > 1 else title
            
            # Parse date
            if pub_date:
                try:
                    posted_at = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                except:
                    posted_at = datetime.now()
            else:
                posted_at = datetime.now()
            
            # Generate ID from URL
            job_id = hashlib.md5(link.encode()).hexdigest()[:16]
            
            return {
                "id": job_id,
                "title": job_title,
                "company": company,
                "location": "Remote",
                "url": link,
                "posted_at": posted_at.isoformat(),
                "stack": "",
                "description": "",
                "source": self.name
            }
        except Exception as e:
            logger.error(f"Error parsing job from {self.name}: {e}")
            return None
