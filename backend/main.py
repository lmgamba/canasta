from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import Base, engine, get_db
from backend.models import Item, Receipt
from backend.schemas import ReceiptRead
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

# Maximum upload size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024


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
            detail="Image file is too large. Maximum size is 10 MB.",
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
        db.flush()  # Assign receipt.id before creating Items

        for item_data in parsed.get("items", []):
            item = Item(
                name=item_data["name"],
                quantity=item_data.get("quantity", 1.0),
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
                category=item_data["category"],
                receipt_id=receipt.id,
            )
            db.add(item)

        db.commit()

        # Re-query the receipt with items eagerly loaded to avoid
        # DetachedInstanceError after the session closes.
        stmt = (
            select(Receipt)
            .where(Receipt.id == receipt.id)
            .options(selectinload(Receipt.items))
        )
        receipt = db.execute(stmt).scalar_one()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return receipt
