# Plan: 006 · Item Detail View

## 1. Endpoint (`main.py`)
- `GET /api/items/{normalized_name}/purchases` — all purchases of a product.

## 2. Frontend (`ItemDetail.tsx`)
- Table showing all purchases: date, store, quantity, unit price, total.
- Header with product name and aggregate stats (total spent, times purchased).

## 3. Tests
- Test item history endpoint returns correct purchases.
