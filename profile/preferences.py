import streamlit as st
from database.connection import DatabaseError
from profile.profile_database import get_active_profile


@st.cache_data(ttl=10)
def get_profile_preferences(user_id):
    try:
        return get_active_profile(user_id)

    except DatabaseError:
        return None


def get_ai_personalization_context(user_id):
    profile = get_profile_preferences(user_id)

    if not profile:
        return """
Personalization Context:
- No student profile is saved yet.
- Use a balanced teaching style suitable for a general student.
"""

    return f"""
Personalization Context:
- Student Name: {profile.get('full_name') or 'Student'}
- Education Level: {profile.get('education_level') or 'Not specified'}
- Preferred Language: {profile.get('preferred_language') or 'English'}
- Learning Style: {profile.get('learning_style') or 'Mixed'}
- Exam Type: {profile.get('exam_type') or 'Semester'}
- Weak Subjects: {profile.get('weak_subjects') or 'None specified'}
- Current Study Goal: {profile.get('current_study_goal') or 'Not specified'}
- Daily Study Time: {profile.get('daily_study_time') or 'Not specified'} hour(s)
- Preferred Explanation Level: {profile.get('preferred_explanation_level') or 'Beginner'}

Personalization Instructions:
- Adapt difficulty to the education level and preferred explanation level.
- If learning style is Visual, include diagram descriptions, visual analogies, and memory maps.
- If learning style is Practical, include real-world examples and applied scenarios.
- If learning style is Reading, provide clean notes and structured summaries.
- If learning style is Mixed, combine concise notes, examples, and recall cues.
- If exam type is Placement or Interview, include interview tips and common questions.
- If weak subjects are relevant, reinforce fundamentals and add revision cues.
- Respect the preferred language where possible while keeping technical terms clear.
"""


def get_preferred_quiz_difficulty(user_id, default="Medium"):
    profile = get_profile_preferences(user_id)

    if not profile:
        return default

    return profile.get("preferred_quiz_difficulty") or default


def get_preferred_flashcard_count(user_id, default=10):
    profile = get_profile_preferences(user_id)

    if not profile:
        return default

    return int(profile.get("preferred_flashcard_count") or default)


def get_preferred_theme(user_id, default="Dark"):
    profile = get_profile_preferences(user_id)

    if not profile:
        return default

    return profile.get("preferred_theme") or default
