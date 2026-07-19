from modules.gemini_config import generate_content
from modules.prompts import notes_summarizer_prompt

def summarize_notes(notes):

    return generate_content(
        notes_summarizer_prompt(notes)
    )
