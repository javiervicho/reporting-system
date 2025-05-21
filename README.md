# Environmental Incident Reporting Platform

A FastAPI-based API for citizens to report environmental incidents like pollution, illegal dumping, etc. The platform provides geotagged incident reports and search capabilities based on proximity, type, or textual similarity.

## Features

- Geotagged incident reporting
- Search for incidents by proximity (spatial search)
- Search within geographical areas (geofencing)
- Textual similarity search for incident descriptions
- Auto-tagging of incidents

## Technology Stack

- **FastAPI**: Modern, fast API framework
- **PostgreSQL**: Database with PostGIS and pgvector extensions
- **SQLAlchemy**: ORM for database interactions
- **GeoAlchemy2**: For geospatial data handling
- **pgvector**: For vector similarity search
- **Sentence Transformers**: For text embedding generation

## Requirements

- Python 3.8+
- PostgreSQL 13+ with PostGIS and pgvector extensions
- Docker (optional, for containerized deployment)

## Setup

### Environment Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/environmental-incident-reporting.git
   cd environmental-incident-reporting
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the sample:
   ```
   # Application Settings
   PROJECT_NAME=Environmental Incident Reporting API

   # Database Settings
   POSTGRES_SERVER=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=incident_reporting
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password

   # For testing
   TEST_DATABASE_URI=postgresql://postgres:your_password@localhost:5432/incident_reporting_test

   # Embedding Model
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```

### Database Setup

1. Create a PostgreSQL database:
   ```
   createdb incident_reporting
   ```

2. Install the required PostgreSQL extensions:
   ```sql
   CREATE EXTENSION postgis;
   CREATE EXTENSION vector;
   ```

3. The application will create the necessary tables on startup.

## Running the Application

1. Start the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

2. Access the API documentation at:
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## API Endpoints

- `POST /api/v1/incidents/`: Create a new incident report
- `GET /api/v1/incidents/`: List incidents (with optional filtering)
- `GET /api/v1/incidents/{incident_id}`: Get a specific incident
- `PUT /api/v1/incidents/{incident_id}`: Update an incident
- `DELETE /api/v1/incidents/{incident_id}`: Delete an incident

### Specialized Search Endpoints

- `GET /api/v1/incidents/search/proximity/`: Search by proximity to a point
- `GET /api/v1/incidents/search/area/`: Search within a geographical area
- `GET /api/v1/incidents/search/similar/`: Search for incidents with similar descriptions

## Testing

Run tests using pytest:

```
pytest
```

For integration tests that require a database:

```
export TEST_DATABASE_URI=postgresql://postgres:your_password@localhost:5432/incident_reporting_test
pytest tests/integration
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

