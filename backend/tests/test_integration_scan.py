from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.database import Base, engine
from backend.main import app
from backend.models import Category

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
    assert data["store_name"] == "Test Store"
    assert data["receipt_date"] == "2025-01-15"
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Milk"
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
    assert data["store_name"] == "DB Store"
    assert len(data["items"]) == 2
    # Verify items have database IDs (persisted)
    assert data["items"][0]["id"] is not None
    assert data["items"][0]["receipt_id"] == data["id"]
