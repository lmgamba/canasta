# 006 · Item Detail View — Tasks

## Backend Schemas

- [x] Add `ItemPurchase` schema to `backend/schemas.py`
      (receipt_date, store_name, quantity, unit_price, total_price).
- [x] Add `ItemPurchaseHistory` schema to `backend/schemas.py`
      (normalized_name, total_spend, purchase_count, purchases: list[ItemPurchase]).

## Endpoint

- [x] Add `GET /api/items/purchases?name={normalized_name}` to `backend/main.py`.
- [x] Return HTTP 404 with clear message if no purchases found.
- [x] Use `COALESCE(normalized_name, name)` to support pre-004 items.
- [x] Verify endpoint manually — curled against the seeded dev DB instead
      of Postman; response shape matches `ItemPurchaseHistory` exactly.

## Frontend

- [x] Create `frontend/src/pages/ItemDetail.tsx` — read `name` from
      query params, fetch endpoint on mount.
- [x] Render aggregate stats header: product name, total spend, purchase count.
- [x] Render purchases table: date, store, quantity, unit price, total price,
      ordered by date descending.
- [x] Add back button using `useNavigate(-1)`.
- [x] Add `/items/detail` route to `App.tsx` — introduced `react-router-dom`
      (`BrowserRouter` in `main.tsx`) since the app previously had no real
      routing, only a local view-switcher; `NavBar` now uses `NavLink`.
- [x] Update Dashboard top items table — wrap item names in links to
      `/items/detail?name={normalized_name}`.

## Tests

- [x] `test_item_detail_happy_path` — returns correct purchases and aggregate
      stats for a known product.
- [x] `test_item_detail_multiple_stores` — same product from two stores
      appears as separate purchases.
- [x] `test_item_detail_single_purchase` — product bought once returns
      purchase_count of 1.
- [x] `test_item_detail_not_found` — unknown name returns 404.
- [x] `test_item_detail_url_encoding` — accented characters in name
      resolve correctly.
- [x] Run all tests and verify 0 failures (43/43 passed).
- [x] Validate against all acceptance criteria in `spec.md` (8/8 met,
      confirmed by manual click-through: Dashboard → item detail → back).
- [x] After all tests, ask for approval to move feature 006 to "Done" in `../../constitution/roadmap.md`.

## Verification Notes

- Backend: pytest 43/43, plus manual curl against the seeded dev DB
  (`Queso curado` → correct aggregate + purchase row, unknown name → 404).
- Frontend: `tsc -b`, `eslint .`, and production `vite build` (609 modules)
  all clean.
- Dev servers restarted (backend without `--reload` needed a manual
  restart to pick up the new route) and left running on :8000/:5173 with
  the same seeded data for manual click-through testing.
