# Plan: 004 · Product Normalization Engine

## 1. Normalizer Module (`backend/normalizer.py`)
- `normalize_product_name(name: str) -> str`:
  - Lowercase.
  - Strip leading/trailing whitespace, collapse multiple spaces.
  - Remove store-specific alphanumeric codes (e.g., "LN120", "COD12345").
  - Remove manufacturer brand prefixes where redundant.
- `find_best_match(name: str, existing_names: list[str], threshold: float = 85) -> str | None`:
  - Use `rapidfuzz.fuzz.ratio` for similarity scoring.
  - Return best match above threshold, or None.

## 2. Schema Changes (`models.py`)
- Add `normalized_name: Mapped[str]` column to Item.

## 3. Insertion Logic (`main.py`)
- Before saving each item, normalize its name.
- Query existing `normalized_name` values, run fuzzy match.
- If match found, use the existing standard name; otherwise use the new normalized name.

## 4. Dependencies
- Add `rapidfuzz` to `requirements.txt`.

## 5. Tests
- `test_normalizer.py` (3-4 tests): normalize happy path, brand removal, code stripping, fuzzy match.
