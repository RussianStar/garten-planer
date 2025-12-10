from __future__ import annotations

from datetime import date, timedelta
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Estimate(BaseModel):
    typical: float = Field(..., description="Best guess or median value")
    lower: Optional[float] = Field(None, description="Optimistic bound (p10/min)")
    upper: Optional[float] = Field(None, description="Pessimistic bound (p90/max)")
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    source: Literal["kb", "user", "learned", "sensor"] = "kb"
    updated_at: Optional[date] = None

    def normalized(self) -> "Estimate":
        """
        Ensure lower/upper are present. If missing, fill with typical.
        """
        lower = self.lower if self.lower is not None else self.typical
        upper = self.upper if self.upper is not None else self.typical
        return Estimate(
            typical=self.typical,
            lower=lower,
            upper=upper,
            confidence=self.confidence,
            source=self.source,
            updated_at=self.updated_at,
        )

    def add(self, other: "Estimate") -> "Estimate":
        """
        Add two estimates component-wise, propagating uncertainty pessimistically
        by summing bounds.
        """
        a, b = self.normalized(), other.normalized()
        return Estimate(
            typical=a.typical + b.typical,
            lower=a.lower + b.lower if a.lower is not None and b.lower is not None else None,
            upper=a.upper + b.upper if a.upper is not None and b.upper is not None else None,
            confidence=min(a.confidence, b.confidence),
            source="learned",
        )

    def to_date_range(self, start: date) -> dict:
        """
        Convert a duration estimate (in days) to absolute dates from a start date.
        """
        days = self.normalized()
        return {
            "earliest": start + timedelta(days=int(days.lower)),
            "typical": start + timedelta(days=int(days.typical)),
            "latest": start + timedelta(days=int(days.upper)),
        }


DurationEstimate = Estimate  # alias for clarity


CropStateKind = Literal[
    "SeedStored",
    "SeedSownNursery",
    "SeedlingsGrowingNursery",
    "HardenedOff",
    "InBedVegetative",
    "InBedHarvestable",
    "Finished",
]


class LifecycleArrow(BaseModel):
    id: str
    crop_variety_id: str
    from_state: CropStateKind
    to_state: CropStateKind
    duration: DurationEstimate
    survival_rate: Optional[Estimate] = None
    temp_c: Optional[Estimate] = None
    sun_hours_per_day: Optional[Estimate] = None
    requires_bed: bool = False
    required_nursery_types: Optional[list[str]] = None


class ScheduleEvent(BaseModel):
    id: str
    planting_id: str
    kind: Literal["sow", "transplant", "harvest_start", "clear_bed"]
    earliest: date
    typical: date
    latest: date


class PlanResult(BaseModel):
    crop_variety_id: str
    sow_date: date
    events: list[ScheduleEvent]
