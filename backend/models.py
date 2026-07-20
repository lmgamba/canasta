import enum
from datetime import UTC, date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


# All valid item categories assigned by the LLM during receipt scanning
class Category(str, enum.Enum):
    FRUITS = "Fruits"
    VEGETABLES = "Vegetables"
    CARBS_GRAINS = "Carbs & Grains"
    MEAT = "Meat"
    FISH_SEAFOOD = "Fish & Seafood"
    DAIRY = "Dairy"
    PROTEIN_SNACKS = "Protein Snacks"
    SWEETS = "Sweets"
    BEVERAGES = "Beverages"
    FROZEN_VEGGIES = "Frozen Veggies"
    OTHER_FROZEN = "Other Frozen"
    CLEANING = "Cleaning"
    PERSONAL_CARE = "Personal Care"
    OTHER = "Other"


class Receipt(Base):
    __tablename__ = "receipts"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_receipt_total_amount_non_negative"),
    )

    # Unique identifier for each receipt
    id: Mapped[int] = mapped_column(primary_key=True)

    # The date printed on the receipt (not when it was scanned)
    date: Mapped[date] = mapped_column(Date)

    # Name of the store where the receipt was issued
    store_name: Mapped[str] = mapped_column(String)

    # Total amount spent on this receipt
    total_amount: Mapped[float] = mapped_column(Float)

    # File path to the uploaded receipt image (nullable because it is
    # discarded after the LLM extracts data from it)
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)

    # Timestamp when this receipt record was created in the database
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    # All items belonging to this receipt (one-to-many)
    items: Mapped[list["Item"]] = relationship(back_populates="receipt")


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        CheckConstraint(
            "category IN ('Fruits','Vegetables','Carbs & Grains','Meat',"
            "'Fish & Seafood','Dairy','Protein Snacks','Sweets','Beverages',"
            "'Frozen Veggies','Other Frozen','Cleaning','Personal Care','Other')",
            name="ck_item_category_valid",
        ),
    )

    # Unique identifier for each item
    id: Mapped[int] = mapped_column(primary_key=True)

    # Name of the product as it appears on the receipt
    name: Mapped[str] = mapped_column(String)

    # Quantity purchased — Float because receipts can show fractional
    # amounts (e.g. 0.5 kg of cheese, 1.2 litres of milk)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)

    # Price per unit of the product
    unit_price: Mapped[float] = mapped_column(Float)

    # Total price for this line item (quantity × unit_price)
    total_price: Mapped[float] = mapped_column(Float)

    # Category assigned by the LLM — one of the Category enum values.
    # values_callable stores the display value (e.g. "Dairy") not the
    # member name (e.g. "DAIRY") so it matches the CHECK constraint.
    category: Mapped[Category] = mapped_column(
        Enum(Category, values_callable=lambda x: [e.value for e in x])
    )

    # Foreign key linking this item back to its parent receipt
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"))

    # The receipt this item belongs to (many-to-one)
    receipt: Mapped["Receipt"] = relationship(back_populates="items")
