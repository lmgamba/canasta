from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models import Category, Item, Receipt


def _in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_receipt_can_be_created_with_required_fields():
    """Happy path — create a receipt with all required fields."""
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            receipt_date=date(2025, 1, 15),
            store_name="Test Store",
            total_amount=42.50,
        )
        session.add(receipt)
        session.commit()
        assert receipt.id is not None
        assert receipt.store_name == "Test Store"
        assert receipt.total_amount == 42.50


def test_receipt_requires_store_name():
    """Missing required field — store_name is NOT NULL."""
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            receipt_date=date(2025, 1, 15),
            total_amount=10.0,
        )
        session.add(receipt)
        with pytest.raises(IntegrityError):
            session.commit()


def test_item_category_rejects_invalid_value():
    """Invalid value — category must be one of the defined enum values."""
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            receipt_date=date(2025, 1, 15),
            store_name="Test Store",
            total_amount=5.0,
        )
        session.add(receipt)
        session.flush()
        item = Item(
            name="Mystery",
            quantity=1.0,
            unit_price=1.0,
            total_price=1.0,
            category="InvalidCategory",
            receipt_id=receipt.id,
        )
        session.add(item)
        with pytest.raises((IntegrityError, ValueError)):
            session.flush()
