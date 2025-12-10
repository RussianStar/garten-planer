from __future__ import annotations

from datetime import date, timedelta
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Estimate(BaseModel):
    """Numeric value wrapped with explicit uncertainty/error bars."""

    typical: float = Field(..., description="Best guess or median value")
    lower: Optional[float] = Field(None, description="Optimistic bound (p10/min)")
    upper: Optional[float] = Field(None, description="Pessimistic bound (p90/max)")
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    source: Literal["kb", "user", "learned", "sensor"] = "kb"
    updated_at: Optional[date] = None

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------
    @classmethod
    def from_single(
        cls, value: float, *, confidence: float = 0.3, source: Literal["kb", "user", "learned", "sensor"] = "user"
    ) -> "Estimate":
        """Create an estimate from a single number (lower/upper default to the same value)."""

        return cls(
            typical=value,
            lower=value,
            upper=value,
            confidence=confidence,
            source=source,
        )

    @classmethod
    def from_range(
        cls,
        lower: float,
        upper: float,
        *,
        typical: Optional[float] = None,
        confidence: float = 0.6,
        source: Literal["kb", "user", "learned", "sensor"] = "user",
    ) -> "Estimate":
        """Create an estimate from a range, defaulting to the midpoint as typical."""

        typical_value = typical if typical is not None else (lower + upper) / 2
        return cls(
            typical=typical_value,
            lower=lower,
            upper=upper,
            confidence=confidence,
            source=source,
        )

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

    def scale(self, factor: float) -> "Estimate":
        """Scale an estimate by a constant factor, preserving bounds and confidence."""

        normalized = self.normalized()
        return Estimate(
            typical=normalized.typical * factor,
            lower=normalized.lower * factor if normalized.lower is not None else None,
            upper=normalized.upper * factor if normalized.upper is not None else None,
            confidence=normalized.confidence,
            source=normalized.source,
            updated_at=normalized.updated_at,
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

    def to_window(self, start: date, risk_tolerance: float = 0.5) -> dict:
        """
        Convert a duration estimate into a date window influenced by risk tolerance.

        - earliest: always uses the optimistic bound
        - target: interpolates between typical and upper based on risk tolerance
          (0.0 = very cautious → upper bound, 1.0 = aggressive → typical)
        - latest: pessimistic bound
        """

        bounded_risk = max(0.0, min(1.0, risk_tolerance))
        normalized = self.normalized()
        target_days = normalized.typical + (normalized.upper - normalized.typical) * (1 - bounded_risk)

        return {
            "earliest": start + timedelta(days=int(normalized.lower)),
            "typical": start + timedelta(days=int(target_days)),
            "latest": start + timedelta(days=int(normalized.upper)),
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


class CropState(BaseModel):
    """Concrete state node in a crop lifecycle graph."""

    id: str
    kind: CropStateKind
    crop_variety_id: str
    location: Optional[Literal["nursery", "bed", "storage"]] = None
    notes: Optional[str] = None


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


class PlantingGoal(BaseModel):
    crop_variety_id: str
    desired_plants: int
    target_sow_date: date


class Strategy(BaseModel):
    """Planning strategy, e.g., risk tolerance and aggressiveness."""

    risk_tolerance: float = Field(0.5, ge=0.0, le=1.0)
    prefer_early_harvest: bool = False


class PlanningProblem(BaseModel):
    """Container for inputs needed to generate a lifecycle plan."""

    goals: list[PlantingGoal]
    lifecycle_arrows: list[LifecycleArrow]
    strategy: Strategy = Strategy()
