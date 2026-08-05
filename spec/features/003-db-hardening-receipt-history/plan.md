# Plan: 003 · DB Hardening & Receipt History

## 1. Schema Changes (`models.py`)
- Add `UniqueConstraint("date", "store_name", "total_amount")` to Receipt.
- Add `UniqueConstraint("receipt_id", "name")` to Item.
- Change `ForeignKey("receipts.id")` to `ForeignKey("receipts.id", ondelete="CASCADE")`.

## 2. Insertion Logic (`main.py`)
- Wrap `db.commit()` in try/except for `IntegrityError`.
  - Duplicate receipt → HTTP 409 "This receipt has already been scanned."
- Use `INSERT ... ON CONFLICT (receipt_id, name) DO UPDATE` for items:
  - Combine quantities: `quantity = quantity + excluded.quantity`
  - Combine totals: `total_price = total_price + excluded.total_price`

## 3. Delete Endpoint
- `DELETE /api/receipts/{receipt_id}` — delete receipt and cascade to items.
- Return HTTP 204 on success, HTTP 404 if not found.

## 4. History Endpoint
- `GET /api/receipts` — return all receipts with item counts, ordered by date desc.

## 5. DB Reset & Seed Script
- Delete `canasta.db` and let the app recreate tables with new constraints.
- Create `backend/seed.py` — inserts 2-3 controlled test receipts into an empty DB.
  - Purpose: fast reset during development. Delete `canasta.db`, run `python seed.py`,
    app is back to a clean predictable state in ~2 seconds.

## 6. Tests
- Duplicate receipt returns 409.
- Duplicate item on same receipt combines quantities.
- Delete receipt removes it and its items.
- Get receipts returns list with item counts.
