# 003 · DB Hardening & Receipt History — Plan

## Approach

Harden the data layer first (constraints, cascade, UPSERT), then add the two
new endpoints, then build the frontend. The schema changes require a database
reset since SQLAlchemy's `ddl-auto=update` adds tables but does not modify
existing ones. A seed script makes the reset fast and repeatable during
development.

## Implementation

1. Update `backend/models.py`:
   - Add `UniqueConstraint("receipt_date", "store_name", "total_amount")`
     to `Receipt` — prevents duplicate receipts.
   - Add `UniqueConstraint("receipt_id", "name")` to `Item` — enables UPSERT
     logic per item per receipt.
   - Change `ForeignKey("receipts.id")` to
     `ForeignKey("receipts.id", ondelete="CASCADE")` on `Item.receipt_id`
     — deleting a receipt cascades to its items automatically.

2. Delete `~/.canasta/canasta.db` and restart the app to recreate tables
   with the new constraints.

3. Update `POST /api/receipts/scan` in `backend/main.py`:
   - Wrap `db.commit()` in try/except for `IntegrityError` on the receipt
     insert → return HTTP 409 "This receipt has already been scanned."
   - Replace item insert with `INSERT ... ON CONFLICT (receipt_id, name)
DO UPDATE SET quantity = quantity + excluded.quantity,
total_price = total_price + excluded.total_price`.

4. Add `GET /api/receipts` endpoint in `backend/main.py`:
   - Query all receipts with item count via SQLAlchemy,
     ordered by `receipt_date` descending.
   - Return list of `ReceiptSummary` schema (id, date, store, total, item_count).

5. Add `DELETE /api/receipts/{receipt_id}` endpoint in `backend/main.py`:
   - Look up receipt by id → 404 if not found.
   - Delete receipt — cascade handles items.
   - Return HTTP 204.

6. Add `ReceiptSummary` schema to `backend/schemas.py`.

7. Create `backend/seed.py` — standalone script that connects to the database
   and inserts 3 controlled receipts:
   - Receipt A: multiple items, varied categories.
   - Receipt B: fractional quantities (e.g. 0.5kg cheese).
   - Receipt C: identical to A — used to test duplicate detection.

8. Create `frontend/src/pages/History.tsx`:
   - On mount, fetch `GET /api/receipts`.
   - Render a list: date, store name, total, item count, delete button.
   - On delete, call `DELETE /api/receipts/{id}` and refresh the list.

9. Wire `History` into `App.tsx` with basic routing (two views: Upload, History).

10. Add integration tests to `backend/tests/test_integration_scan.py`:
    - Duplicate receipt returns 409.
    - Duplicate item on same receipt combines quantities.
    - Delete receipt removes it and its items.
    - Get receipts returns list with correct item counts.

## Decisions

- **UniqueConstraint on (receipt_date, store_name, total_amount)** — chosen
  over a hash or timestamp because these three fields together are what a user
  would naturally consider "the same receipt." Pure date alone is too loose;
  adding total makes accidental collision virtually impossible.
- **UPSERT for items instead of reject** — a duplicate item on the same receipt
  is more likely a scanning artifact than a user error. Combining quantities
  is the correct semantic: the user bought that product twice.
- **seed.py not committed to git** — dev-only utility that connects to a local
  database. Not relevant to other environments and should not run in CI.
- **Database reset instead of migration** — we are in early development with
  no production data. A manual reset is faster and simpler than writing a
  migration. Flyway/Liquibase is deferred to pre-deploy.

## Risks

- **UniqueConstraint on item name is exact-match only** — Gemini may extract
  "NESTEA TE VERDE" and "NESTEA TE VERDE 33CL" as different names for the same
  product. The UPSERT only fires on an exact match. Full normalization is
  deferred to feature 004.
- **CASCADE delete is irreversible** — no soft delete or undo in v1. Noted in
  README as a known limitation; user must be aware.
- **Schema reset loses test data** — any receipts scanned before this feature
  are deleted. seed.py restores a clean state immediately.
