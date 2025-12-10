from __future__ import annotations

"""Adapter functions for translating inbound payloads into domain models.

These ports ensure boundary data is normalized (e.g., optional error bars are
filled) before the planner consumes it.
"""

from typing import Any, Optional

from .models import Estimate, LifecycleArrow, PlantingGoal, PlanningProblem, Strategy


def adapt_estimate(payload: dict[str, Any]) -> Estimate:
    """Create an Estimate while tolerating missing error bars.

    The adapter normalizes the estimate so callers can rely on lower/upper being
    present, even if the inbound payload only provided a single value.
    """

    estimate = Estimate(**payload)
    return estimate.normalized()


def adapt_lifecycle_arrow(payload: dict[str, Any]) -> LifecycleArrow:
    """Convert a raw lifecycle arrow payload into a domain model with safe defaults."""

    duration_payload: dict[str, Any] = payload.get("duration", {})
    duration = adapt_estimate(duration_payload)

    survival_payload: Optional[dict[str, Any]] = payload.get("survival_rate")
    survival_rate = adapt_estimate(survival_payload) if survival_payload else None

    temp_payload: Optional[dict[str, Any]] = payload.get("temp_c")
    temp_c = adapt_estimate(temp_payload) if temp_payload else None

    sun_payload: Optional[dict[str, Any]] = payload.get("sun_hours_per_day")
    sun_hours_per_day = adapt_estimate(sun_payload) if sun_payload else None

    return LifecycleArrow(
        id=payload["id"],
        crop_variety_id=payload["crop_variety_id"],
        from_state=payload["from_state"],
        to_state=payload["to_state"],
        duration=duration,
        survival_rate=survival_rate,
        temp_c=temp_c,
        sun_hours_per_day=sun_hours_per_day,
        requires_bed=payload.get("requires_bed", False),
        required_nursery_types=payload.get("required_nursery_types"),
    )


def adapt_planning_problem(payload: dict[str, Any]) -> PlanningProblem:
    """Build a PlanningProblem from inbound data, normalizing estimates at the boundary."""

    goals = [PlantingGoal(**goal) for goal in payload.get("goals", [])]
    arrows = [adapt_lifecycle_arrow(arrow) for arrow in payload.get("lifecycle_arrows", [])]
    strategy = Strategy(**payload.get("strategy", {})) if payload.get("strategy") else Strategy()

    return PlanningProblem(goals=goals, lifecycle_arrows=arrows, strategy=strategy)

