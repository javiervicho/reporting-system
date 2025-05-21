import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.db.session import get_db
from app.services.incident_service import create_incident

client = TestClient(app)

# Override the get_db dependency to use a testing database
@pytest.fixture
def mock_db():
    # Create a mock database session
    db = MagicMock()
    return db

@pytest.fixture
def client_with_db(mock_db):
    """
    Test client that uses a mocked database session.
    """
    app.dependency_overrides[get_db] = lambda: mock_db
    yield client
    app.dependency_overrides = {}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Environmental Incident Reporting API" in response.json()["message"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('app.api.v1.endpoints.incidents.create_incident')
def test_create_incident_api(mock_create_incident, client_with_db):
    # Set up the mock to return a sample incident
    mock_incident = MagicMock()
    mock_incident.id = 1
    mock_incident.title = "Test Incident"
    mock_incident.description = "This is a test incident"
    mock_incident.incident_type = "Pollution"
    mock_incident.severity = 3
    mock_incident.longitude = 10.0
    mock_incident.latitude = 20.0
    mock_incident.status = "reported"
    
    mock_create_incident.return_value = mock_incident
    
    # Test data
    test_data = {
        "title": "Test Incident",
        "description": "This is a test incident",
        "incident_type": "Pollution",
        "severity": 3,
        "longitude": 10.0,
        "latitude": 20.0
    }
    
    # Make the request
    response = client_with_db.post("/api/v1/incidents/", json=test_data)
    
    # Verify the response
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Incident"
    assert data["incident_type"] == "Pollution" 