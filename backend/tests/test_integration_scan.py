from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.database import Base, SessionLocal, engine
from backend.main import app
from backend.models import Category, Item

client = TestClient(app)


def _make_jpeg_bytes():
    """Create a minimal valid JPEG file in memory (magic bytes only)."""
    return b"\xff\xd8\xff\xe0" + b"\x00" * 100


def _make_png_bytes():
    """Create a minimal valid PNG file in memory (magic bytes only)."""
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


def _mock_gemini_response(store_name="Test Store", items=None):
    """Build a mock Gemini response with receipt data."""
    if items is None:
        items = [
            {
                "name": "Milk",
                "quantity": 1.0,
                "unit_price": 3.50,
                "total_price": 3.50,
                "category": "Dairy",
            }
        ]
    mock = MagicMock()
    mock.text = (
        f'{{"store_name": "{store_name}", "date": "2025-01-15", '
        f'"total_amount": 3.50, "items": {items}}}'.replace("'", '"')
    )
    return mock


def test_scan_receipt_returns_200_with_valid_jpeg():
    """Happy path — upload JPEG, get back Receipt with items."""
    mock_response = _mock_gemini_response()
    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.return_value = {
            "store_name": "Test Store",
            "date": "2025-01-15",
            "total_amount": 3.50,
            "items": [
                {
                    "name": "Milk",
                    "quantity": 1.0,
                    "unit_price": 3.50,
                    "total_price": 3.50,
                    "category": "Dairy",
                }
            ],
        }
        response = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
    assert response.status_code == 200
    data = response.json()
    # store_name and item name are uppercased at insertion time — see
    # test_scan_receipt_uppercases_store_and_item_names for why.
    assert data["store_name"] == "TEST STORE"
    assert data["receipt_date"] == "2025-01-15"
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "MILK"
    assert data["items"][0]["category"] == "Dairy"


