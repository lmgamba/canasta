from contextlib import asynccontextmanager
from datetime import date
from typing import Literal

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from backend.database import Base, engine, get_db
from backend.models import Item, Receipt
from backend.normalizer import find_best_match, normalize_product_name
from backend.schemas import (
    ReceiptRead,
    ReceiptSummary,
    SpendingByCategoryItem,
    SpendingOverTimeItem,
    TopItem,
)
from backend.scanner import scan_receipt


# Create all database tables (Receipt, Item) on application startup.
# This runs once when the server boots — safe to call repeatedly because
# CREATE TABLE IF NOT EXISTS is idempotent.
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Canasta", lifespan=lifespan)

# Allow all origins during local development so the Vite frontend
# on port 5173 can call the backend on port 8000 without CORS errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    """Simple health check endpoint used to verify the backend is running."""
    return {"status": "ok"}


# Magic byte signatures for image format validation.
# JPEG files start with FF D8 FF, PNG files start with 89 50 4E 47.
VALID_IMAGE_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
}

# Maximum upload size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024


def _detect_image_type(first_bytes: bytes) -> str | None:
    """Detect image format from magic bytes. Returns MIME type or None."""
    for signature, mime_type in VALID_IMAGE_SIGNATURES.items():
        if first_bytes.startswith(signature):
            return mime_type
    return None


@app.post("/api/receipts/scan", response_model=ReceiptRead)
async def scan_receipt_endpoint(file: UploadFile):
    """Accept a receipt image, send to Gemini, persist and return the result."""
    # Read the file content into memory (images are never saved to disk).
    content = await file.read()

    # Validate file size before sending to Gemini to avoid large payloads.
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image file is too large. Maximum size is 5 MB.",
        )

    # Validate the actual file content using magic bytes,
    # not just the filename extension which can be forged.
    image_type = _detect_image_type(content[:8])
    if image_type is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a JPEG or PNG image.",
        )

    # Send the image to Gemini and parse the response.
    # ValueError is raised if Gemini cannot read the receipt.
    try:
        parsed = scan_receipt(content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while scanning the receipt. Please try again.",
        ) from e

    # Persist the Receipt and all its Items in a single database transaction.
    # If any Item fails to save, the entire transaction rolls back.
    db = next(get_db())
    try:
        # Parse the date string from Gemini into a Python date object.
        # Gemini returns dates as "YYYY-MM-DD" strings.
        receipt_date = date.fromisoformat(parsed["date"])

        receipt = Receipt(
            receipt_date=receipt_date,
            store_name=parsed["store_name"],
            total_amount=parsed["total_amount"],
        )
        db.add(receipt)
        # Assign receipt.id before creating Items. This flush is where a
        # duplicate receipt (same date + store + total) raises IntegrityError.
        db.flush()

        # Fetch all existing normalized names so the fuzzy matcher can
        # map new items to established standard names across receipts.
        existing_names = [
            row[0]
            for row in db.execute(select(Item.normalized_name)).all()
            if row[0] is not None
        ]

        for item_data in parsed.get("items", []):
            # Normalize the raw product name from Gemini.
            raw_name = item_data["name"]
            normalized = normalize_product_name(raw_name)

            # Check if an existing normalized name matches closely enough
            # to reuse the standard name instead of creating a new variant.
            matched = find_best_match(normalized, existing_names)
            normalized = matched if matched else normalized

            # UPSERT each item: if a row with the same (receipt_id, name)
            # already exists, combine its quantity and total price instead of
            # inserting a duplicate line.
            item_stmt = sqlite_insert(Item).values(
                name=item_data["name"],
                normalized_name=normalized,
                quantity=item_data.get("quantity", 1.0),
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
                category=item_data["category"],
                receipt_id=receipt.id,
            )
            item_stmt = item_stmt.on_conflict_do_update(
                index_elements=["receipt_id", "name"],
                set_={
                    "quantity": item_stmt.excluded.quantity + Item.quantity,
                    "total_price": item_stmt.excluded.total_price + Item.total_price,
                },
            )
            db.execute(item_stmt)

            # Track the newly added normalized name so subsequent items
            # in the same receipt can match against it.
            if normalized not in existing_names:
                existing_names.append(normalized)

        db.commit()

        # Re-query the receipt with items eagerly loaded to avoid
        # DetachedInstanceError after the session closes.
        stmt = (
            select(Receipt)
            .where(Receipt.id == receipt.id)
            .options(selectinload(Receipt.items))
        )
        receipt = db.execute(stmt).scalar_one()
    except IntegrityError:
        # The (date, store_name, total_amount) unique constraint was violated —
        # the user scanned a receipt that already exists.
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This receipt has already been scanned.",
        ) from None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return receipt


