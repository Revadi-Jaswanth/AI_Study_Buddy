from modules.gemini_config import model

def solve_doubt(question):

    response = model.generate_content(
        question
    )

    return response.text