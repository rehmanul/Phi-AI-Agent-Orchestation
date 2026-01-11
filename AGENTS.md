# Repository Guidelines

## Project Structure & Module Organization
The backend is a FastAPI service under `api/` with shared utilities in `core/`. Agent modules live in `agents/` (one folder per agent), and external integrations live in `integrations/`. The web UI is a Next.js 14 app in `dashboard/` (`dashboard/src/app` for routes, `dashboard/src/components` for shared UI). Database migrations are tracked in `migrations/`, and container assets are in `docker/`.

## Build, Test, and Development Commands
Backend (local + infra):
```bash
cp .env.example .env
docker-compose up -d
pip install -e .
alembic upgrade head
uvicorn api.main:app --reload
```
Dashboard:
```bash
cd dashboard
npm install
npm run dev
```
Checks:
```bash
pytest
ruff check .
mypy .
npm run lint
```

## Coding Style & Naming Conventions
Python uses Black and Ruff with a 100-char line length. Use 4-space indentation, `snake_case` for functions/variables, `PascalCase` for classes, and `UPPER_CASE` for constants. React components should be `PascalCase` in `*.tsx` (for example, `DocumentList.tsx`).

## Testing Guidelines
Backend tests use pytest with files named `test_*.py` under `tests/` (create the folder if it does not exist). Add coverage for API routes, document processing, and review workflow changes. Run `pytest` before submitting changes.

## Commit & Pull Request Guidelines
Recent history favors imperative, present-tense messages (for example, "Add Documents link", "Fix mermaid TypeScript declaration"). PRs should include: a concise summary, test commands run, UI screenshots when changing the dashboard, and notes for new env vars or migrations.

## Security & Configuration
Configuration is environment-driven; keep `.env.example` in sync with required settings. Do not introduce API key requirements for core document workflows; keep processing local and deterministic. Never commit secrets.
