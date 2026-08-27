# Roadmap

## Done ✅

1. **001 · Project Setup** — initialize repo, folder structure, backend skeleton, 
   frontend skeleton, database connection, and AGENTS.md.
2. **002 · Receipt Scanner** — upload a receipt image, send to Google Gemini 3.6 Flash (Vision), 
   extract and save items to the database.
3. **003 · DB Hardening & Receipt History** — Add DB constraints for duplicate receipts 
   `(date, store, total)` and items. Build history list (date, store, total, item count) 
   with delete capability (great for cleaning test scans!).
4. **004 · Product Normalization Engine** — Add name cleaning & fuzzy matching (`rapidfuzz`) 
   to map store-specific names (e.g., "PECHUGA PAVO 1954") to unified master products 
   before feeding the dashboard.
5. **005 · Consumption Dashboard** — Analytics endpoints (spending over time, by category, 
   top items) and a Dashboard page with Recharts line/bar charts and a top-items table.

## Current 🔜

## Backlog 💡

6. **006 · Item Detail View** — Click any item to see its full purchase history across 
   all receipts.

## v2 Ideas 💡

- **Health angle** — flag ultra-processed vs whole foods, track fresh produce ratio.
- **Budget goals** — set a monthly limit per category and get warnings.
- **Export** — download your data as CSV.
- **Multi-receipt batch scan** — upload several receipts at once.

> Each feature folder lives in `spec/features/NNN-name/` with `spec.md`, 
> `plan.md`, and `tasks.md` before any code is written.
