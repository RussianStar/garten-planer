from __future__ import annotations

from datetime import date

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import Strategy
from .scheduler import demo_tomato_arrows, plan_linear_lifecycle

app = FastAPI(title="Garden Planner (uncertainty-aware)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/demo/plan")
def demo_plan(
    sow_date: date = Query(default=date.today(), description="Starting sow date"),
    risk_tolerance: float = Query(
        default=0.5, ge=0.0, le=1.0, description="0=cautious (use upper bounds), 1=aggressive (lean on typical)"
    ),
):
    """
    Returns a small tomato lifecycle plan with date windows derived from
    uncertainty-aware durations. Intended as a quick integration target for the
    frontend prototype.
    """
    arrows = demo_tomato_arrows()
    strategy = Strategy(risk_tolerance=risk_tolerance)
    plan = plan_linear_lifecycle("tomato", arrows, sow_date, strategy=strategy)
    return plan
