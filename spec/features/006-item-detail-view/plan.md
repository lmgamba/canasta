# 006 · Item Detail View — Plan

## Approach

Single new endpoint that returns both aggregate stats and purchase list in one
response, avoiding a second API call from the frontend. No schema changes —
this feature is read-only. Frontend is a new page accessible from the Dashboard
top items list via React Router navigation.

## Implementation

1. Add `ItemPurchase` and `ItemPurchaseHistory` Pydantic schemas to
   `backend/schemas.py`:
   - `ItemPurchase`: receipt_date, store_name, quantity, unit_price, total_price.
   - `ItemPurchaseHistory`: normalized_name, total_spend, purchase_count,
     purchases: list[ItemPurchase].

2. Add `GET /api/items/purchases` endpoint to `backend/main.py`:
   - Accept `?name` query parameter (URL-safe, supports spaces via encoding).
   - Query items where `COALESCE(normalized_name, name)` matches the parameter.
   - If no results → HTTP 404 "No purchases found for this product."
   - Compute `total_spend` and `purchase_count` from the results.
   - Return `ItemPurchaseHistory` ordered by `receipt_date` descending.

3. Create `frontend/src/pages/ItemDetail.tsx`:
   - Read `name` from React Router query params on mount.
   - Fetch `GET /api/items/purchases?name={name}`.
   - Render aggregate stats header: normalized name, total spend,
     purchase count.
   - Render purchases table: date, store, quantity, unit price, total price.
   - Render back button using `useNavigate(-1)` to return to previous page.

4. Add route for `ItemDetail` in `App.tsx`:
   `/items/detail` with `?name` query param.

5. Update Dashboard top items table — wrap each item name in a link that
   navigates to `/items/detail?name={normalized_name}`.

6. Write tests in `backend/tests/test_item_detail.py`.

## Decisions

- **Query parameter over path parameter for `normalized_name`** — product names
  contain spaces, accents, and special characters that make path parameters
  fragile. Query parameters handle URL encoding naturally.
  `/api/items/purchases?name=tortita+arroz` is safer than
  `/api/items/tortita arroz/purchases`.
- **Single endpoint returning both stats and list** — avoids two round-trips
  from the frontend. Stats are trivially derived from the same query.
- **`COALESCE(normalized_name, name)`** — items scanned before feature 004
  have no `normalized_name`. Falling back to raw `name` keeps the endpoint
  functional for all items in the database.
- **`useNavigate(-1)` for back navigation** — works regardless of which page
  the user came from. Simpler than hardcoding a route.

## Risks

- **`COALESCE(normalized_name, name)` may return inconsistent results** —
  items scanned before feature 004 use raw name; items after use normalized
  name. A search for "tortita arroz" won't find "TORTITA ARROZ" from an
  old scan. Acceptable limitation in v1; backfill is a v2 concern.
- **URL encoding of special characters** — accented characters (á, é, ñ)
  must be encoded in the query param. React Router and FastAPI handle this
  automatically, but worth verifying manually with a real Spanish product name.
