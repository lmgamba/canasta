# 001 · Project Setup — Tasks

- [x] Create root folder structure: `backend/`, `frontend/`, `spec/`.
- [x] Initialize Python virtual environment: `.venv` lives at project root by design (not inside `backend/`).
- [x] Create `requirements.txt` with: fastapi, uvicorn, sqlalchemy, google-generativeai, 
      python-dotenv, pytest, pillow.
- [x] Create `backend/database.py` — SQLAlchemy engine, session factory, 
      auto-create `~/.canasta/` directory on startup.
- [x] Create `backend/models.py` — `Receipt` and `Item` models with all fields 
      defined in `tech-stack.md`.
- [ ] Create `backend/schemas.py` — Pydantic schemas mirroring the models.
- [ ] Create `backend/main.py` — FastAPI app, CORS middleware, 
      `GET /api/health` route, database initialization on startup.
- [ ] Create `.env.example` — `OPENAI_API_KEY=your-key-here`.
- [ ] Create `.gitignore` — covers `.env`, `__pycache__`, `.venv`, `*.db`, 
      `.canasta/`.
- [ ] Scaffold React app in `frontend/` using Vite with TypeScript template.
- [ ] Create `frontend/src/styles/tokens.css` — all dark theme CSS variables.
- [ ] Apply dark background to `frontend/src/index.css` using tokens.
- [ ] Create placeholder `App.tsx` — shows "Canasta" in accent color.
- [ ] Verify `GET /api/health` returns `{"status": "ok"}`.
- [ ] Verify `~/.canasta/canasta.db` is created on first backend run.
- [ ] Verify `Receipt` and `Item` tables exist in the database.
- [ ] Verify frontend loads on port 5173 with dark background.
- [ ] Create `README.md` with setup instructions.
- [ ] Validate against all acceptance criteria in `spec.md`.
- [ ] Move feature 001 to "Done" in `../../constitution/roadmap.md`.