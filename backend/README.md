Backend scaffold for the uncertainty-aware garden planner.

- `app/main.py` starts a FastAPI server exposing a small demo plan endpoint with a
  `risk_tolerance` knob so the API always returns date *windows* rather than
  point estimates.
- `app/models.py` defines the core Estimate and lifecycle types, including helpers
  for building estimates from single numbers or ranges and a `PlanningProblem`
  container for future graph-based planning.
- `app/scheduler.py` contains utilities to propagate uncertainty through lifecycle
  arrows and convert those into schedule windows.

Run locally (after installing deps into a venv):

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
