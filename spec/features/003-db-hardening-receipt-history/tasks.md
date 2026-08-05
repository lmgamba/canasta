# Tasks: 003 · DB Hardening & Receipt History

## Schema
- [ ] Add `UniqueConstraint("date", "store_name", "total_amount")` to Receipt in `models.py`.
- [ ] Add `UniqueConstraint("receipt_id", "name")` to Item in `models.py`.
- [ ] Change `ForeignKey("receipts.id")` to `ForeignKey("receipts.id", ondelete="CASCADE")` in Item.

## Insertion Logic
- [ ] Update `main.py` to catch `IntegrityError` on duplicate receipt → HTTP 409.
- [ ] Update `main.py` to use UPSERT (`INSERT ... ON CONFLICT DO UPDATE`) for items.

## Endpoints
- [ ] Add `GET /api/receipts` endpoint — list all receipts with item counts.
- [ ] Add `DELETE /api/receipts/{receipt_id}` endpoint — delete receipt and items.

## DB Reset & Seed
- [ ] Delete existing `canasta.db` and let the app recreate tables with new constraints.
- [ ] Create `backend/seed.py` — insert 2-3 controlled test receipts with edge cases.
  - Include: one receipt with multiple items, one receipt with fractional quantities,
    one receipt that tests duplicate detection.
  - Usage: delete `canasta.db`, run `python seed.py` to reset to a clean predictable state.

## Tests
- [ ] Add duplicate receipt test to `test_integration_scan.py`.
- [ ] Add duplicate item UPSERT test to `test_integration_scan.py`.
- [ ] Add delete receipt test to `test_integration_scan.py`.
- [ ] Add get receipts test to `test_integration_scan.py`.
