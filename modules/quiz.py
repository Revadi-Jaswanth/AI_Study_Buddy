from modules.gemini_config import model

def generate_quiz(topic,difficulty):

    prompt = f"""
    Create 10 MCQs.

    Topic:
    {topic}

    Difficulty:
    {difficulty}

    Include answers.
    """

    response = model.generate_content(
        prompt
    )

    return response.text