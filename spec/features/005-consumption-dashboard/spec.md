# 005 · Consumption Dashboard

**Status:** done

## What it does

Provides three analytics endpoints and a frontend dashboard page with charts
showing spending over time, spending by category, and most purchased items.
All product-level aggregation uses `normalized_name` from feature 004 for
accurate cross-store metrics.

## Why

Data collected through scanning is useless without visualization. The dashboard
is the core value proposition of Canasta — the reason a user would choose it
over just keeping receipts.

## Acceptance Criteria

- [ ] `GET /api/analytics/spending-over-time?period=weekly` returns weekly
      totals ordered by date ascending.
- [ ] `GET /api/analytics/spending-over-time?period=monthly` returns monthly
      totals ordered by date ascending.
- [ ] `GET /api/analytics/spending-by-category` returns total spend per
      category, ordered by spend descending.
- [ ] `GET /api/analytics/top-items` returns the most purchased items by
      total spend, using `normalized_name` for aggregation.
- [ ] All endpoints return well-defined Pydantic schemas.
- [ ] Dashboard page renders a line chart for spending over time.
- [ ] Dashboard page renders a bar or pie chart for category breakdown.
- [ ] Dashboard page renders a top items list.
- [ ] Dashboard shows a friendly empty state when no receipts exist yet.
- [ ] Navigation bar connects Upload, History, and Dashboard pages.

## Out of Scope

- Date range filtering on analytics (backlog).
- Export of chart data as CSV (feature 006 backlog).
- Budget goal overlays on charts (backlog).
- Comparison between time periods (backlog).
