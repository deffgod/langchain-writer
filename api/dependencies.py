from services.plan_generator import PlanAdaptationService, PlanGenerationService


def get_plan_service() -> PlanGenerationService:
    """Dependency provider for PlanGenerationService."""
    return PlanGenerationService()


def get_adaptation_service() -> PlanAdaptationService:
    """Dependency provider for PlanAdaptationService."""
    return PlanAdaptationService()
