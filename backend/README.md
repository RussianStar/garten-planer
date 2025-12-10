Backend scaffold for the uncertainty-aware garden planner.

- `app/main.py` starts a FastAPI server exposing a small demo plan endpoint.
- `app/models.py` defines the core Estimate and lifecycle types.
- `app/scheduler.py` contains utilities to propagate uncertainty through lifecycle arrows.

Run locally (after installing deps into a venv):

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
