# 004 · Product Normalization Engine — Tasks

## Database Reset

- [ ] Delete `~/.canasta/canasta.db` and restart the app to recreate tables
      with new schema. Run `python backend/seed.py` to restore test data.

## Dependencies

- [ ] Add `rapidfuzz` to `requirements.txt` and install.

## Schema

- [ ] Add `normalized_name: Mapped[Optional[str]]` (nullable) to `Item`
      in `backend/models.py`.

## Normalizer Module

- [ ] Create `backend/normalizer.py` with `normalize_product_name()` —
      lowercase, collapse whitespace, strip alphanumeric codes.
- [ ] Add `find_best_match()` to `backend/normalizer.py` —
      fuzzy match using `rapidfuzz`, threshold 85%, returns best match or None.

## Insertion Logic

- [ ] Update item insertion in `backend/main.py` to normalize each item name
      before saving.
- [ ] Query existing `normalized_name` values and run `find_best_match()`
      before each insert.
- [ ] Save `normalized_name` alongside each item.

## Tests

- [ ] Create `backend/tests/test_normalizer.py`:
  - [ ] `test_normalize_happy_path` — basic lowercase and whitespace collapse.
  - [ ] `test_normalize_strips_codes` — removes alphanumeric store codes.
  - [ ] `test_fuzzy_match_above_threshold` — similar names merge correctly.
  - [ ] `test_fuzzy_match_below_threshold` — dissimilar names stay separate.

- [ ] Run all tests and verify 0 failures.
- [ ] Validate against all acceptance criteria in `spec.md`.
- [ ] After all tests, ask for approval to move feature 004 to "Done" in `../../constitution/roadmap.md`.
