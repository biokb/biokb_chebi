import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from biokb_chebi.api.main import app, get_session
from biokb_chebi.db.manager import DbManager

# Create a new test database engine (SQLite in-memory for testing)
test_engine = create_engine("sqlite:///tests/dbs/test.db")
TestSessionLocal = sessionmaker(bind=test_engine)


# Dependency override to use test database
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override to the FastAPI dependency
app.dependency_overrides[get_session] = override_get_db

@pytest.fixture()
def client_with_data():
    # Create tables in the test database
    dm = DbManager(test_engine)
    dm.set_data_folder(os.path.join("tests", "dummy_data"))
    dm.import_data()
    return TestClient(app)

def test_server(client_with_data: TestClient):
    response = client_with_data.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Running!"}