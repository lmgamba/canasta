# Canasta

Canasta is a local-first grocery intelligence app that scans supermarket receipts 
using GPT-4o Vision and reveals consumption patterns over time. 
Single-user, runs entirely on localhost, no auth, no cloud.

## Stack

- **Language (backend):** Python 3.13+
- **Language (frontend):** TypeScript (strict mode)
- **Backend framework:** FastAPI
- **Frontend framework:** React 18 + Vite
- **Database:** SQLite via SQLAlchemy (file at `~/.canasta/canasta.db`)
- **LLM:** Google Gemini 2.0 Flash (Vision) via google-generativeai SDK
- **Styling:** CSS Modules (no Tailwind) — dark theme tokens in `frontend/src/styles/tokens.css`
- **Tests:** pytest (backend only)

## Commands

- `uvicorn backend.main:app --reload` — starts backend on localhost:8000
- `npm run dev` — starts frontend on localhost:5173
- `pytest` — runs backend tests (must pass before every commit)
- `pip install -r requirements.txt` — installs backend dependencies
- `npm install` — installs frontend dependencies

## Project Structure

- `backend/` — FastAPI app: routes, models, database, scanner logic
- `backend/main.py` — entry point, all route definitions
- `backend/scanner.py` — GPT-4o Vision integration and receipt parsing
- `backend/models.py` — SQLAlchemy ORM models
- `backend/schemas.py` — Pydantic schemas for validation
- `backend/database.py` — SQLAlchemy setup and session factory
- `frontend/src/pages/` — one file per page: Upload, Dashboard, History
- `frontend/src/components/` — reusable UI components
- `frontend/src/styles/` — CSS modules and global design tokens
- `spec/` — project specification (constitution + features)

## Conventions

- snake_case for all Python identifiers.
- camelCase for TypeScript variables and functions, PascalCase for React components.
- All API routes prefixed with `/api/`.
- All API error responses return `{"detail": "<message>"}` — never a raw string.
- Backend tests live in `backend/tests/` — one test file per module.
- Validate all user input at the FastAPI route level using Pydantic schemas.
- Gemini API key loaded from `.env` as `GEMINI_API_KEY` via `python-dotenv` — never hardcoded.
- Design tokens (colors, fonts, spacing) defined once in `tokens.css` — never inline.
- Unit tests: test individual functions in isolation (e.g. parsing logic in `scanner.py`).
- Integration tests: test full request → database flow via FastAPI's `TestClient`.
- Both live in `backend/tests/` — prefix integration tests with `integration_` 
  (e.g. `integration_test_receipts.py`).

## Do NOT

- Do not commit `.env`, `canasta.db`, or any file under `~/.canasta/`.
- Do not store receipt images permanently — extract data, then discard the file.
- Do not add Python or npm dependencies without updating `requirements.txt` 
  or `package.json`.
- Do not add new API routes without a corresponding Pydantic schema.
- Do not use `any` in TypeScript without a comment explaining why.
- Do not touch `spec/constitution/` without explicit instruction — 
  it is the source of truth.
- Do not implement features not listed in `spec/constitution/roadmap.md`.

## Workflow

- Before any non-trivial task, propose a plan and wait for approval.
- One task at a time — when done, summarize what changed so I can review it.
- If less than 80% confident, ask. Do not invent or assume.
- Every new feature starts with `spec/features/NNN-name/` containing 
  `spec.md`, `plan.md`, and `tasks.md` before any code is written.
- For every new function or endpoint, write unit tests in `backend/tests/` 
  before marking the task as done. Write them yourself, if assistance needed, ask for human input.
- Test file naming: `test_<module>.py` (e.g. `test_scanner.py` for `scanner.py`).
- Each test function name must describe the scenario: 
  `test_health_endpoint_returns_ok`, not `test_health`.
- Cover at minimum: happy path, missing input, and invalid input for every endpoint.
- Run `pytest` after every backend change and show me the output 
  before continuing.
- Always use Conventional Commits format: `type(scope): description` 
  (e.g. `feat(scanner): add receipt upload endpoint`).
- Never push to GitHub automatically — stage and summarize changes, 
  then wait for explicit approval before any `git push`.
- Never commit directly to `main` or `develop` — always work on a 
  feature branch and wait for PR approval.

## Documentation

- Project constitution: `spec/constitution/`
- Feature specs: `spec/features/`
- Tech stack details: `spec/constitution/tech-stack.md`
- Roadmap: `spec/constitution/roadmap.md`