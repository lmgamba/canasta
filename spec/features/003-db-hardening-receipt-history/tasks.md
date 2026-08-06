# 003 · DB Hardening & Receipt History — Tasks

## Schema

- [x] Add `UniqueConstraint("date", "store_name", "total_amount")`
      to `Receipt` in `backend/models.py`.
- [x] Add `UniqueConstraint("receipt_id", "name")` to `Item` in `backend/models.py`.
- [x] Change `ForeignKey("receipts.id")` to
      `ForeignKey("receipts.id", ondelete="CASCADE")` on `Item.receipt_id`.

## Database Reset

- [x] Delete `~/.canasta/canasta.db` and restart the app to recreate tables
      with new constraints. Verify tables exist with correct schema.
- [x] Enable `PRAGMA foreign_keys=ON` per connection so ON DELETE CASCADE fires.

## Backend

- [x] Add `ReceiptSummary` schema to `backend/schemas.py`
      (id, receipt_date, store_name, total_amount, item_count).
- [x] Update `POST /api/receipts/scan` in `backend/main.py` to catch
      `IntegrityError` on duplicate receipt → HTTP 409 with user-friendly message.
- [x] Update `POST /api/receipts/scan` in `backend/main.py` to use UPSERT
      for items (`INSERT ... ON CONFLICT DO UPDATE`).
- [x] Add `GET /api/receipts` endpoint — list all receipts with item counts,
      ordered by date descending.
- [x] Add `DELETE /api/receipts/{receipt_id}` endpoint — 204 on success,
      404 if not found.

## Seed Script

- [x] Create `backend/seed.py` — inserts 3 controlled receipts
      (varied categories, fractional quantities, duplicate for 409 testing).
- [x] Add `backend/seed.py` to `.gitignore`.
- [x] Verify: delete `canasta.db`, run `python -m backend.seed`, app returns
      correct data in under 2 seconds (measured ~0.4s).

## Frontend

- [ ] Create `frontend/src/pages/History.tsx` — fetch and list all receipts
      with date, store, total, item count, and delete button per row.
- [ ] Wire delete button to `DELETE /api/receipts/{id}` — refresh list on success.
- [ ] Wire `History` page into `App.tsx` routing alongside Upload page.

## Tests

- [x] Add duplicate receipt test — same scan twice returns 409.
- [x] Add UPSERT test — duplicate item on same receipt combines quantities.
- [x] Add delete test — receipt and items removed, returns 204.
- [x] Add get receipts test — returns list with correct item counts.
- [x] Add `conftest.py` autouse fixture — clears tables between tests to isolate runs.
- [x] Run all tests and verify 0 failures (23/23 passed).
- [x] Validate against all acceptance criteria in `spec.md` (7/7 met).
- [x] After all tests, ask for approval to move feature 003 to "Done" in `../../constitution/roadmap.md`.
