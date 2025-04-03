from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from models import HealthMetrics, NeuroPlan, PlanParameters, ProgressionMetrics, Week


class UserProfileCreate(BaseModel):
    """Schema for creating a new user profile and generating a plan."""

    name: str
    age: int = Field(..., ge=0, le=120)
    fitness_level: str = Field(..., regex="^(beginner|intermediate|advanced)$")
    goals: List[str]
    health_metrics: HealthMetrics
    preferred_training_days: int = Field(..., ge=1, le=7)
    time_per_session: int = Field(..., ge=15, le=180)
    equipment_available: List[str] = []
    medical_conditions: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "age": 30,
                "fitness_level": "intermediate",
                "goals": ["improve balance", "enhance focus"],
                "health_metrics": {
                    "vision_metrics": {
                        "eye_mobility_score": 85,
                        "visual_processing_speed": 0.75,
                    },
                    "heart_rate_zones": {
                        "resting": 65,
                        "aerobic": 135,
                        "anaerobic": 165,
                    },
                    "neurological_status": {
                        "balance_score": 80,
                        "coordination_score": 75,
                        "reaction_time": 0.25,
                    },
                },
                "preferred_training_days": 4,
                "time_per_session": 45,
                "equipment_available": ["resistance bands", "balance board"],
                "medical_conditions": [],
            }
        }


class ProgressUpdate(BaseModel):
    """Schema for recording progress updates."""

    date: str
    completed_workouts: List[str]
    health_metrics: HealthMetrics
    perceived_difficulty: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None


class AdaptationRequest(BaseModel):
    """Schema for requesting plan adaptation."""

    current_plan: NeuroPlan
    new_metrics: HealthMetrics
    progress_data: List[ProgressUpdate]


class PlanResponse(BaseModel):
    """Schema for API responses containing plan data."""

    status: str
    data: Optional[NeuroPlan] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None
