from modules.gemini_config import model

def generate_plan(subject,days):

    prompt = f"""
    Create study plan.

    Subject:
    {subject}

    Days:
    {days}

    Give day wise schedule.
    """

    response = model.generate_content(
        prompt
    )

    return response.text