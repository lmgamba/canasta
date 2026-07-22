# 002 · Receipt Scanner — Plan

## Approach

Create a single endpoint that receives an image, passes it to Gemini Vision 
with a carefully structured prompt, parses the JSON response, and persists 
the data. All Gemini logic lives in `backend/scanner.py` — isolated from 
the route so it can be tested and replaced independently.

## Implementation

1. Create `backend/scanner.py` — initialize Gemini client from `GEMINI_API_KEY`, 
   define `scan_receipt(image_bytes: bytes) -> dict` function.
2. Write the Gemini prompt in `scanner.py` — instruct the model to return 
   strict JSON with fields: `store_name`, `date`, `total_amount`, `items[]` 
   (each with `name`, `quantity`, `unit_price`, `total_price`, `category`).
3. Add category mapping in `scanner.py` — map Gemini's category output 
   to the 14 valid Category enum values. Default to `Other` if unrecognized.
4. Add `POST /api/receipts/scan` route in `backend/main.py` — accept 
   `UploadFile`, validate it is an image, call `scanner.scan_receipt()`, 
   persist Receipt + Items in a single db transaction, return `ReceiptRead`.
5. Add error handling — `HTTPException(400)` for invalid file type, 
   `HTTPException(422)` for Gemini parse failure, 
   `HTTPException(500)` for unexpected errors with user-friendly messages.
6. Write `backend/tests/test_scanner.py` — mock Gemini API to test 
   parsing logic without real API calls.
7. Write integration test in `backend/tests/integration_test_scan.py` — 
   test the full endpoint with a real sample receipt image.

## Decisions

- **Gemini response as JSON** — prompt instructs Gemini to return only valid JSON. 
  Safer than parsing free text. If JSON parsing fails, return user-friendly error.
- **`scanner.py` isolated from routes** — keeps the route thin and makes 
  the Gemini logic independently testable with mocks.
- **Images processed in memory, never saved** — per AGENTS.md hard limits. 
  Use `await file.read()` and pass bytes directly to Gemini.
- **Single db transaction for Receipt + Items** — if saving any item fails, 
  the whole receipt rolls back. No partial data in the database.
- **Default category `Other`** — Gemini may return categories that don't 
  match exactly. Map known variants, default unknown to `Other` rather than failing.

## Risks

- **Gemini returns malformed JSON** — mitigated by wrapping parse in try/except 
  and returning a user-friendly error message.
- **Gemini misreads handwritten or blurry receipts** — out of scope for v1, 
  documented in README as a known limitation.
- **Category mismatch between Gemini output and enum** — mitigated by 
  category mapping + `Other` fallback in `scanner.py`.
- **Large image files** — add file size validation (max 10MB) at the 
  route level before sending to Gemini.