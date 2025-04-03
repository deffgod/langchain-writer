from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, root_validator, validator

from .base import Effect, TimestampedModel, UserBenefit
from .validators import WorkoutValidator

T = TypeVar("T", bound=BaseModel)


class WorkoutType(str, Enum):
    WARM_UP = "warm_up"
    MAIN_WORKOUT = "main_workout"
    COOL_DOWN = "cool_down"


class IntensityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Workout(TimestampedModel, WorkoutValidator):
    """Model for a single workout session."""

    name: str
    duration: int  # minutes
    workout_type: WorkoutType
    intensity: IntensityLevel
    focus: List[str]
    equipment_needed: List[str]
    effects: List[Effect]
    user_benefits: List[UserBenefit]
    practical_tips: List[str]
    description: Optional[str] = None

    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate that the workout name is appropriate."""
        if not v.strip():
            raise ValueError("Workout name cannot be empty")
        if len(v) > 100:
            raise ValueError("Workout name must be less than 100 characters")
        return v.strip()

    @validator("duration")
    def validate_duration(cls, v: int) -> int:
        """Validate that duration is reasonable."""
        if not 5 <= v <= 180:
            raise ValueError("Duration must be between 5 and 180 minutes")
        return v

    @validator("focus")
    def validate_focus(cls, v: List[str]) -> List[str]:
        """Validate that focus areas are valid."""
        if not v:
            raise ValueError("At least one focus area is required")

        valid_areas = [
            "balance",
            "coordination",
            "reaction_time",
            "visual_processing",
            "strength",
            "endurance",
            "flexibility",
            "cognitive",
        ]
        for area in v:
            if area.lower() not in valid_areas:
                raise ValueError(f"Focus area must be one of: {', '.join(valid_areas)}")
        return [area.lower() for area in v]

    @validator("equipment_needed")
    def validate_equipment(cls, v: List[str]) -> List[str]:
        """Validate that equipment items are valid."""
        valid_equipment = [
            "resistance bands",
            "balance board",
            "yoga mat",
            "dumbbells",
            "kettlebell",
            "foam roller",
            "medicine ball",
            "stability ball",
            "bosu ball",
            "jump rope",
            "pull-up bar",
            "none",
        ]
        for item in v:
            if item.lower() not in valid_equipment:
                raise ValueError(
                    f"Equipment must be one of: {', '.join(valid_equipment)}"
                )
        return [item.lower() for item in v]

    @validator("effects")
    def validate_effects(cls, v: List[Effect]) -> List[Effect]:
        """Validate that effects are appropriate."""
        if not v:
            raise ValueError("At least one effect is required")
        return v

    @validator("user_benefits")
    def validate_benefits(cls, v: List[UserBenefit]) -> List[UserBenefit]:
        """Validate that user benefits are appropriate."""
        if not v:
            raise ValueError("At least one user benefit is required")
        return v

    @validator("practical_tips")
    def validate_tips(cls, v: List[str]) -> List[str]:
        """Validate that practical tips are appropriate."""
        if not v:
            raise ValueError("At least one practical tip is required")
        for tip in v:
            if not tip.strip():
                raise ValueError("Practical tip cannot be empty")
            if len(tip) > 200:
                raise ValueError("Practical tip must be less than 200 characters")
        return [tip.strip() for tip in v]

    @validator("description")
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate that description is not too long."""
        if v is not None:
            if len(v) > 1000:
                raise ValueError("Description must be less than 1000 characters")
            return v.strip() or None
        return v

    @root_validator(pre=True)
    def validate_workout_consistency(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that the workout is consistent."""
        workout_type = values.get("workout_type")
        intensity = values.get("intensity")
        duration = values.get("duration")

        if not all([workout_type, intensity, duration]):
            return values

        try:
            duration_int = int(str(duration))
        except (TypeError, ValueError):
            return values

        # Validate warm-up and cool-down durations
        if workout_type == WorkoutType.WARM_UP and duration_int > 20:
            raise ValueError("Warm-up should not exceed 20 minutes")
        if workout_type == WorkoutType.COOL_DOWN and duration_int > 15:
            raise ValueError("Cool-down should not exceed 15 minutes")

        # Validate intensity based on workout type
        if (
            workout_type in [WorkoutType.WARM_UP, WorkoutType.COOL_DOWN]
            and intensity == IntensityLevel.HIGH
        ):
            raise ValueError(f"{workout_type} should not have high intensity")

        # Validate main workout duration based on intensity
        if workout_type == WorkoutType.MAIN_WORKOUT:
            if intensity == IntensityLevel.HIGH and duration_int > 60:
                raise ValueError("High intensity workouts should not exceed 60 minutes")
            if intensity == IntensityLevel.LOW and duration_int < 20:
                raise ValueError("Low intensity workouts should be at least 20 minutes")

        return values


class Day(BaseModel):
    """Model for a training day."""

    date: str
    workouts: List[Workout]
    total_duration: Optional[int] = None
    notes: Optional[str] = None

    @validator("date")
    def validate_date(cls, v: str) -> str:
        """Validate that date is in correct format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    @validator("workouts")
    def validate_workouts(cls, v: List[Workout]) -> List[Workout]:
        """Validate that workouts are properly ordered."""
        if not v:
            return v

        # Check workout order (warm-up -> main -> cool-down)
        workout_types = [w.workout_type for w in v]
        if WorkoutType.WARM_UP in workout_types:
            if workout_types.index(WorkoutType.WARM_UP) != 0:
                raise ValueError("Warm-up must be the first workout")

        if WorkoutType.COOL_DOWN in workout_types:
            if workout_types.index(WorkoutType.COOL_DOWN) != len(workout_types) - 1:
                raise ValueError("Cool-down must be the last workout")

        return v

    @root_validator(pre=True)
    def calculate_total_duration(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total duration from workouts."""
        workouts = values.get("workouts", [])
        if workouts:
            values["total_duration"] = sum(w.duration for w in workouts)
        return values

    @validator("notes")
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate that notes are not too long."""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Notes must be less than 500 characters")
            return v.strip() or None
        return v


class WeeklyFocus(BaseModel):
    """Model for weekly training focus."""

    primary: str
    secondary: Optional[str] = None
    notes: Optional[str] = None

    @validator("primary", "secondary")
    def validate_focus_area(cls, v: Optional[str]) -> Optional[str]:
        """Validate that focus areas are valid."""
        if v is None:
            return v

        valid_areas = [
            "balance",
            "coordination",
            "reaction_time",
            "visual_processing",
            "strength",
            "endurance",
            "flexibility",
            "cognitive",
            "foundation",
            "assessment",
            "recovery",
            "technique",
        ]
        if v.lower() not in valid_areas:
            raise ValueError(f"Focus area must be one of: {', '.join(valid_areas)}")
        return v.lower()

    @validator("notes")
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate that notes are not too long."""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Notes must be less than 500 characters")
            return v.strip() or None
        return v


class RecoveryProtocols(BaseModel):
    """Model for recovery protocols."""

    recommended_sleep: int  # hours
    hydration_target: float  # liters
    nutrition_tips: List[str]
    recovery_exercises: List[str]

    @validator("recommended_sleep")
    def validate_sleep(cls, v: int) -> int:
        """Validate that sleep duration is reasonable."""
        if not 6 <= v <= 10:
            raise ValueError("Recommended sleep must be between 6 and 10 hours")
        return v

    @validator("hydration_target")
    def validate_hydration(cls, v: float) -> float:
        """Validate that hydration target is reasonable."""
        if not 1.5 <= v <= 4.0:
            raise ValueError("Hydration target must be between 1.5 and 4.0 liters")
        return round(v, 1)

    @validator("nutrition_tips", "recovery_exercises")
    def validate_tips_and_exercises(cls, v: List[str]) -> List[str]:
        """Validate that tips and exercises are appropriate."""
        if not v:
            raise ValueError("At least one item is required")
        for item in v:
            if not item.strip():
                raise ValueError("Item cannot be empty")
            if len(item) > 200:
                raise ValueError("Item must be less than 200 characters")
        return [item.strip() for item in v]


class Week(BaseModel):
    """Model for a training week."""

    week_number: int
    focus: WeeklyFocus
    days: List[Day]
    recovery_protocols: RecoveryProtocols
    notes: Optional[str] = None

    @validator("week_number")
    def validate_week_number(cls, v: int) -> int:
        """Validate that week number is positive."""
        if v < 1:
            raise ValueError("Week number must be positive")
        return v

    @validator("days")
    def validate_days(cls, v: List[Day]) -> List[Day]:
        """Validate that days are properly ordered."""
        if not v:
            return v

        # Check that dates are sequential
        dates = [datetime.strptime(day.date, "%Y-%m-%d") for day in v]
        for i in range(1, len(dates)):
            delta = dates[i] - dates[i - 1]
            if delta.days != 1:
                raise ValueError("Days must be sequential")

        return v

    @validator("notes")
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate that notes are not too long."""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Notes must be less than 500 characters")
            return v.strip() or None
        return v
