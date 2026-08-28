"""Seed the database with controlled test receipts.

Dev-only utility. Deletes all existing rows, then inserts a small set of
realistic receipts representing different edge cases:

  Receipt A — fruits, dairy, meat across categories.
  Receipt B — fractional quantities (0.5 kg cheese).
  Receipt C — identical (date, store, total) to Receipt A, so it triggers the
              unique-constraint (HTTP 409 duplicate) path.

Usage (run from the project root so the `backend` package is importable):
    rm ~/.canasta/canasta.db   # or let tables be recreated on next boot
    python -m backend.seed
"""

from datetime import date

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from backend.database import SessionLocal, engine
from backend.models import Base, Category, Item, Receipt


def _reset_tables() -> None:
    """Remove all rows without dropping the schema (idempotent on empty DB)."""
    with SessionLocal() as db:
        db.execute(delete(Item))
        db.execute(delete(Receipt))
        db.commit()


def _build_receipt(
    receipt_date: date,
    store_name: str,
    total_amount: float,
    items: list[dict],
) -> Receipt:
    """Build a Receipt with all its Item rows (not yet persisted)."""
    receipt = Receipt(
        receipt_date=receipt_date,
        store_name=store_name,
        total_amount=total_amount,
    )
    for item_data in items:
        receipt.items.append(
            Item(
                name=item_data["name"],
                quantity=item_data.get("quantity", 1.0),
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
                category=Category(item_data["category"]),
            )
        )
    return receipt


def seed() -> None:
    """Wipe the database and insert the controlled receipt set."""
    # Create tables if the database file was freshly deleted.
    Base.metadata.create_all(bind=engine)
    _reset_tables()

    receipt_a = _build_receipt(
        receipt_date=date(2025, 1, 15),
        store_name="Mercadona",
        total_amount=23.45,
        items=[
            {
                "name": "Manzanas",
                "quantity": 1.0,
                "unit_price": 2.30,
                "total_price": 2.30,
                "category": "Fruits",
            },
            {
                "name": "Pechuga de pollo",
                "quantity": 0.75,
                "unit_price": 6.20,
                "total_price": 4.65,
                "category": "Meat",
            },
            {
                "name": "Tomates",
                "quantity": 1.0,
                "unit_price": 1.80,
                "total_price": 1.80,
                "category": "Vegetables",
            },
        ],
    )
    receipt_b = _build_receipt(
        receipt_date=date(2025, 1, 16),
        store_name="Carrefour",
        total_amount=8.40,
        items=[
            {
                "name": "Queso curado",
                "quantity": 0.5,
                "unit_price": 12.80,
                "total_price": 6.40,
                "category": "Dairy",
            },
            {
                "name": "Leche entera",
                "quantity": 1.0,
                "unit_price": 2.00,
                "total_price": 2.00,
                "category": "Dairy",
            },
        ],
    )

    with SessionLocal() as db:
        db.add_all([receipt_a, receipt_b])
        db.commit()
        print(f"Seeded {len([receipt_a, receipt_b])} receipts (A and B).")

    # Deliberately attempt to insert a receipt whose (date, store, total)
    # matches Receipt A. The unique constraint rejects it, proving the
    # duplicate-detection path works — this prints but does not fail the seed.
    receipt_c = _build_receipt(
        receipt_date=date(2025, 1, 15),
        store_name="Mercadona",
        total_amount=23.45,
        items=[
            {
                "name": "Manzanas",
                "quantity": 1.0,
                "unit_price": 2.30,
                "total_price": 2.30,
                "category": "Fruits",
            },
        ],
    )
    try:
        with SessionLocal() as db:
            db.add(receipt_c)
            db.commit()
        print("Unexpected: duplicate receipt was inserted without conflict.")
    except IntegrityError:
        print("Duplicate receipt (A duplicate) correctly rejected by unique constraint.")


if __name__ == "__main__":
    seed()