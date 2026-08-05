from unittest.mock import MagicMock, patch

import pytest

from backend.models import Category
from backend.scanner import map_category, scan_receipt


def test_map_category_known_value():
    """Happy path — known category string maps to correct enum."""
    assert map_category("dairy") == Category.DAIRY
    assert map_category("meat") == Category.MEAT
    assert map_category("cleaning") == Category.CLEANING


def test_map_category_unknown_value():
    """Unknown string falls back to Category.OTHER."""
    assert map_category("something weird") == Category.OTHER
    assert map_category("") == Category.OTHER


def test_map_category_case_insensitive():
    """Comparison is case-insensitive."""
    assert map_category("DAIRY") == Category.DAIRY
    assert map_category("Dairy") == Category.DAIRY
    assert map_category("  Dairy  ") == Category.DAIRY


def test_scan_receipt_invalid_json():
    """Gemini returns non-JSON text — raises ValueError with friendly message."""
    mock_response = MagicMock()
    mock_response.text = "I cannot read this receipt"
    with patch("backend.scanner.client") as mock_client:
        mock_client.models.generate_content.return_value = mock_response
        with pytest.raises(ValueError, match="Could not read the receipt"):
            scan_receipt(b"fake-image-bytes")


def test_scan_receipt_error_response():
    """Gemini returns an error object — raises ValueError with friendly message."""
    mock_response = MagicMock()
    mock_response.text = '{"error": "blurry image"}'
    with patch("backend.scanner.client") as mock_client:
        mock_client.models.generate_content.return_value = mock_response
        with pytest.raises(ValueError, match="Could not read the receipt"):
            scan_receipt(b"fake-image-bytes")
