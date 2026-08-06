from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Directory where the SQLite database file lives
DATABASE_DIR = Path.home() / ".canasta"
DATABASE_PATH = DATABASE_DIR / "canasta.db"

# Create the data directory (and parents) if it doesn't exist yet
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Create the SQLAlchemy engine pointing to the SQLite file.
# check_same_thread=False is required because FastAPI serves requests
# from multiple threads while SQLite only allows one writer at a time.
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)


# Enable foreign key enforcement per connection. SQLite has this disabled by
# default — without it, ON DELETE CASCADE never fires. We hook the engine's
# connection creation event to set the pragma on every new connection.
@event.listens_for(engine, "connect")
def _enable_foreign_keys(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session factory — each request gets its own session via get_db().
# autocommit and autoflush are explicitly disabled so we control
# when transactions are committed and when the session is refreshed.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Base class for all ORM models (Receipt, Item, etc.)
class Base(DeclarativeBase):
    pass


# FastAPI dependency that yields a database session and ensures
# it is closed after the request finishes.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
