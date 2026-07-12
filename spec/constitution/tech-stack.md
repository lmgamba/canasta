# Tech Stack and Conventions

## Technologies

- **Language (backend):** Python 3.13+
- **Language (frontend):** TypeScript (strict mode)
- **Backend framework:** FastAPI
- **Frontend framework:** React 18 + Vite
- **Database:** SQLite via SQLAlchemy (file stored at `~/.canasta/canasta.db`)
- **LLM:** Google Gemini 2.0 Flash (Vision) via google-generativeai SDK
- **Tests:** pytest (backend) — frontend has no test suite in v1
- **Deployment:** local only — user runs via `uvicorn` and opens `localhost:8000`

## Key Files / Modules

- `backend/main.py` — FastAPI app entry point, all route definitions
- `backend/database.py` — SQLAlchemy setup and session management
- `backend/models.py` — SQLAlchemy ORM models (Receipt, Item)
- `backend/scanner.py` — GPT-4o Vision integration, receipt parsing logic
- `backend/schemas.py` — Pydantic schemas for request/response validation
- `frontend/src/pages/` — one file per page (Upload, Dashboard, History)
- `frontend/src/components/` — reusable UI components
- `~/.canasta/canasta.db` — user's SQLite database (never committed to git)

## Commands

- `uvicorn backend.main:app --reload` — starts the backend on localhost:8000
- `npm run dev` — starts the frontend on localhost:5173
- `pytest` — runs backend tests
- `pip install -r requirements.txt` — installs backend dependencies
- `npm install` — installs frontend dependencies

## Data Model

- `Receipt` — represents one scanned receipt: date, store name, total amount, image path.
- `Item` — represents one line on a receipt: name, quantity, unit price, total price, category. Belongs to a Receipt.
- `category` — one of: Dairy, Produce, Meat & Fish, Bakery, Snacks, Beverages, Cleaning, Personal Care, Other. Assigned by GPT-4o.

## Conventions

- snake_case for all Python identifiers.
- camelCase for TypeScript variables and functions, PascalCase for components.
- All API routes prefixed with `/api/`.
- FastAPI routes live in `main.py` for v1 — split into routers only if file exceeds 200 lines.
- Error responses always return `{"detail": "<message>"}` to match FastAPI defaults.
- Never commit `.env` or `~/.canasta/` contents to git.
- Gemini API key loaded from `.env` as `GEMINI_API_KEY` via `python-dotenv` — never hardcoded.

## Visual Style

- **Theme:** Dark mode only. Background ranges from `#121212` (deepest) to `#1E1E1E` (cards/containers).
- **Typography:** Off-white `#F5F5F5` for primary text, muted `#9E9E9E` for secondary/labels.
- **Accent color:** Mint green `#00E676` — used for CTAs, highlights, active states, and positive data points.
- **Fonts:** Monospaced font (JetBrains Mono or similar) for receipt data, item names, and numbers. Clean sans-serif (Inter) for UI labels and navigation.
- **Components:** Rounded containers (`border-radius: 12px`), subtle glowing borders using `box-shadow: 0 0 0 1px #00E67620` on hover states.
- **Data density:** Prioritize information density over whitespace — this is a utility tool, not a marketing page.
- **No Tailwind** — use CSS modules or plain CSS to have full control over the dark theme tokens.

## Hard Limits

- Never store receipt images permanently — only extract data from them, then discard.
- Never commit `canasta.db` or any `.env` file to git.
- No user authentication in v1 — single user app by design.
- Do not add dependencies without updating `requirements.txt` or `package.json`.
- Gemini 2.0 Flash is the only LLM provider in v1 — no abstraction layer needed yet.