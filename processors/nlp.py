"""
NLP Processing Module
Text analysis and keyword extraction
"""

from typing import List, Dict, Set
import re
import logging

logger = logging.getLogger(__name__)


# Common tech keywords for extraction
TECH_KEYWORDS = {
    "languages": ["python", "javascript", "java", "c++", "go", "rust", "ruby", "php", "typescript", "swift", "kotlin"],
    "frameworks": ["django", "flask", "fastapi", "react", "vue", "angular", "spring", "express", "nextjs", "rails"],
    "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible"],
    "ml_ai": ["tensorflow", "pytorch", "keras", "scikit-learn", "machine learning", "deep learning", "nlp", "computer vision"],
    "tools": ["git", "jenkins", "circleci", "github actions", "jira", "confluence"]
}


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract relevant keywords from text
    
    Args:
        text: Input text
        min_length: Minimum keyword length
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    text_lower = text.lower()
    keywords = set()
    
    # Extract tech keywords
    for category, terms in TECH_KEYWORDS.items():
        for term in terms:
            if term in text_lower:
                keywords.add(term)
    
    # Extract capitalized words (likely important terms)
    capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
    keywords.update([w.lower() for w in capitalized if len(w) >= min_length])
    
    # Extract common job-related terms
    job_terms = ["senior", "junior", "lead", "principal", "staff", "full-time", "part-time", "remote", "hybrid"]
    for term in job_terms:
        if term in text_lower:
            keywords.add(term)
    
    logger.debug(f"Extracted {len(keywords)} keywords")
    return sorted(list(keywords))


def extract_tech_stack(text: str) -> List[str]:
    """
    Extract technology stack from job description
    
    Args:
        text: Job description or title
        
    Returns:
        List of technologies
    """
    if not text:
        return []
    
    text_lower = text.lower()
    stack = set()
    
    # Search all tech categories
    for category, terms in TECH_KEYWORDS.items():
        for term in terms:
            if term in text_lower:
                stack.add(term)
    
    return sorted(list(stack))


def analyze_sentiment(text: str) -> str:
    """
    Simple sentiment analysis
    
    Args:
        text: Input text
        
    Returns:
        Sentiment: 'positive', 'negative', or 'neutral'
    """
    if not text:
        return "neutral"
    
    text_lower = text.lower()
    
    positive_words = [
        "great", "excellent", "amazing", "fantastic", "competitive", "flexible",
        "innovative", "exciting", "growth", "opportunity", "benefits"
    ]
    
    negative_words = [
        "demanding", "stressful", "difficult", "challenging", "unpaid",
        "required", "must have", "mandatory"
    ]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using simple word overlap
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    if not text1 or not text2:
        return 0.0
    
    # Tokenize and clean
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    # Calculate Jaccard similarity
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    similarity = len(intersection) / len(union)
    return round(similarity, 3)


def extract_experience_level(text: str) -> str:
    """
    Extract experience level from job text
    
    Args:
        text: Job title or description
        
    Returns:
        Experience level: 'junior', 'mid', 'senior', or 'unknown'
    """
    if not text:
        return "unknown"
    
    text_lower = text.lower()
    
    if any(term in text_lower for term in ["junior", "entry", "graduate", "intern"]):
        return "junior"
    elif any(term in text_lower for term in ["senior", "lead", "principal", "staff", "expert"]):
        return "senior"
    elif any(term in text_lower for term in ["mid", "intermediate", "experienced"]):
        return "mid"
    
    return "unknown"


def detect_remote_work(text: str) -> bool:
    """
    Detect if job is remote-friendly
    
    Args:
        text: Job description or location
        
    Returns:
        True if remote work is mentioned
    """
    if not text:
        return False
    
    text_lower = text.lower()
    remote_keywords = [
        "remote", "work from home", "wfh", "distributed", "anywhere",
        "virtual", "home office", "location independent"
    ]
    
    return any(keyword in text_lower for keyword in remote_keywords)
