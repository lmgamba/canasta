# Roadmap

## Done ✅

1. **001 · Project Setup** — initialize repo, folder structure, backend skeleton, 
   frontend skeleton, database connection, and AGENTS.md.

## Current 🔜

2. **002 · Receipt Scanner** — upload a receipt image, send to Google Gemini 2.5 Flash (Vision), 
   extract and save items to the database.

## Backlog 💡

3. **003 · Receipt History** — list all scanned receipts with date, store name, 
   total, and item count.
4. **004 · Consumption Dashboard** — charts and stats showing spending by category, 
   most purchased items, and weekly/monthly trends.
5. **005 · Item Detail View** — click any item to see its full purchase history 
   across all receipts.

## v2 Ideas 💡

- **Health angle** — flag ultra-processed vs whole foods, track fresh produce ratio.
- **Budget goals** — set a monthly limit per category and get warnings.
- **Export** — download your data as CSV.
- **Multi-receipt batch scan** — upload several receipts at once.

> Each feature folder lives in `spec/features/NNN-name/` with `spec.md`, 
> `plan.md`, and `tasks.md` before any code is written.