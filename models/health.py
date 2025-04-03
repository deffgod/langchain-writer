from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from .base import TimestampedModel
from .validators import HealthMetricsValidator


class VisionMetrics(BaseModel):
    eye_mobility_score: float  # 0-100
    visual_processing_speed: float  # seconds


class HeartRateZones(BaseModel):
    resting: int
    aerobic: int
    anaerobic: int


class NeurologicalStatus(BaseModel):
    balance_score: float  # 0-100
    coordination_score: float  # 0-100
    reaction_time: float  # seconds


class PhysicalMetrics(BaseModel):
    height: Optional[float]  # cm
    weight: Optional[float]  # kg
    body_fat: Optional[float]  # percentage


class HealthMetrics(TimestampedModel):
    """Model for tracking health-related metrics."""

    user_id: str
    date: datetime

    # Sleep metrics
    sleep_duration: float  # Hours of sleep
    sleep_quality: int  # 0-100 score

    # Cognitive metrics
    stress_level: int  # 0-100 score
    mental_fatigue: int  # 0-100 score
    cognitive_performance: int  # 0-100 score

    # Physical metrics
    heart_rate: int
    resting_heart_rate: int
    blood_pressure_systolic: int
    blood_pressure_diastolic: int

    # Recovery metrics
    fatigue_level: int  # 0-100 score
    recovery_rate: int  # 0-100 score
    hydration_level: int  # 0-100 score

    # Vision metrics
    visual_acuity: float  # 20/20 scale
    depth_perception: int  # 0-100 score
    tracking_speed: int  # 0-100 score

    # Balance metrics
    static_balance: int  # 0-100 score
    dynamic_balance: int  # 0-100 score

    class Config:
        """Pydantic model configuration."""

        validate_assignment = True

    @validator(
        "sleep_quality",
        "stress_level",
        "mental_fatigue",
        "cognitive_performance",
        "fatigue_level",
        "recovery_rate",
        "hydration_level",
        "depth_perception",
        "tracking_speed",
        "static_balance",
        "dynamic_balance",
    )
    def validate_percentage(cls, v):
        """Validate that the value is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError("Value must be between 0 and 100")
        return v

    @validator("sleep_duration")
    def validate_sleep_duration(cls, v):
        """Validate that sleep duration is reasonable."""
        if not 0 <= v <= 24:
            raise ValueError("Sleep duration must be between 0 and 24 hours")
        return v

    @validator("heart_rate", "resting_heart_rate")
    def validate_heart_rate(cls, v):
        """Validate that heart rate is reasonable."""
        if not 30 <= v <= 220:
            raise ValueError("Heart rate must be between 30 and 220 bpm")
        return v

    @validator("blood_pressure_systolic")
    def validate_systolic(cls, v):
        """Validate that systolic blood pressure is reasonable."""
        if not 70 <= v <= 200:
            raise ValueError("Systolic blood pressure must be between 70 and 200 mmHg")
        return v

    @validator("blood_pressure_diastolic")
    def validate_diastolic(cls, v):
        """Validate that diastolic blood pressure is reasonable."""
        if not 40 <= v <= 130:
            raise ValueError("Diastolic blood pressure must be between 40 and 130 mmHg")
        return v

    @validator("visual_acuity")
    def validate_visual_acuity(cls, v):
        """Validate that visual acuity is reasonable."""
        if not 0 <= v <= 2:  # 20/10 to 20/400 in decimal form
            raise ValueError("Visual acuity must be between 0 and 2")
        return v


class ProgressionMetrics(BaseModel):
    target_balance_improvement: float  # percentage
    target_coordination_improvement: float  # percentage
    target_reaction_time_improvement: float  # seconds
    target_visual_processing_improvement: float  # seconds
