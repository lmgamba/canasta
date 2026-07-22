from datetime import date

import pytest
from pydantic import ValidationError

from backend.models import Category
from backend.schemas import ItemCreate, ReceiptCreate


def test_item_create_valid():
    """Happy path — create an item with all required fields."""
    item = ItemCreate(
        name="Milk",
        quantity=1.0,
        unit_price=3.50,
        total_price=3.50,
        category=Category.DAIRY,
    )
    assert item.name == "Milk"
    assert item.quantity == 1.0


def test_item_create_missing_name():
    """Missing required field — name is required."""
    with pytest.raises(ValidationError):
        ItemCreate(
            quantity=1.0,
            unit_price=2.0,
            total_price=2.0,
            category=Category.OTHER,
        )


def test_item_create_invalid_category():
    """Invalid value — category must be a valid Category enum."""
    with pytest.raises(ValidationError):
        ItemCreate(
            name="Mystery",
            quantity=1.0,
            unit_price=1.0,
            total_price=1.0,
            category="Nonexistent",
        )
