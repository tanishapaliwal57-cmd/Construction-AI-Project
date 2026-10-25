# Construction AI Assistant

A starter full-stack project for construction-site image analysis, safety checks, crack assessment, construction planning, cost estimation, and property valuation.

## Stack
- Backend: Python 3.9+, FastAPI, Pydantic, Pillow, python-dotenv, optional Google Gemini API
- Frontend: React + Vite + TypeScript
- AI: Gemini multimodal API when `GEMINI_API_KEY` is configured; safe demo-mode fallback otherwise

## Run locally

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows; on macOS/Linux use: cp .env.example .env
uvicorn app.main:app --reload
```
Backend docs: http://127.0.0.1:8000/docs

### 2. Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite, usually http://localhost:5173.

## Enable Gemini
Add your API key to `backend/.env`:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```
Never commit `.env` or expose the API key in the frontend. Without a key, the app returns clearly labelled demo analysis.

## Run with Docker
```bash
cp backend/.env.example backend/.env
docker compose up --build
```
Frontend: http://localhost:5173 · API docs: http://localhost:8000/docs

## Tests
```bash
cd backend && pip install -r requirements-dev.txt && pytest
cd frontend && npm run build   # type-check + build
```
GitHub Actions (`.github/workflows/ci.yml`) runs both on every push.

## Main API
- `GET /health`
- `POST /api/analyze` — optional image + description + structured project data
- `POST /api/estimate` — JSON `{area_sqft, floors, budget_inr?}` → materials, cost, budget check
- `POST /api/valuation` — JSON `{area_sqft, rate_per_sqft, age_years, condition}` → rough valuation
- `POST /api/plan` — JSON `{area_sqft, floors, building_type}` → phased indicative schedule

## Important limitations
- This is an educational starter, not a certified engineering, safety, or valuation system.
- Image analysis may miss hazards or cracks. Do not use it to approve site safety or structural integrity.
- Estimates are illustrative and depend on local rates, measurements, quality, and regulations.
- Always obtain review from a qualified site engineer/structural engineer and local professionals.
