from datetime import date

import pytest
from sqlalchemy import CheckConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models import Category, Item, Receipt


def _in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_receipt_can_be_created_with_required_fields():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
            store_name="Test Store",
            total_amount=42.50,
        )
        session.add(receipt)
        session.commit()
        assert receipt.id is not None
        assert receipt.store_name == "Test Store"
        assert receipt.total_amount == 42.50


def test_receipt_created_at_is_set_automatically():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
            store_name="Test Store",
            total_amount=10.0,
        )
        session.add(receipt)
        session.commit()
        assert receipt.created_at is not None


def test_item_belongs_to_receipt():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
            store_name="Test Store",
            total_amount=5.0,
        )
        item = Item(
            name="Milk",
            quantity=1.0,
            unit_price=3.50,
            total_price=3.50,
            category=Category.DAIRY,
        )
        receipt.items.append(item)
        session.add(receipt)
        session.commit()
        assert len(receipt.items) == 1
        assert receipt.items[0].name == "Milk"
        assert item.receipt_id == receipt.id


def test_item_quantity_can_be_fractional():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
            store_name="Test Store",
            total_amount=5.0,
        )
        item = Item(
            name="Cheese",
            quantity=0.5,
            unit_price=12.0,
            total_price=6.0,
            category=Category.DAIRY,
        )
        receipt.items.append(item)
        session.add(receipt)
        session.commit()
        assert receipt.items[0].quantity == 0.5


def test_all_category_values_are_valid():
    expected = {
        "Fruits", "Vegetables", "Carbs & Grains", "Meat",
        "Fish & Seafood", "Dairy", "Protein Snacks", "Sweets",
        "Beverages", "Frozen Veggies", "Other Frozen",
        "Cleaning", "Personal Care", "Other",
    }
    actual = {cat.value for cat in Category}
    assert actual == expected


def test_item_default_quantity_is_one():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
            store_name="Test Store",
            total_amount=5.0,
        )
        item = Item(
            name="Bread",
            unit_price=2.0,
            total_price=2.0,
            category=Category.CARBS_GRAINS,
        )
        receipt.items.append(item)
        session.add(receipt)
        session.commit()
        assert receipt.items[0].quantity == 1.0


def test_receipt_requires_store_name():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
            total_amount=10.0,
        )
        session.add(receipt)
        with pytest.raises(IntegrityError):
            session.commit()


def test_receipt_requires_total_amount():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
            store_name="Test Store",
        )
        session.add(receipt)
        with pytest.raises(IntegrityError):
            session.commit()


def test_item_requires_name():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
            store_name="Test Store",
            total_amount=5.0,
        )
        session.add(receipt)
        session.flush()
        item = Item(
            quantity=1.0,
            unit_price=2.0,
            total_price=2.0,
            category=Category.OTHER,
            receipt_id=receipt.id,
        )
        session.add(item)
        with pytest.raises(IntegrityError):
            session.commit()


def test_item_requires_receipt_id():
    engine = _in_memory_db()
    with Session(engine) as session:
        item = Item(
            name="Milk",
            quantity=1.0,
            unit_price=3.0,
            total_price=3.0,
            category=Category.DAIRY,
        )
        session.add(item)
        with pytest.raises(IntegrityError):
            session.commit()


def test_item_category_rejects_invalid_value():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
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


def test_receipt_total_amount_cannot_be_negative():
    engine = _in_memory_db()
    with Session(engine) as session:
        receipt = Receipt(
            date=date(2025, 1, 15),
            store_name="Test Store",
            total_amount=-5.0,
        )
        session.add(receipt)
        with pytest.raises(IntegrityError):
            session.commit()
