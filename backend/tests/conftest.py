import os
import tempfile
from pathlib import Path

# Point the test suite at an isolated SQLite file instead of the real
# ~/.canasta/canasta.db, so running pytest never wipes real user data.
# Must run before any `backend.*` import — backend.database reads
# CANASTA_DB_PATH once at import time. setdefault lets CI or a developer
# still override it explicitly.
os.environ.setdefault("CANASTA_DB_PATH", str(Path(tempfile.gettempdir()) / "canasta-test.db"))

import pytest

from backend.database import Base, SessionLocal, engine
from backend.models import Item, Receipt

# The real app only creates tables via FastAPI's lifespan handler, which
# TestClient doesn't run unless used as a context manager. Create them here
# once so the isolated test DB has a schema regardless of how each test
# constructs its client.
Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def _clear_database():
    """Remove all rows before each test.

    Since feature 003, the (date, store, total) unique constraint makes
    the database reject re-inserting the same receipt. Without clearing
    tables between tests, a second run of the suite would hit HTTP 409 on
    data left over from the first run.
    """
    db = SessionLocal()
    try:
        db.query(Item).delete()
        db.query(Receipt).delete()
        db.commit()
    finally:
        db.close()