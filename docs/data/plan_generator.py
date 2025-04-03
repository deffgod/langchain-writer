import json

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from langchain_writer import ChatWriter
from langchain_writer.tools import GraphTool, LLMTool

# Load environment variables
load_dotenv()

# Initialize the chat model, defaults to Palmyra X 004
chat = ChatWriter()

# Create a graph tool with the neurofitness knowledge graph ID
# This would contain exercise data, neural connections, fitness principles
neuro_graph_tool = GraphTool(graph_ids=["871c6606-6038-4974-90fb-39a771c6bdc4"])

# Create an LLM tool with Palmyra Creative for personalized plan generation
plan_generation_tool = LLMTool(
    model_name="palmyra-creative",
    description="A specialized model that can generate personalized neurofitness training plans.",
)

# Bind each Writer tool to a separate chat model instance
chat_with_neuro_graph = chat.bind_tools([neuro_graph_tool])
chat_with_plan_generator = chat.bind_tools([plan_generation_tool])

# Define templates for different types of plan generation
FITNESS_PLAN_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a neurofitness expert specializing in creating personalized training programs that combine neurological and physical training.",
        ),
        (
            "human",
            """
        Create a comprehensive neurofitness plan based on this user profile:

        User Profile:
        {user_profile}

        Neurotesting Results:
        {neuro_results}

        Fitness Goals:
        {fitness_goals}

        Training Preferences:
        {training_preferences}

        Include:
        1. Weekly schedule for {duration_weeks} weeks
        2. Daily workout routines with specific exercises
        3. Progression mechanisms
        4. Targeted neurological effects
        5. Equipment requirements
    """,
        ),
    ]
)

WORKOUT_ADAPTATION_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a neurofitness adaptation specialist who adjusts training programs based on user progress and feedback.",
        ),
        (
            "human",
            """
        Analyze this user's progress data and adapt their current workout plan:

        Current Plan:
        {current_plan}

        Progress Metrics:
        {progress_metrics}

        User Feedback:
        {user_feedback}

        Latest Neurotesting Results:
        {latest_neuro_results}

        Recommend specific adjustments to intensity, exercise selection, duration, or frequency.
        Provide a detailed explanation of why each adjustment is recommended.
    """,
        ),
    ]
)


# Query the knowledge graph for exercise recommendations based on neural profile
def get_exercise_recommendations(user_profile, neuro_results, focus_areas):
    kg_query = [
        HumanMessage(
            f"""
            Recommend exercises for a user with the following profile and neurological assessment:

            Profile: {json.dumps(user_profile)}
            Neuro Results: {json.dumps(neuro_results)}

            Focus specifically on these areas: {', '.join(focus_areas)}

            For each recommended exercise, provide:
            - Name and description
            - Primary neurological effect
            - Secondary physical benefits
            - Appropriate intensity and progression
            - Required equipment
            """
        )
    ]

    kg_response = chat_with_neuro_graph.invoke(kg_query)
    return kg_response.content


# Generate a personalized fitness plan
def generate_fitness_plan(
    user_profile, neuro_results, fitness_goals, training_preferences, duration_weeks=4
):
    # First, get recommended exercises from the knowledge graph
    focus_areas = [goal["area"] for goal in fitness_goals]
    recommended_exercises = get_exercise_recommendations(
        user_profile, neuro_results, focus_areas
    )

    # Format the input for the plan generation model
    formatted_prompt = FITNESS_PLAN_TEMPLATE.format_messages(
        user_profile=json.dumps(user_profile, indent=2),
        neuro_results=json.dumps(neuro_results, indent=2),
        fitness_goals=json.dumps(fitness_goals, indent=2),
        training_preferences=json.dumps(training_preferences, indent=2),
        duration_weeks=duration_weeks,
    )

    # Generate the fitness plan
    response = chat_with_plan_generator.invoke(formatted_prompt)

    # Parse the response into a structured plan format
    # This would include additional processing to format the plan correctly for the app
    fitness_plan = process_plan_response(response.content)

    return fitness_plan


# Adapt an existing plan based on user progress
def adapt_fitness_plan(
    current_plan, progress_metrics, user_feedback, latest_neuro_results
):
    formatted_prompt = WORKOUT_ADAPTATION_TEMPLATE.format_messages(
        current_plan=json.dumps(current_plan, indent=2),
        progress_metrics=json.dumps(progress_metrics, indent=2),
        user_feedback=user_feedback,
        latest_neuro_results=json.dumps(latest_neuro_results, indent=2),
    )

    response = chat_with_plan_generator.invoke(formatted_prompt)
    adapted_plan = process_adaptation_response(response.content, current_plan)

    return adapted_plan


