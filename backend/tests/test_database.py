from sqlalchemy import inspect

from backend.database import engine


def test_engine_connects_to_sqlite():
    """Engine can connect and execute a basic query."""
    with engine.connect() as conn:
        result = conn.exec_driver_sql("SELECT 1")
        assert result.scalar() == 1
