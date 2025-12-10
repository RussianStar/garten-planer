# Garten Planer – Uncertainty-Aware Skeleton

This scaffold wires a Python FastAPI backend with a Bun/Vite/React frontend to demonstrate the “arrows + error bars” model for crop lifecycles.

## Layout

- `backend/` – FastAPI app exposing `/demo/plan` with lifecycle arrows and date windows.
- `frontend/` – React + Vite UI (run with Bun) that fetches the demo plan and renders fuzzy timelines.

## Quickstart

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
Requires [Bun](https://bun.sh/).
```bash
cd frontend
bun install
bun run dev
```

Point the browser to `http://localhost:5173`. The frontend expects the backend at `http://localhost:8000` (override with `VITE_API_BASE`).

## Next steps
- Replace demo data in `backend/app/scheduler.py` with real lifecycle arrows from storage.
- Add POST endpoints to save lifecycles and observations.
- Enhance frontend to edit estimates and show Gantt grouped by week with windows.
