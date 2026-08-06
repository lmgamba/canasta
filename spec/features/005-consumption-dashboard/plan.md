# 005 · Consumption Dashboard — Plan

## Approach

Build analytics endpoints first and verify each with Postman before touching
the frontend. All three endpoints are read-only aggregations — no schema
changes needed, no database reset required. Frontend uses Recharts for charts,
consistent with the React ecosystem and zero additional config.

## Implementation

1. Add `SpendingOverTimeItem`, `SpendingByCategoryItem`, and `TopItem` Pydantic
   schemas to `backend/schemas.py`.

2. Add `GET /api/analytics/spending-over-time` to `backend/main.py`:
   - Accept `?period=weekly` or `?period=monthly` query parameter.
   - Group receipts by ISO week or calendar month.
   - Return list of `SpendingOverTimeItem` (period_label, total_amount).

3. Add `GET /api/analytics/spending-by-category` to `backend/main.py`:
   - Group items by `category`, sum `total_price`.
   - Return list of `SpendingByCategoryItem` (category, total_amount).

4. Add `GET /api/analytics/top-items` to `backend/main.py`:
   - Group items by `normalized_name`, sum `total_price` and count occurrences.
   - Return list of `TopItem` (normalized_name, total_spend, purchase_count),
     ordered by `total_spend` descending.

5. Create `frontend/src/components/NavBar.tsx` — links to Upload, History,
   Dashboard. Apply dark theme tokens. Render on all pages via `App.tsx`.

6. Create `frontend/src/pages/Dashboard.tsx`:
   - On mount, fetch all three analytics endpoints in parallel.
   - If all return empty data, render a friendly empty state:
     "No receipts yet — scan your first receipt to see your spending patterns."
   - Render spending-over-time as a Recharts `LineChart`.
   - Render spending-by-category as a Recharts `BarChart`.
   - Render top items as a styled table.

7. Wire `Dashboard` into `App.tsx` routing alongside Upload and History.

8. Add `recharts` to `frontend/package.json` and install.

## Decisions

- **Recharts over Chart.js or Victory** — Recharts is React-native (components,
  not imperative canvas API), well maintained, and has the smallest bundle size
  of the three for the charts needed. Chart.js requires a wrapper library in
  React; Victory has a heavier API for simple use cases.
- **`period` as a query parameter, not two separate endpoints** — same data
  shape, same aggregation logic, one parameter difference. Two endpoints would
  duplicate route handler code for no benefit.
- **Parallel fetch on Dashboard mount** — three independent endpoints; no
  reason to waterfall them. `Promise.all` keeps the page load time to one
  round-trip.
- **Empty state at component level** — each chart checks its own data and
  renders a placeholder if empty, rather than a single page-level empty state.
  This way a user with receipts but no items still sees partial data.

## Risks

- **`normalized_name` may be null for receipts scanned before feature 004** —
  `top-items` query must filter out null `normalized_name` values or fall back
  to raw `name`. Add a `COALESCE(normalized_name, name)` in the query.
- **SQLite date grouping is less ergonomic than PostgreSQL** — SQLite has no
  native `DATE_TRUNC`. Use `strftime('%Y-%W', date)` for weekly and
  `strftime('%Y-%m', date)` for monthly grouping.
- **Recharts requires a fixed container width** — charts in a responsive layout
  need a `ResponsiveContainer` wrapper or they render at 0px width. Must be
  applied to every chart component.
