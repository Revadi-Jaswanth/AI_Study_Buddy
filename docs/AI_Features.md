# AI Features

AI Study Buddy uses Gemini to generate educational content. Prompt engineering is centralized in `modules/prompts.py`.

## Topic Explainer

Produces structured Markdown with overview, simple explanation, detailed explanation, examples, diagram descriptions, advantages, disadvantages, key points, interview questions, exam tips, and revision notes.

## Notes Summarizer

Summarizes pasted notes or extracted PDF text into exam-ready Markdown sections.

## Interactive Quiz

Generates structured JSON with questions, four options, correct answer, explanation, difficulty, and topic. The quiz engine displays one question at a time and calculates score, percentage, review items, and time taken.

## Interactive Flashcards

Generates structured JSON flashcards with question, answer, hint, difficulty, and category. The flashcard engine tracks known cards, revision cards, completion, and weak cards.

## Study Planner

Creates a day-wise study plan using subject, available days, and profile context such as study time, weak subjects, exam type, and learning style.

## Doubt Solver

Answers a student doubt with direct answer, detailed explanation, example, step-by-step solution, common mistakes, interview perspective, and summary.

## Personalization

The student profile influences all prompt builders. The AI adapts to:

- education level
- preferred language
- learning style
- exam type
- weak subjects
- current study goal
- daily study time
- explanation level

If no profile exists, prompts fall back to a balanced general teaching style.
