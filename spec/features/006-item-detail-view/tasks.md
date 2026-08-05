# 006 · Item Detail View — Tasks

## Backend Schemas

- [ ] Add `ItemPurchase` schema to `backend/schemas.py`
      (receipt_date, store_name, quantity, unit_price, total_price).
- [ ] Add `ItemPurchaseHistory` schema to `backend/schemas.py`
      (normalized_name, total_spend, purchase_count, purchases: list[ItemPurchase]).

## Endpoint

- [ ] Add `GET /api/items/purchases?name={normalized_name}` to `backend/main.py`.
- [ ] Return HTTP 404 with clear message if no purchases found.
- [ ] Use `COALESCE(normalized_name, name)` to support pre-004 items.
- [ ] Verify endpoint manually with Postman before moving to frontend.

## Frontend

- [ ] Create `frontend/src/pages/ItemDetail.tsx` — read `name` from
      query params, fetch endpoint on mount.
- [ ] Render aggregate stats header: product name, total spend, purchase count.
- [ ] Render purchases table: date, store, quantity, unit price, total price,
      ordered by date descending.
- [ ] Add back button using `useNavigate(-1)`.
- [ ] Add `/items/detail` route to `App.tsx`.
- [ ] Update Dashboard top items table — wrap item names in links to
      `/items/detail?name={normalized_name}`.

## Tests

- [ ] `test_item_detail_happy_path` — returns correct purchases and aggregate
      stats for a known product.
- [ ] `test_item_detail_multiple_stores` — same product from two stores
      appears as separate purchases.
- [ ] `test_item_detail_single_purchase` — product bought once returns
      purchase_count of 1.
- [ ] `test_item_detail_not_found` — unknown name returns 404.
- [ ] `test_item_detail_url_encoding` — accented characters in name
      resolve correctly.
- [ ] Run all tests and verify 0 failures.
- [ ] Validate against all acceptance criteria in `spec.md`.
- [ ] After all tests, ask for approval to move feature 006 to "Done" in `../../constitution/roadmap.md`.
