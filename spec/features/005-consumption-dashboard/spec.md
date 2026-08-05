# 005 · Consumption Dashboard

## Problem
Users have no visibility into their spending patterns after scanning receipts.
Data sits in the database without any visual analysis.

## Goal
Display charts and stats showing spending by category, most purchased items,
and weekly/monthly trends, using normalized product names for accurate cross-store
aggregation.

## Acceptance Criteria
- Dashboard shows total spending over time (weekly/monthly line chart).
- Spending breakdown by category (pie or bar chart).
- Most purchased items list (by frequency or total spend).
- All charts use `normalized_name` for product-level aggregation.

## Scope
- `backend/main.py` — analytics endpoints
- `frontend/src/pages/Dashboard.tsx` — charts and stats
- `frontend/src/components/` — chart components
