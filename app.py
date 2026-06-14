import streamlit as st

from modules.explain import explain_topic
from modules.summarize import summarize_notes
from modules.quiz import generate_quiz
from modules.flashcards import generate_flashcards
from modules.planner import generate_plan
from modules.doubt_solver import solve_doubt

from utils.pdf_reader import extract_pdf_text

# -------------------
# PAGE CONFIG
# -------------------

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

# -------------------
# CUSTOM CSS
# -------------------

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.feature-box {
    background-color:#f5f7ff;
    padding:15px;
    border-radius:12px;
    margin-bottom:15px;
}

.result-box {
    padding:15px;
    border-radius:10px;
    border:1px solid #ddd;
}

</style>
""", unsafe_allow_html=True)

# -------------------
# HEADER
# -------------------

st.markdown("""
<div style="
background:linear-gradient(90deg,#4f46e5,#06b6d4);
padding:25px;
border-radius:15px;
text-align:center;
">
<h1 style="color:white;">
📚 AI Study Buddy
</h1>

<p style="color:white;font-size:18px;">
Personalized Learning Assistant Using Generative AI
</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# -------------------
# SIDEBAR
# -------------------

with st.sidebar:

    st.title("📚 Features")

    option = st.radio(
        "Choose Tool",
        [
            "📖 Topic Explainer",
            "📝 Notes Summarizer",
            "❓ Quiz Generator",
            "🃏 Flashcards",
            "🎯 Study Planner",
            "💬 Doubt Solver"
        ]
    )

    st.divider()

    st.info(
        "Powered by Gemini AI"
    )

# -------------------
# DASHBOARD METRICS
# -------------------

col1, col2, col3 = st.columns(3)

col1.metric("AI Features", "6")
col2.metric("Learning Modes", "3")
col3.metric("Powered By", "Gemini")

st.divider()

# ==================================================
# TOPIC EXPLAINER
# ==================================================

if option == "📖 Topic Explainer":

    st.subheader("📖 Topic Explainer")

    topic = st.text_input(
        "Enter Topic"
    )

    level = st.selectbox(
        "Select Learning Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

    if st.button("Explain Topic"):

        if topic:

            with st.spinner(
                "Generating Explanation..."
            ):

                result = explain_topic(
                    topic,
                    level
                )

            st.success("Explanation Ready")

            st.markdown(result)

# ==================================================
# NOTES SUMMARIZER
# ==================================================

elif option == "📝 Notes Summarizer":

    st.subheader("📝 Notes Summarizer")

    input_type = st.radio(
        "Choose Input",
        [
            "Paste Notes",
            "Upload PDF"
        ]
    )

    notes = ""

    if input_type == "Paste Notes":

        notes = st.text_area(
            "Paste Notes Here",
            height=250
        )

    else:

        pdf_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"]
        )

        if pdf_file:

            notes = extract_pdf_text(
                pdf_file
            )

            st.success(
                "PDF Loaded Successfully"
            )

    if st.button("Summarize Notes"):

        if notes:

            with st.spinner(
                "Creating Summary..."
            ):

                result = summarize_notes(
                    notes
                )

            st.success(
                "Summary Generated"
            )

            st.markdown(result)

# ==================================================
# QUIZ GENERATOR
# ==================================================

elif option == "❓ Quiz Generator":

    st.subheader("❓ Quiz Generator")

    topic = st.text_input(
        "Enter Topic"
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    if st.button(
        "Generate Quiz"
    ):

        if topic:

            with st.spinner(
                "Generating Quiz..."
            ):

                result = generate_quiz(
                    topic,
                    difficulty
                )

            st.success(
                "Quiz Generated"
            )

            st.markdown(result)

# ==================================================
# FLASHCARDS
# ==================================================

elif option == "🃏 Flashcards":

    st.subheader(
        "🃏 Flashcards Generator"
    )

    topic = st.text_input(
        "Enter Topic"
    )

    if st.button(
        "Generate Flashcards"
    ):

        if topic:

            with st.spinner(
                "Generating Flashcards..."
            ):

                result = generate_flashcards(
                    topic
                )

            st.success(
                "Flashcards Generated"
            )

            st.markdown(result)

# ==================================================
# STUDY PLANNER
# ==================================================

elif option == "🎯 Study Planner":

    st.subheader(
        "🎯 Study Planner"
    )

    subject = st.text_input(
        "Subject Name"
    )

    days = st.number_input(
        "Days Until Exam",
        min_value=1,
        max_value=365,
        value=10
    )

    if st.button(
        "Generate Plan"
    ):

        with st.spinner(
            "Creating Study Plan..."
        ):

            result = generate_plan(
                subject,
                days
            )

        st.success(
            "Plan Ready"
        )

        st.markdown(result)

# ==================================================
# DOUBT SOLVER
# ==================================================

elif option == "💬 Doubt Solver":

    st.subheader(
        "💬 AI Doubt Solver"
    )

    question = st.text_area(
        "Ask Your Doubt"
    )

    if st.button(
        "Solve Doubt"
    ):

        if question:

            with st.spinner(
                "Thinking..."
            ):

                result = solve_doubt(
                    question
                )

            st.success(
                "Answer Generated"
            )

            st.markdown(result)