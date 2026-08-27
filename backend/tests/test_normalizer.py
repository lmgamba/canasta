from backend.normalizer import find_best_match, normalize_product_name


def test_normalize_happy_path():
    """Basic lowercase and whitespace collapse."""
    assert normalize_product_name("  YOPRO   DRINK  ") == "yopro drink"


def test_normalize_strips_codes():
    """Standalone alphanumeric store codes are removed."""
    assert normalize_product_name("COD12345 Queso curado") == "queso curado"
    assert normalize_product_name("LN120 Leche entera") == "leche entera"


def test_normalize_name_that_is_only_a_code_falls_back():
    """A name that is nothing but a store code isn't stripped to empty."""
    assert normalize_product_name("LN120") == "ln120"
    assert normalize_product_name("COD12345") == "cod12345"


def test_normalize_strips_code_glued_to_quantity():
    """A code with no space before it (e.g. after a quantity) is still stripped."""
    assert normalize_product_name("YOPRO DRINK 300LN120") == "yopro drink 300"


def test_fuzzy_match_above_threshold():
    """Similar names above 85% threshold merge to the existing standard name."""
    existing = ["mozzarella queso", "leche entera"]
    # "mozzarella lonchas" is 76.9% similar to "mozzarella queso" — below threshold
    assert find_best_match("mozzarella lonchas", existing) is None
    # Exact match returns the standard name
    assert find_best_match("mozzarella queso", existing) == "mozzarella queso"
    # Case-insensitive match (existing names are normalized)
    assert find_best_match("MOZZARELLA QUESO", existing) == "mozzarella queso"


def test_fuzzy_match_below_threshold():
    """Dissimilar names stay separate — no match returned."""
    existing = ["yopro drink", "leche entera"]
    assert find_best_match("tortita arroz", existing) is None
    assert find_best_match("manzanas", existing) is None


def test_fuzzy_match_empty_list():
    """Empty existing names list returns None."""
    assert find_best_match("anything", []) is None