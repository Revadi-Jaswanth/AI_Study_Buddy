from pathlib import Path
from html import escape
import time

import streamlit as st

from analytics.dashboard import render_analytics_dashboard
from analytics.queries import get_dashboard_data
from config import APP_CONFIG
from database.connection import DatabaseError
from database.history import (
    delete_all_history,
    delete_history_record,
    get_history_by_id,
    get_history_statistics,
    get_recent_history,
    save_history_record,
    search_history,
)
from database.quiz_attempts import (
    delete_quiz_attempt,
    get_quiz_analytics,
    get_quiz_attempts,
    save_quiz_attempt,
)
from database.pdf_exports import save_pdf_export
from database.flashcard_sessions import (
    delete_flashcard_session,
    get_flashcard_analytics,
    get_flashcard_session,
    get_flashcard_sessions,
    save_flashcard_session,
)
from database.user_settings import get_student_name
from database.auth import authenticate_user, register_user, delete_user_account
from components.auth_layout import render_auth_layout
from components.hero_section import render_hero_section
from components.auth_form import render_login_form, render_signup_form
from components.welcome_dashboard import render_welcome_dashboard
from exports.pdf_export import PDFExportError, create_pdf_export
from modules.doubt_solver import solve_doubt
from modules.explain import explain_topic
from modules.flashcard_engine import (
    build_flashcards_markdown,
    calculate_flashcard_progress,
    format_study_time,
    generate_interactive_flashcards,
)
from modules.flashcard_parser import FlashcardParseError
from modules.gemini_config import GeminiAPIError
from modules.planner import generate_plan
from modules.quiz_engine import (
    build_quiz_result_markdown,
    calculate_quiz_result,
    format_time_taken,
    generate_interactive_quiz,
)
from modules.quiz_parser import QuizParseError
from modules.summarize import summarize_notes
from profile.preferences import (
    get_profile_preferences,
    get_preferred_flashcard_count,
    get_preferred_quiz_difficulty,
    get_preferred_theme,
)
from profile.profile_ui import render_student_profile
from utils.logging_config import get_logger
from utils.pdf_reader import extract_pdf_text


logger = get_logger(__name__)

WELCOME_DASHBOARD = "🏠 Dashboard"
TOPIC_EXPLAINER = "📖 Topic Explainer"
NOTES_SUMMARIZER = "📝 Notes Summarizer"
QUIZ_GENERATOR = "❓ Quiz Generator"
FLASHCARDS = "🃏 Flashcards"
STUDY_PLANNER = "🎯 Study Planner"
DOUBT_SOLVER = "💬 Doubt Solver"
STUDY_HISTORY = "🕘 Study History"
QUIZ_HISTORY = "📊 Quiz History"
FLASHCARD_HISTORY = "🧠 Flashcard History"
ANALYTICS_DASHBOARD = "📊 Analytics Dashboard"
STUDENT_PROFILE = "👤 Student Profile"

FEATURES = [
    TOPIC_EXPLAINER,
    NOTES_SUMMARIZER,
    QUIZ_GENERATOR,
    FLASHCARDS,
    STUDY_PLANNER,
    DOUBT_SOLVER,
]

NAVIGATION_ITEMS = [WELCOME_DASHBOARD] + FEATURES + [
    STUDY_HISTORY,
    QUIZ_HISTORY,
    FLASHCARD_HISTORY,
    ANALYTICS_DASHBOARD,
    STUDENT_PROFILE,
]

PRIMARY_NAVIGATION_ITEMS = FEATURES

HISTORY_NAVIGATION_ITEMS = [
    STUDY_HISTORY,
    QUIZ_HISTORY,
    FLASHCARD_HISTORY,
]

FEATURE_DETAILS = {
    TOPIC_EXPLAINER: {
        "icon": "📖",
        "title": "Topic Explainer",
        "description": "Turn any concept into a clear lesson for your level.",
    },
    NOTES_SUMMARIZER: {
        "icon": "📝",
        "title": "Notes Summarizer",
        "description": "Condense pasted notes or readable PDFs into exam-ready points.",
    },
    QUIZ_GENERATOR: {
        "icon": "❓",
        "title": "Quiz Generator",
        "description": "Create practice MCQs by topic and difficulty.",
    },
    FLASHCARDS: {
        "icon": "🃏",
        "title": "Flashcards",
        "description": "Generate quick question-and-answer revision cards.",
    },
    STUDY_PLANNER: {
        "icon": "🎯",
        "title": "Study Planner",
        "description": "Build a day-wise study schedule before an exam.",
    },
    DOUBT_SOLVER: {
        "icon": "💬",
        "title": "Doubt Solver",
        "description": "Ask a study doubt and get a focused explanation.",
    },
}

FEATURE_NAME_TO_OPTION = {
    details["title"]: option
    for option, details in FEATURE_DETAILS.items()
}

INPUT_KEYS = {
    TOPIC_EXPLAINER: "topic_explainer_topic",
    NOTES_SUMMARIZER: "notes_summarizer_notes",
    QUIZ_GENERATOR: "quiz_generator_topic",
    FLASHCARDS: "flashcards_topic",
    STUDY_PLANNER: "study_planner_subject",
    DOUBT_SOLVER: "doubt_solver_question",
}


def clean_text(value):
    return value.strip() if value else ""


def select_primary_tool():
    st.session_state.selected_tool = st.session_state.primary_tool