def test_scan_receipt_returns_400_for_invalid_file_type():
    """Invalid file — a text file pretending to be a receipt."""
    response = client.post(
        "/api/receipts/scan",
        files={"file": ("receipt.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_scan_receipt_returns_422_when_gemini_fails():
    """Gemini cannot read the receipt — returns 422 with friendly message."""
    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.side_effect = ValueError(
            "Could not read the receipt. Please upload a clearer photo."
        )
        response = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
    assert response.status_code == 422
    assert "Could not read the receipt" in response.json()["detail"]


def test_scan_receipt_returns_400_for_oversized_file():
    """File too large — exceeds 5 MB limit."""
    large_image = b"\xff\xd8\xff" + b"\x00" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/api/receipts/scan",
        files={"file": ("receipt.jpg", large_image, "image/jpeg")},
    )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"]


def test_scan_receipt_persists_to_database():
    """Integration — Receipt and Items are saved to the database."""
    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.return_value = {
            "store_name": "DB Store",
            "date": "2025-06-01",
            "total_amount": 10.0,
            "items": [
                {
                    "name": "Bread",
                    "quantity": 2.0,
                    "unit_price": 2.50,
                    "total_price": 5.0,
                    "category": "Carbs & Grains",
                },
                {
                    "name": "Cheese",
                    "quantity": 0.5,
                    "unit_price": 10.0,
                    "total_price": 5.0,
                    "category": "Dairy",
                },
            ],
        }
        response = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.png", _make_png_bytes(), "image/png")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["store_name"] == "DB STORE"
    assert len(data["items"]) == 2
    # Verify items have database IDs (persisted)
    assert data["items"][0]["id"] is not None
    assert data["items"][0]["receipt_id"] == data["id"]


def test_scan_receipt_returns_409_for_duplicate():
    """Scanning the same receipt twice returns 409, not a duplicate row."""
    payload = {
        "store_name": "Dup Store",
        "date": "2025-03-10",
        "total_amount": 9.99,
        "items": [
            {
                "name": "Apple",
                "quantity": 3.0,
                "unit_price": 1.0,
                "total_price": 3.0,
                "category": "Fruits",
            }
        ],
    }
    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.return_value = payload
        first = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
        second = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
    assert first.status_code == 200
    assert second.status_code == 409
    assert "already been scanned" in second.json()["detail"]


def test_scan_receipt_returns_409_for_duplicate_with_different_casing():
    """Same receipt, but Gemini returns different store-name casing on the
    second scan (e.g. "Carrefour Express" vs "CARREFOUR EXPRESS") — still
    caught as a duplicate, since store_name is uppercased before storing."""
    first_payload = {
        "store_name": "Carrefour Express",
        "date": "2025-03-11",
        "total_amount": 9.99,
        "items": [
            {
                "name": "Apple",
                "quantity": 3.0,
                "unit_price": 1.0,
                "total_price": 3.0,
                "category": "Fruits",
            }
        ],
    }
    second_payload = {**first_payload, "store_name": "CARREFOUR EXPRESS"}

    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.return_value = first_payload
        first = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
        mock_scan.return_value = second_payload
        second = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
    assert first.status_code == 200
    assert first.json()["store_name"] == "CARREFOUR EXPRESS"
    assert second.status_code == 409


def test_scan_receipt_upserts_duplicate_item_quantities():
    """Scan re-adding the same item name combines its quantity and total."""
    # Items deliberately appear on the same receipt with the same name.
    payload = {
        "store_name": "Upsert Store",
        "date": "2025-04-01",
        "total_amount": 12.0,
        "items": [
            {
                "name": "Milk",
                "quantity": 2.0,
                "unit_price": 3.0,
                "total_price": 6.0,
                "category": "Dairy",
            },
            {
                "name": "Milk",
                "quantity": 2.0,
                "unit_price": 3.0,
                "total_price": 6.0,
                "category": "Dairy",
            },
        ],
    }
    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.return_value = payload
        response = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
    assert response.status_code == 200
    data = response.json()
    # The two identical lines collapse into one with combined quantity/total.
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "MILK"
    assert data["items"][0]["quantity"] == 4.0
    assert data["items"][0]["total_price"] == 12.0


def test_scan_receipt_persists_normalized_name():
    """Integration — a saved item gets a cleaned normalized_name in the DB."""
    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.return_value = {
            "store_name": "Normalize Store",
            "date": "2025-08-01",
            "total_amount": 3.50,
            "items": [
                {
                    "name": "YOPRO DRINK 300LN120",
                    "quantity": 1.0,
                    "unit_price": 3.50,
                    "total_price": 3.50,
                    "category": "Beverages",
                }
            ],
        }
        response = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
    assert response.status_code == 200
    receipt_id = response.json()["id"]

    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.receipt_id == receipt_id).one()
        assert item.normalized_name == "yopro drink 300"
    finally:
        db.close()


def test_scan_receipt_reuses_normalized_name_across_receipts():
    """A near-duplicate item name on a later receipt merges into the
    existing standard normalized_name instead of creating a variant."""
    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.return_value = {
            "store_name": "Store A",
            "date": "2025-08-02",
            "total_amount": 3.50,
            "items": [
                {
                    "name": "MOZZARELLA QUESO",
                    "quantity": 1.0,
                    "unit_price": 3.50,
                    "total_price": 3.50,
                    "category": "Dairy",
                }
            ],
        }
        client.post(
            "/api/receipts/scan",
            files={"file": ("receipt1.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )

        mock_scan.return_value = {
            "store_name": "Store B",
            "date": "2025-08-03",
            "total_amount": 4.00,
            "items": [
                {
                    "name": "MOZZARELLA QUESO FRESCO",
                    "quantity": 1.0,
                    "unit_price": 4.00,
                    "total_price": 4.00,
                    "category": "Dairy",
                }
            ],
        }
        response = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt2.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
    receipt_id = response.json()["id"]

    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.receipt_id == receipt_id).one()
        # Merges into Store A's standard name, not its own "...fresco" variant.
        assert item.normalized_name == "mozzarella queso"
    finally:
        db.close()


def test_get_receipts_returns_list_with_item_counts():
    """GET /api/receipts lists receipts ordered by date desc with item counts."""
    payload = {
        "store_name": "List Store",
        "date": "2025-05-05",
        "total_amount": 15.5,
        "items": [
            {
                "name": "Yogurt",
                "quantity": 2.0,
                "unit_price": 2.0,
                "total_price": 4.0,
                "category": "Dairy",
            },
            {
                "name": "Eggs",
                "quantity": 1.0,
                "unit_price": 5.5,
                "total_price": 5.5,
                "category": "Protein Snacks",
            },
        ],
    }
    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.return_value = payload
        client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
    response = client.get("/api/receipts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["store_name"] == "LIST STORE"
    assert data[0]["item_count"] == 2


def test_delete_receipt_removes_items_and_returns_204():
    """DELETE removes the receipt and its items; 404 if receipt missing."""
    payload = {
        "store_name": "Delete Store",
        "date": "2025-07-01",
        "total_amount": 20.0,
        "items": [
            {
                "name": "Rice",
                "quantity": 1.0,
                "unit_price": 2.0,
                "total_price": 2.0,
                "category": "Carbs & Grains",
            }
        ],
    }
    with patch("backend.main.scan_receipt") as mock_scan:
        mock_scan.return_value = payload
        create_response = client.post(
            "/api/receipts/scan",
            files={"file": ("receipt.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
        deleted_id = create_response.json()["id"]

        del_response = client.delete(f"/api/receipts/{deleted_id}")
        assert del_response.status_code == 204
        # Receipt no longer listed.
        assert client.get("/api/receipts").json() == []

    # Deleting a non-existent receipt returns 404.
    assert client.delete("/api/receipts/999").status_code == 404
