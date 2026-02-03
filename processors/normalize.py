"""
Data Normalization Module
Standardizes raw data into consistent format
"""

from datetime import datetime
from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)


def normalize_job(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize raw job data into standard format
    
    Args:
        raw_data: Raw job data from collector
        
    Returns:
        Normalized job dictionary
    """
    try:
        normalized = {
            "id": _normalize_id(raw_data),
            "title": _normalize_text(raw_data.get("title", "")),
            "company": _normalize_text(raw_data.get("company", "Unknown")),
            "location": _normalize_location(raw_data.get("location", "")),
            "stack": _normalize_stack(raw_data.get("stack", [])),
            "url": _normalize_url(raw_data.get("url", "")),
            "posted_at": _normalize_date(raw_data.get("posted_at")),
            "source": raw_data.get("source", "unknown"),
            "raw_data": str(raw_data)
        }
        
        logger.debug(f"Normalized job: {normalized['id']}")
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing job data: {e}")
        raise


def _normalize_id(raw_data: Dict[str, Any]) -> str:
    """Generate or normalize job ID"""
    if "id" in raw_data and raw_data["id"]:
        return str(raw_data["id"])
    
    # Generate ID from title + company + url hash
    import hashlib
    unique_str = f"{raw_data.get('title', '')}{raw_data.get('company', '')}{raw_data.get('url', '')}"
    return hashlib.md5(unique_str.encode()).hexdigest()[:16]


def _normalize_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\-\.\,\(\)]', '', text)
    
    return text.strip()


def _normalize_location(location: str) -> str:
    """Normalize location string"""
    if not location:
        return "Unknown"
    
    location = _normalize_text(location)
    
    # Common mappings
    location_map = {
        "wfh": "remote",
        "work from home": "remote",
        "anywhere": "remote",
        "global": "remote"
    }
    
    location_lower = location.lower()
    for key, value in location_map.items():
        if key in location_lower:
            return value.title()
    
    return location.title()


def _normalize_stack(stack: Any) -> str:
    """Normalize tech stack to comma-separated string"""
    if isinstance(stack, str):
        # Already a string, just clean it
        stack = stack.lower().strip()
        return ",".join([s.strip() for s in stack.split(",")])
    
    if isinstance(stack, list):
        # List of technologies
        return ",".join([str(s).lower().strip() for s in stack if s])
    
    return ""


def _normalize_url(url: str) -> str:
    """Normalize URL"""
    if not url:
        return ""
    
    url = url.strip()
    
    # Add https if no protocol
    if url and not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    return url


def _normalize_date(date_value: Any) -> datetime:
    """Normalize date to datetime object"""
    if isinstance(date_value, datetime):
        return date_value
    
    if isinstance(date_value, str):
        # Try ISO format with timezone first (most common)
        try:
            # Handle ISO 8601 format with timezone (e.g., 2026-02-02T07:00:28+00:00)
            from dateutil import parser
            return parser.isoparse(date_value)
        except:
            pass
        
        # Try various date formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_value, fmt)
            except ValueError:
                continue
    
    # Try integer timestamp
    if isinstance(date_value, (int, float)):
        try:
            return datetime.fromtimestamp(date_value)
        except:
            pass
    
    # Default to now if can't parse
    logger.warning(f"Could not parse date: {date_value}, using current time")
    return datetime.now()


def normalize_signal(raw_data: Dict[str, Any], signal_type: str) -> Dict[str, Any]:
    """
    Normalize raw signal data
    
    Args:
        raw_data: Raw signal data
        signal_type: Type of signal (trend, anomaly, spike)
        
    Returns:
        Normalized signal dictionary
    """
    try:
        import hashlib
        unique_str = f"{signal_type}{raw_data.get('title', '')}{datetime.utcnow().isoformat()}"
        signal_id = hashlib.md5(unique_str.encode()).hexdigest()[:16]
        
        normalized = {
            "id": signal_id,
            "signal_type": signal_type,
            "title": _normalize_text(raw_data.get("title", "")),
            "description": _normalize_text(raw_data.get("description", "")),
            "data": str(raw_data.get("data", {})),
            "source": raw_data.get("source", "unknown"),
            "detected_at": datetime.utcnow()
        }
        
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing signal data: {e}")
        raise
