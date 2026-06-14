from modules.gemini_config import model

def generate_flashcards(topic):

    prompt = f"""
    Create 10 flashcards.

    Topic:
    {topic}

    Format:

    Question:
    Answer:
    """

    response = model.generate_content(
        prompt
    )

    return response.text