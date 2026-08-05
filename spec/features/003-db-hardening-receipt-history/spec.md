# 003 · DB Hardening & Receipt History

## Problem
The database has no protection against duplicate receipts or items. A user
re-uploading the same receipt creates duplicate entries. There is also no way
to view or manage previously scanned receipts.

## Goal
Lock down data integrity with database constraints and UPSERT logic, and provide
a receipt history view so users can browse and delete past scans.

## Acceptance Criteria
- Duplicate receipts (same date + store + total) return HTTP 409, not a crash.
- Duplicate items on the same receipt combine quantities and totals (UPSERT).
- Deleting a receipt cascades to its items (ON DELETE CASCADE).
- History page lists all receipts with date, store name, total, and item count.
- Users can delete a receipt from the history view.

## Scope
- `backend/models.py` — UniqueConstraints, ON DELETE CASCADE
- `backend/main.py` — integrity error handling, UPSERT logic, DELETE endpoint
- `backend/tests/` — integration tests for duplicates and delete
- `frontend/src/pages/History.tsx` — receipt history list with delete
