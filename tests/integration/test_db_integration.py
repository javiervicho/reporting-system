import pytest
import os
import sqlalchemy as sa
from sqlalchemy import text
from geoalchemy2.functions import ST_AsText
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.session import engine, Base
from app.models.incident import Incident

# These tests require a real PostgreSQL database with PostGIS and pgvector extensions

@pytest.fixture(scope="module")
def setup_database():
    """
    Setup test database with required extensions and tables.
    This requires a running PostgreSQL instance with PostGIS and pgvector.
    """
    # Check if we're in a test environment
    if "TEST_DATABASE_URI" not in os.environ:
        pytest.skip(
            "Skipping integration tests. Set TEST_DATABASE_URI environment variable to run."
        )
    
    # Create tables and extensions
    with engine.begin() as conn:
        # Create PostGIS extension if it doesn't exist
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        
        # Create pgvector extension if it doesn't exist
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Clean up tables after tests
    Base.metadata.drop_all(engine)

def test_postgis_point_storage(setup_database):
    """
    Test that PostGIS point geometries can be stored and retrieved correctly.
    """
    with engine.begin() as conn:
        # Create a test incident with a specific location
        stmt = sa.insert(Incident).values(
            title="Test GIS Incident",
            description="Testing PostGIS functionality",
            incident_type="Test",
            severity=1,
            longitude=10.123,
            latitude=20.456,
            location=text("ST_SetSRID(ST_MakePoint(10.123, 20.456), 4326)"),
            description_embedding=[0.1] * 384
        ).returning(Incident.id)
        
        result = conn.execute(stmt)
        incident_id = result.scalar_one()
        
        # Retrieve the incident and verify the location
        stmt = sa.select(ST_AsText(Incident.location)).where(Incident.id == incident_id)
        result = conn.execute(stmt)
        point_wkt = result.scalar_one()
        
        # Point should be in WKT format like 'POINT(10.123 20.456)'
        assert "POINT(10.123 20.456)" in point_wkt

def test_pgvector_storage(setup_database):
    """
    Test that pgvector embeddings can be stored and retrieved correctly.
    """
    test_embedding = [0.1] * 384  # 384 dimensions
    
    with engine.begin() as conn:
        # Create a test incident with an embedding
        stmt = sa.insert(Incident).values(
            title="Test Vector Incident",
            description="Testing pgvector functionality",
            incident_type="Test",
            severity=1,
            longitude=0.0,
            latitude=0.0,
            location=text("ST_SetSRID(ST_MakePoint(0.0, 0.0), 4326)"),
            description_embedding=test_embedding
        ).returning(Incident.id)
        
        result = conn.execute(stmt)
        incident_id = result.scalar_one()
        
        # Retrieve the incident and verify the embedding
        stmt = sa.select(Incident.description_embedding).where(Incident.id == incident_id)
        result = conn.execute(stmt)
        retrieved_embedding = result.scalar_one()
        
        # Check embedding dimensions and values
        assert len(retrieved_embedding) == 384
        assert all(abs(a - b) < 1e-6 for a, b in zip(test_embedding, retrieved_embedding))

def test_vector_similarity_search(setup_database):
    """
    Test vector similarity search using pgvector.
    """
    # Create multiple incidents with different embeddings
    embeddings = [
        [0.1] * 384,  # Incident 1
        [0.2] * 384,  # Incident 2
        [0.3] * 384,  # Incident 3
    ]
    
    with engine.begin() as conn:
        # Insert test incidents
        for i, emb in enumerate(embeddings):
            stmt = sa.insert(Incident).values(
                title=f"Vector Test {i+1}",
                description=f"Testing vector similarity search {i+1}",
                incident_type="Test",
                severity=1,
                longitude=float(i),
                latitude=float(i),
                location=text(f"ST_SetSRID(ST_MakePoint({float(i)}, {float(i)}), 4326)"),
                description_embedding=emb
            )
            conn.execute(stmt)
        
        # Query for most similar incidents to the first embedding
        query_embedding = [0.11] * 384  # Slightly different from first embedding
        
        stmt = sa.select(Incident.id, Incident.title).order_by(
            text("description_embedding <-> :embedding").bindparams(embedding=query_embedding)
        ).limit(2)
        
        result = conn.execute(stmt)
        similar_incidents = result.fetchall()
        
        # First result should be the most similar one (the first incident)
        assert len(similar_incidents) == 2
        assert similar_incidents[0].title == "Vector Test 1" 