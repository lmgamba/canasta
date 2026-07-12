# 001 · Project Setup — Plan

## Approach

Initialize the project in two independent parts — backend and frontend — 
that can be started separately. The database initializes automatically on 
first backend startup. No code generation tools (no cookiecutter, no Vite 
templates with extras) — lean scaffolding only.

## Implementation

1. Create root folder structure — `backend/`, `frontend/`, `spec/`.
2. Initialize Python virtual environment in `backend/` — `python -m venv .venv`.
3. Create `backend/main.py` — FastAPI app with single `GET /api/health` route.
4. Create `backend/database.py` — SQLAlchemy engine pointing to `~/.canasta/canasta.db`, 
   creates the directory if it doesn't exist, runs `create_all` on startup.
5. Create `backend/models.py` — `Receipt` and `Item` SQLAlchemy models.
6. Create `backend/schemas.py` — Pydantic schemas mirroring the models.
7. Create `requirements.txt` — fastapi, uvicorn, sqlalchemy, openai, python-dotenv, pytest.
8. Create `.env.example` — `OPENAI_API_KEY=your-key-here`.
9. Create `.gitignore` — covers `.env`, `__pycache__`, `.venv`, `*.db`.
10. Scaffold React app in `frontend/` using Vite — `npm create vite@latest`.
11. Create `frontend/src/styles/tokens.css` — all dark theme CSS variables defined once.
12. Apply tokens to `frontend/src/index.css` — dark background on body.
13. Create placeholder `App.tsx` — displays "Canasta" in accent color, dark background.
14. Create `README.md` — setup instructions, commands, requirements.

## Decisions

- **SQLAlchemy over raw SQLite** — gives ORM models that future features 
  can use directly. Raw SQL discarded because it doesn't scale cleanly across features.
- **`~/.canasta/` for database** — survives project folder deletion or updates. 
  A local `data/` folder was discarded because it risks accidental git commits.
- **Vite over Create React App** — CRA is deprecated. Vite is faster and 
  is the current standard.
- **No Docker for v1** — adds complexity with no benefit for a single-user local app.
- **CSS Modules + tokens.css over Tailwind** — full control over dark theme 
  tokens without fighting Tailwind's config.

## Risks

- **Windows path for `~/.canasta/`** — `Path.home()` in Python resolves correctly 
  on Windows, Mac, and Linux. Use `pathlib.Path.home() / ".canasta"` explicitly, 
  never hardcode the path.
- **Vite CORS with FastAPI** — frontend on 5173 calling backend on 8000 requires 
  CORS middleware in FastAPI from day one, otherwise every API call will fail.