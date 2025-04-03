from datetime import datetime

import pytest

from models import (
    HealthMetrics,
    HeartRateZones,
    NeurologicalStatus,
    NeuroPlan,
    PhysicalMetrics,
    PlanParameters,
    VisionMetrics,
)


def test_create_neuro_plan():
    plan = NeuroPlan(
        plan_title="Test Plan",
        plan_parameters=PlanParameters(
            plan_duration_weeks=2,
            training_days=["Monday", "Wednesday", "Friday"],
            daily_training_duration="45 minutes",
            goals=["Improve brain function"],
            active_courses=["Neuro training"],
        ),
        health_metrics=HealthMetrics(
            neurological_status=NeurologicalStatus(
                vision=VisionMetrics(
                    right_eye="good", left_eye_mobility="good", binocular="excellent"
                ),
                balance="excellent",
                coordination="good",
            ),
            physical_metrics=PhysicalMetrics(
                heart_rate=HeartRateZones(
                    resting=75,
                    max=187,
                    zones={
                        "recovery": "up to 131",
                        "aerobic": "131-142",
                        "anaerobic": "142-164",
                    },
                )
            ),
        ),
        fitness_plan=[],
        progression_metrics={
            "training_intensity": {
                "week1": "moderate",
                "week2": "moderate with high elements",
            },
            "complexity": {"week1": "basic", "week2": "advanced"},
            "focus_areas": {
                "vision": "daily exercises",
                "coordination": "progressive complexity increase",
                "endurance": "gradual load increase",
            },
        },
        recommendations={
            "preparation": ["Prepare equipment in advance"],
            "recovery": ["Ensure adequate sleep"],
            "progression": ["Gradually increase exercise complexity"],
        },
    )

    assert plan.plan_title == "Test Plan"
    assert len(plan.plan_parameters.training_days) == 3
    assert plan.health_metrics.neurological_status.balance == "excellent"
    assert plan.health_metrics.physical_metrics.heart_rate.resting == 75
