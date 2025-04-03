from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, conlist, root_validator, validator

from .base import TimestampedModel
from .health import HealthMetrics, ProgressionMetrics
from .validators import PlanValidator
from .workout import IntensityLevel, Week


class PlanParameters(BaseModel):
    """Parameters for a neuro fitness training plan."""

    duration_weeks: int
    training_days_per_week: int
    session_duration: int  # minutes
    equipment_available: List[str]
    focus_areas: List[str]
    difficulty_level: str  # "beginner", "intermediate", "advanced"

    @validator("duration_weeks")
    def validate_duration(cls, v):
        """Validate that duration is reasonable."""
        if not 1 <= v <= 52:
            raise ValueError("Duration must be between 1 and 52 weeks")
        return v

    @validator("training_days_per_week")
    def validate_training_days(cls, v):
        """Validate that training days is reasonable."""
        if not 1 <= v <= 7:
            raise ValueError("Training days must be between 1 and 7")
        return v

    @validator("session_duration")
    def validate_session_duration(cls, v):
        """Validate that session duration is reasonable."""
        if not 10 <= v <= 180:
            raise ValueError("Session duration must be between 10 and 180 minutes")
        return v

    @validator("difficulty_level")
    def validate_difficulty(cls, v):
        """Validate that difficulty level is valid."""
        valid_levels = ["beginner", "intermediate", "advanced"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Difficulty must be one of: {', '.join(valid_levels)}")
        return v.lower()

    @validator("focus_areas")
    def validate_focus_areas(cls, v):
        """Validate that focus areas are valid."""
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

    @validator("equipment_available")
    def validate_equipment(cls, v):
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


class Recommendations(BaseModel):
    """Model for plan recommendations."""

    preparation: List[str]
    recovery: List[str]
    nutrition: List[str]
    sleep: List[str]

    class Config:
        min_anystr_length = 1
        max_anystr_length = 200

    @validator("preparation", "recovery", "nutrition", "sleep")
    def validate_recommendation_list(cls, v: List[str]) -> List[str]:
        """Validate that recommendation lists are not empty and items are not too long."""
        if not v:
            raise ValueError("Recommendations list cannot be empty")
        for item in v:
            if not item.strip():
                raise ValueError("Recommendation cannot be empty")
            if len(item) > 200:
                raise ValueError("Recommendation must be less than 200 characters")
        return v

    @validator("preparation")
    def validate_preparation(cls, v: List[str]) -> List[str]:
        """Validate preparation recommendations."""
        required_topics = ["warm-up", "equipment", "safety"]
        if not any(topic in " ".join(v).lower() for topic in required_topics):
            raise ValueError(
                "Preparation recommendations must include warm-up, equipment setup, or safety guidelines"
            )
        return v

    @validator("recovery")
    def validate_recovery(cls, v: List[str]) -> List[str]:
        """Validate recovery recommendations."""
        required_topics = ["cool-down", "rest", "stretching"]
        if not any(topic in " ".join(v).lower() for topic in required_topics):
            raise ValueError(
                "Recovery recommendations must include cool-down, rest, or stretching guidelines"
            )
        return v

    @validator("nutrition")
    def validate_nutrition(cls, v: List[str]) -> List[str]:
        """Validate nutrition recommendations."""
        required_topics = ["hydration", "meal", "protein", "timing"]
        if not any(topic in " ".join(v).lower() for topic in required_topics):
            raise ValueError(
                "Nutrition recommendations must include hydration, meal planning, or nutrient timing"
            )
        return v

    @validator("sleep")
    def validate_sleep(cls, v: List[str]) -> List[str]:
        """Validate sleep recommendations."""
        required_topics = ["hours", "schedule", "quality"]
        if not any(topic in " ".join(v).lower() for topic in required_topics):
            raise ValueError(
                "Sleep recommendations must include duration, schedule, or quality guidelines"
            )
        return v


class NeuroPlan(TimestampedModel, PlanValidator):
    """Model for a complete neuro fitness training plan."""

    plan_title: str
    plan_parameters: PlanParameters
    weeks: List[Week]
    progression_metrics: ProgressionMetrics
    recommendations: Recommendations
    notes: Optional[str] = None

    @validator("plan_title")
    def validate_title(cls, v: str) -> str:
        """Validate that the plan title is appropriate."""
        if not v.strip():
            raise ValueError("Plan title cannot be empty")
        if len(v) > 100:
            raise ValueError("Plan title must be less than 100 characters")
        return v.strip()

    @validator("weeks")
    def validate_weeks(cls, v: List[Week], values: Dict[str, Any]) -> List[Week]:
        """Validate that weeks match plan parameters."""
        if not v:
            raise ValueError("Plan must have at least one week")

        plan_params = values.get("plan_parameters")
        if plan_params and len(v) != plan_params.duration_weeks:
            raise ValueError(
                f"Number of weeks ({len(v)}) must match plan duration "
                f"({plan_params.duration_weeks})"
            )

        # Validate week numbers are sequential
        for i, week in enumerate(v, 1):
            if week.week_number != i:
                raise ValueError(
                    f"Week numbers must be sequential, got {week.week_number} at position {i}"
                )

        return v

    @validator("progression_metrics")
    def validate_progression_metrics(
        cls, v: ProgressionMetrics, values: Dict[str, Any]
    ) -> ProgressionMetrics:
        """Validate that progression metrics are reasonable."""
        plan_params = values.get("plan_parameters")
        if not plan_params:
            return v

        # Validate that improvement targets are reasonable based on duration
        max_improvements = {
            "beginner": {
                "balance": 30,
                "coordination": 25,
                "reaction_time": 20,
                "visual_processing": 25,
            },
            "intermediate": {
                "balance": 20,
                "coordination": 15,
                "reaction_time": 15,
                "visual_processing": 20,
            },
            "advanced": {
                "balance": 10,
                "coordination": 10,
                "reaction_time": 10,
                "visual_processing": 15,
            },
        }

        difficulty = plan_params.difficulty_level
        duration_factor = (
            plan_params.duration_weeks / 12
        )  # Normalize to yearly improvement

        if (
            v.target_balance_improvement
            > max_improvements[difficulty]["balance"] * duration_factor
        ):
            raise ValueError(
                f"Balance improvement target too high for {difficulty} level "
                f"({v.target_balance_improvement}% > {max_improvements[difficulty]['balance'] * duration_factor}%)"
            )

        if (
            v.target_coordination_improvement
            > max_improvements[difficulty]["coordination"] * duration_factor
        ):
            raise ValueError(
                f"Coordination improvement target too high for {difficulty} level "
                f"({v.target_coordination_improvement}% > {max_improvements[difficulty]['coordination'] * duration_factor}%)"
            )

        if (
            v.target_reaction_time_improvement
            > max_improvements[difficulty]["reaction_time"] * duration_factor
        ):
            raise ValueError(
                f"Reaction time improvement target too high for {difficulty} level "
                f"({v.target_reaction_time_improvement}% > {max_improvements[difficulty]['reaction_time'] * duration_factor}%)"
            )

        if (
            v.target_visual_processing_improvement
            > max_improvements[difficulty]["visual_processing"] * duration_factor
        ):
            raise ValueError(
                f"Visual processing improvement target too high for {difficulty} level "
                f"({v.target_visual_processing_improvement}% > {max_improvements[difficulty]['visual_processing'] * duration_factor}%)"
            )

        return v

    @validator("notes")
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate that notes are not too long."""
        if v is not None:
            if len(v) > 1000:
                raise ValueError("Notes must be less than 1000 characters")
            return v.strip() or None
        return v

    @root_validator(pre=True)
    def validate_plan_consistency(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate overall plan consistency."""
        plan_params = values.get("plan_parameters")
        weeks = values.get("weeks", [])
        progression_metrics = values.get("progression_metrics")
        recommendations = values.get("recommendations")

        if not all([plan_params, progression_metrics, recommendations]) or not weeks:
            return values  # Skip validation if any required field is missing

        if not isinstance(plan_params, PlanParameters):
            return values  # Skip validation if plan_params is not the right type

        # Validate focus areas consistency
        plan_focus_areas = set(plan_params.focus_areas)
        week_focus_areas = set()
        for week in weeks:
            if not week or not hasattr(week, "focus") or not week.focus:
                continue
            if week.focus.primary:
                week_focus_areas.add(week.focus.primary.lower())
            if week.focus.secondary:
                week_focus_areas.add(week.focus.secondary.lower())

        if not plan_focus_areas.issuperset(week_focus_areas):
            raise ValueError(
                f"Week focus areas {week_focus_areas - plan_focus_areas} "
                f"not included in plan focus areas {plan_focus_areas}"
            )

        # Validate training days consistency
        for week in weeks:
            if not week or not hasattr(week, "days") or not week.days:
                continue
            training_days = sum(
                1
                for day in week.days
                if day and hasattr(day, "workouts") and day.workouts
            )
            if training_days > plan_params.training_days_per_week:
                raise ValueError(
                    f"Week {week.week_number} has {training_days} training days, "
                    f"but plan specifies {plan_params.training_days_per_week}"
                )

        # Validate session duration consistency
        for week in weeks:
            if not week or not hasattr(week, "days") or not week.days:
                continue
            for day in week.days:
                if not day or not hasattr(day, "workouts") or not day.workouts:
                    continue
                for workout in day.workouts:
                    if (
                        workout
                        and hasattr(workout, "duration")
                        and workout.duration > plan_params.session_duration
                    ):
                        raise ValueError(
                            f"Workout in week {week.week_number} exceeds "
                            f"session duration limit ({workout.duration} > "
                            f"{plan_params.session_duration})"
                        )

        # Validate equipment usage consistency
        available_equipment = set(plan_params.equipment_available)
        for week in weeks:
            if not week or not hasattr(week, "days") or not week.days:
                continue
            for day in week.days:
                if not day or not hasattr(day, "workouts") or not day.workouts:
                    continue
                for workout in day.workouts:
                    if (
                        workout
                        and hasattr(workout, "equipment_needed")
                        and workout.equipment_needed
                    ):
                        equipment_needed = set(workout.equipment_needed)
                        if not available_equipment.issuperset(equipment_needed):
                            raise ValueError(
                                f"Workout in week {week.week_number} requires unavailable "
                                f"equipment: {equipment_needed - available_equipment}"
                            )

        # Validate progression metrics consistency
        if not isinstance(progression_metrics, ProgressionMetrics):
            return (
                values  # Skip validation if progression_metrics is not the right type
            )

        difficulty_factors = {"beginner": 1.0, "intermediate": 0.7, "advanced": 0.5}
        difficulty = plan_params.difficulty_level
        duration_weeks = plan_params.duration_weeks

        # Calculate expected improvements based on difficulty and duration
        expected_improvement = (
            20 * difficulty_factors[difficulty] * (duration_weeks / 12)
        )

        metrics = [
            ("balance", progression_metrics.target_balance_improvement),
            ("coordination", progression_metrics.target_coordination_improvement),
            ("reaction_time", progression_metrics.target_reaction_time_improvement),
            (
                "visual_processing",
                progression_metrics.target_visual_processing_improvement,
            ),
        ]

        for metric_name, target in metrics:
            if target > expected_improvement * 1.5:  # Allow 50% above expected
                raise ValueError(
                    f"{metric_name.replace('_', ' ').title()} improvement target "
                    f"({target}%) is too aggressive for {difficulty} level "
                    f"(expected around {expected_improvement}%)"
                )

        return values

    class Config:
        """Pydantic model configuration."""

        validate_assignment = True
        schema_extra = {
            "example": {
                "plan_title": "Beginner Neuro-Enhancement Program",
                "plan_parameters": {
                    "duration_weeks": 8,
                    "training_days_per_week": 3,
                    "session_duration": 45,
                    "equipment_available": ["resistance bands", "balance board"],
                    "focus_areas": ["balance", "coordination", "reaction_time"],
                    "difficulty_level": "beginner",
                },
                "weeks": [
                    {
                        "week_number": 1,
                        "focus": {
                            "primary": "Foundation and Assessment",
                            "secondary": "Basic Movement Patterns",
                        },
                        "days": [],  # Simplified for example
                        "recovery_protocols": {
                            "recommended_sleep": 8,
                            "hydration_target": 2.5,
                            "nutrition_tips": [
                                "Focus on whole foods",
                                "Increase protein intake",
                            ],
                            "recovery_exercises": [
                                "Light stretching",
                                "Deep breathing",
                            ],
                        },
                    }
                ],
                "progression_metrics": {
                    "target_balance_improvement": 20,
                    "target_coordination_improvement": 15,
                    "target_reaction_time_improvement": 0.1,
                    "target_visual_processing_improvement": 0.2,
                },
                "recommendations": {
                    "preparation": [
                        "Ensure proper hydration",
                        "Light warm-up before sessions",
                    ],
                    "recovery": [
                        "Cool-down stretches",
                        "Adequate rest between sessions",
                    ],
                    "nutrition": ["Balanced meals", "Post-workout protein"],
                    "sleep": ["Aim for 7-9 hours", "Consistent sleep schedule"],
                },
            }
        }