# Helper function to process the raw plan response into structured data
def process_plan_response(raw_plan):
    """
    Processes the raw text response into a structured fitness plan object
    that conforms to the database schema.
    """
    # In a real implementation, this would parse the text and create a structured plan
    # For this example, we'll assume the model outputs JSON-formatted text
    try:
        # Attempt to parse as JSON
        plan_data = json.loads(raw_plan)
    except json.JSONDecodeError:
        # If not JSON, use a more complex parsing approach
        plan_data = extract_plan_data(raw_plan)

    # Validate and structure the plan according to database schema
    structured_plan = {
        "plan_title": plan_data.get("title", "Personalized Neurofitness Program"),
        "plan_duration_weeks": plan_data.get("duration_weeks", 4),
        "daily_training_duration": plan_data.get("daily_duration", "45 minutes"),
        "training_days": plan_data.get(
            "training_days", ["Monday", "Wednesday", "Friday"]
        ),
        "goals": plan_data.get("goals", []),
        "weekly_structure": [],
    }

    # Process weekly structure
    for week in plan_data.get("weeks", []):
        week_structure = {
            "week": week.get("week_number"),
            "focus": week.get("focus", "General neurofitness"),
            "days": [],
        }

        # Process daily workouts
        for day in week.get("days", []):
            day_program = {
                "day": day.get("day_number"),
                "wday_name": day.get("day_name"),
                "theme": day.get("theme", ""),
                "workouts": [],
            }

            # Process exercises
            for exercise in day.get("exercises", []):
                workout = {
                    "type": exercise.get("type", "Main workout"),
                    "name": exercise.get("name", ""),
                    "duration": exercise.get("duration", ""),
                    "intensity": exercise.get("intensity", "medium"),
                    "focus": exercise.get("focus", ""),
                    "equipment": exercise.get("equipment", []),
                    "effects": {
                        "primary": exercise.get("primary_effects", []),
                        "secondary": exercise.get("secondary_effects", []),
                    },
                }
                day_program["workouts"].append(workout)

            week_structure["days"].append(day_program)

        structured_plan["weekly_structure"].append(week_structure)

    return structured_plan


# Helper function to extract structured data from text response
def extract_plan_data(raw_text):
    """
    Extracts structured data from a non-JSON text response.
    This would use regex or other parsing techniques in a real implementation.
    """
    # This would be a more complex implementation in practice
    # Simplified example:
    plan_data = {
        "title": "Extracted Neurofitness Program",
        "duration_weeks": 4,
        "daily_duration": "45 minutes",
        "training_days": ["Monday", "Wednesday", "Friday"],
        "goals": ["Improve brain function", "Enhance mobility"],
        "weeks": [],
    }

    # In a real implementation, this would parse the text structure
    # and extract each component of the plan

    return plan_data


# Helper function to process adaptation response
def process_adaptation_response(adaptation_text, current_plan):
    """
    Processes adaptation recommendations and applies them to the current plan.
    """
    # Similar to process_plan_response, but focuses on modifications
    # to the existing plan rather than creating a new one

    # For now, we'll return a copy of the current plan with a note about adaptation
    adapted_plan = current_plan.copy()
    adapted_plan["adaptation_notes"] = adaptation_text

    return adapted_plan


# Main function to generate a fitness plan
def generate_neurofitness_plan(user_id):
    # In a real implementation, these would be fetched from the database
    user_profile = get_user_profile(user_id)
    neuro_results = get_neuro_results(user_id)
    fitness_goals = get_fitness_goals(user_id)
    training_preferences = get_training_preferences(user_id)

    # Generate the personalized plan
    fitness_plan = generate_fitness_plan(
        user_profile,
        neuro_results,
        fitness_goals,
        training_preferences,
        duration_weeks=4,
    )

    # Save the plan to the database
    save_fitness_plan(user_id, fitness_plan)

    return fitness_plan


# Example usage
if __name__ == "__main__":
    # In a real implementation, this would be called from an API endpoint
    user_id = "example_user_123"
    generate_neurofitness_plan(user_id)