@app.get("/api/receipts", response_model=list[ReceiptSummary])
def get_receipts():
    """List all receipts ordered by date descending, with item counts."""
    db = next(get_db())
    try:
        stmt = (
            select(Receipt)
            .options(selectinload(Receipt.items))
            .order_by(Receipt.receipt_date.desc(), Receipt.id.desc())
        )
        receipts = db.execute(stmt).scalars().all()
    finally:
        db.close()

    # Build the summary list, computing each receipt's item count
    # from its eagerly-loaded items.
    return [
        ReceiptSummary(
            id=r.id,
            receipt_date=r.receipt_date,
            store_name=r.store_name,
            total_amount=r.total_amount,
            item_count=len(r.items),
        )
        for r in receipts
    ]


@app.delete("/api/receipts/{receipt_id}", status_code=204)
def delete_receipt(receipt_id: int):
    """Delete a receipt and all its items (ON DELETE CASCADE)."""
    db = next(get_db())
    try:
        receipt = db.get(Receipt, receipt_id)
        if receipt is None:
            raise HTTPException(status_code=404, detail="Receipt not found.")
        db.delete(receipt)
        db.commit()
    finally:
        db.close()


@app.get("/api/analytics/spending-over-time", response_model=list[SpendingOverTimeItem])
def get_spending_over_time(period: Literal["weekly", "monthly"] = "weekly"):
    """Total spend per week or month, ordered by date ascending."""
    # SQLite has no DATE_TRUNC — strftime produces a zero-padded, lexically
    # sortable label directly (e.g. "2025-32" or "2025-08").
    period_expr = (
        func.strftime("%Y-%W", Receipt.receipt_date)
        if period == "weekly"
        else func.strftime("%Y-%m", Receipt.receipt_date)
    )

    db = next(get_db())
    try:
        stmt = (
            select(
                period_expr.label("period_label"),
                func.sum(Receipt.total_amount).label("total_amount"),
            )
            .group_by(period_expr)
            .order_by(period_expr)
        )
        rows = db.execute(stmt).all()
    finally:
        db.close()

    return [
        SpendingOverTimeItem(period_label=row.period_label, total_amount=row.total_amount)
        for row in rows
    ]


@app.get("/api/analytics/spending-by-category", response_model=list[SpendingByCategoryItem])
def get_spending_by_category():
    """Total spend per category, ordered by spend descending."""
    db = next(get_db())
    try:
        stmt = (
            select(Item.category, func.sum(Item.total_price).label("total_amount"))
            .group_by(Item.category)
            .order_by(func.sum(Item.total_price).desc())
        )
        rows = db.execute(stmt).all()
    finally:
        db.close()

    return [
        SpendingByCategoryItem(category=row.category.value, total_amount=row.total_amount)
        for row in rows
    ]


@app.get("/api/analytics/top-items", response_model=list[TopItem])
def get_top_items(limit: int = 10):
    """Most purchased items by total spend, aggregated by normalized name.

    Falls back to the raw name for items saved before feature 004 added
    normalized_name, so pre-existing rows aren't dropped from the ranking.
    """
    name_expr = func.coalesce(Item.normalized_name, Item.name)

    db = next(get_db())
    try:
        stmt = (
            select(
                name_expr.label("normalized_name"),
                func.sum(Item.total_price).label("total_spend"),
                func.count(Item.id).label("purchase_count"),
            )
            .group_by(name_expr)
            .order_by(func.sum(Item.total_price).desc())
            .limit(limit)
        )
        rows = db.execute(stmt).all()
    finally:
        db.close()

    return [
        TopItem(
            normalized_name=row.normalized_name,
            total_spend=row.total_spend,
            purchase_count=row.purchase_count,
        )
        for row in rows
    ]
