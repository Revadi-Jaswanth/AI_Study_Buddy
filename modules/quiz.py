from modules.gemini_config import generate_content
from modules.prompts import legacy_quiz_markdown_prompt

def generate_quiz(topic,difficulty):

    return generate_content(
        legacy_quiz_markdown_prompt(topic, difficulty)
    )
