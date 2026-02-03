"""
Database Connection and Session Management
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import config
from .models import Base
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database Manager"""
    
    def __init__(self, db_url: str = None):
        """Initialize database connection"""
        self.db_url = db_url or config.DB_URL
        self.engine = create_engine(
            self.db_url,
            echo=False,
            connect_args={"check_same_thread": False} if "sqlite" in self.db_url else {}
        )
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        logger.info(f"Database initialized: {self.db_url}")
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("Database tables dropped")
    
    @contextmanager
    def get_session(self):
        """Get database session with context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_direct(self) -> Session:
        """Get session directly (remember to close it!)"""
        return self.SessionLocal()


# Global database instance
_db_instance = None


def get_db() -> Database:
    """Get or create database singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def init_db():
    """Initialize database and create tables"""
    db = get_db()
    db.create_tables()
    return db
