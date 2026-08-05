# 004 · Product Normalization Engine — Plan

## Approach

Isolate all normalization logic in a new `backend/normalizer.py` module so it
can be tested independently without touching the database or API. Wire it into
the item insertion flow in `main.py` after the Gemini extraction step.
Reset the database before starting — adding a nullable column to an existing
table is not handled by `ddl-auto=update`.

## Implementation

1. Delete `~/.canasta/canasta.db` and restart the app to recreate tables.
   Run `python backend/seed.py` to restore test data.

2. Add `rapidfuzz` to `requirements.txt` and install.

3. Add `normalized_name: Mapped[Optional[str]]` column to `Item` in
   `backend/models.py` — nullable to support existing rows on schema change.

4. Create `backend/normalizer.py`:
   - `normalize_product_name(name: str) -> str`:
     - Lowercase.
     - Strip leading/trailing whitespace, collapse multiple spaces.
     - Remove store-specific alphanumeric codes via regex
       (e.g. "LN120", "COD12345" — pattern: standalone uppercase+digit tokens).
     - Strip redundant brand prefixes where identifiable.
   - `find_best_match(name: str, existing_names: list[str],
threshold: float = 85) -> str | None`:
     - Use `rapidfuzz.fuzz.ratio` for similarity scoring.
     - Return best match above threshold, or `None` if no match found.

5. Update item insertion in `backend/main.py`:
   - After extracting items from Gemini, normalize each item name.
   - Query all existing `normalized_name` values from the database.
   - Run `find_best_match()` — if match found, use the existing standard name;
     otherwise use the new normalized name.
   - Save `normalized_name` alongside the item.

6. Write `backend/tests/test_normalizer.py` — unit tests for both functions.

## Decisions

- **Threshold at 85%** — chosen as the balance point between false positives
  (wrong match, e.g. "MOZZARELLA LONCHAS" → "MOZZARELLA QUESO") and false
  negatives (missed match, e.g. "YOPRO DRINK" not matched to "YOPRO BEBER").
  Below 80% produces too many wrong merges; above 90% misses obvious variants.
  Adjustable via the `threshold` parameter without code changes.
- **`normalizer.py` isolated from routes** — same rationale as `scanner.py`:
  pure functions are easier to test and replace independently.
- **Nullable `normalized_name`** — avoids a migration script. Existing rows
  stay valid; new rows always get a value. A backfill script is a v2 concern.
- **`rapidfuzz` over `fuzzywuzzy`** — same algorithm, 10-100x faster, no
  dependency on `python-Levenshtein`, MIT licensed.

## Risks

- **Performance at scale** — querying all existing `normalized_name` values
  for every item on every scan will get slow as the database grows. For a
  personal app with hundreds of receipts this is acceptable; for thousands,
  an index or in-memory cache would be needed. Noted, not solved in v1.
- **False positives at 85%** — "TORTITA ARROZ" and "TORTITA MAIZ" could match
  above threshold and be incorrectly merged. Edge case, but worth monitoring
  manually in v1.
- **Regex code-stripping may over-strip** — a pattern like "A1" could be a
  legitimate product abbreviation. Start conservative with the regex and expand
  only when confirmed false positives appear.
