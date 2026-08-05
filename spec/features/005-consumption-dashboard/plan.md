# Plan: 005 · Consumption Dashboard

## 1. Analytics Endpoints (`main.py`)
- `GET /api/analytics/spending-over-time` — weekly/monthly totals.
- `GET /api/analytics/spending-by-category` — category breakdown.
- `GET /api/analytics/top-items` — most purchased items by frequency or spend.

## 2. Frontend (`Dashboard.tsx`)
- Line chart for spending over time.
- Bar/pie chart for category breakdown.
- Table for top items.

## 3. Tests
- Test each analytics endpoint returns correct structure.
