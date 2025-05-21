import pytest
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import numpy as np

from app.schemas.incident import IncidentCreate
from app.services.incident_service import create_incident, generate_embedding, get_incident

# Mock for the embedding model
@pytest.fixture
def mock_embedding():
    # Return a fixed embedding vector for testing
    return [0.1] * 384  # 384 dimensions for the default model

@pytest.fixture
def mock_db():
    # Create a mock database session
    db = MagicMock(spec=Session)
    return db

@patch('app.services.incident_service.embedding_model')
def test_generate_embedding(mock_model):
    # Set up the mock to return a fixed numpy array
    fixed_embedding = np.array([0.1] * 384)  # 384 dimensions for the default model
    mock_model.encode.return_value = fixed_embedding
    
    # Test the function
    text = "Test incident description"
    result = generate_embedding(text)
    
    # Verify the model was called correctly
    mock_model.encode.assert_called_once_with(text)
    
    # Verify the result is converted to a list
    assert isinstance(result, list)
    assert len(result) == 384
    assert result == fixed_embedding.tolist()

@patch('app.services.incident_service.generate_embedding')
def test_create_incident(mock_gen_embedding, mock_db):
    # Set up the mock to return a fixed embedding
    mock_gen_embedding.return_value = [0.1] * 384
    
    # Create a test incident
    incident_data = IncidentCreate(
        title="Test Incident",
        description="This is a test incident description",
        incident_type="Pollution",
        severity=3,
        longitude=10.0,
        latitude=20.0
    )
    
    # Call the service function
    result = create_incident(mock_db, incident_data)
    
    # Verify the database session methods were called
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    
    # Verify the embedding was generated
    mock_gen_embedding.assert_called_once_with(incident_data.description) 