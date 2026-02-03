"""
Scoring Engine Module
Scores jobs and signals based on rules
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Scorer:
    """Signal scoring engine"""
    
    def __init__(self, rules_file: str = None):
        """Initialize scorer with rules"""
        if rules_file is None:
            rules_file = Path(__file__).parent.parent / "rules" / "job_rules.yaml"
        
        self.rules = self._load_rules(rules_file)
        logger.info(f"Scorer initialized with rules from {rules_file}")
    
    def _load_rules(self, rules_file: str) -> Dict[str, Any]:
        """Load scoring rules from YAML"""
        try:
            with open(rules_file, 'r') as f:
                rules = yaml.safe_load(f)
                return rules
        except FileNotFoundError:
            logger.warning(f"Rules file not found: {rules_file}, using defaults")
            return self._get_default_rules()
        except Exception as e:
            logger.error(f"Error loading rules: {e}, using defaults")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default scoring rules"""
        return {
            "keywords": ["python", "backend", "ai", "ml", "data", "engineer"],
            "min_score": 70,
            "max_age_days": 7,
            "locations": ["remote", "kenya", "africa"],
            "weights": {
                "freshness": 30,
                "keyword": 40,
                "stack": 20,
                "location": 10
            }
        }
    
    def score_job(self, job: Dict[str, Any]) -> int:
        """
        Score a job based on rules
        
        Args:
            job: Normalized job dictionary
            
        Returns:
            Score (0-100)
        """
        score = 0
        weights = self.rules.get("weights", {})
        
        # 1. Freshness Score (0-30 points)
        freshness_score = self._score_freshness(
            job.get("posted_at"),
            max_days=self.rules.get("max_age_days", 7)
        )
        score += int(freshness_score * weights.get("freshness", 30) / 30)
        
        # 2. Keyword Score (0-40 points)
        keyword_score = self._score_keywords(
            job.get("title", ""),
            self.rules.get("keywords", [])
        )
        score += int(keyword_score * weights.get("keyword", 40) / 100)
        
        # 3. Stack Score (0-20 points)
        stack_score = self._score_stack(
            job.get("stack", ""),
            self.rules.get("keywords", [])
        )
        score += int(stack_score * weights.get("stack", 20) / 100)
        
        # 4. Location Score (0-10 points)
        location_score = self._score_location(
            job.get("location", ""),
            self.rules.get("locations", [])
        )
        score += int(location_score * weights.get("location", 10) / 100)
        
        # Cap at 100
        score = min(score, 100)
        
        logger.debug(f"Job scored: {job.get('id')} = {score}")
        return score
    
    def _score_freshness(self, posted_at: datetime, max_days: int = 7) -> int:
        """Score based on how fresh the job is (0-30)"""
        if not isinstance(posted_at, datetime):
            return 0
        
        age_days = (datetime.utcnow() - posted_at).days
        
        if age_days < 0:
            age_days = 0
        
        if age_days > max_days:
            return 0
        
        # Linear decay: fresh = 30, old = 0
        return int(30 * (1 - age_days / max_days))
    
    def _score_keywords(self, text: str, keywords: List[str]) -> int:
        """Score based on keyword matches (0-100)"""
        if not text or not keywords:
            return 0
        
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)
        
        # Score: percentage of keywords matched
        score = int((matches / len(keywords)) * 100)
        return min(score, 100)
    
    def _score_stack(self, stack: str, keywords: List[str]) -> int:
        """Score based on tech stack matches (0-100)"""
        if not stack or not keywords:
            return 0
        
        stack_items = [s.strip().lower() for s in stack.split(",")]
        keywords_lower = [kw.lower() for kw in keywords]
        
        matches = sum(1 for item in stack_items if any(kw in item for kw in keywords_lower))
        
        if not stack_items:
            return 0
        
        # Score: percentage of stack items that match keywords
        score = int((matches / len(stack_items)) * 100)
        return min(score, 100)
    
    def _score_location(self, location: str, preferred_locations: List[str]) -> int:
        """Score based on location preference (0-100)"""
        if not location or not preferred_locations:
            return 0
        
        location_lower = location.lower()
        
        for pref_loc in preferred_locations:
            if pref_loc.lower() in location_lower:
                return 100
        
        return 0


# Global scorer instance
_scorer_instance = None


def get_scorer() -> Scorer:
    """Get or create scorer singleton"""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = Scorer()
    return _scorer_instance


def score_job(job: Dict[str, Any]) -> int:
    """Score a job using global scorer"""
    scorer = get_scorer()
    return scorer.score_job(job)
