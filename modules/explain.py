from modules.gemini_config import generate_content
from modules.prompts import topic_explainer_prompt

def explain_topic(topic, level):

    return generate_content(
        topic_explainer_prompt(topic, level)
    )
