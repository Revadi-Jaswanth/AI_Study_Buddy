from modules.gemini_config import model

def summarize_notes(notes):

    prompt = f"""
    Summarize these notes.

    Create:
    - Key Points
    - Important Concepts
    - Exam Notes

    Notes:
    {notes}
    """

    response = model.generate_content(
        prompt
    )

    return response.text