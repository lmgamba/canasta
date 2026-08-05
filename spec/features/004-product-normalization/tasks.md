# Tasks: 004 · Product Normalization Engine

## Normalizer
- [ ] Create `backend/normalizer.py` with `normalize_product_name()`.
- [ ] Add `find_best_match()` using `rapidfuzz` to `normalizer.py`.

## Schema
- [ ] Add `normalized_name: Mapped[str]` column to Item in `models.py`.

## Insertion Logic
- [ ] Integrate normalization + fuzzy matching into item insertion in `main.py`.

## Dependencies
- [ ] Add `rapidfuzz` to `requirements.txt` and install.

## Tests
- [ ] Create `test_normalizer.py` — normalize_product_name tests.
- [ ] Create `test_normalizer.py` — find_best_match tests.
