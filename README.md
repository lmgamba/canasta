# Canasta

Local-first grocery intelligence app. Scan supermarket receipts with Google Gemini 2.5 Flash (Vision) and discover your consumption patterns over time.

## Prerequisites

- Python 3.13+
- Node.js 18+
- A Google Gemini API key

## Setup

```bash
# Clone and enter the project
git clone <repo-url> && cd canasta

# Backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Add your Gemini API key
cp .env.example .env
# Edit .env and replace your-key-here with your actual key

# Frontend
cd frontend && npm install && cd ..
```

## Running

```bash
# Terminal 1 — backend (localhost:8000)
uvicorn backend.main:app --reload

# Terminal 2 — frontend (localhost:5173)
cd frontend && npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Testing

```bash
pytest
```

## Project Structure

```
canasta/
├── backend/
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # SQLAlchemy engine & session
│   ├── models.py        # Receipt & Item ORM models
│   ├── schemas.py       # Pydantic validation schemas
│   └── tests/           # Backend tests (pytest)
├── frontend/
│   └── src/
│       ├── App.tsx      # Root component
│       ├── index.css    # Global styles (imports tokens)
│       └── styles/
│           └── tokens.css  # Dark theme design tokens
├── spec/                # Project specification
└── requirements.txt
```
