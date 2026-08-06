# 003 · DB Hardening & Receipt History

**Status:** done

## What it does

Adds database constraints to prevent duplicate receipts and items, wires up
UPSERT logic so re-scanning the same receipt is handled gracefully, and
provides a receipt history page where users can browse and delete past scans.

## Why

Without constraints, re-uploading the same receipt silently creates duplicate
data that corrupts every metric on the dashboard. History and delete are the
minimum needed for a user to manage their own data — especially test scans
during development.

## Acceptance Criteria

- [ ] Scanning a receipt with the same date, store name, and total as an
      existing receipt returns HTTP 409 with message
      "This receipt has already been scanned."
- [ ] Scanning a receipt where an item name already exists for that receipt
      combines quantities and totals instead of creating a duplicate row.
- [ ] Deleting a receipt via `DELETE /api/receipts/{id}` removes the receipt
      and all its items. Returns 204 on success, 404 if not found.
- [ ] `GET /api/receipts` returns all receipts ordered by date descending,
      each with date, store name, total amount, and item count.
- [ ] Frontend History page lists all receipts with date, store, total,
      item count, and a delete button per receipt.
- [ ] Deleting a receipt from the UI refreshes the list immediately.
- [ ] `backend/seed.py` resets the database to a clean predictable state
      in under 2 seconds.

## Out of Scope

- Product name normalization across receipts (feature 004).
- Fuzzy matching of similar item names (feature 004).
- Pagination of the history list (backlog).
- Editing receipt data manually (backlog).
