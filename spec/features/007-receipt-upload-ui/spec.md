# 007 · Receipt Upload UI

**Status:** done

## What it does

Replaces the "Upload page coming soon" placeholder with a working page: pick
or drag a receipt photo, send it to `POST /api/receipts/scan`, and show the
result — a summary of the extracted items on success, or a clear message on
failure. This is the last of the three pillars from `mission.md` without a
frontend, and the only way a user can currently get data into Canasta is by
calling the API directly.

## Why

Receipt scanning (002), the Dashboard (005), and History (003/006) all
exist, but nothing in the UI lets a user actually scan a receipt. Without
this, Canasta isn't usable end-to-end through the browser at all.

## Acceptance Criteria

- [ ] Upload page has a file picker and drag-and-drop target for JPEG/PNG
      images.
- [ ] Selecting or dropping a file shows an image preview before submitting.
- [ ] Submitting sends the file to `POST /api/receipts/scan` and shows a
      loading state while Gemini processes it.
- [ ] On success (200), shows the extracted receipt: store name, date,
      total, and the item list with categories.
- [ ] On 400 (invalid type / too large), shows the backend's error message.
- [ ] On 409 (duplicate receipt), shows the backend's error message.
- [ ] On 422 (Gemini couldn't read the receipt), shows the backend's error
      message and lets the user try again with a different photo.
- [ ] On 500, shows a generic friendly error and lets the user retry.
- [ ] After a successful scan, the user can navigate to History or
      Dashboard to see the new receipt reflected.
- [ ] Before scanning, if 4+ scans have happened in the last 60 seconds,
      shows a non-blocking warning that the Gemini free tier's per-minute
      limit (5 RPM) is about to be hit.
- [ ] Before scanning, if 19+ scans have happened in the last 24 hours,
      shows a non-blocking warning that the Gemini free tier's daily limit
      (20 RPD) is about to be hit.

## Out of Scope

- Batch upload of multiple receipts at once (v2, per 002's spec).
- Editing extracted items before saving (backlog).
- Drag-and-drop of non-image files with inline validation messaging beyond
  the existing backend error text.
- Progress percentage during upload (a simple loading state is enough —
  Gemini calls are single-shot, not chunked).
- Blocking the user from scanning past the rate-limit warning, or special
  handling of an actual 429 from Gemini — the warning is an advisory
  heuristic (client-tracked, rolling window), not enforcement; an actual
  rate-limit error still falls through to the existing 500 handling.
