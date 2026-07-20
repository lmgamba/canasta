from sqlalchemy import inspect

from backend.database import engine


def test_engine_connects_to_sqlite():
    with engine.connect() as conn:
        result = conn.exec_driver_sql("SELECT 1")
        assert result.scalar() == 1


def test_canasta_db_file_exists():
    from backend.database import DATABASE_PATH

    assert DATABASE_PATH.exists()
