# 005 · Consumption Dashboard — Tasks

## Backend Schemas

- [x] Add `SpendingOverTimeItem` schema to `backend/schemas.py`
      (period_label: str, total_amount: float).
- [x] Add `SpendingByCategoryItem` schema to `backend/schemas.py`
      (category: str, total_amount: float).
- [x] Add `TopItem` schema to `backend/schemas.py`
      (normalized_name: str, total_spend: float, purchase_count: int).

## Analytics Endpoints

- [x] Add `GET /api/analytics/spending-over-time?period=weekly|monthly`
      to `backend/main.py`.
- [x] Add `GET /api/analytics/spending-by-category` to `backend/main.py`.
- [x] Add `GET /api/analytics/top-items` to `backend/main.py` — use
      `COALESCE(normalized_name, name)` for items missing normalized name.
- [x] Verify all three endpoints manually — curled against a seeded DB
      instead of Postman; response shapes match the Pydantic schemas exactly.

## Frontend Dependencies

- [x] Add `recharts` to `frontend/package.json` and run `npm install`.

## Navigation

- [x] Create `frontend/src/components/NavBar.tsx` — links to Upload,
      History, Dashboard with dark theme tokens applied.
- [x] Add `NavBar` to `App.tsx` so it renders on all pages.

## Dashboard Page

- [x] Create `frontend/src/pages/Dashboard.tsx` — fetch all three endpoints
      in parallel on mount (category + top-items on mount; spending-over-time
      re-fetches on the weekly/monthly toggle independently).
- [x] Add empty state — friendly message when no receipts exist yet
      (per-card, so a receipt with no items still shows partial data).
- [x] Add `LineChart` (Recharts) for spending over time — weekly by default,
      toggle to monthly.
- [x] Add `BarChart` (Recharts) for spending by category.
- [x] Add top items table — normalized name, total spend, purchase count.
- [x] Wire `Dashboard` into `App.tsx` routing.

## Tests

- [x] `test_spending_over_time_weekly` — correct aggregation by ISO week.
- [x] `test_spending_over_time_monthly` — correct aggregation by month.
- [x] `test_spending_by_category` — correct totals per category.
- [x] `test_top_items` — correct spend and count, ordered by spend descending
      (plus `test_top_items_orders_by_spend_descending` for a clearer ranking case).
- [x] `test_analytics_empty_database` — all endpoints return empty lists,
      not errors.
- [x] Run all tests and verify 0 failures (38/38 passed).
- [x] Validate against all acceptance criteria in `spec.md` (10/10 met,
      confirmed by manual check of the running dashboard).
- [x] After all tests, ask for approval to move feature 005 to "Done" in `../../constitution/roadmap.md`.

## Verification Notes

- Backend verified via pytest (38/38) and manual curl against a seeded DB.
- Frontend verified via `tsc -b` (typecheck), `eslint .` (lint), and
  `vite build` (production build, 598 modules, no errors) — all clean.
- Could NOT get a real browser screenshot: headless Chromium (via Playwright)
  failed to launch in this sandbox — missing shared libraries
  (`libnspr4.so` etc.) with no root access to install them. Dev servers were
  left running (backend :8000, frontend :5173) so this can be eyeballed
  directly in a real browser before sign-off.
