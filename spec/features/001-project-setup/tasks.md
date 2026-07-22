# 001 · Project Setup — Tasks

- [x] Create root folder structure: `backend/`, `frontend/`, `spec/`.
- [x] Initialize Python virtual environment: `.venv` lives at project root by design (not inside `backend/`).
- [x] Create `requirements.txt` with: fastapi, uvicorn, sqlalchemy, google-generativeai, 
      python-dotenv, pytest, pillow.
- [x] Create `backend/database.py` — SQLAlchemy engine, session factory, 
      auto-create `~/.canasta/` directory on startup.
- [x] Create `backend/models.py` — `Receipt` and `Item` models with all fields 
      defined in `tech-stack.md`.
- [x] Create `backend/schemas.py` — Pydantic schemas mirroring the models.
- [x] Create `backend/main.py` — FastAPI app, CORS middleware, 
      `GET /api/health` route, database initialization on startup.
- [x] Create `.env.example` — `GEMINI_API_KEY=your-key-here`.
- [x] Create `.gitignore` — covers `.env`, `__pycache__`, `.venv`, `*.db`, 
      `.canasta/`.
- [x] Scaffold React app in `frontend/` using Vite with TypeScript template.
- [x] Create `frontend/src/styles/tokens.css` — all dark theme CSS variables.
- [x] Apply dark background to `frontend/src/index.css` using tokens.
- [x] Create placeholder `App.tsx` — shows "Canasta" in accent color.
- [x] Verify `GET /api/health` returns `{"status": "ok"}`.
- [x] Verify `~/.canasta/canasta.db` is created on first backend run.
- [x] Verify `Receipt` and `Item` tables exist in the database.
- [x] Verify frontend loads on port 5173 with dark background.
- [x] Create `README.md` with setup instructions.
- [x] Validate against all acceptance criteria in `spec.md`.
- [x] Move feature 001 to "Done" in `../../constitution/roadmap.md`.