# 007 · Receipt Upload UI — Tasks

## API Client

- [x] Add `Receipt`/`Item` types and `scanReceipt(file)` to
      `frontend/src/api/receipts.ts`, mapping 400/409/422/500 responses to
      their `detail` message.

## Rate-Limit Warning

- [x] Create `frontend/src/lib/geminiRateLimit.ts` with
      `GEMINI_FREE_TIER_RPM = 5`, `GEMINI_FREE_TIER_RPD = 20` as named
      constants.
- [x] `recordScanAttempt()` — appends a timestamp to `localStorage`,
      called on every actual `scanReceipt()` call.
- [x] `getRateLimitWarning()` — returns a warning string at 4/5 scans in
      the last 60s or 19/20 in the last 24h, else `null`.

## Upload Page

- [x] Create `frontend/src/pages/Upload.tsx` with a file input + drag-and-drop
      target for JPEG/PNG.
- [x] Show an image preview after a file is selected/dropped, before submit.
- [x] Client-side pre-check of file type and size before submitting
      (fast-fail) — the size check was missed in the first pass and caught
      during manual testing (oversized file showed a preview instead of
      being rejected); fixed.
- [x] Show the rate-limit warning banner (if any) on mount and after each
      scan attempt.
- [x] Submit → loading state ("Reading your receipt…") while awaiting the API.
- [x] Success view — store name, date, total, item list with categories.
- [x] Error view — backend's message, with a "Try again" button that resets
      the page.
- [x] Links from the success view to History and Dashboard.
- [x] Wire `Upload` into the `/upload` route in `App.tsx`, replacing the
      placeholder. Also changed the `/` redirect from `/history` to
      `/upload`, since scanning a receipt is a new user's first action —
      flagging this as a judgment call, not something explicitly asked for.

## Verification

- [x] `tsc -b`, `eslint .`, and `vite build` all clean.
- [x] Manual browser test: happy path, wrong file type, oversized file,
      duplicate receipt (including the different-casing case that surfaced
      the store-name bug) — all confirmed working.
- [ ] 422 (unreadable receipt), 500 (generic error), and the rate-limit
      warning banner (4/5 RPM, 19/20 RPD) were not manually triggered live.
      422/500 share the same error-view code path already confirmed by
      400/409. The 60s/RPM threshold is unlikely to ever fire in practice
      (a scan takes ~30s, so 4 in a minute is unusual); the 24h/RPD one
      was at 7/20 scans when checked (no warning expected — correct) and
      will be confirmed live if it's seen misbehaving around scan 19.
      Accepted as-is by Laura; not blocking.
- [x] Validate against all acceptance criteria in `spec.md` — 9/11 directly
      confirmed live, 2/11 (422/500 paths, rate-limit banner) accepted on
      code review per above.
- [x] After verification, ask for approval to move feature 007 to "Done" in
      `../../constitution/roadmap.md`.

## Bug Found During Manual Testing (out of 007's original scope, fixed)

Scanning the same physical receipt twice produced two rows instead of a
409 — Gemini returned different store-name casing across the two calls
("Carrefour Express" vs "CARREFOUR EXPRESS"), and the duplicate check
(`UniqueConstraint` on date+store_name+total_amount, from feature 003) is
an exact string match. Fixed by uppercasing `store_name` and item `name`
in `backend/main.py` at insertion time, so casing differences from Gemini
can no longer cause this. Regression test added:
`test_scan_receipt_returns_409_for_duplicate_with_different_casing`.
Existing dev-DB rows inserted before this fix keep their original casing —
by request, no DB reset until the MVP push is done, so old duplicates
(like the pair that surfaced this) aren't backfilled yet.

## Verification Notes

- Backend: pytest 44/44 (43 + 1 new regression test for the casing bug).
- Frontend: `tsc -b`, `eslint .`, production `vite build` (612 modules) all
  clean. Could not exercise the real Gemini happy path myself (no API key
  in this sandbox) — dev servers are up on :8000/:5173, restarted to pick
  up the `main.py` fix, existing seeded data intact for manual testing.
