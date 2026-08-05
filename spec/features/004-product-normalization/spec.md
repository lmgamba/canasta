# 004 · Product Normalization Engine

**Status:** proposed

## What it does

Normalizes product names during item insertion by cleaning store-specific noise
and using fuzzy matching to map near-identical names to a single standard name.
Adds a `normalized_name` column to `items` so the dashboard can aggregate
spending across stores by unified product.

## Why

The same product appears with different names across stores — "YOPRO DRINK 300"
vs "YoPro BEBER DANONE", "MOZZARELLA QUESO" vs "MOZZARELLA LONCHAS". Without
normalization, every variant is counted as a separate product and cross-store
analytics are meaningless.

## Acceptance Criteria

- [ ] `normalize_product_name()` lowercases, collapses whitespace, and strips
      store-specific alphanumeric codes (e.g. "LN120", "COD12345").
- [ ] `find_best_match()` maps names with ≥85% similarity to a single
      standard name.
- [ ] `normalized_name` column exists on `items` table, nullable to support
      existing rows during schema migration.
- [ ] Every new item saved to the database has a `normalized_name` value.
- [ ] Dashboard queries can `GROUP BY normalized_name` for cross-store
      aggregation (consumed by feature 005).

## Out of Scope

- Dashboard implementation (feature 005).
- Manual correction of normalized names by the user (backlog).
- Multi-language normalization — Spanish and English product names only in v1.
- ML-based entity resolution — fuzzy matching is sufficient for v1.
