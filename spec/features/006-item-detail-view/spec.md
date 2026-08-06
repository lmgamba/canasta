# 006 · Item Detail View

**Status:** proposed

## What it does

Provides an endpoint and frontend page showing the complete purchase history
of a single product across all receipts and stores. Accessible by clicking
any item in the Dashboard top items list or the History item breakdown.
Uses `normalized_name` to group variants of the same product.

## Why

Knowing total spending by category is useful, but knowing exactly how often
you buy a specific product, at what price, and from which store is more
actionable. This is the drill-down layer that makes the dashboard meaningful.

## Acceptance Criteria

- [ ] `GET /api/items/purchases?name={normalized_name}` returns all purchases
      of that product across all receipts.
- [ ] Response includes aggregate stats: `total_spend` and `purchase_count`.
- [ ] Response includes per-purchase detail: date, store name, quantity,
      unit price, total price — ordered by date descending.
- [ ] Endpoint returns HTTP 404 with a clear message if no purchases exist
      for the given name.
- [ ] Frontend `ItemDetail` page renders aggregate stats in a header.
- [ ] Frontend renders a table of all purchases with date, store, quantity,
      unit price, and total price.
- [ ] Page is reachable by clicking an item in the Dashboard top items list.
- [ ] Page has a back button that returns the user to the previous page.

## Out of Scope

- Price trend chart over time for a single product (backlog).
- Comparison between stores for the same product (backlog).
- Entry point from History page item breakdown (backlog — add in a future pass).
- Editing or deleting individual item purchases (backlog).
