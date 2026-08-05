# 003 · DB Hardening & Receipt History — Tasks

## Schema

- [ ] Add `UniqueConstraint("receipt_date", "store_name", "total_amount")`
      to `Receipt` in `backend/models.py`.
- [ ] Add `UniqueConstraint("receipt_id", "name")` to `Item` in `backend/models.py`.
- [ ] Change `ForeignKey("receipts.id")` to
      `ForeignKey("receipts.id", ondelete="CASCADE")` on `Item.receipt_id`.

## Database Reset

- [ ] Delete `~/.canasta/canasta.db` and restart the app to recreate tables
      with new constraints. Verify tables exist with correct schema.

## Backend

- [ ] Add `ReceiptSummary` schema to `backend/schemas.py`
      (id, receipt_date, store_name, total_amount, item_count).
- [ ] Update `POST /api/receipts/scan` in `backend/main.py` to catch
      `IntegrityError` on duplicate receipt → HTTP 409 with user-friendly message.
- [ ] Update `POST /api/receipts/scan` in `backend/main.py` to use UPSERT
      for items (`INSERT ... ON CONFLICT DO UPDATE`).
- [ ] Add `GET /api/receipts` endpoint — list all receipts with item counts,
      ordered by date descending.
- [ ] Add `DELETE /api/receipts/{receipt_id}` endpoint — 204 on success,
      404 if not found.

## Seed Script

- [ ] Create `backend/seed.py` — inserts 3 controlled receipts
      (varied categories, fractional quantities, duplicate for 409 testing).
- [ ] Add `backend/seed.py` to `.gitignore`.
- [ ] Verify: delete `canasta.db`, run `python backend/seed.py`, app returns
      correct data in under 2 seconds.

## Frontend

- [ ] Create `frontend/src/pages/History.tsx` — fetch and list all receipts
      with date, store, total, item count, and delete button per row.
- [ ] Wire delete button to `DELETE /api/receipts/{id}` — refresh list on success.
- [ ] Wire `History` page into `App.tsx` routing alongside Upload page.

## Tests

- [ ] Add duplicate receipt test — same scan twice returns 409.
- [ ] Add UPSERT test — duplicate item on same receipt combines quantities.
- [ ] Add delete test — receipt and items removed, returns 204.
- [ ] Add get receipts test — returns list with correct item counts.
- [ ] Run all tests and verify 0 failures.
- [ ] Validate against all acceptance criteria in `spec.md`.
- [ ] After all tests, ask for approval to move feature 003 to "Done" in `../../constitution/roadmap.md`.
