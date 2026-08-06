import pytest

from backend.database import SessionLocal
from backend.models import Item, Receipt


@pytest.fixture(autouse=True)
def _clear_database():
    """Remove all rows before each test.

    Since feature 003, the (date, store, total) unique constraint makes
    the real database reject re-inserting the same receipt. Without clearing
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