# 007 · Receipt Upload UI — Plan

## Approach

No backend changes — `POST /api/receipts/scan` already handles validation,
Gemini extraction, and persistence (feature 002/003). This is purely a
frontend page: file input → preview → submit → render one of
(loading | success | error).

## Implementation

1. Add `scanReceipt(file)` and a full `Receipt`/`Item` type to
   `frontend/src/api/receipts.ts`, alongside the existing
   `fetchReceipts`/`deleteReceipt`. Maps backend error responses (400, 409,
   422, 500) to their `detail` message; anything else to a generic message.

2. Create `frontend/src/pages/Upload.tsx`:
   - Local state machine: `idle | previewing | uploading | success | error`.
   - File input (`accept="image/jpeg,image/png"`) plus a drag-and-drop
     target over the same drop zone.
   - On file selection: validate it's a JPEG/PNG client-side (fast-fail
     before hitting the network), generate an object URL for preview.
   - On submit: call `scanReceipt`, show a loading state (Gemini calls take
     a few seconds), then render success or error.
   - Success view: store name, date, total, item list with category badges,
     and links to History/Dashboard.
   - Error view: the message from the API, with a "Try again" button that
     resets to `idle`.

3. Wire `Upload` into `App.tsx`'s `/upload` route, replacing the placeholder
   paragraph.

4. No new dependencies — plain `<input type="file">` and drag events are
   sufficient; not pulling in a dropzone library for this.

5. Create `frontend/src/lib/geminiRateLimit.ts`:
   - Constants `GEMINI_FREE_TIER_RPM = 5` and `GEMINI_FREE_TIER_RPD = 20`,
     commented as the confirmed free-tier limits for `gemini-3.6-flash` —
     a one-line change if the tier changes.
   - `recordScanAttempt()`: appends `Date.now()` to a `localStorage` array
     (key `canasta-scan-timestamps`), called right before each
     `scanReceipt()` call — this tracks actual Gemini calls, not merely
     file selections that fail client-side validation.
   - `getRateLimitWarning()`: prunes entries older than 24h, counts entries
     within the last 60s and within the last 24h, returns a warning string
     if either count is at `n-1` of its limit (4/5 RPM or 19/20 RPD), else
     `null`. Checked on `Upload` page mount and again right after each
     scan attempt, so the banner updates live.

6. Write `frontend/src/pages/Upload.test.tsx`? — no, this repo has no
   frontend test suite in v1 (per `tech-stack.md`). Skip; verify manually
   in a real browser instead, same as 005/006.

## Decisions

- **No new frontend dependency for drag-and-drop** — native HTML5 drag
  events (`onDragOver`/`onDrop`) plus a plain file input cover this without
  adding a library for a single drop zone.
- **Client-side type/size pre-check before the network call** — the backend
  already validates (magic bytes, 5 MB limit), but rejecting an obviously
  wrong file (e.g. a `.txt`) instantly, without a round-trip, is a better
  experience. The backend remains the source of truth; this is a fast-fail
  convenience only, not a replacement for its validation.
- **Object URL for preview, revoked on unmount/reset** — avoids reading the
  whole file into a data URL just to preview it.
- **One page, one state machine** — no separate "preview" and "result"
  routes; keeps the upload flow on a single URL, consistent with how
  History and Dashboard are single pages with internal loading/error state.
- **`localStorage`, not backend tracking, for the rate-limit warning** —
  Canasta is single-user and local-first; there's no session or auth to
  hang server-side tracking off of, and the thing being warned about
  (Gemini's own quota) is inherently a client-of-Gemini concern, not
  something the backend needs to persist. A rolling window is a reasonable
  approximation of Google's actual reset behavior (fixed at midnight
  Pacific) — see Risks.
- **Warn at n-1, don't block** — the count is this browser's own record of
  attempts, not the real-time quota Google is enforcing (could be behind if
  a request was made another way, e.g. curl). Blocking on a guess would be
  worse than an occasional missed warning.

## Risks

- **Gemini latency** — a scan can take several seconds; the loading state
  must make it clear the app hasn't frozen (spinner + "Reading your
  receipt…" copy, not just a disabled button).
- **Large images on slow connections** — the existing 5 MB cap and
  magic-byte check are already in place server-side; nothing new needed
  here beyond surfacing the resulting error clearly.
- **Rolling 24h window vs. Google's midnight-Pacific reset** — the daily
  warning can be conservative (warns before Google would actually reset)
  or lenient (Google already reset hours ago but the local window hasn't
  rolled off yet) by up to a few hours. Acceptable for an advisory warning;
  not worth the complexity of timezone-aware reset logic in v1.
- **`localStorage` cleared or a second browser/device used** — the count
  resets to zero, silently under-warning. Acceptable given this is a
  single-user local app typically used from one browser.
