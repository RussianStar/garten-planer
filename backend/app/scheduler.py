from __future__ import annotations

from datetime import date
from typing import Iterable
from uuid import uuid4

from .models import (
    DurationEstimate,
    LifecycleArrow,
    PlanResult,
    PlanningProblem,
    ScheduleEvent,
    Strategy,
)


def sum_durations(durations: Iterable[DurationEstimate]) -> DurationEstimate:
    total: DurationEstimate | None = None
    for dur in durations:
        total = dur if total is None else total.add(dur)
    return total or DurationEstimate(typical=0, lower=0, upper=0, confidence=1.0)


def plan_linear_lifecycle(
    crop_variety_id: str,
    arrows: list[LifecycleArrow],
    sow_date: date,
    strategy: Strategy | None = None,
) -> PlanResult:
    """
    Simple planner that assumes arrows are already in execution order and form
    a single path (SeedStored -> ... -> Finished). It returns schedule events
    with earliest/typical/latest dates by summing duration estimates.
    """
    events: list[ScheduleEvent] = []
    cursor_date = sow_date
    chosen_strategy = strategy or Strategy()

    for arrow in arrows:
        # duration window for this step
        date_range = arrow.duration.to_window(cursor_date, risk_tolerance=chosen_strategy.risk_tolerance)

        # map lifecycle transitions to coarse schedule event kinds
        kind = classify_event_kind(arrow)

        events.append(
            ScheduleEvent(
                id=str(uuid4()),
                planting_id=crop_variety_id,
                kind=kind,
                earliest=date_range["earliest"],
                typical=date_range["typical"],
                latest=date_range["latest"],
            )
        )

        # advance cursor by selected typical; downstream arrows accumulate around the strategy preference
        cursor_date = date_range["typical"]

    return PlanResult(crop_variety_id=crop_variety_id, sow_date=sow_date, events=events)


def plan_from_problem(problem: PlanningProblem) -> list[PlanResult]:
    """
    Entry point for a richer planning problem. For now we only support
    generating one plan per goal using a linear arrow list filtered by crop.
    """

    plans: list[PlanResult] = []
    for goal in problem.goals:
        crop_arrows = [arrow for arrow in problem.lifecycle_arrows if arrow.crop_variety_id == goal.crop_variety_id]
        plans.append(
            plan_linear_lifecycle(
                crop_variety_id=goal.crop_variety_id,
                arrows=crop_arrows,
                sow_date=goal.target_sow_date,
                strategy=problem.strategy,
            )
        )
    return plans


def classify_event_kind(arrow: LifecycleArrow) -> ScheduleEvent.__fields__["kind"].type_:  # type: ignore
    """
    Heuristic mapping from state transitions to schedule event kinds.
    """
    if arrow.from_state == "SeedStored" and "Nursery" in arrow.to_state:
        return "sow"
    if arrow.to_state == "InBedVegetative":
        return "transplant"
    if arrow.to_state == "InBedHarvestable":
        return "harvest_start"
    if arrow.to_state == "Finished":
        return "clear_bed"
    return "sow"


# Demo data for quick smoke tests
def demo_tomato_arrows() -> list[LifecycleArrow]:
    def de(t: int, lo: int, hi: int) -> DurationEstimate:
        return DurationEstimate(typical=t, lower=lo, upper=hi, confidence=0.6)

    return [
        LifecycleArrow(
            id="seed-to-germinate",
            crop_variety_id="tomato",
            from_state="SeedStored",
            to_state="SeedSownNursery",
            duration=DurationEstimate(typical=0, lower=0, upper=0, confidence=1.0),
        ),
        LifecycleArrow(
            id="germinate",
            crop_variety_id="tomato",
            from_state="SeedSownNursery",
            to_state="SeedlingsGrowingNursery",
            duration=de(7, 4, 10),
        ),
        LifecycleArrow(
            id="harden",
            crop_variety_id="tomato",
            from_state="SeedlingsGrowingNursery",
            to_state="HardenedOff",
            duration=de(24, 21, 28),
        ),
        LifecycleArrow(
            id="transplant",
            crop_variety_id="tomato",
            from_state="HardenedOff",
            to_state="InBedVegetative",
            duration=de(2, 1, 3),
        ),
        LifecycleArrow(
            id="grow-to-harvest",
            crop_variety_id="tomato",
            from_state="InBedVegetative",
            to_state="InBedHarvestable",
            duration=de(70, 55, 85),
        ),
        LifecycleArrow(
            id="clear",
            crop_variety_id="tomato",
            from_state="InBedHarvestable",
            to_state="Finished",
            duration=de(0, 0, 0),
        ),
    ]
