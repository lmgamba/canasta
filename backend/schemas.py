from datetime import date, datetime

from pydantic import BaseModel, Field

from backend.models import Category


# ── Item schemas ────────────────────────────────────────────────

class ItemCreate(BaseModel):
    """Schema for creating a single item on a receipt."""

    name: str = Field(..., min_length=1, description="Product name from the receipt")
    quantity: float = Field(default=1.0, gt=0, description="Quantity purchased (e.g. 0.5 for half a kilogram)")
    unit_price: float = Field(..., ge=0, description="Price per unit")
    total_price: float = Field(..., ge=0, description="Total price for this line item")
    category: Category = Field(..., description="Category assigned by the LLM")


class ItemRead(ItemCreate):
    """Schema for returning an item from the database."""

    id: int
    receipt_id: int


# ── Receipt schemas ─────────────────────────────────────────────

class ReceiptCreate(BaseModel):
    """Schema for creating a new receipt with its items."""

    receipt_date: date = Field(..., description="Date printed on the receipt")
    store_name: str = Field(..., min_length=1, description="Name of the store")
    total_amount: float = Field(..., ge=0, description="Total amount spent")
    image_path: str | None = Field(default=None, description="Path to the uploaded receipt image")
    items: list[ItemCreate] = Field(default_factory=list, description="Line items on the receipt")


class ReceiptRead(BaseModel):
    """Schema for returning a receipt from the database."""

    id: int
    receipt_date: date
    store_name: str
    total_amount: float
    image_path: str | None
    created_at: datetime
    items: list[ItemRead] = []

    model_config = {"from_attributes": True}


class ReceiptSummary(BaseModel):
    """Schema for the receipt history list — one row per receipt.

    item_count is computed with an aggregate query, not stored on the row.
    """

    id: int
    receipt_date: date
    store_name: str
    total_amount: float
    item_count: int


# ── Analytics schemas ───────────────────────────────────────────

class SpendingOverTimeItem(BaseModel):
    """One point in the spending-over-time series."""

    period_label: str = Field(..., description="ISO week (YYYY-WW) or month (YYYY-MM) label")
    total_amount: float = Field(..., description="Total amount spent in this period")


class SpendingByCategoryItem(BaseModel):
    """Total spend within a single category."""

    category: str = Field(..., description="Item category")
    total_amount: float = Field(..., description="Total amount spent in this category")


class TopItem(BaseModel):
    """One row in the most-purchased-items ranking."""

    normalized_name: str = Field(..., description="Normalized product name")
    total_spend: float = Field(..., description="Total amount spent on this product")
    purchase_count: int = Field(..., description="Number of line items recorded for this product")
