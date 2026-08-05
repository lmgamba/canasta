# 004 · Product Normalization Engine

## Problem
The same product appears with different names across stores (e.g., "YOPRO DRINK 300"
from store A vs "YoPro BEBER DANONE" from store B; "MOZZARELLA QUESO" vs
"MOZZARELLA LONCHAS"). This makes cross-store analytics unreliable because each
variant is counted as a separate product.

## Goal
Normalize product names by cleaning store-specific noise and using fuzzy matching
to map near-identical names to a single standard product, enabling accurate
cross-store spending metrics.

## Acceptance Criteria
- Product names are normalized (lowercased, whitespace collapsed, brand noise removed).
- Store-specific codes (e.g., "LN120", "COD12345") are stripped.
- Fuzzy matching maps similar names (≥85% similarity) to a single standard name.
- `normalized_name` column on `items` stores the unified product name.
- Dashboard queries can `GROUP BY normalized_name` for cross-store aggregation.

## Scope
- `backend/normalizer.py` — new module for name normalization + fuzzy matching
- `backend/models.py` — add `normalized_name` column to Item
- `backend/main.py` — apply normalization during item insertion
- `backend/tests/test_normalizer.py` — unit tests
