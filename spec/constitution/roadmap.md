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
6. **006 · Item Detail View** — Purchase-history endpoint and page, reachable from the 
   Dashboard top items list. Introduced `react-router-dom` for real routing.
7. **007 · Receipt Upload UI** — Upload page (file picker, drag-and-drop, preview, 
   success/error views) plus a client-side Gemini free-tier rate-limit warning. 
   Closes the last gap in `mission.md`'s three pillars — **Canasta is now a 
   functional MVP**, usable end-to-end through the browser.

## Current 🔜

## Backlog 💡

- **008 · Multi-Receipt Batch Upload** — accept multiple images at once on the Upload 
  page, looping the existing single-receipt endpoint per file. Deferred from 007 to 
  keep that feature's scope to a single, provable upload flow first.
- **DB reset for pre-007 mixed-case rows** — `store_name`/item `name` are uppercased 
  going forward (007's fix), but rows inserted before it keep their original casing. 
  Deliberately deferred until the MVP push is fully done, per Laura's call.

## v2 Ideas 💡

- **Health angle** — flag ultra-processed vs whole foods, track fresh produce ratio.
- **Budget goals** — set a monthly limit per category and get warnings.
- **Export** — download your data as CSV.
- **Multi-receipt batch scan** — upload several receipts at once.

> Each feature folder lives in `spec/features/NNN-name/` with `spec.md`, 
> `plan.md`, and `tasks.md` before any code is written.
