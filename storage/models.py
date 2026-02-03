"""
Database Models for SignalForge
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Job(Base):
    """Job Signal Model"""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=True)  # Job description
    stack = Column(Text, nullable=True)  # JSON string of tech stack
    url = Column(String, nullable=False)
    posted_at = Column(DateTime, nullable=False)
    score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    raw_data = Column(Text, nullable=True)  # Original data for reference
    source = Column(String, nullable=True)  # Where the job was collected from
    alerted = Column(Integer, default=0)  # 0 = not alerted, 1 = alerted
    
    def __repr__(self):
        return f"<Job(id='{self.id}', title='{self.title}', company='{self.company}', score={self.score})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "stack": self.stack.split(",") if self.stack else [],
            "url": self.url,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "score": self.score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source": self.source,
            "alerted": bool(self.alerted)
        }


class Signal(Base):
    """Generic Signal Model for trends and anomalies"""
    __tablename__ = "signals"
    
    id = Column(String, primary_key=True)
    signal_type = Column(String, nullable=False)  # 'trend', 'anomaly', 'spike'
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    data = Column(Text, nullable=True)  # JSON data
    score = Column(Integer, default=0)
    detected_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String, nullable=True)
    alerted = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Signal(id='{self.id}', type='{self.signal_type}', score={self.score})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "signal_type": self.signal_type,
            "title": self.title,
            "description": self.description,
            "score": self.score,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "source": self.source,
            "alerted": bool(self.alerted)
        }
