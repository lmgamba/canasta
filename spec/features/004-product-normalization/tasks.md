# 004 · Product Normalization Engine — Tasks

## Database Reset

- [x] Delete `~/.canasta/canasta.db` and restart the app to recreate tables
      with new schema. Run `python -m backend.seed` to restore test data.

## Dependencies

- [x] Add `rapidfuzz` to `requirements.txt` and install.

## Schema

- [x] Add `normalized_name: Mapped[Optional[str]]` (nullable) to `Item`
      in `backend/models.py`.

## Normalizer Module

- [x] Create `backend/normalizer.py` with `normalize_product_name()` —
      lowercase, collapse whitespace, strip alphanumeric codes.
- [x] Add `find_best_match()` to `backend/normalizer.py` —
      fuzzy match using `rapidfuzz`, threshold 85%, returns best match or None.

## Insertion Logic

- [x] Update item insertion in `backend/main.py` to normalize each item name
      before saving.
- [x] Query existing `normalized_name` values and run `find_best_match()`
      before each insert.
- [x] Save `normalized_name` alongside each item.

## Tests

- [x] Create `backend/tests/test_normalizer.py`:
  - [x] `test_normalize_happy_path` — basic lowercase and whitespace collapse.
  - [x] `test_normalize_strips_codes` — removes alphanumeric store codes.
  - [x] `test_normalize_name_that_is_only_a_code_falls_back` — a name that's
        entirely a store code doesn't normalize to an empty string.
  - [x] `test_normalize_strips_code_glued_to_quantity` — a code with no space
        before it (e.g. "300LN120") is still stripped.
  - [x] `test_fuzzy_match_above_threshold` — similar names merge correctly.
  - [x] `test_fuzzy_match_below_threshold` — dissimilar names stay separate.
- [x] Add integration coverage in `backend/tests/test_integration_scan.py`:
  - [x] `test_scan_receipt_persists_normalized_name` — a scanned item is
        saved to the DB with a populated `normalized_name`.
  - [x] `test_scan_receipt_reuses_normalized_name_across_receipts` — a
        near-duplicate name on a later receipt merges into the existing
        standard name end-to-end.

- [x] Run all tests and verify 0 failures (32/32 passed).
- [x] Validate against all acceptance criteria in `spec.md` (5/5 met).
- [x] After all tests, ask for approval to move feature 004 to "Done" in `../../constitution/roadmap.md`.
