import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.models import Category

# Load environment variables from .env file so GEMINI_API_KEY is available
load_dotenv()

# Initialize the Gemini client with the API key from the environment.
# The client handles auth, retries, and connection pooling.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 3.6 Flash — fast, cheap, and capable of reading images.
MODEL_NAME = "gemini-3.6-flash"

# Mapping from strings Gemini typically returns to our Category enum values.
# Gemini may return variations like "dairy products" or "Dairy" — this map
# normalizes them to the exact enum value we store in the database.
CATEGORY_MAP: dict[str, Category] = {
    # Fruits & Vegetables
    "fruits": Category.FRUITS,
    "fruit": Category.FRUITS,
    "fresh fruits": Category.FRUITS,
    "vegetables": Category.VEGETABLES,
    "vegetable": Category.VEGETABLES,
    "fresh vegetables": Category.VEGETABLES,
    "produce": Category.VEGETABLES,
    # Carbs & Grains
    "carbs": Category.CARBS_GRAINS,
    "grains": Category.CARBS_GRAINS,
    "carbs & grains": Category.CARBS_GRAINS,
    "bread": Category.CARBS_GRAINS,
    "bakery": Category.CARBS_GRAINS,
    "cereal": Category.CARBS_GRAINS,
    "pasta": Category.CARBS_GRAINS,
    "rice": Category.CARBS_GRAINS,
    # Meat
    "meat": Category.MEAT,
    "beef": Category.MEAT,
    "pork": Category.MEAT,
    "chicken": Category.MEAT,
    "poultry": Category.MEAT,
    # Fish & Seafood
    "fish": Category.FISH_SEAFOOD,
    "seafood": Category.FISH_SEAFOOD,
    "fish & seafood": Category.FISH_SEAFOOD,
    # Dairy
    "dairy": Category.DAIRY,
    "dairy products": Category.DAIRY,
    "milk": Category.DAIRY,
    "cheese": Category.DAIRY,
    "yogurt": Category.DAIRY,
    "butter": Category.DAIRY,
    # Protein Snacks
    "protein snacks": Category.PROTEIN_SNACKS,
    "protein": Category.PROTEIN_SNACKS,
    "nuts": Category.PROTEIN_SNACKS,
    "seeds": Category.PROTEIN_SNACKS,
    # Sweets
    "sweets": Category.SWEETS,
    "candy": Category.SWEETS,
    "chocolate": Category.SWEETS,
    "dessert": Category.SWEETS,
    "snacks": Category.SWEETS,
    # Beverages
    "beverages": Category.BEVERAGES,
    "drinks": Category.BEVERAGES,
    "juice": Category.BEVERAGES,
    "soda": Category.BEVERAGES,
    "water": Category.BEVERAGES,
    "coffee": Category.BEVERAGES,
    "tea": Category.BEVERAGES,
    # Frozen Veggies
    "frozen veggies": Category.FROZEN_VEGGIES,
    "frozen vegetables": Category.FROZEN_VEGGIES,
    # Other Frozen
    "frozen": Category.OTHER_FROZEN,
    "frozen food": Category.OTHER_FROZEN,
    "frozen foods": Category.OTHER_FROZEN,
    "ice cream": Category.OTHER_FROZEN,
    # Cleaning
    "cleaning": Category.CLEANING,
    "cleaning products": Category.CLEANING,
    "household": Category.CLEANING,
    "detergent": Category.CLEANING,
    # Personal Care
    "personal care": Category.PERSONAL_CARE,
    "hygiene": Category.PERSONAL_CARE,
    "toiletries": Category.PERSONAL_CARE,
    "health": Category.PERSONAL_CARE,
}


def map_category(raw_category: str) -> Category:
    """Map a category string from Gemini to a valid Category enum value.

    Falls back to Category.OTHER if the string doesn't match any known
    category in our mapping. The comparison is case-insensitive.
    """
    normalized = raw_category.strip().lower()
    return CATEGORY_MAP.get(normalized, Category.OTHER)


# The prompt instructs Gemini to return only valid JSON with specific fields.
# We use text + image as a multimodal input so Gemini can both read the
# receipt image and understand the structured output format we need.
SCAN_PROMPT = """\
You are a receipt scanner. Analyze this supermarket receipt image and extract \
all information as strict JSON. Do not include any text outside the JSON.

Return ONLY a JSON object with this exact structure:
{
  "store_name": "string — name of the store",
  "date": "YYYY-MM-DD — date printed on the receipt",
  "total_amount": number — total amount spent,
  "items": [
    {
      "name": "string — product name",
      "quantity": number — quantity purchased (use 1 if not visible),
      "unit_price": number — price per unit,
      "total_price": number — total price for this line item,
      "category": "string — one of: Fruits, Vegetables, Carbs & Grains, Meat, Fish & Seafood, Dairy, Protein Snacks, Sweets, Beverages, Frozen Veggies, Other Frozen, Cleaning, Personal Care, Other"
    }
  ]
}

Rules:
- If you cannot read the receipt clearly, return {"error": "Could not read the receipt"}.
- Use the exact category strings listed above — do not invent new ones.
- If a field is unclear, make your best estimate based on what you can see.
- All prices should be numbers (not strings).
"""


def scan_receipt(image_bytes: bytes) -> dict:
    """Send a receipt image to Gemini 2.5 Flash and parse the response.

    Args:
        image_bytes: Raw bytes of the receipt image (JPEG, PNG, etc.).

    Returns:
        A dict with keys: store_name, date, total_amount, items.
        Each item has: name, quantity, unit_price, total_price, category.

    Raises:
        ValueError: If Gemini returns invalid JSON or an error response.
    """
    # Wrap the raw image bytes in a Gemini Part object.
    # This tells Gemini the data is an image with the given MIME type.
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    # Send the image and prompt to Gemini in a single request.
    # The response contains the model's text output which should be JSON.
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[SCAN_PROMPT, image_part],
    )

    # Extract the text from Gemini's response and strip whitespace.
    raw_text = response.text.strip()

    # Try to parse the response as JSON.
    # Gemini may sometimes wrap JSON in markdown code fences — strip those.
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            "Could not read the receipt. Please upload a clearer photo."
        ) from e

    # If Gemini returned an error object instead of receipt data,
    # convert it to a ValueError with a user-friendly message.
    if "error" in parsed:
        raise ValueError(
            "Could not read the receipt. Please upload a clearer photo."
        )

    # Map each item's category string to a valid Category enum value.
    # Unknown categories default to Category.OTHER.
    for item in parsed.get("items", []):
        raw_cat = item.get("category", "Other")
        item["category"] = map_category(raw_cat).value

    return parsed
