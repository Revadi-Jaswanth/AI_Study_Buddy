from modules.gemini_config import generate_content
from modules.prompts import doubt_solver_prompt

def solve_doubt(question):

    return generate_content(
        doubt_solver_prompt(question)
    )
