from datetime import datetime, timedelta
from typing import Any, Dict, List

from pydantic import root_validator, validator

from .health import HealthMetrics
from .plan import NeuroPlan, PlanParameters
from .workout import IntensityLevel, WorkoutType


class HealthMetricsValidator:
    """Validation rules for health metrics."""

    @validator("vision_metrics")
    def validate_vision_metrics(cls, v):
        if not 0 <= v.eye_mobility_score <= 100:
            raise ValueError("Eye mobility score must be between 0 and 100")
        if not 0 <= v.visual_processing_speed <= 2.0:
            raise ValueError(
                "Visual processing speed must be between 0 and 2.0 seconds"
            )
        return v

    @validator("heart_rate_zones")
    def validate_heart_rate_zones(cls, v):
        if not 40 <= v.resting <= 100:
            raise ValueError("Resting heart rate must be between 40 and 100")
        if not v.resting < v.aerobic < v.anaerobic:
            raise ValueError(
                "Heart rate zones must be in ascending order: resting < aerobic < anaerobic"
            )
        return v

    @validator("neurological_status")
    def validate_neurological_status(cls, v):
        if not 0 <= v.balance_score <= 100:
            raise ValueError("Balance score must be between 0 and 100")
        if not 0 <= v.coordination_score <= 100:
            raise ValueError("Coordination score must be between 0 and 100")
        if not 0.1 <= v.reaction_time <= 1.0:
            raise ValueError("Reaction time must be between 0.1 and 1.0 seconds")
        return v


class PlanValidator:
    """Validation rules for training plans."""

    @root_validator
    def validate_plan_structure(cls, values):
        plan_params = values.get("plan_parameters")
        weeks = values.get("weeks")

        if not plan_params or not weeks:
            return values

        # Validate number of weeks matches plan duration
        if len(weeks) != plan_params.duration_weeks:
            raise ValueError(
                f"Number of weeks ({len(weeks)}) does not match plan duration ({plan_params.duration_weeks})"
            )

        # Validate weekly structure
        for week in weeks:
            if len(week.days) != 7:
                raise ValueError("Each week must contain exactly 7 days")

            training_days = sum(1 for day in week.days if day.workouts)
            if training_days > plan_params.training_days_per_week:
                raise ValueError(
                    f"Week contains more training days ({training_days}) than specified in plan parameters ({plan_params.training_days_per_week})"
                )

        return values

    @validator("progression_metrics")
    def validate_progression_metrics(cls, v):
        if v.target_balance_improvement < 0 or v.target_balance_improvement > 50:
            raise ValueError(
                "Target balance improvement must be between 0 and 50 percent"
            )
        if (
            v.target_reaction_time_improvement < 0
            or v.target_reaction_time_improvement > 0.5
        ):
            raise ValueError(
                "Target reaction time improvement must be between 0 and 0.5 seconds"
            )
        return v


class WorkoutValidator:
    """Validation rules for workouts."""

    @validator("duration")
    def validate_duration(cls, v):
        if v < 5 or v > 120:
            raise ValueError("Workout duration must be between 5 and 120 minutes")
        return v

    @validator("intensity")
    def validate_intensity(cls, v):
        if v not in [level.value for level in IntensityLevel]:
            raise ValueError(f"Invalid intensity level: {v}")
        return v

    @validator("workout_type")
    def validate_workout_type(cls, v):
        if v not in [wtype.value for wtype in WorkoutType]:
            raise ValueError(f"Invalid workout type: {v}")
        return v

    @root_validator
    def validate_workout_structure(cls, values):
        workout_type = values.get("workout_type")
        duration = values.get("duration")
        intensity = values.get("intensity")

        if workout_type == WorkoutType.WARM_UP and duration > 15:
            raise ValueError("Warm-up duration should not exceed 15 minutes")

        if workout_type == WorkoutType.COOL_DOWN and duration > 10:
            raise ValueError("Cool-down duration should not exceed 10 minutes")

        if workout_type == WorkoutType.WARM_UP and intensity == IntensityLevel.HIGH:
            raise ValueError("Warm-up intensity should not be high")

        return values
