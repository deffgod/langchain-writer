from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from services.plan_generator import PlanAdaptationService, PlanGenerationService

from models import HealthMetrics, NeuroPlan, PlanParameters, Week

from .dependencies import get_adaptation_service, get_plan_service
from .schemas import AdaptationRequest, PlanResponse, ProgressUpdate, UserProfileCreate

router = APIRouter(prefix="/api/v1")


@router.post("/plans/", response_model=PlanResponse)
async def create_plan(
    user_profile: UserProfileCreate,
    plan_service: PlanGenerationService = Depends(get_plan_service),
):
    """Create a new neuro fitness plan."""
    try:
        plan = await plan_service.generate_plan(
            user_profile.dict(), user_profile.health_metrics
        )
        return PlanResponse(status="success", data=plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str):
    """Retrieve a specific plan."""
    # Implementation would fetch plan from database
    pass


@router.put("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: str,
    adaptation_request: AdaptationRequest,
    adaptation_service: PlanAdaptationService = Depends(get_adaptation_service),
):
    """Update an existing plan based on progress."""
    try:
        updated_plan = await adaptation_service.adapt_plan(
            current_plan=adaptation_request.current_plan,
            new_metrics=adaptation_request.new_metrics,
            progress_data=adaptation_request.progress_data,
        )
        return PlanResponse(status="success", data=updated_plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plans/{plan_id}/progress", response_model=PlanResponse)
async def record_progress(
    plan_id: str,
    progress: ProgressUpdate,
    adaptation_service: PlanAdaptationService = Depends(get_adaptation_service),
):
    """Record progress and get updated recommendations."""
    # Implementation would record progress and update plan
    pass
