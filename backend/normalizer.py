"""Product name normalization for cross-store aggregation.

Provides two functions:

- normalize_product_name — cleans raw receipt text (lowercase, collapse
  whitespace, strip store-specific alphanumeric codes).
- find_best_match — fuzzy-matches a cleaned name against a list of existing
  standard names using rapidfuzz, returning the best match above a
  configurable similarity threshold.
"""

import re

from rapidfuzz import fuzz


# Pattern: uppercase-letter + digit tokens (e.g. LN120, COD12345), typically
# store internal codes rather than part of the product name. The negative
# lookbehind (rather than \b) on the left lets this match codes glued
# directly onto a preceding quantity (e.g. "300LN120"), while still
# refusing to split a code out of the middle of a longer word.
_CODE_PATTERN = re.compile(r"(?<![A-Za-z])[A-Z]{1,4}\d{2,5}\b")


def normalize_product_name(name: str) -> str:
    """Clean a raw product name into a normalized form.

    Steps:
      1. Strip leading/trailing whitespace and collapse multiple spaces.
      2. Remove store-specific alphanumeric codes (e.g. "LN120", "COD12345").
         Must run before lowercasing so the pattern matches uppercase codes.
         If the name is nothing but a code, skip this step — an empty
         normalized name would silently merge unrelated products under "".
      3. Lowercase.

    >>> normalize_product_name("  YOPRO DRINK 300LN120  ")
    'yopro drink 300'
    """
    result = name.strip()
    result = re.sub(r"\s+", " ", result)
    stripped = _CODE_PATTERN.sub("", result).strip()
    if stripped:
        result = stripped
    result = result.lower()
    return result


def find_best_match(
    name: str,
    existing_names: list[str],
    threshold: float = 85.0,
) -> str | None:
    """Fuzzy-match a name against existing normalized names.

    Uses rapidfuzz's token_set_ratio which is resilient to word reordering
    and partial overlaps (useful when "YOPRO DRINK" vs "YOPRO BEBER DANONE"
    share tokens but differ in order).

    The input name is normalized (lowercased) before comparison so the
    matcher is case-insensitive.

    Returns the best matching name above `threshold`, or None if no match.
    """
    if not existing_names:
        return None

    normalized = normalize_product_name(name)
    best_match = None
    best_score = 0.0

    for existing in existing_names:
        score = fuzz.token_set_ratio(normalized, existing)
        if score > best_score:
            best_score = score
            best_match = existing

    if best_score >= threshold:
        return best_match
    return None