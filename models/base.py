from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    id: UUID = Field(default_factory=uuid4)


class Effect(BaseModel):
    effect: str
    details: List[str]
    timeframe: Optional[Dict[str, str]]


class UserBenefit(BaseModel):
    dailyLife: Dict[str, List[str]]
    progressTimeline: Dict[str, str]
    measureableResults: Dict[str, str]


class MonitoringProtocol(BaseModel):
    pre_workout: List[str]
    post_workout: List[str]