def render_auth_page():
    """Redesigned auth landing page layout delegation."""
    # Turn the tabs element itself into the floating glassmorphism card and align it to the top
    st.markdown(
        """
        <style>
        .stTabs {
            background-color: var(--surface) !important;
            border: 1px solid var(--line) !important;
            border-radius: 16px !important;
            box-shadow: var(--shadow) !important;
            padding: 2rem !important;
            margin-top: 0 !important;
        }
        div[data-testid="column"] > div {
            padding-top: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    def left_side():
        render_hero_section()

    def right_side():
        # Setup modern sign in and onboarding sign up forms inside glass card tabs
        tab1, tab2 = st.tabs(["🔐 Log In", "📝 Sign Up"])
        with tab1:
            render_login_form(authenticate_user)
        with tab2:
            render_signup_form(register_user, authenticate_user)

    render_auth_layout(left_side, right_side)


def get_sidebar_student_name():
    user_id = st.session_state.get("user_id")
    profile = get_profile_preferences(user_id)

    if not profile:
        return st.session_state.get("user_name", "Hello User")

    name = clean_text(profile.get("full_name"))
    return escape(name or st.session_state.get("user_name", "Hello User"))


def render_sidebar_profile_card():
    student_name = get_sidebar_student_name()

    st.markdown(
        """
        <div class="profile-card-wrapper">
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Open Profile",
        key="sidebar_profile_card_button",
        use_container_width=True,
    ):
        st.session_state.selected_tool = STUDENT_PROFILE
        st.rerun()

    st.markdown(
        f"""
            <div class="profile-card-face">
                <span class="profile-card-title">Student Profile</span>
                <strong class="profile-card-name">{student_name}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def load_css(theme):
    css_files = ["theme.css", "layout.css", "components.css", "animations.css"]
    combined_css = ""
    for filename in css_files:
        path = Path("styles") / filename
        if path.exists():
            combined_css += path.read_text(encoding="utf-8") + "\n"

    # Append theme-specific variable overrides and sidebar contrast fixes
    if theme == "light":
        combined_css += """
        :root {
            --bg: #fafafa;
            --surface: #ffffff;
            --surface-soft: #f4f4f5;
            --surface-strong: #ffffff;
            --text: #09090b;
            --muted: #71717a;
            --line: rgba(9, 9, 11, 0.06);
            --accent: #4f46e5;
            --accent-gradient: linear-gradient(135deg, #4f46e5, #2563eb);
            --accent-2: #059669;
            --accent-3: #d97706;
            --danger: #e11d48;
            --shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
            --dot-color: rgba(9, 9, 11, 0.05);
        }
        [data-testid="stSidebar"] * {
            color: #09090b !important;
        }
        [data-testid="stSidebar"] .sidebar-label,
        [data-testid="stSidebar"] .sidebar-brand small,
        [data-testid="stSidebar"] .sidebar-note span,
        [data-testid="stSidebar"] .stMarkdown p {
            color: #71717a !important;
        }
        """
    else:
        combined_css += """
        [data-testid="stSidebar"] * {
            color: #f4f4f5 !important;
        }
        [data-testid="stSidebar"] .sidebar-label,
        [data-testid="stSidebar"] .sidebar-brand small,
        [data-testid="stSidebar"] .sidebar-note span,
        [data-testid="stSidebar"] .stMarkdown p {
            color: #a1a1aa !important;
        }
        """

    if combined_css:
        st.markdown(
            f"<style>{combined_css}</style>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"<div class='theme-root {theme}'></div>",
        unsafe_allow_html=True,
    )


def show_gemini_error(error):
    st.error(
        str(error),
        icon="⚠️",
    )


def show_database_error(error):
    st.warning(
        f"History is temporarily unavailable: {error}",
        icon="⚠️",
    )


def format_timestamp(value):
    if not value:
        return "Unknown time"

    if hasattr(value, "strftime"):
        return value.strftime("%d %b %Y, %I:%M %p")

    return str(value)


def make_preview(value, limit=180):
    text = clean_text(value)

    if len(text) <= limit:
        return text

    return f"{text[:limit].rstrip()}..."


def record_history(option, user_prompt, ai_response):
    try:
        user_id = st.session_state.get("user_id")
        save_history_record(
            user_id,
            FEATURE_DETAILS[option]["title"],
            user_prompt,
            ai_response,
        )

    except DatabaseError as error:
        show_database_error(error)


def render_pdf_download(option, user_prompt, ai_response):
    try:
        student_name = None

        try:
            user_id = st.session_state.get("user_id")
            student_name = get_student_name(user_id)

        except DatabaseError:
            student_name = None

        filename, pdf_bytes = create_pdf_export(
            FEATURE_DETAILS[option]["title"],
            user_prompt,
            ai_response,
            student_name=student_name,
        )

    except PDFExportError as error:
        st.error(
            str(error),
            icon="⚠️",
        )
        return

    st.download_button(
        "📥 Download PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        key=f"download_{option}_{abs(hash(user_prompt + ai_response))}",
        on_click=record_pdf_export,
        args=(
            FEATURE_DETAILS[option]["title"],
            user_prompt,
            filename,
        ),
    )


def render_quiz_result_download(topic, result):
    try:
        student_name = None

        try:
            user_id = st.session_state.get("user_id")
            student_name = get_student_name(user_id)

        except DatabaseError:
            student_name = None

        result_markdown = build_quiz_result_markdown(
            topic,
            st.session_state.quiz_data["difficulty"],
            result,
        )
        filename, pdf_bytes = create_pdf_export(
            "Quiz Result",
            topic,
            result_markdown,
            student_name=student_name,
        )

    except PDFExportError as error:
        st.error(
            str(error),
            icon="⚠️",
        )
        return

    st.download_button(
        "📥 Download Quiz Result PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        key=f"download_quiz_result_{abs(hash(topic + str(result['score'])))}",
        on_click=record_pdf_export,
        args=(
            "Quiz Result",
            topic,
            filename,
        ),
    )


def reuse_prompt(feature_name, user_prompt):
    option = FEATURE_NAME_TO_OPTION.get(feature_name)

    if not option:
        st.warning(
            "This prompt cannot be reused because the original tool was not recognized.",
            icon="💡",
        )
        return

    st.session_state.selected_tool = option
    st.session_state[INPUT_KEYS[option]] = user_prompt
    st.rerun()


def reset_quiz_session():
    for key in [
        "quiz_data",
        "quiz_current_index",
        "quiz_answers",
        "quiz_started_at",
        "quiz_submitted",
        "quiz_result",
        "quiz_attempt_saved",
    ]:
        st.session_state.pop(key, None)

    for key in list(st.session_state.keys()):
        if key.startswith("quiz_answer_"):
            st.session_state.pop(key, None)


def record_pdf_export(feature_name, topic, file_name):
    try:
        user_id = st.session_state.get("user_id")
        save_pdf_export(
            user_id,
            feature_name,
            topic,
            file_name,
        )

    except DatabaseError:
        pass


def reset_flashcard_session():
    for key in [
        "flashcard_data",
        "flashcard_current_index",
        "flashcard_statuses",
        "flashcard_revealed",
        "flashcard_started_at",
        "flashcard_completed",
        "flashcard_result",
        "flashcard_session_saved",
        "flashcard_review_mode",
    ]:
        st.session_state.pop(key, None)


def render_flashcards_download(topic, flashcards):
    try:
        student_name = None

        try:
            user_id = st.session_state.get("user_id")
            student_name = get_student_name(user_id)

        except DatabaseError:
            student_name = None

        flashcards_markdown = build_flashcards_markdown(
            topic,
            flashcards,
        )
        filename, pdf_bytes = create_pdf_export(
            "Flashcards",
            topic,
            flashcards_markdown,
            student_name=student_name,
        )

    except PDFExportError as error:
        st.error(
            str(error),
            icon="⚠️",
        )
        return

    st.download_button(
        "📥 Download Flashcards PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        key=f"download_flashcards_{abs(hash(topic + str(len(flashcards))))}",
        on_click=record_pdf_export,
        args=(
            "Flashcards",
            topic,
            filename,
        ),
    )


def show_progress(label):
    progress = st.progress(
        0,
        text=label,
    )

    progress.progress(
        35,
        text=label,
    )

    return progress


def finish_progress(progress, label):
    progress.progress(
        100,
        text=label,
    )


def render_hero():
    st.markdown(
        """
        <section class="hero-section" style="background: linear-gradient(135deg, #4f46e5, #06b6d4); padding: 2.25rem 2.5rem; border-radius: 14px; color: #ffffff; margin-bottom: 1.75rem; box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.15); display: flex; justify-content: space-between; align-items: center; gap: 2rem; flex-wrap: wrap;">
            <div class="hero-copy" style="max-width: 60%; text-align: left;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
                    <span style="font-size: 32px;">📚</span>
                    <h1 style="font-size: 32px; font-weight: 800; margin: 0; color: #ffffff; letter-spacing: -0.02em; line-height: 1;">AI Study Buddy</h1>
                </div>
                <p style="margin: 0; color: rgba(255, 255, 255, 0.9); font-size: 14.5px; font-weight: 500; letter-spacing: 0.01em;">
                    Personalized Learning Assistant Using Generative AI
                </p>
            </div>
            <div class="hero-panel" style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px); padding: 1.25rem; border-radius: 12px; width: 220px; text-align: center; position: relative;">
                <div class="hero-panel-top" style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; text-transform: uppercase; color: rgba(255, 255, 255, 0.8); margin-bottom: 1rem;">
                    <span>Live Toolkit</span>
                    <strong style="color: #ffffff;">6 AI tools</strong>
                </div>
                <div class="hero-orbit" style="display: flex; justify-content: space-between; align-items: center; gap: 6px; font-size: 20px;">
                    <span>📖</span>
                    <span>📝</span>
                    <span>❓</span>
                    <span>🃏</span>
                    <span>🎯</span>
                    <span>💬</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metrics():
    st.markdown('<section class="metrics-grid">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <span>AI Features</span>
                <strong>6</strong>
                <small>Core study workflows</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <span>Learning Modes</span>
                <strong>3</strong>
                <small>Learn, practice, revise</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <span>Powered By</span>
                <strong>Gemini</strong>
                <small>Generative AI responses</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</section>", unsafe_allow_html=True)


def render_feature_cards():
    cards = ""

    for feature in FEATURES:
        detail = FEATURE_DETAILS[feature]
        cards += f"""
        <article class="feature-card">
            <span class="feature-icon">{detail["icon"]}</span>
            <h3>{detail["title"]}</h3>
            <p>{detail["description"]}</p>
        </article>
        """

    st.markdown(
        f"""
        <section class="feature-grid">
            {cards}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_tool_header(option):
    detail = FEATURE_DETAILS[option]

    st.markdown(
        f"""
        <div class="tool-header">
            <span>{detail["icon"]}</span>
            <div>
                <h2>{detail["title"]}</h2>
                <p>{detail["description"]}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_history_metrics():
    try:
        user_id = st.session_state.get("user_id")
        stats = get_history_statistics(user_id)

    except DatabaseError as error:
        show_database_error(error)
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total AI Requests",
            stats["total_requests"],
        )

    with col2:
        st.metric(
            "Today's Requests",
            stats["today_requests"],
        )

    with col3:
        st.metric(
            "Most Used Feature",
            stats["most_used_feature"],
        )


def render_recent_activity_sidebar():
    st.markdown("<div class='sidebar-label'>Recent Activity</div>", unsafe_allow_html=True)

    try:
        user_id = st.session_state.get("user_id")
        recent_items = get_recent_history(user_id, 5)

    except DatabaseError as error:
        st.caption(f"History unavailable: {error}")
        return

    if not recent_items:
        st.caption("No recent AI activity yet.")
        return

    for item in recent_items:
        st.markdown(
            f"""
            <div class="recent-activity-item">
                <strong>{item["feature_name"]}</strong>
                <span>{make_preview(item["user_prompt"], 42)}</span>
                <small>{format_timestamp(item["created_at"])}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )


@st.dialog("Delete History Record")
def confirm_delete_record(history_id):
    st.warning(
        "This will permanently delete this history item.",
        icon="⚠️",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Delete Record", type="primary"):
            try:
                user_id = st.session_state.get("user_id")
                delete_history_record(user_id, history_id)
                st.session_state.pop("pending_delete_id", None)
                st.success("History record deleted.", icon="✅")
                st.rerun()

            except DatabaseError as error:
                show_database_error(error)

    with col2:
        if st.button("Cancel"):
            st.session_state.pop("pending_delete_id", None)
            st.rerun()


@st.dialog("Delete Entire History")
def confirm_delete_all_history():
    st.warning(
        "This will permanently delete every saved AI study history item.",
        icon="⚠️",
    )

    confirmation = st.text_input(
        "Type DELETE to confirm"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Delete Entire History", type="primary"):
            if confirmation != "DELETE":
                st.warning("Please type DELETE to confirm.", icon="💡")
                return

            try:
                user_id = st.session_state.get("user_id")
                delete_all_history(user_id)
                st.session_state.confirm_delete_all = False
                st.success("Entire history deleted.", icon="✅")
                st.rerun()

            except DatabaseError as error:
                show_database_error(error)

    with col2:
        if st.button("Cancel"):
            st.session_state.confirm_delete_all = False
            st.rerun()


@st.dialog("History Details")
def show_history_details(history_id):
    try:
        user_id = st.session_state.get("user_id")
        record = get_history_by_id(user_id, history_id)

    except DatabaseError as error:
        show_database_error(error)
        return

    if not record:
        st.warning("This history item was not found.", icon="💡")
        return

    st.caption(format_timestamp(record["created_at"]))
    st.subheader(record["feature_name"])
    st.markdown("**Prompt**")
    st.write(record["user_prompt"])
    st.markdown("**AI Response**")
    st.markdown(record["ai_response"])


def render_study_history():
    st.markdown(
        """
        <div class="tool-header">
            <span>🕘</span>
            <div>
                <h2>Study History</h2>
                <p>Browse, search, reuse, and manage previous AI study sessions.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_history_metrics()

    st.divider()

    search_col, feature_col, date_col = st.columns([1.4, 1, 1])

    with search_col:
        keyword = clean_text(
            st.text_input(
                "Search by Keyword",
                key="history_keyword",
            )
        )

    with feature_col:
        selected_feature = st.selectbox(
            "Filter by Feature",
            [
                "All Features",
                *[details["title"] for details in FEATURE_DETAILS.values()]
            ],
            key="history_feature",
        )

    with date_col:
        filter_by_date = st.checkbox(
            "Filter by Date",
            key="history_filter_by_date",
        )
        history_date = st.date_input(
            "Date",
            key="history_date",
            disabled=not filter_by_date,
        )

    feature_filter = "" if selected_feature == "All Features" else selected_feature
    selected_date = history_date if filter_by_date else None

    try:
        user_id = st.session_state.get("user_id")
        history_items = search_history(
            user_id,
            keyword=keyword,
            feature_name=feature_filter,
            history_date=selected_date,
        )

    except DatabaseError as error:
        show_database_error(error)
        return

    if not history_items:
        st.info("No history found. Generate an AI response to start building your study history.", icon="💡")
        return

    delete_all_col, count_col = st.columns([1, 2])

    with delete_all_col:
        if st.button("Delete Entire History"):
            st.session_state.confirm_delete_all = True
            st.rerun()

    with count_col:
        st.caption(f"Showing {len(history_items)} saved study session(s).")

    for item in history_items:
        with st.container(border=True):
            st.markdown(f"### {item['feature_name']}")
            st.caption(format_timestamp(item["created_at"]))
            st.markdown(f"**Prompt:** {make_preview(item['user_prompt'], 220)}")
            st.markdown(f"**Response Preview:** {make_preview(item['ai_response'], 320)}")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("View Details", key=f"details_{item['id']}"):
                    st.session_state.detail_history_id = item["id"]
                    st.rerun()

            with col2:
                if st.button("Reuse Prompt", key=f"reuse_{item['id']}"):
                    reuse_prompt(
                        item["feature_name"],
                        item["user_prompt"],
                    )

            with col3:
                if st.button("Delete Record", key=f"delete_{item['id']}"):
                    st.session_state.pending_delete_id = item["id"]
                    st.rerun()


@st.dialog("Delete Quiz Attempt")
def confirm_delete_quiz_attempt(attempt_id):
    st.warning(
        "This will permanently delete this quiz attempt.",
        icon="⚠️",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Delete Attempt", type="primary"):
            try:
                user_id = st.session_state.get("user_id")
                delete_quiz_attempt(user_id, attempt_id)
                st.session_state.pop("pending_quiz_delete_id", None)
                st.success("Quiz attempt deleted.", icon="✅")
                st.rerun()

            except DatabaseError as error:
                show_database_error(error)

    with col2:
        if st.button("Cancel"):
            st.session_state.pop("pending_quiz_delete_id", None)
            st.rerun()


def render_quiz_history():
    st.markdown(
        """
        <div class="tool-header">
            <span>📊</span>
            <div>
                <h2>Quiz History</h2>
                <p>Review previous quiz attempts, scores, and topic performance.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        user_id = st.session_state.get("user_id")
        analytics = get_quiz_analytics(user_id)

    except DatabaseError as error:
        show_database_error(error)
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Highest Score", f"{analytics['highest_score']}%")

    with col2:
        st.metric("Average Score", f"{analytics['average_score']}%")

    with col3:
        st.metric("Best Topic", analytics["best_topic"])

    with col4:
        st.metric("Most Attempted", analytics["most_attempted_topic"])

    st.divider()

    search_col, sort_col = st.columns([1.3, 1])

    with search_col:
        keyword = clean_text(
            st.text_input(
                "Search by Topic",
                key="quiz_history_keyword",
            )
        )

    with sort_col:
        sort_by = st.selectbox(
            "Sort",
            [
                "Date Desc",
                "Date Asc",
                "Score Desc",
                "Score Asc",
            ],
            key="quiz_history_sort",
        )

    try:
        user_id = st.session_state.get("user_id")
        attempts = get_quiz_attempts(
            user_id,
            keyword=keyword,
            sort_by=sort_by,
        )

    except DatabaseError as error:
        show_database_error(error)
        return

    if not attempts:
        st.info("No quiz attempts found. Complete an interactive quiz to see results here.", icon="💡")
        return

    for attempt in attempts:
        with st.container(border=True):
            st.markdown(f"### {attempt['topic']}")
            st.caption(format_timestamp(attempt["created_at"]))

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Difficulty", attempt["difficulty"])

            with col2:
                st.metric("Questions", attempt["question_count"])

            with col3:
                st.metric("Score", f"{attempt['score']} / {attempt['question_count']}")

            with col4:
                st.metric("Percentage", f"{attempt['percentage']}%")

            st.caption(f"Time Taken: {format_time_taken(attempt['time_taken_seconds'])}")

            if st.button("Delete Attempt", key=f"delete_quiz_attempt_{attempt['id']}"):
                st.session_state.pending_quiz_delete_id = attempt["id"]
                st.rerun()


@st.dialog("Delete Flashcard Session")
def confirm_delete_flashcard_session(session_id):
    st.warning(
        "This will permanently delete this flashcard session.",
        icon="⚠️",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Delete Session", type="primary"):
            try:
                user_id = st.session_state.get("user_id")
                delete_flashcard_session(user_id, session_id)
                st.session_state.pop("pending_flashcard_delete_id", None)
                st.success("Flashcard session deleted.", icon="✅")
                st.rerun()

            except DatabaseError as error:
                show_database_error(error)

    with col2:
        if st.button("Cancel"):
            st.session_state.pop("pending_flashcard_delete_id", None)
            st.rerun()


@st.dialog("Flashcard Session Details")
def show_flashcard_session_details(session_id):
    try:
        user_id = st.session_state.get("user_id")
        session = get_flashcard_session(user_id, session_id)

    except DatabaseError as error:
        show_database_error(error)
        return

    if not session:
        st.warning("This flashcard session was not found.", icon="💡")
        return

    st.subheader(session["topic"])
    st.caption(format_timestamp(session["created_at"]))
    st.write(f"Total Cards: {session['total_cards']}")
    st.write(f"Known Cards: {session['known_cards']}")
    st.write(f"Need Revision: {session['revision_cards']}")
    st.write(f"Completion: {session['completion']}%")
    st.write(f"Study Time: {format_study_time(session['study_time_seconds'])}")


def render_flashcard_history():
    st.markdown(
        """
        <div class="tool-header">
            <span>🧠</span>
            <div>
                <h2>Flashcard History</h2>
                <p>Track flashcard sessions, mastery, completion, and study time.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        user_id = st.session_state.get("user_id")
        analytics = get_flashcard_analytics(user_id)

    except DatabaseError as error:
        show_database_error(error)
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sessions", analytics["total_sessions"])

    with col2:
        st.metric("Avg Completion", f"{analytics['average_completion']}%")

    with col3:
        st.metric("Avg Mastery", f"{analytics['average_mastery']}%")

    with col4:
        st.metric("Most Studied", analytics["most_studied_topic"])

    st.divider()

    search_col, sort_col = st.columns([1.3, 1])

    with search_col:
        keyword = clean_text(
            st.text_input(
                "Search by Topic",
                key="flashcard_history_keyword",
            )
        )

    with sort_col:
        sort_by = st.selectbox(
            "Sort",
            [
                "Date Desc",
                "Date Asc",
                "Completion Desc",
                "Completion Asc",
            ],
            key="flashcard_history_sort",
        )

    try:
        user_id = st.session_state.get("user_id")
        sessions = get_flashcard_sessions(
            user_id,
            keyword=keyword,
            sort_by=sort_by,
        )

    except DatabaseError as error:
        show_database_error(error)
        return

    if not sessions:
        st.info("No flashcard sessions found. Complete a flashcard session to see history here.", icon="💡")
        return

    for session in sessions:
        with st.container(border=True):
            st.markdown(f"### {session['topic']}")
            st.caption(format_timestamp(session["created_at"]))

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Completion", f"{session['completion']}%")

            with col2:
                st.metric("Cards Mastered", f"{session['known_cards']} / {session['total_cards']}")

            with col3:
                st.metric("Need Revision", session["revision_cards"])

            with col4:
                st.metric("Study Time", format_study_time(session["study_time_seconds"]))

            action_col1, action_col2, action_col3 = st.columns(3)

            with action_col1:
                if st.button("View", key=f"view_flashcard_session_{session['id']}"):
                    st.session_state.detail_flashcard_session_id = session["id"]
                    st.rerun()

            with action_col2:
                if st.button("Restart Session", key=f"restart_flashcard_session_{session['id']}"):
                    reset_flashcard_session()
                    st.session_state.selected_tool = FLASHCARDS
                    st.session_state[INPUT_KEYS[FLASHCARDS]] = session["topic"]
                    st.rerun()

            with action_col3:
                if st.button("Delete", key=f"delete_flashcard_session_{session['id']}"):
                    st.session_state.pending_flashcard_delete_id = session["id"]
                    st.rerun()


def render_footer():
    st.markdown(
        """
        <footer class="app-footer">
            <strong>AI Study Buddy</strong>
            <span>Version 2.0 UI refresh · Built with Streamlit and Gemini AI</span>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def render_topic_explainer():
    render_tool_header(TOPIC_EXPLAINER)

    topic = st.text_input("Enter Topic", key=INPUT_KEYS[TOPIC_EXPLAINER])
    level = st.selectbox("Select Learning Level", ["Beginner", "Intermediate", "Advanced"])

    if st.button("Explain Topic", type="primary"):
        topic = clean_text(topic)

        if not topic:
            st.warning("Please enter a topic before generating an explanation.", icon="💡")
            return

        progress = show_progress("Preparing explanation...")

        with st.spinner("Generating Explanation..."):
            try:
                result = explain_topic(topic, level)
                finish_progress(progress, "Explanation ready")
                st.success("Explanation Ready", icon="✅")
                record_history(TOPIC_EXPLAINER, topic, result)
                st.markdown(result)
                render_pdf_download(TOPIC_EXPLAINER, topic, result)
            except GeminiAPIError as error:
                progress.empty()
                show_gemini_error(error)


def render_notes_summarizer():
    render_tool_header(NOTES_SUMMARIZER)

    input_type = st.radio("Choose Input", ["Paste Notes", "Upload PDF"], horizontal=True)
    notes = ""

    if input_type == "Paste Notes":
        notes = st.text_area(
            "Paste Notes Here",
            height=250,
            key=INPUT_KEYS[NOTES_SUMMARIZER],
        )
    else:
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

        if pdf_file:
            try:
                notes = extract_pdf_text(pdf_file)

                if clean_text(notes):
                    st.success("PDF Loaded Successfully", icon="✅")
                else:
                    st.warning("The PDF was loaded, but no readable text was found.", icon="💡")
            except Exception:
                st.error("Could not read this PDF. Please upload a valid text-based PDF.", icon="⚠️")

    if st.button("Summarize Notes", type="primary"):
        notes = clean_text(notes)

        if not notes:
            st.warning("Please paste notes or upload a readable PDF before summarizing.", icon="💡")
            return

        progress = show_progress("Creating summary...")

        with st.spinner("Creating Summary..."):
            try:
                result = summarize_notes(notes)
                finish_progress(progress, "Summary generated")
                st.success("Summary Generated", icon="✅")
                record_history(NOTES_SUMMARIZER, notes, result)
                st.markdown(result)
                render_pdf_download(NOTES_SUMMARIZER, notes, result)
            except GeminiAPIError as error:
                progress.empty()
                show_gemini_error(error)


def render_quiz_generator():
    render_tool_header(QUIZ_GENERATOR)

    topic = st.text_input("Enter Topic", key=INPUT_KEYS[QUIZ_GENERATOR])
    difficulty_options = ["Easy", "Medium", "Hard"]
    preferred_difficulty = get_preferred_quiz_difficulty("Medium")
    difficulty = st.selectbox(
        "Difficulty",
        difficulty_options,
        index=difficulty_options.index(preferred_difficulty)
        if preferred_difficulty in difficulty_options
        else 1,
    )
    question_count = st.selectbox("Number of Questions", [5, 10, 15, 20], index=1)

    col1, col2 = st.columns([1, 1])

    with col1:
        generate_clicked = st.button("Generate Quiz", type="primary")

    with col2:
        if st.button("Reset Quiz"):
            reset_quiz_session()
            st.rerun()

    if generate_clicked:
        topic = clean_text(topic)

        if not topic:
            st.warning("Please enter a topic before generating a quiz.", icon="💡")
            return

        progress = show_progress("Building quiz...")

        with st.spinner("Generating Quiz..."):
            try:
                quiz_data = generate_interactive_quiz(
                    topic,
                    difficulty,
                    question_count,
                )
                finish_progress(progress, "Quiz generated")
                st.success("Quiz Generated", icon="✅")
                record_history(QUIZ_GENERATOR, topic, quiz_data["raw_response"])
                st.session_state.quiz_data = quiz_data
                st.session_state.quiz_current_index = 0
                st.session_state.quiz_answers = {}
                st.session_state.quiz_started_at = time.time()
                st.session_state.quiz_submitted = False
                st.session_state.quiz_attempt_saved = False
                st.rerun()

            except GeminiAPIError as error:
                progress.empty()
                show_gemini_error(error)

            except QuizParseError as error:
                progress.empty()
                st.error(str(error), icon="⚠️")

    if "quiz_data" not in st.session_state:
        st.info("Generate a quiz to begin the interactive assessment.", icon="💡")
        return

    if st.session_state.get("quiz_submitted"):
        render_submitted_quiz()
        return

    render_active_quiz()


def render_active_quiz():
    quiz_data = st.session_state.quiz_data
    questions = quiz_data["questions"]
    current_index = st.session_state.get("quiz_current_index", 0)
    current_question = questions[current_index]
    progress_value = (current_index + 1) / len(questions)

    st.progress(
        progress_value,
        text=f"Question {current_index + 1} of {len(questions)}",
    )

    st.markdown(f"### Question {current_index + 1}")
    st.write(current_question["question"])

    selected_answer = st.radio(
        "Choose one answer",
        ["A", "B", "C", "D"],
        format_func=lambda option: f"{option}. {current_question['options'][option]}",
        key=f"quiz_answer_{current_index}",
        index=["A", "B", "C", "D"].index(st.session_state.quiz_answers[current_index])
        if current_index in st.session_state.quiz_answers
        else None,
    )

    if selected_answer:
        st.session_state.quiz_answers[current_index] = selected_answer

    answered_count = len(st.session_state.quiz_answers)
    st.caption(f"Answered {answered_count} of {len(questions)} questions")

    previous_col, next_col, submit_col = st.columns(3)

    with previous_col:
        if st.button("Previous", disabled=current_index == 0):
            st.session_state.quiz_current_index = max(0, current_index - 1)
            st.rerun()

    with next_col:
        if st.button("Next", disabled=current_index == len(questions) - 1):
            st.session_state.quiz_current_index = min(len(questions) - 1, current_index + 1)
            st.rerun()

    with submit_col:
        if st.button("Submit Quiz", type="primary"):
            if answered_count < len(questions):
                st.warning("Please answer every question before submitting.", icon="💡")
                return

            elapsed_seconds = int(time.time() - st.session_state.quiz_started_at)
            result = calculate_quiz_result(
                questions,
                st.session_state.quiz_answers,
                elapsed_seconds,
            )
            st.session_state.quiz_result = result
            st.session_state.quiz_submitted = True

            try:
                user_id = st.session_state.get("user_id")
                save_quiz_attempt(
                    user_id,
                    quiz_data["topic"],
                    quiz_data["difficulty"],
                    quiz_data["question_count"],
                    result["score"],
                    result["percentage"],
                    result["time_taken_seconds"],
                )
                st.session_state.quiz_attempt_saved = True

            except DatabaseError as error:
                show_database_error(error)

            st.rerun()


def render_submitted_quiz():
    quiz_data = st.session_state.quiz_data
    result = st.session_state.quiz_result

    st.success("Quiz Submitted", icon="✅")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Final Score", f"{result['score']} / {result['total_questions']}")

    with col2:
        st.metric("Percentage", f"{result['percentage']}%")

    with col3:
        st.metric("Correct", result["correct_answers"])

    with col4:
        st.metric("Wrong", result["wrong_answers"])

    with col5:
        st.metric("Time Taken", format_time_taken(result["time_taken_seconds"]))

    render_quiz_result_download(
        quiz_data["topic"],
        result,
    )

    st.divider()
    st.subheader("Review Mode")

    for item in result["review_items"]:
        with st.container(border=True):
            st.markdown(f"### Question {item['question_number']}")
            st.write(item["question"])

            for option, option_text in item["options"].items():
                label = f"{option}. {option_text}"

                if option == item["correct_answer"]:
                    st.success(label)
                elif option == item["student_answer"] and not item["is_correct"]:
                    st.error(label)
                else:
                    st.write(label)

            student_answer = item["student_answer"] or "Not answered"
            st.markdown(f"**Student Answer:** {student_answer}")
            st.markdown(f"**Correct Answer:** {item['correct_answer']}")
            st.markdown(f"**Explanation:** {item['explanation']}")

    if st.button("Start New Quiz", type="primary"):
        reset_quiz_session()
        st.rerun()


def render_flashcards():
    render_tool_header(FLASHCARDS)

    topic = st.text_input("Enter Topic", key=INPUT_KEYS[FLASHCARDS])
    preferred_card_count = get_preferred_flashcard_count(10)
    card_count_options = [5, 10, 15, 20]
    card_count = st.selectbox(
        "Number of Flashcards",
        card_count_options,
        index=card_count_options.index(preferred_card_count)
        if preferred_card_count in card_count_options
        else 1,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        generate_clicked = st.button("Generate Flashcards", type="primary")

    with col2:
        if st.button("Restart Session"):
            reset_flashcard_session()
            st.rerun()

    if generate_clicked:
        topic = clean_text(topic)

        if not topic:
            st.warning("Please enter a topic before generating flashcards.", icon="💡")
            return

        progress = show_progress("Creating flashcards...")

        with st.spinner("Generating Flashcards..."):
            try:
                flashcard_data = generate_interactive_flashcards(topic, card_count)
                finish_progress(progress, "Flashcards generated")
                st.success("Flashcards Generated", icon="✅")
                record_history(
                    FLASHCARDS,
                    topic,
                    build_flashcards_markdown(
                        topic,
                        flashcard_data["flashcards"],
                    ),
                )
                st.session_state.flashcard_data = flashcard_data
                st.session_state.flashcard_current_index = 0
                st.session_state.flashcard_statuses = {}
                st.session_state.flashcard_revealed = False
                st.session_state.flashcard_started_at = time.time()
                st.session_state.flashcard_completed = False
                st.session_state.flashcard_session_saved = False
                st.session_state.flashcard_review_mode = False
                st.rerun()

            except GeminiAPIError as error:
                progress.empty()
                show_gemini_error(error)

            except FlashcardParseError as error:
                progress.empty()
                st.error(str(error), icon="⚠️")

    if "flashcard_data" not in st.session_state:
        st.info("Generate flashcards to begin an active learning session.", icon="💡")
        return

    if st.session_state.get("flashcard_completed"):
        render_completed_flashcard_session()
        return

    render_active_flashcard_session()


def render_active_flashcard_session():
    flashcard_data = st.session_state.flashcard_data
    cards = flashcard_data["flashcards"]
    current_index = st.session_state.get("flashcard_current_index", 0)

    if current_index < 0 or current_index >= len(cards):
        st.session_state.flashcard_current_index = 0
        current_index = 0

    current_card = cards[current_index]
    statuses = st.session_state.get("flashcard_statuses", {})
    elapsed_seconds = int(time.time() - st.session_state.flashcard_started_at)
    progress = calculate_flashcard_progress(cards, statuses, elapsed_seconds)

    st.progress(
        (current_index + 1) / len(cards),
        text=f"Card {current_index + 1} of {len(cards)}",
    )

    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

    with metric_col1:
        st.metric("Cards Studied", progress["cards_studied"])

    with metric_col2:
        st.metric("Known", progress["known_cards"])

    with metric_col3:
        st.metric("Need Revision", progress["revision_cards"])

    with metric_col4:
        st.metric("Remaining", progress["remaining_cards"])

    with metric_col5:
        st.metric("Completion", f"{progress['completion']}%")

    st.progress(
        progress["completion"] / 100,
        text="Learning completion",
    )

    st.markdown(f"### Card {current_index + 1}")
    st.caption(f"Difficulty: {current_card['difficulty']}")

    with st.container(border=True):
        st.markdown("#### Question")
        st.write(current_card["question"])

        if current_card.get("hint"):
            st.info(f"Hint: {current_card['hint']}", icon="💡")

        if st.session_state.get("flashcard_revealed"):
            st.divider()
            st.markdown("#### Answer")
            st.success(current_card["answer"], icon="✅")
        else:
            if st.button("Reveal Answer", type="primary"):
                st.session_state.flashcard_revealed = True
                st.toast("Answer revealed")
                st.rerun()

    if st.session_state.get("flashcard_revealed"):
        know_col, revision_col, skip_col = st.columns(3)

        with know_col:
            if st.button("✅ I Know This"):
                _mark_flashcard(current_index, "known", len(cards))

        with revision_col:
            if st.button("❌ Need Revision"):
                _mark_flashcard(current_index, "revision", len(cards))

        with skip_col:
            if st.button("Skip"):
                _move_to_flashcard(min(current_index + 1, len(cards) - 1))

    nav_col1, nav_col2, nav_col3 = st.columns(3)

    with nav_col1:
        if st.button("Previous Card", disabled=current_index == 0):
            _move_to_flashcard(current_index - 1)

    with nav_col2:
        jump_to = st.number_input(
            "Jump to Card",
            min_value=1,
            max_value=len(cards),
            value=current_index + 1,
            step=1,
        )

        if st.button("Go to Card"):
            _move_to_flashcard(jump_to - 1)

    with nav_col3:
        if st.button("Next Card", disabled=current_index == len(cards) - 1):
            _move_to_flashcard(current_index + 1)

    finish_disabled = progress["cards_studied"] == 0

    if st.button("Finish Session", type="primary", disabled=finish_disabled):
        _complete_flashcard_session()


def _mark_flashcard(index, status, card_count):
    st.session_state.flashcard_statuses[index] = status

    if index < card_count - 1:
        st.session_state.flashcard_current_index = index + 1

    st.session_state.flashcard_revealed = False
    st.rerun()


def _move_to_flashcard(index):
    st.session_state.flashcard_current_index = index
    st.session_state.flashcard_revealed = False
    st.rerun()


def _complete_flashcard_session():
    flashcard_data = st.session_state.flashcard_data
    elapsed_seconds = int(time.time() - st.session_state.flashcard_started_at)
    result = calculate_flashcard_progress(
        flashcard_data["flashcards"],
        st.session_state.flashcard_statuses,
        elapsed_seconds,
    )

    st.session_state.flashcard_result = result
    st.session_state.flashcard_completed = True

    if not st.session_state.get("flashcard_session_saved"):
        try:
            user_id = st.session_state.get("user_id")
            save_flashcard_session(
                user_id,
                flashcard_data["topic"],
                result["total_cards"],
                result["known_cards"],
                result["revision_cards"],
                result["completion"],
                result["study_time_seconds"],
            )
            st.session_state.flashcard_session_saved = True

        except DatabaseError as error:
            show_database_error(error)

    st.rerun()


def render_completed_flashcard_session():
    flashcard_data = st.session_state.flashcard_data
    result = st.session_state.flashcard_result

    st.success("Flashcard Session Complete", icon="✅")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Cards Studied", result["cards_studied"])

    with col2:
        st.metric("Known", result["known_cards"])

    with col3:
        st.metric("Need Revision", result["revision_cards"])

    with col4:
        st.metric("Completion", f"{result['completion']}%")

    with col5:
        st.metric("Study Time", format_study_time(result["study_time_seconds"]))

    render_flashcards_download(
        flashcard_data["topic"],
        flashcard_data["flashcards"],
    )

    st.divider()

    if result["weak_cards"]:
        st.subheader("Cards Marked Need Revision")

        for index, card in enumerate(result["weak_cards"], start=1):
            with st.container(border=True):
                st.markdown(f"### Weak Card {index}")
                st.caption(f"Difficulty: {card['difficulty']}")
                st.markdown("**Question**")
                st.write(card["question"])
                st.markdown("**Answer**")
                st.write(card["answer"])

        if st.button("Study Weak Cards Again", type="primary"):
            st.session_state.flashcard_data = {
                "topic": f"{flashcard_data['topic']} - Revision",
                "card_count": len(result["weak_cards"]),
                "flashcards": result["weak_cards"],
                "raw_response": build_flashcards_markdown(
                    flashcard_data["topic"],
                    result["weak_cards"],
                ),
            }
            st.session_state.flashcard_current_index = 0
            st.session_state.flashcard_statuses = {}
            st.session_state.flashcard_revealed = False
            st.session_state.flashcard_started_at = time.time()
            st.session_state.flashcard_completed = False
            st.session_state.flashcard_session_saved = False
            st.session_state.flashcard_review_mode = True
            st.rerun()

    else:
        st.info("Great work. No cards were marked for revision.", icon="✅")

    if st.button("Start New Flashcard Session"):
        reset_flashcard_session()
        st.rerun()


def render_study_planner():
    render_tool_header(STUDY_PLANNER)

    subject = st.text_input("Subject Name", key=INPUT_KEYS[STUDY_PLANNER])
    days = st.number_input("Days Until Exam", min_value=1, max_value=365, value=10)

    if st.button("Generate Plan", type="primary"):
        subject = clean_text(subject)

        if not subject:
            st.warning("Please enter a subject before generating a study plan.", icon="💡")
            return

        progress = show_progress("Designing study plan...")

        with st.spinner("Creating Study Plan..."):
            try:
                result = generate_plan(subject, days)
                finish_progress(progress, "Plan ready")
                st.success("Plan Ready", icon="✅")
                record_history(STUDY_PLANNER, subject, result)
                st.markdown(result)
                render_pdf_download(STUDY_PLANNER, subject, result)
            except GeminiAPIError as error:
                progress.empty()
                show_gemini_error(error)


def render_doubt_solver():
    render_tool_header(DOUBT_SOLVER)

    question = st.text_area("Ask Your Doubt", key=INPUT_KEYS[DOUBT_SOLVER])

    if st.button("Solve Doubt", type="primary"):
        question = clean_text(question)

        if not question:
            st.warning("Please enter your doubt before asking the AI.", icon="💡")
            return

        progress = show_progress("Thinking through your doubt...")

        with st.spinner("Thinking..."):
            try:
                result = solve_doubt(question)
                finish_progress(progress, "Answer generated")
                st.success("Answer Generated", icon="✅")
                record_history(DOUBT_SOLVER, question, result)
                st.markdown(result)
                render_pdf_download(DOUBT_SOLVER, question, result)
            except GeminiAPIError as error:
                progress.empty()
                show_gemini_error(error)


st.set_page_config(
    page_title=APP_CONFIG.page_title,
    page_icon=APP_CONFIG.page_icon,
    layout="wide",
)

# Always load the light theme styling for the application layout
load_css("light")

logger.info("AI Study Buddy application started.")

if "user_id" not in st.session_state:
    render_auth_page()
    st.stop()

st.session_state.theme = "light"

if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = WELCOME_DASHBOARD

with st.sidebar:
    render_sidebar_profile_card()

    # Separated Dashboard option placed above Workspace, matching expander header designs
    if st.button(
        "🏠 Dashboard",
        key="sidebar_nav_dashboard",
        type="primary" if st.session_state.get("selected_tool") == WELCOME_DASHBOARD else "secondary",
        use_container_width=True
    ):
        st.session_state.selected_tool = WELCOME_DASHBOARD
        st.rerun()

    if st.session_state.get("selected_tool") in PRIMARY_NAVIGATION_ITEMS:
        st.session_state.primary_tool = st.session_state.selected_tool

    if "primary_tool" not in st.session_state:
        st.session_state.primary_tool = FEATURES[0]

    st.markdown("<div class='sidebar-label'>Workspace</div>", unsafe_allow_html=True)
    st.radio(
        "Choose Tool",
        PRIMARY_NAVIGATION_ITEMS,
        key="primary_tool",
        label_visibility="collapsed",
        on_change=select_primary_tool,
    )

    with st.expander("Analytics", expanded=st.session_state.get("selected_tool") == ANALYTICS_DASHBOARD):
        if st.button(
            ANALYTICS_DASHBOARD,
            key="analytics_nav_dashboard",
            type="primary" if st.session_state.get("selected_tool") == ANALYTICS_DASHBOARD else "secondary",
        ):
            st.session_state.selected_tool = ANALYTICS_DASHBOARD
            st.rerun()

    with st.expander("History", expanded=st.session_state.get("selected_tool") in HISTORY_NAVIGATION_ITEMS):
        for history_item in HISTORY_NAVIGATION_ITEMS:
            if st.button(
                history_item,
                key=f"history_nav_{history_item}",
                type="primary" if st.session_state.get("selected_tool") == history_item else "secondary",
            ):
                st.session_state.selected_tool = history_item
                st.rerun()

    st.markdown(
        """
        <div class="sidebar-bottom">
            <div class="sidebar-brand">
                <span>📚</span>
                <div>
                    <strong>AI Study Buddy</strong>
                    <small>Study smarter with AI</small>
                </div>
            </div>
            <div class="sidebar-note">
                <strong>Powered by Gemini AI</strong>
                <span>Choose a tool and start with a topic, note, PDF, or question.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🚪 Sign Out", key="sidebar_sign_out_button", use_container_width=True):
        st.session_state.clear()
        st.rerun()

option = st.session_state.get("selected_tool", WELCOME_DASHBOARD)

load_css(st.session_state.theme)

render_hero()

if option == WELCOME_DASHBOARD:
    user_id = st.session_state.get("user_id")
    profile = get_profile_preferences(user_id) or {}
    analytics_data = get_dashboard_data(user_id) or {}
    render_welcome_dashboard(profile, analytics_data)
elif option == TOPIC_EXPLAINER:
    render_topic_explainer()
elif option == NOTES_SUMMARIZER:
    render_notes_summarizer()
elif option == QUIZ_GENERATOR:
    render_quiz_generator()
elif option == FLASHCARDS:
    render_flashcards()
elif option == STUDY_PLANNER:
    render_study_planner()
elif option == DOUBT_SOLVER:
    render_doubt_solver()
elif option == STUDY_HISTORY:
    render_study_history()
elif option == QUIZ_HISTORY:
    render_quiz_history()
elif option == FLASHCARD_HISTORY:
    render_flashcard_history()
elif option == ANALYTICS_DASHBOARD:
    render_analytics_dashboard()
elif option == STUDENT_PROFILE:
    render_student_profile()

if st.session_state.get("pending_delete_id"):
    confirm_delete_record(st.session_state.pending_delete_id)

if st.session_state.get("pending_quiz_delete_id"):
    confirm_delete_quiz_attempt(st.session_state.pending_quiz_delete_id)

if st.session_state.get("pending_flashcard_delete_id"):
    confirm_delete_flashcard_session(st.session_state.pending_flashcard_delete_id)

if st.session_state.get("confirm_delete_all"):
    confirm_delete_all_history()

if st.session_state.get("detail_history_id"):
    detail_id = st.session_state.detail_history_id
    st.session_state.pop("detail_history_id", None)
    show_history_details(detail_id)

if st.session_state.get("detail_flashcard_session_id"):
    detail_id = st.session_state.detail_flashcard_session_id
    st.session_state.pop("detail_flashcard_session_id", None)
    show_flashcard_session_details(detail_id)

render_footer()
