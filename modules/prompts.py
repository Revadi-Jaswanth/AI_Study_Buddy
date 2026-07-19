GENERAL_MARKDOWN_RULES = """
You are an experienced, patient teacher creating premium educational content.
Use clear, student-friendly language and avoid unnecessary complexity.
Use consistent Markdown formatting.
Use Markdown headings exactly as requested.
Use bullet points and numbered lists where helpful.
Use tables when they improve clarity.
Keep explanations accurate, practical, and exam-oriented.
Never use inconsistent section names.
Do not add unrelated content.
"""


GENERAL_JSON_RULES = """
You are an experienced assessment designer and teacher.
Return ONLY valid JSON.
Do not include Markdown.
Do not include code fences.
Do not include comments.
Do not include any explanation outside the JSON object.
Use double quotes for all JSON keys and string values.
Ensure the JSON can be parsed directly with json.loads().
"""


def personalization_context():
    try:
        import streamlit as st
        from profile.preferences import get_ai_personalization_context

        user_id = st.session_state.get("user_id")
        if user_id:
            return get_ai_personalization_context(user_id)

        return """
Personalization Context:
- No student profile is available.
- Use a balanced teaching style suitable for a general student.
"""

    except Exception:
        return """
Personalization Context:
- No student profile is available.
- Use a balanced teaching style suitable for a general student.
"""


def topic_explainer_prompt(topic, level):
    return f"""
{GENERAL_MARKDOWN_RULES}
{personalization_context()}

Create a complete topic explanation for a {level} student.

Topic: {topic}

Return the response using exactly these Markdown sections:

# Overview
# Simple Explanation
# Detailed Explanation
# Real World Example
# Diagram Description
# Advantages
# Disadvantages
# Key Points
# Interview Questions
# Exam Tips
# Quick Revision Notes

Section guidance:
- Overview: Give a short, clear introduction.
- Simple Explanation: Explain like teaching a beginner.
- Detailed Explanation: Add depth without overcomplicating.
- Real World Example: Use a practical example.
- Diagram Description: Describe a simple diagram the student could draw.
- Advantages and Disadvantages: Use bullet points.
- Key Points: Use concise revision bullets.
- Interview Questions: Provide 5 useful questions with short answers.
- Exam Tips: Mention what examiners usually expect.
- Quick Revision Notes: Make it compact and memorable.
"""


def notes_summarizer_prompt(notes):
    return f"""
{GENERAL_MARKDOWN_RULES}
{personalization_context()}

Summarize the following study notes into premium exam-ready material.

Notes:
{notes}

Return the response using exactly these Markdown sections:

# Executive Summary
# Key Concepts
# Important Definitions
# Important Formulas
# Bullet Point Revision
# Frequently Asked Questions
# Possible Exam Questions
# One Minute Revision

Section guidance:
- If formulas are not applicable, write "Not applicable" under Important Formulas.
- Use tables for definitions or comparisons when useful.
- Keep the summary faithful to the notes.
- Do not invent unsupported facts unless needed for basic clarity.
"""


def quiz_json_prompt(topic, difficulty, question_count):
    return f"""
{GENERAL_JSON_RULES}
{personalization_context()}

Create an interactive multiple-choice quiz.

Topic: {topic}
Difficulty: {difficulty}
Number of Questions: {question_count}

Return exactly this JSON structure:

{{
  "questions": [
    {{
      "question": "Clear question text",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }},
      "correct_answer": "A",
      "explanation": "Student-friendly explanation of the correct answer",
      "difficulty": "{difficulty}",
      "topic": "{topic}"
    }}
  ]
}}

Rules:
- Create exactly {question_count} questions.
- correct_answer must be only "A", "B", "C", or "D".
- Every question must have exactly four options.
- Options must be plausible and non-repetitive.
- Explanations must teach the concept, not just reveal the answer.
- Keep question difficulty aligned with {difficulty}.
- If the student's weak subjects or study goal are related to the topic, emphasize fundamentals and common mistakes.
- If the student's exam type is Placement or Interview, include practical and interview-oriented question framing.
"""


def legacy_quiz_markdown_prompt(topic, difficulty):
    return f"""
{GENERAL_MARKDOWN_RULES}
{personalization_context()}

Create 10 multiple-choice questions.

Topic: {topic}
Difficulty: {difficulty}

Use this exact Markdown structure:

# Quiz: {topic}

For each question:
## Question N
- A. Option
- B. Option
- C. Option
- D. Option

Correct Answer: A/B/C/D

Explanation: Short teaching explanation.
"""


def flashcards_json_prompt(topic, card_count):
    return f"""
{GENERAL_JSON_RULES}
{personalization_context()}

Create a professional flashcard learning set.

Topic: {topic}
Number of Flashcards: {card_count}

Return exactly this JSON structure:

{{
  "flashcards": [
    {{
      "question": "Question side text",
      "answer": "Answer side text",
      "hint": "Short hint for recall",
      "difficulty": "Easy",
      "category": "Concept"
    }}
  ]
}}

Rules:
- Create exactly {card_count} flashcards.
- difficulty must be "Easy", "Medium", or "Hard".
- category should be a short label such as "Definition", "Concept", "Formula", "Example", or "Application".
- hint must be present. Use an empty string only if no useful hint exists.
- Questions should test active recall.
- Answers should be concise, accurate, and revision-friendly.
- Emphasize weak subjects, common mistakes, and recent learning gaps when they are relevant to the topic.
"""


def legacy_flashcards_markdown_prompt(topic):
    return f"""
{GENERAL_MARKDOWN_RULES}
{personalization_context()}

Create 10 revision flashcards.

Topic: {topic}

Use this exact Markdown structure:

# Flashcards: {topic}

## Card N
Difficulty: Easy/Medium/Hard
Category: Definition/Concept/Formula/Example/Application
Hint: Short hint
Question: Question side text
Answer: Answer side text
"""


def study_planner_prompt(subject, days):
    return f"""
{GENERAL_MARKDOWN_RULES}
{personalization_context()}

Create a professional study plan.

Subject: {subject}
Days Available: {days}

Return the response using exactly these Markdown sections:

# Study Goal
# Daily Schedule
# Topics
# Priority Level
# Estimated Time
# Break Recommendations
# Revision Day
# Final Revision Checklist
# Motivational Tip

Section guidance:
- Daily Schedule must be day-wise.
- Use tables for the schedule when useful.
- Priority Level should classify topics as High, Medium, or Low.
- Include realistic breaks and revision time.
- Keep the plan achievable for a student.
- Use the student's daily study time, weak subjects, current goal, exam type, exam date, and learning style when available.
"""


def doubt_solver_prompt(question):
    return f"""
{GENERAL_MARKDOWN_RULES}
{personalization_context()}

Solve the student's doubt like an expert teacher.

Student Doubt:
{question}

Return the response using exactly these Markdown sections:

# Direct Answer
# Detailed Explanation
# Example
# Step-by-Step Solution
# Common Mistakes
# Interview Perspective
# Summary

Section guidance:
- Direct Answer: Give the answer immediately.
- Detailed Explanation: Explain the concept clearly.
- Example: Use a simple concrete example.
- Step-by-Step Solution: Use numbered steps where applicable.
- Common Mistakes: Mention likely confusion points.
- Interview Perspective: Explain how this may be asked in interviews.
- Summary: Keep it short and revision-friendly.
"""
