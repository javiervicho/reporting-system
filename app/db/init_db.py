import logging
from sqlalchemy import text

from app.db.session import engine
from app.db.base import Base

logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Initialize the database with required extensions and tables.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize PostGIS and pgvector extensions
    with engine.begin() as conn:
        # Check if PostGIS extension exists
        postgis_result = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")).scalar()
        if not postgis_result:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
                logger.info("PostGIS extension created successfully")
            except Exception as e:
                logger.error(f"Error creating PostGIS extension: {e}")
                raise
        
        # Check if pgvector extension exists
        pgvector_result = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).scalar()
        if not pgvector_result:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("pgvector extension created successfully")
            except Exception as e:
                logger.error(f"Error creating pgvector extension: {e}")
                raise
    
    logger.info("Database initialized successfully") 