from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from langchain_writer import ChatWriter
from langchain_writer.tools import GraphTool
from models import (
    Day,
    Effect,
    HealthMetrics,
    IntensityLevel,
    NeuroPlan,
    PlanParameters,
    RecoveryProtocols,
    UserBenefit,
    Week,
    WeeklyFocus,
    Workout,
    WorkoutType,
)


class PlanGenerationService:
    def __init__(self, api_key: str, graph_ids: List[str]):
        self.llm = ChatWriter(model="palmyra-x-004", temperature=0.7, api_key=api_key)
        self.graph_tool = GraphTool(graph_ids=graph_ids)
        self.llm_with_tools = self.llm.bind_tools([self.graph_tool])

        # Cache for knowledge graph queries
        self._query_cache = {}

    async def generate_plan(
        self, user_profile: Dict, health_metrics: HealthMetrics
    ) -> NeuroPlan:
        """Generate a personalized neuro fitness plan."""

        # Query knowledge graph for comprehensive recommendations
        knowledge = await self._query_knowledge_graph(user_profile, health_metrics)

        # Generate plan parameters with cognitive load balancing
        plan_params = await self._generate_plan_parameters(user_profile, knowledge)

        # Generate weekly structure with neural-physical balance
        weeks = await self._generate_weeks(plan_params, health_metrics, knowledge)

        # Create complete plan with progression tracking
        plan = NeuroPlan(
            plan_title=f"Personalized Neurofitness Program for {user_profile['name']}",
            plan_parameters=plan_params,
            health_metrics=health_metrics,
            weeks=weeks,
            progression_metrics=await self._generate_progression_metrics(weeks),
            recommendations=await self._generate_recommendations(
                health_metrics,
                plan_params,
                await self._generate_progression_metrics(weeks),
            ),
            notes=f"Generated on {datetime.now().strftime('%Y-%m-%d')} based on latest health metrics",
        )

        return plan

    async def _query_knowledge_graph(
        self, user_profile: Dict, health_metrics: HealthMetrics
    ) -> Dict:
        """Query the knowledge graph for comprehensive exercise and progression recommendations."""
        cache_key = f"{user_profile['id']}_{health_metrics.id}"
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]

        # Query exercise recommendations based on cognitive domains
        cognitive_query = await self._query_cognitive_domains(health_metrics)

        # Query physical exercise correlations
        physical_query = await self._query_physical_correlations(
            user_profile, health_metrics
        )

        # Query progression patterns
        progression_query = await self._query_progression_patterns(health_metrics)

        # Combine and process all query results
        knowledge = {
            "cognitive_domains": cognitive_query,
            "physical_correlations": physical_query,
            "progression_patterns": progression_query,
            "timestamp": datetime.now().isoformat(),
        }

        self._query_cache[cache_key] = knowledge
        return knowledge

    async def _query_cognitive_domains(self, health_metrics: HealthMetrics) -> Dict:
        """Query exercises and activities based on cognitive domain scores."""
        response = await self.llm_with_tools.ainvoke(
            f"""Analyze cognitive domains and recommend exercises based on these metrics:
            Vision: {health_metrics.vision_metrics}
            Neurological: {health_metrics.neurological_status}

            For each cognitive domain:
            1. Identify optimal exercises
            2. Specify cognitive load levels
            3. Define progression thresholds
            4. List contraindications
            """
        )
        return response.additional_kwargs.get("graph_data", {})

    async def _query_physical_correlations(
        self, user_profile: Dict, health_metrics: HealthMetrics
    ) -> Dict:
        """Query physical exercise correlations with cognitive benefits."""
        response = await self.llm_with_tools.ainvoke(
            f"""Find exercises with optimal neural-physical balance based on:
            Profile: {user_profile}
            Heart Rate Zones: {health_metrics.heart_rate_zones}
            Physical Metrics: {health_metrics.physical_metrics}

            Identify:
            1. Exercises with dual benefits (physical and cognitive)
            2. Optimal intensity ranges
            3. Recovery requirements
            4. Adaptation indicators
            """
        )
        return response.additional_kwargs.get("graph_data", {})

    async def _query_progression_patterns(self, health_metrics: HealthMetrics) -> Dict:
        """Query successful progression patterns for similar profiles."""
        response = await self.llm_with_tools.ainvoke(
            f"""Analyze progression patterns for profiles with similar metrics:
            Balance Score: {health_metrics.neurological_status.balance_score}
            Coordination Score: {health_metrics.neurological_status.coordination_score}
            Reaction Time: {health_metrics.neurological_status.reaction_time}

            Determine:
            1. Optimal progression rates
            2. Success indicators
            3. Risk factors
            4. Adaptation timeframes
            """
        )
        return response.additional_kwargs.get("graph_data", {})

    async def _generate_plan_parameters(
        self, user_profile: Dict, knowledge: Dict
    ) -> PlanParameters:
        """Generate plan parameters based on user profile and knowledge graph data."""
        # Calculate optimal training frequency based on cognitive load
        cognitive_domains = knowledge.get("cognitive_domains", {})
        physical_correlations = knowledge.get("physical_correlations", {})

        # Determine optimal training days based on cognitive recovery needs
        optimal_training_days = self._calculate_optimal_training_days(
            cognitive_domains, user_profile.get("preferred_training_days", 3)
        )

        # Calculate session duration based on cognitive load capacity
        session_duration = self._calculate_session_duration(
            cognitive_domains, user_profile.get("time_per_session", 45)
        )

        # Determine equipment needs based on recommended exercises
        equipment_needed = self._determine_equipment_needs(
            physical_correlations, user_profile.get("equipment_available", [])
        )

        # Identify focus areas based on cognitive and physical needs
        focus_areas = self._identify_focus_areas(
            cognitive_domains, physical_correlations
        )

        # Determine appropriate difficulty level
        difficulty_level = self._determine_difficulty_level(
            cognitive_domains, user_profile.get("fitness_level", "beginner")
        )

        return PlanParameters(
            duration_weeks=8,  # Standard program length
            training_days_per_week=optimal_training_days,
            session_duration=session_duration,
            equipment_available=equipment_needed,
            focus_areas=focus_areas,
            difficulty_level=difficulty_level,
        )

    def _calculate_optimal_training_days(
        self, cognitive_domains: Dict, preferred_days: int
    ) -> int:
        """Calculate optimal number of training days based on cognitive load."""
        # Get cognitive recovery requirements
        vision_load = cognitive_domains.get("vision", {}).get("recovery_time", 24)
        neuro_load = cognitive_domains.get("neurological", {}).get("recovery_time", 24)

        # Calculate minimum recovery time needed
        min_recovery_hours = max(vision_load, neuro_load)

        # Determine maximum safe training days
        max_days = 7 - (min_recovery_hours // 24)

        # Return the lower of preferred days or maximum safe days
        return min(preferred_days, max_days)

    def _calculate_session_duration(
        self, cognitive_domains: Dict, preferred_duration: int
    ) -> int:
        """Calculate optimal session duration based on cognitive load capacity."""
        # Get cognitive load thresholds
        vision_threshold = cognitive_domains.get("vision", {}).get(
            "optimal_duration", 45
        )
        neuro_threshold = cognitive_domains.get("neurological", {}).get(
            "optimal_duration", 45
        )

        # Calculate optimal duration
        optimal_duration = min(vision_threshold, neuro_threshold)

        # Ensure duration is within safe limits
        return max(min(preferred_duration, optimal_duration), 15)

    def _determine_equipment_needs(
        self, physical_correlations: Dict, available_equipment: List[str]
    ) -> List[str]:
        """Determine necessary equipment based on recommended exercises."""
        recommended_equipment = set()

        # Extract equipment needs from recommended exercises
        for exercise in physical_correlations.get("recommended_exercises", []):
            equipment = exercise.get("required_equipment", [])
            recommended_equipment.update(equipment)

        # Filter by available equipment
        return list(recommended_equipment.intersection(set(available_equipment)))

    def _identify_focus_areas(
        self, cognitive_domains: Dict, physical_correlations: Dict
    ) -> List[str]:
        """Identify key focus areas based on cognitive and physical needs."""
        focus_areas = set()

        # Add cognitive focus areas
        for domain, data in cognitive_domains.items():
            if data.get("priority", "low") in ["high", "medium"]:
                focus_areas.add(domain)

        # Add physical focus areas
        for correlation in physical_correlations.get("correlations", []):
            if correlation.get("impact_level", "low") in ["high", "medium"]:
                focus_areas.add(correlation.get("focus_area"))

        return list(focus_areas)

    def _determine_difficulty_level(
        self, cognitive_domains: Dict, base_level: str
    ) -> str:
        """Determine appropriate difficulty level based on cognitive capacity."""
        # Calculate average cognitive scores
        scores = []
        for domain in cognitive_domains.values():
            score = domain.get("capacity_score", 50)
            scores.append(score)

        avg_score = sum(scores) / len(scores) if scores else 50

        # Adjust difficulty based on cognitive capacity
        if avg_score < 40:
            return "beginner"
        elif avg_score < 70:
            return base_level
        else:
            return "advanced" if base_level != "beginner" else "intermediate"

    async def _generate_weeks(
        self,
        plan_params: PlanParameters,
        health_metrics: HealthMetrics,
        knowledge: Dict,
    ) -> List[Week]:
        """Generate weekly workout plans with neural-physical balance."""
        weeks = []

        for week_num in range(1, plan_params.duration_weeks + 1):
            # Calculate progressive overload for this week
            intensity_factor = self._calculate_intensity_progression(
                week_num, plan_params.duration_weeks
            )

            # Generate weekly focus based on progression
            weekly_focus = self._generate_weekly_focus(
                week_num, knowledge, plan_params.focus_areas
            )

            # Generate daily workouts with balanced load
            days = await self._generate_daily_workouts(
                week_num, plan_params, health_metrics, knowledge, intensity_factor
            )

            # Create recovery protocols based on weekly load
            recovery_protocols = self._create_recovery_protocols(
                days, health_metrics, knowledge
            )

            # Assemble the week
            week = Week(
                week_number=week_num,
                focus=weekly_focus,
                days=days,
                recovery_protocols=recovery_protocols,
                notes=f"Week {week_num} - Intensity Factor: {intensity_factor:.2f}",
            )

            weeks.append(week)

        return weeks

    def _calculate_intensity_progression(
        self, current_week: int, total_weeks: int
    ) -> float:
        """Calculate progressive overload factor for the current week."""
        base_intensity = 0.6  # Start at 60% intensity
        max_intensity = 0.9  # Max out at 90% intensity

        # Linear progression over the weeks
        progression = (current_week - 1) / (total_weeks - 1)

        # Apply progressive overload with diminishing returns
        intensity = base_intensity + (max_intensity - base_intensity) * (
            1 - (1 - progression) ** 2
        )

        return min(max_intensity, intensity)

    def _generate_weekly_focus(
        self, week_num: int, knowledge: Dict, focus_areas: List[str]
    ) -> WeeklyFocus:
        """Generate focus areas for the week based on progression patterns."""
        progression_patterns = knowledge.get("progression_patterns", {})

        # Determine primary focus based on week number and patterns
        primary_focus = focus_areas[week_num % len(focus_areas)]

        # Find complementary focus area
        secondary_focus = None
        for area in focus_areas:
            if area != primary_focus:
                complementary_score = progression_patterns.get(
                    "complementary_scores", {}
                ).get(f"{primary_focus}_{area}", 0)
                if complementary_score > 0.7:  # High complementary score threshold
                    secondary_focus = area
                    break

        return WeeklyFocus(
            primary=primary_focus,
            secondary=secondary_focus,
            notes=f"Focus on {primary_focus}"
            + (f" with {secondary_focus}" if secondary_focus else ""),
        )

    async def _generate_daily_workouts(
        self,
        week_num: int,
        plan_params: PlanParameters,
        health_metrics: HealthMetrics,
        knowledge: Dict,
        intensity_factor: float,
    ) -> List[Day]:
        """Generate daily workouts with balanced neural and physical load."""
        days = []
        training_days = set(range(0, 7))  # 0 = Monday, 6 = Sunday

        # Distribute training days evenly through the week
        rest_days = self._calculate_rest_days(
            training_days, plan_params.training_days_per_week
        )
        training_days = training_days - rest_days

        for day_num in range(7):
            if day_num in rest_days:
                # Create rest day
                day = Day(
                    date=f"Week {week_num} Day {day_num + 1}",
                    workouts=[],
                    total_duration=0,
                    notes="Rest and Recovery Day",
                )
            else:
                # Generate workouts for training day
                workouts = await self._generate_workouts_for_day(
                    day_num, plan_params, health_metrics, knowledge, intensity_factor
                )

                day = Day(
                    date=f"Week {week_num} Day {day_num + 1}",
                    workouts=workouts,
                    total_duration=sum(w.duration for w in workouts),
                    notes=f"Training Day - {len(workouts)} workouts",
                )

            days.append(day)

        return days

    def _calculate_rest_days(self, available_days: set, training_days: int) -> set:
        """Calculate optimal rest day distribution."""
        num_rest_days = 7 - training_days
        rest_days = set()

        # Ensure at least one rest day between high-intensity days
        day_spacing = max(1, 7 // (training_days + 1))

        for i in range(num_rest_days):
            rest_day = (i * day_spacing) % 7
            rest_days.add(rest_day)

        return rest_days

    async def _generate_workouts_for_day(
        self,
        day_num: int,
        plan_params: PlanParameters,
        health_metrics: HealthMetrics,
        knowledge: Dict,
        intensity_factor: float,
    ) -> List[Workout]:
        """Generate workouts for a specific day with appropriate progression."""
        workouts = []

        # Add warm-up
        workouts.append(
            await self._create_workout(
                "Warm-up", WorkoutType.WARM_UP, IntensityLevel.LOW, 15, knowledge
            )
        )

        # Main workout with neural-physical balance
        main_duration = (
            plan_params.session_duration - 25
        )  # Subtract warm-up and cool-down
        workouts.append(
            await self._create_workout(
                "Main Workout",
                WorkoutType.MAIN_WORKOUT,
                self._calculate_intensity_level(intensity_factor),
                main_duration,
                knowledge,
            )
        )

        # Add cool-down
        workouts.append(
            await self._create_workout(
                "Cool-down", WorkoutType.COOL_DOWN, IntensityLevel.LOW, 10, knowledge
            )
        )

        return workouts

    async def _create_workout(
        self,
        name: str,
        workout_type: WorkoutType,
        intensity: IntensityLevel,
        duration: int,
        knowledge: Dict,
    ) -> Workout:
        """Create a workout with appropriate exercises and progression."""
        # Query the knowledge graph for specific exercises
        exercises = await self._query_exercises(
            workout_type, intensity, duration, knowledge
        )

        return Workout(
            name=name,
            duration=duration,
            workout_type=workout_type,
            intensity=intensity,
            focus=exercises.get("focus", []),
            equipment=exercises.get("equipment", []),
            effects=exercises.get("effects", []),
            user_benefits=exercises.get("benefits", []),
            practical_tips=exercises.get("tips", []),
            description=exercises.get("description", ""),
        )

    def _calculate_intensity_level(self, intensity_factor: float) -> IntensityLevel:
        """Calculate intensity level based on progression factor."""
        if intensity_factor < 0.7:
            return IntensityLevel.LOW
        elif intensity_factor < 0.85:
            return IntensityLevel.MEDIUM
        else:
            return IntensityLevel.HIGH

    async def _query_exercises(
        self,
        workout_type: WorkoutType,
        intensity: IntensityLevel,
        duration: int,
        knowledge: Dict,
    ) -> Dict:
        """Query specific exercises from the knowledge graph."""
        response = await self.llm_with_tools.ainvoke(
            f"""Recommend exercises for a {workout_type.value} workout:
            Intensity: {intensity.value}
            Duration: {duration} minutes

            Consider:
            1. Exercise sequence and flow
            2. Neural engagement levels
            3. Physical intensity balance
            4. Recovery requirements
            """
        )
        return response.additional_kwargs.get("graph_data", {})

    async def _generate_progression_metrics(self, weeks: List[Week]) -> Dict:
        """Generate progression metrics based on the workout plan."""
        # Calculate target improvements for each domain
        balance_progression = self._calculate_domain_progression(
            weeks,
            "balance",
            base_improvement=10,  # 10% base improvement target
            weekly_factor=1.5,  # 1.5% additional per week
        )

        coordination_progression = self._calculate_domain_progression(
            weeks,
            "coordination",
            base_improvement=8,  # 8% base improvement target
            weekly_factor=1.2,  # 1.2% additional per week
        )

        reaction_time_progression = self._calculate_domain_progression(
            weeks,
            "reaction_time",
            base_improvement=5,  # 5% base improvement target
            weekly_factor=0.8,  # 0.8% additional per week
        )

        visual_processing_progression = self._calculate_domain_progression(
            weeks,
            "visual_processing",
            base_improvement=7,  # 7% base improvement target
            weekly_factor=1.0,  # 1.0% additional per week
        )

        return {
            "target_balance_improvement": balance_progression,
            "target_coordination_improvement": coordination_progression,
            "target_reaction_time_improvement": reaction_time_progression,
            "target_visual_processing_improvement": visual_processing_progression,
            "weekly_targets": self._generate_weekly_targets(weeks),
            "adaptation_thresholds": self._calculate_adaptation_thresholds(weeks),
        }

    def _calculate_domain_progression(
        self,
        weeks: List[Week],
        domain: str,
        base_improvement: float,
        weekly_factor: float,
    ) -> float:
        """Calculate progressive improvement targets for a specific domain."""
        # Count focused training sessions for this domain
        domain_sessions = sum(
            1
            for week in weeks
            for day in week.days
            for workout in day.workouts
            if domain in workout.focus
        )

        # Calculate total training volume for domain
        domain_volume = sum(
            workout.duration
            for week in weeks
            for day in week.days
            for workout in day.workouts
            if domain in workout.focus
        )

        # Calculate target improvement based on volume and progression factor
        volume_factor = domain_volume / (
            len(weeks) * 7 * 60
        )  # Normalize to hours per week
        progression_weeks = len(weeks)

        target_improvement = (
            base_improvement
            + (weekly_factor * progression_weeks)
            + (volume_factor * 5)  # 5% additional per hour of focused training per week
        )

        return min(target_improvement, 50)  # Cap at 50% improvement

    def _generate_weekly_targets(self, weeks: List[Week]) -> List[Dict]:
        """Generate specific targets for each week."""
        weekly_targets = []

        for week in weeks:
            # Calculate target metrics based on week's focus and intensity
            week_intensity = self._calculate_week_intensity(week)

            targets = {
                "week": week.week_number,
                "focus_areas": [week.focus.primary]
                + ([week.focus.secondary] if week.focus.secondary else []),
                "target_intensity": week_intensity,
                "minimum_sessions": len([day for day in week.days if day.workouts]),
                "recovery_quality": "high" if week_intensity > 0.8 else "moderate",
                "adaptation_markers": [
                    "Improved balance during complex movements",
                    "Better visual tracking in dynamic situations",
                    "Faster reaction times in varied contexts",
                    "Enhanced movement precision",
                ],
            }

            weekly_targets.append(targets)

        return weekly_targets

    def _calculate_week_intensity(self, week: Week) -> float:
        """Calculate the overall intensity for a week."""
        if not week.days:
            return 0.0

        intensity_scores = {
            IntensityLevel.LOW: 0.3,
            IntensityLevel.MEDIUM: 0.6,
            IntensityLevel.HIGH: 0.9,
        }

        total_duration = 0
        weighted_intensity = 0

        for day in week.days:
            for workout in day.workouts:
                weighted_intensity += (
                    workout.duration * intensity_scores[workout.intensity]
                )
                total_duration += workout.duration

        return weighted_intensity / total_duration if total_duration > 0 else 0.0

    def _calculate_adaptation_thresholds(self, weeks: List[Week]) -> Dict:
        """Calculate adaptation thresholds for adjusting the program."""
        return {
            "performance": {
                "significant_improvement": 15,  # 15% improvement triggers program advancement
                "plateau": 5,  # Less than 5% improvement triggers adjustment
                "regression": -5,  # 5% decline triggers program modification
            },
            "recovery": {
                "optimal_rest_heart_rate": "Within 5 bpm of baseline",
                "sleep_quality": "85% of optimal",
                "subjective_readiness": "7/10 minimum",
            },
            "progression_gates": {
                "balance": "80% success rate in current difficulty",
                "coordination": "85% movement accuracy",
                "reaction_time": "10% improvement from baseline",
                "visual_processing": "15% improvement in tracking tasks",
            },
        }

    async def _generate_recommendations(
        self,
        health_metrics: HealthMetrics,
        plan_params: PlanParameters,
        progression_metrics: Dict,
    ) -> List[str]:
        """Generate personalized recommendations based on health metrics and plan parameters."""
        recommendations = []

        # Analyze cognitive load and recovery needs
        cognitive_load = await self._analyze_cognitive_load(health_metrics)
        recovery_needs = self._analyze_recovery_needs(health_metrics, plan_params)

        # Add cognitive load management recommendations
        if cognitive_load > 0.8:  # High cognitive load
            recommendations.extend(
                [
                    "Prioritize quality sleep (8-9 hours) to support cognitive recovery",
                    "Include mindfulness practices between training sessions",
                    "Consider shorter, more frequent training sessions",
                ]
            )
        elif cognitive_load > 0.6:  # Moderate cognitive load
            recommendations.extend(
                [
                    "Maintain regular sleep schedule (7-8 hours)",
                    "Include active recovery techniques between sessions",
                    "Monitor cognitive fatigue during training",
                ]
            )

        # Add recovery-based recommendations
        if recovery_needs["sleep_deficit"]:
            recommendations.append(
                f"Increase sleep duration by {recovery_needs['sleep_deficit']} hours "
                "to support neural adaptation"
            )

        if recovery_needs["hydration_status"] < 0.7:
            recommendations.append(
                "Increase daily water intake to support cognitive function and recovery"
            )

        # Add progression-based recommendations
        for domain, threshold in progression_metrics["progression_gates"].items():
            recommendations.append(
                f"Focus on achieving {threshold} in {domain} before progressing difficulty"
            )

        # Add equipment-specific recommendations
        if plan_params.equipment_available:
            recommendations.append(
                "Utilize available equipment to maximize training variety and progression"
            )
        else:
            recommendations.append(
                "Focus on bodyweight exercises and cognitive challenges that require minimal equipment"
            )

        # Add intensity management recommendations
        weekly_targets = progression_metrics["weekly_targets"]
        high_intensity_weeks = sum(
            1 for week in weekly_targets if week["target_intensity"] > 0.8
        )

        if (
            high_intensity_weeks > len(weekly_targets) / 3
        ):  # More than 1/3 high intensity
            recommendations.extend(
                [
                    "Monitor fatigue levels closely during high-intensity weeks",
                    "Ensure adequate recovery between high-intensity sessions",
                    "Consider supplementary recovery techniques (e.g., cold therapy, compression)",
                ]
            )

        # Add neural adaptation recommendations
        recommendations.extend(
            [
                "Practice visualization techniques to enhance motor learning",
                "Incorporate dual-task exercises to challenge cognitive-motor integration",
                "Use varied environmental contexts to promote adaptability",
            ]
        )

        return recommendations[:10]  # Limit to top 10 most relevant recommendations

    async def _analyze_cognitive_load(self, health_metrics: HealthMetrics) -> float:
        """Analyze cognitive load based on health metrics."""
        # Calculate cognitive load score (0-1)
        factors = {
            "sleep_quality": health_metrics.sleep_quality / 100,
            "stress_level": 1 - (health_metrics.stress_level / 100),
            "mental_fatigue": 1 - (health_metrics.mental_fatigue / 100),
            "cognitive_performance": health_metrics.cognitive_performance / 100,
        }

        weights = {
            "sleep_quality": 0.3,
            "stress_level": 0.25,
            "mental_fatigue": 0.25,
            "cognitive_performance": 0.2,
        }

        return sum(score * weights[factor] for factor, score in factors.items())

    def _analyze_recovery_needs(
        self, health_metrics: HealthMetrics, plan_params: PlanParameters
    ) -> Dict:
        """Analyze recovery needs based on health metrics and plan parameters."""
        # Calculate sleep deficit
        optimal_sleep = 8  # hours
        current_sleep = health_metrics.sleep_duration
        sleep_deficit = max(0, optimal_sleep - current_sleep)

        # Calculate hydration status (0-1)
        hydration_status = health_metrics.hydration_level / 100

        # Calculate recovery score (0-1)
        recovery_score = (
            0.4 * (health_metrics.sleep_quality / 100)
            + 0.3 * (1 - health_metrics.fatigue_level / 100)
            + 0.3 * (health_metrics.recovery_rate / 100)
        )

        return {
            "sleep_deficit": sleep_deficit,
            "hydration_status": hydration_status,
            "recovery_score": recovery_score,
            "needs_active_recovery": recovery_score < 0.7,
            "needs_extra_rest": sleep_deficit > 1 or recovery_score < 0.5,
        }

    def _create_recovery_protocols(
        self, days: List[Day], health_metrics: HealthMetrics, knowledge: Dict
    ) -> RecoveryProtocols:
        """Create recovery protocols based on weekly training load."""
        # Calculate total training load
        total_duration = sum((day.total_duration or 0) for day in days)
        high_intensity_days = len(
            [
                day
                for day in days
                if any(
                    workout.intensity == IntensityLevel.HIGH for workout in day.workouts
                )
            ]
        )

        # Calculate recommended sleep based on training load and cognitive demands
        base_sleep = 7  # Base recommended sleep hours
        additional_sleep = min(2, (high_intensity_days * 0.5) + (total_duration / 120))
        recommended_sleep = round(base_sleep + additional_sleep)

        # Calculate hydration needs
        base_hydration = 2.0  # Base hydration in liters
        activity_hydration = (
            total_duration / 60 * 0.5
        )  # Additional 0.5L per hour of activity
        hydration_target = round(base_hydration + activity_hydration, 1)

        # Generate recovery recommendations
        return RecoveryProtocols(
            recommended_sleep=recommended_sleep,
            hydration_target=hydration_target,
            nutrition_tips=[
                "Focus on protein-rich foods for recovery",
                "Include complex carbohydrates for energy restoration",
                "Consume anti-inflammatory foods",
                "Time nutrients around workouts",
            ],
            recovery_exercises=[
                "Light stretching",
                "Deep breathing exercises",
                "Gentle mobility work",
                "Progressive muscle relaxation",
            ],
        )


class PlanAdaptationService:
    def __init__(self, plan_generator: PlanGenerationService):
        self.plan_generator = plan_generator

    async def adapt_plan(
        self, current_plan: NeuroPlan, new_metrics: HealthMetrics, progress_data: Dict
    ) -> NeuroPlan:
        """Adapt the existing plan based on new metrics and progress."""
        # Implementation would modify the plan based on progress and new metrics
        pass

    async def _analyze_progress(self, progress_data: Dict) -> Dict:
        """Analyze user progress to inform plan adaptations."""
        # Implementation would analyze progress data
        pass

    async def _generate_adaptations(
        self, current_plan: NeuroPlan, progress_analysis: Dict
    ) -> Dict:
        """Generate specific adaptations to the current plan."""
        # Implementation would generate plan modifications
        pass
