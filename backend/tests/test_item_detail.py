from datetime import date

from fastapi.testclient import TestClient

from backend.database import SessionLocal
from backend.main import app
from backend.models import Item, Receipt

client = TestClient(app)


def _add_receipt(receipt_date, store_name, total_amount, items):
    """Insert a Receipt with Items directly via the ORM, bypassing the
    Gemini scan flow — these tests only exercise the purchase-history query."""
    db = SessionLocal()
    try:
        receipt = Receipt(
            receipt_date=receipt_date, store_name=store_name, total_amount=total_amount
        )
        db.add(receipt)
        db.flush()
        for item in items:
            db.add(Item(receipt_id=receipt.id, **item))
        db.commit()
    finally:
        db.close()


def test_item_detail_happy_path():
    """A known product returns its aggregate stats and purchase detail."""
    _add_receipt(
        date(2025, 5, 1),
        "Mercadona",
        3.5,
        [
            dict(
                name="Leche Entera",
                normalized_name="leche entera",
                quantity=1.0,
                unit_price=3.5,
                total_price=3.5,
                category="Dairy",
            )
        ],
    )

    response = client.get("/api/items/purchases", params={"name": "leche entera"})
    assert response.status_code == 200
    data = response.json()
    assert data["normalized_name"] == "leche entera"
    assert data["total_spend"] == 3.5
    assert data["purchase_count"] == 1
    assert data["purchases"] == [
        {
            "receipt_date": "2025-05-01",
            "store_name": "Mercadona",
            "quantity": 1.0,
            "unit_price": 3.5,
            "total_price": 3.5,
        }
    ]


def test_item_detail_multiple_stores():
    """The same product bought at two stores appears as two purchases,
    ordered by date descending, with correctly summed aggregates."""
    _add_receipt(
        date(2025, 5, 1),
        "Mercadona",
        3.0,
        [
            dict(
                name="Leche Entera",
                normalized_name="leche entera",
                quantity=1.0,
                unit_price=3.0,
                total_price=3.0,
                category="Dairy",
            )
        ],
    )
    _add_receipt(
        date(2025, 5, 10),
        "Carrefour",
        3.2,
        [
            dict(
                name="LECHE ENTERA 1L",
                normalized_name="leche entera",
                quantity=1.0,
                unit_price=3.2,
                total_price=3.2,
                category="Dairy",
            )
        ],
    )

    response = client.get("/api/items/purchases", params={"name": "leche entera"})
    assert response.status_code == 200
    data = response.json()
    assert data["purchase_count"] == 2
    assert data["total_spend"] == 6.2
    # Newest first.
    assert [p["store_name"] for p in data["purchases"]] == ["Carrefour", "Mercadona"]


def test_item_detail_single_purchase():
    """A product bought exactly once reports purchase_count 1."""
    _add_receipt(
        date(2025, 5, 2),
        "Store X",
        1.5,
        [
            dict(
                name="Gum",
                normalized_name="gum",
                quantity=1.0,
                unit_price=1.5,
                total_price=1.5,
                category="Sweets",
            )
        ],
    )

    response = client.get("/api/items/purchases", params={"name": "gum"})
    assert response.status_code == 200
    assert response.json()["purchase_count"] == 1


def test_item_detail_not_found():
    """An unknown product name returns 404 with a clear message."""
    response = client.get("/api/items/purchases", params={"name": "nonexistent product"})
    assert response.status_code == 404
    assert response.json()["detail"] == "No purchases found for this product."


def test_item_detail_url_encoding():
    """Accented characters in the name resolve correctly."""
    _add_receipt(
        date(2025, 5, 3),
        "Store Y",
        2.0,
        [
            dict(
                name="Piña",
                normalized_name="piña",
                quantity=1.0,
                unit_price=2.0,
                total_price=2.0,
                category="Fruits",
            )
        ],
    )

    response = client.get("/api/items/purchases", params={"name": "piña"})
    assert response.status_code == 200
    assert response.json()["normalized_name"] == "piña"
