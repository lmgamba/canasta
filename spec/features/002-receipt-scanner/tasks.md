# 002 · Receipt Scanner — Tasks

- [x] Create `backend/scanner.py` — Gemini client initialization, 
      `scan_receipt(image_bytes: bytes) -> dict` function skeleton.
- [x] Write the Gemini prompt in `scanner.py` — structured JSON output 
      with all required fields and category instructions.
- [x] Add category mapping in `scanner.py` — map Gemini output to 
      valid Category enum values, default to `Other` if unrecognized.
- [x] Add `POST /api/receipts/scan` route in `backend/main.py` — 
      accept `UploadFile`, validate image type and size (max 10MB).
- [x] Connect route to `scanner.scan_receipt()` and persist 
      Receipt + Items in a single db transaction.
- [x] Return `ReceiptRead` schema with nested items on success.
- [x] Add error handling for: invalid file type (400), Gemini parse 
      failure (422), unexpected errors (500) — all with user-friendly messages.
- [x] Write `backend/tests/test_scanner.py` — mock Gemini to test 
      JSON parsing, category mapping, and error handling without real API calls.
- [x] Write `backend/tests/integration_test_scan.py` — test full endpoint 
      with a sample receipt image, verify Receipt and Items saved to db.
- [x] Run all tests and verify 0 failures.
- [x] Validate against all acceptance criteria in `spec.md`.
- [x] Move feature 002 to "Done" in `../../constitution/roadmap.md`.


