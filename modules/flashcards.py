from modules.gemini_config import generate_content
from modules.prompts import legacy_flashcards_markdown_prompt

def generate_flashcards(topic):

    return generate_content(
        legacy_flashcards_markdown_prompt(topic)
    )
