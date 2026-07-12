# 001 · Project Setup

**Status:** in progress

## What it does

Sets up the complete project skeleton so the app runs locally end-to-end: 
FastAPI backend, React frontend, SQLite database, and dark theme applied. 
No business logic — only the foundation every other feature builds on.

## Why

Nothing can be built without a working local environment. This feature ensures 
that after following the README, the app starts on localhost with a connected 
database and a visible UI, even if both are empty.

## Acceptance Criteria

- [ ] Running `uvicorn backend.main:app --reload` starts FastAPI on port 8000 with no errors.
- [ ] Running `npm run dev` starts the React app on port 5173 with no errors.
- [ ] `GET /api/health` returns `{"status": "ok"}`.
- [ ] SQLite database file is created automatically at `~/.canasta/canasta.db` on first run.
- [ ] `Receipt` and `Item` tables exist in the database after first run.
- [ ] Frontend displays a placeholder page with Canasta name and dark theme applied 
      (correct background, accent color, fonts loaded).
- [ ] `.env.example` exists at root with `OPENAI_API_KEY=your-key-here`.
- [ ] `README.md` has setup instructions clear enough to run the app from scratch.
- [ ] `canasta.db` and `.env` are in `.gitignore`.

## Out of Scope

- No real UI pages yet — placeholder only (feature 002+).
- No receipt scanning logic (feature 002).
- No dashboard or charts (feature 004).
