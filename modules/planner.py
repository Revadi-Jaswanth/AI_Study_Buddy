from modules.gemini_config import generate_content
from modules.prompts import study_planner_prompt

def generate_plan(subject,days):

    return generate_content(
        study_planner_prompt(subject, days)
    )
