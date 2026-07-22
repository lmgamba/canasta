from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine


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
