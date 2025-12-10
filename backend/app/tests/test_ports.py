from datetime import date

import pytest

from ..ports import adapt_lifecycle_arrow, adapt_planning_problem


def test_adapt_lifecycle_arrow_propagates_error_bounds():
    raw = {
        "id": "germinate",
        "crop_variety_id": "tomato",
        "from_state": "SeedSownNursery",
        "to_state": "SeedlingsGrowingNursery",
        "duration": {"typical": 7, "lower": 4, "upper": 10, "confidence": 0.6},
    }

    arrow = adapt_lifecycle_arrow(raw)

    assert arrow.duration.typical == 7
    assert arrow.duration.lower == 4
    assert arrow.duration.upper == 10
    assert arrow.duration.confidence == 0.6


def test_adapt_lifecycle_arrow_defaults_missing_bounds():
    raw = {
        "id": "harden",
        "crop_variety_id": "tomato",
        "from_state": "SeedlingsGrowingNursery",
        "to_state": "HardenedOff",
        "duration": {"typical": 24},
    }

    arrow = adapt_lifecycle_arrow(raw)

    assert arrow.duration.typical == 24
    assert arrow.duration.lower == 24
    assert arrow.duration.upper == 24


def test_adapt_planning_problem_normalizes_all_inbound_data():
    payload = {
        "goals": [
            {
                "crop_variety_id": "tomato",
                "desired_plants": 10,
                "target_sow_date": date(2024, 3, 1),
            }
        ],
        "lifecycle_arrows": [
            {
                "id": "germinate",
                "crop_variety_id": "tomato",
                "from_state": "SeedStored",
                "to_state": "SeedSownNursery",
                "duration": {"typical": 0},
            },
            {
                "id": "grow",
                "crop_variety_id": "tomato",
                "from_state": "SeedSownNursery",
                "to_state": "SeedlingsGrowingNursery",
                "duration": {"typical": 7, "lower": 5, "upper": 9},
            },
        ],
        "strategy": {"risk_tolerance": 0.7},
    }

    problem = adapt_planning_problem(payload)

    assert len(problem.goals) == 1
    assert len(problem.lifecycle_arrows) == 2
    assert problem.strategy.risk_tolerance == 0.7

    # Bounds should be present even when omitted for the zero-duration arrow
    zero_arrow = problem.lifecycle_arrows[0]
    assert zero_arrow.duration.lower == 0
    assert zero_arrow.duration.upper == 0

    ranged_arrow = problem.lifecycle_arrows[1]
    assert ranged_arrow.duration.lower == 5
    assert ranged_arrow.duration.upper == 9

