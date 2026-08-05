# 006 · Item Detail View

## Problem
Users cannot drill down into a specific product to see its full purchase history
across all receipts and stores.

## Goal
Allow clicking any item to view its complete purchase history across all receipts,
showing dates, stores, quantities, and prices.

## Acceptance Criteria
- Clicking an item navigates to a detail view.
- Detail view shows all purchases of that product across receipts.
- Displays date, store, quantity, unit price, and total for each purchase.
- Uses `normalized_name` to group purchases of the same product.

## Scope
- `backend/main.py` — item history endpoint
- `frontend/src/pages/ItemDetail.tsx` — item detail page
- `frontend/src/components/` — item history table
