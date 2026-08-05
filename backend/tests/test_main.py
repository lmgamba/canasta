from sqlalchemy import inspect

from fastapi.testclient import TestClient

from backend.database import engine
from backend.main import app


def test_health_endpoint_returns_ok():
    """Happy path — GET /api/health returns 200 with status ok."""
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_tables_created_on_startup():
    """Integration — after app starts, receipts and items tables exist."""
    with TestClient(app):
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
    assert "receipts" in tables
    assert "items" in tables
