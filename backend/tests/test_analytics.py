from datetime import date

from fastapi.testclient import TestClient

from backend.database import SessionLocal
from backend.main import app
from backend.models import Item, Receipt

client = TestClient(app)


def _add_receipt(receipt_date, store_name, total_amount, items):
    """Insert a Receipt with Items directly via the ORM, bypassing the
    Gemini scan flow — these tests only exercise the aggregation queries."""
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
        return receipt.id
    finally:
        db.close()


def test_spending_over_time_weekly():
    """Weekly totals are grouped by ISO-ish week and ordered ascending."""
    week1_label = date(2025, 1, 6).strftime("%Y-%W")
    week2_label = date(2025, 1, 13).strftime("%Y-%W")
    _add_receipt(date(2025, 1, 6), "Store A", 10.0, [])
    _add_receipt(date(2025, 1, 7), "Store B", 5.0, [])
    _add_receipt(date(2025, 1, 13), "Store C", 20.0, [])

    response = client.get("/api/analytics/spending-over-time?period=weekly")
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {"period_label": week1_label, "total_amount": 15.0},
        {"period_label": week2_label, "total_amount": 20.0},
    ]


def test_spending_over_time_monthly():
    """Monthly totals are grouped by calendar month and ordered ascending."""
    _add_receipt(date(2025, 1, 6), "Store A", 10.0, [])
    _add_receipt(date(2025, 1, 20), "Store B", 5.0, [])
    _add_receipt(date(2025, 2, 1), "Store C", 20.0, [])

    response = client.get("/api/analytics/spending-over-time?period=monthly")
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {"period_label": "2025-01", "total_amount": 15.0},
        {"period_label": "2025-02", "total_amount": 20.0},
    ]


def test_spending_by_category():
    """Totals are summed per category and ordered by spend descending."""
    _add_receipt(
        date(2025, 3, 1),
        "Store A",
        13.0,
        [
            dict(name="Milk", unit_price=3.0, total_price=3.0, category="Dairy"),
            dict(name="Cheese", unit_price=10.0, total_price=10.0, category="Dairy"),
        ],
    )
    _add_receipt(
        date(2025, 3, 2),
        "Store B",
        5.0,
        [dict(name="Apple", unit_price=5.0, total_price=5.0, category="Fruits")],
    )

    response = client.get("/api/analytics/spending-by-category")
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {"category": "Dairy", "total_amount": 13.0},
        {"category": "Fruits", "total_amount": 5.0},
    ]


def test_top_items():
    """Items are aggregated by normalized_name, ordered by spend descending."""
    _add_receipt(
        date(2025, 4, 1),
        "Store A",
        13.0,
        [
            dict(
                name="YOPRO DRINK 300",
                normalized_name="yopro drink",
                unit_price=3.0,
                total_price=3.0,
                category="Beverages",
            ),
            dict(
                name="Bread", unit_price=10.0, total_price=10.0, category="Carbs & Grains"
            ),
        ],
    )
    _add_receipt(
        date(2025, 4, 2),
        "Store B",
        3.0,
        [
            dict(
                name="YoPro Beber Danone",
                normalized_name="yopro drink",
                unit_price=3.0,
                total_price=3.0,
                category="Beverages",
            )
        ],
    )

    response = client.get("/api/analytics/top-items")
    assert response.status_code == 200
    data = response.json()
    # "Bread" ($10, one line item, no normalized_name) outspends the merged
    # "yopro drink" ($3 + $3 across two receipts), so it ranks first.
    # Bread's coalesce falls back to its raw name rather than a null bucket.
    assert data[0] == {"normalized_name": "Bread", "total_spend": 10.0, "purchase_count": 1}
    assert data[1] == {
        "normalized_name": "yopro drink",
        "total_spend": 6.0,
        "purchase_count": 2,
    }


def test_top_items_orders_by_spend_descending():
    """Highest total spend ranks first."""
    _add_receipt(
        date(2025, 4, 5),
        "Store C",
        1.0,
        [dict(name="Gum", unit_price=1.0, total_price=1.0, category="Sweets")],
    )
    _add_receipt(
        date(2025, 4, 6),
        "Store D",
        50.0,
        [dict(name="Steak", unit_price=50.0, total_price=50.0, category="Meat")],
    )

    response = client.get("/api/analytics/top-items")
    assert response.status_code == 200
    data = response.json()
    names = [row["normalized_name"] for row in data]
    assert names.index("Steak") < names.index("Gum")


def test_analytics_empty_database():
    """All analytics endpoints return empty lists, not errors, when no data exists."""
    assert client.get("/api/analytics/spending-over-time?period=weekly").json() == []
    assert client.get("/api/analytics/spending-over-time?period=monthly").json() == []
    assert client.get("/api/analytics/spending-by-category").json() == []
    assert client.get("/api/analytics/top-items").json() == []
