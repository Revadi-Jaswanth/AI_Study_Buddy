from modules.gemini_config import model

def explain_topic(topic, level):

    prompt = f"""
    Explain {topic} for a {level} student.

    Include:

    1. Simple Explanation
    2. Detailed Explanation
    3. Real World Example
    4. Key Points
    5. Exam Tips
    """

    response = model.generate_content(
        prompt
    )

    return response.text