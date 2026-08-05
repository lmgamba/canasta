# 005 · Consumption Dashboard — Tasks

## Backend Schemas

- [ ] Add `SpendingOverTimeItem` schema to `backend/schemas.py`
      (period_label: str, total_amount: float).
- [ ] Add `SpendingByCategoryItem` schema to `backend/schemas.py`
      (category: str, total_amount: float).
- [ ] Add `TopItem` schema to `backend/schemas.py`
      (normalized_name: str, total_spend: float, purchase_count: int).

## Analytics Endpoints

- [ ] Add `GET /api/analytics/spending-over-time?period=weekly|monthly`
      to `backend/main.py`.
- [ ] Add `GET /api/analytics/spending-by-category` to `backend/main.py`.
- [ ] Add `GET /api/analytics/top-items` to `backend/main.py` — use
      `COALESCE(normalized_name, name)` for items missing normalized name.
- [ ] Verify all three endpoints manually with Postman before moving to frontend.

## Frontend Dependencies

- [ ] Add `recharts` to `frontend/package.json` and run `npm install`.

## Navigation

- [ ] Create `frontend/src/components/NavBar.tsx` — links to Upload,
      History, Dashboard with dark theme tokens applied.
- [ ] Add `NavBar` to `App.tsx` so it renders on all pages.

## Dashboard Page

- [ ] Create `frontend/src/pages/Dashboard.tsx` — fetch all three endpoints
      in parallel on mount.
- [ ] Add empty state — friendly message when no receipts exist yet.
- [ ] Add `LineChart` (Recharts) for spending over time — weekly by default,
      toggle to monthly.
- [ ] Add `BarChart` (Recharts) for spending by category.
- [ ] Add top items table — normalized name, total spend, purchase count.
- [ ] Wire `Dashboard` into `App.tsx` routing.

## Tests

- [ ] `test_spending_over_time_weekly` — correct aggregation by ISO week.
- [ ] `test_spending_over_time_monthly` — correct aggregation by month.
- [ ] `test_spending_by_category` — correct totals per category.
- [ ] `test_top_items` — correct spend and count, ordered by spend descending.
- [ ] `test_analytics_empty_database` — all endpoints return empty lists,
      not errors.
- [ ] Run all tests and verify 0 failures.
- [ ] Validate against all acceptance criteria in `spec.md`.
- [ ] After all tests, ask for approval to move feature 005 to "Done" in `../../constitution/roadmap.md`.
