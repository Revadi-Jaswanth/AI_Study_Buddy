from datetime import date, timedelta

import streamlit as st

from analytics.charts import (
    ChartError,
    feature_usage_bar,
    quiz_difficulty_bar,
    quiz_performance_line,
    study_time_pie,
    topic_distribution_donut,
    weekly_activity_line,
)
from analytics.queries import get_dashboard_data, get_filter_options
from analytics.stats import activity_to_csv, analytics_to_markdown, seconds_to_label
from database.connection import DatabaseError
from database.pdf_exports import save_pdf_export
from exports.pdf_export import PDFExportError, create_pdf_export


def render_analytics_dashboard():
    st.markdown(
        """
        <div class="tool-header">
            <span>📊</span>
            <div>
                <h2>Analytics Dashboard</h2>
                <p>Understand learning activity, performance, study time, and topic focus.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filters = _render_filters()
    user_id = st.session_state.get("user_id")

    try:
        data = get_dashboard_data(user_id, **filters)

    except DatabaseError as error:
        st.warning(
            f"Analytics are temporarily unavailable: {error}",
            icon="⚠️",
        )
        return

    if data["summary"]["total_ai_requests"] == 0 and data["summary"]["total_quizzes_taken"] == 0:
        st.info(
            "No analytics available yet. Generate study content, complete quizzes, or study flashcards to populate this dashboard.",
            icon="💡",
        )

    _render_export_buttons(data)
    _render_summary_cards(data["summary"])
    _render_performance_cards(data["performance"])
    _render_charts(data)
    _render_recent_activity(data["recent_activity"])


def _render_filters():
    options = get_filter_options()
    today = date.today()
    default_start = today - timedelta(days=30)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        date_range = st.date_input(
            "Date Range",
            value=(default_start, today),
            key="analytics_date_range",
        )

    with col2:
        feature = st.selectbox(
            "Feature",
            options["features"],
            key="analytics_feature",
        )

    with col3:
        topic = st.text_input(
            "Topic",
            key="analytics_topic",
        )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = None, None

    return {
        "start_date": start_date,
        "end_date": end_date,
        "feature": feature,
        "topic": topic.strip(),
    }


def _render_summary_cards(summary):
    st.subheader("Dashboard Cards")
    rows = [
        ("Total AI Requests", summary["total_ai_requests"]),
        ("Topics Explained", summary["total_topics_explained"]),
        ("Notes Summarized", summary["total_notes_summarized"]),
        ("Quizzes Taken", summary["total_quizzes_taken"]),
        ("Flashcard Sessions", summary["total_flashcard_sessions"]),
        ("Study Plans", summary["total_study_plans_created"]),
        ("Doubts Solved", summary["total_doubts_solved"]),
        ("PDFs Exported", summary["total_pdfs_exported"]),
    ]

    for start in range(0, len(rows), 4):
        columns = st.columns(4)

        for column, (label, value) in zip(columns, rows[start:start + 4]):
            with column:
                st.metric(label, value)


def _render_performance_cards(performance):
    st.subheader("Learning Performance")
    row_one = [
        ("Highest Quiz Score", f"{performance['highest_quiz_score']}%"),
        ("Average Quiz Score", f"{performance['average_quiz_score']}%"),
        ("Lowest Quiz Score", f"{performance['lowest_quiz_score']}%"),
        ("Overall Accuracy", f"{performance['overall_accuracy']}%"),
    ]
    row_two = [
        ("Avg Study Duration", seconds_to_label(performance["average_study_session_duration"])),
        ("Most Studied Topic", performance["most_studied_topic"]),
        ("Least Studied Topic", performance["least_studied_topic"]),
        ("Weekly Streak", performance["weekly_learning_streak"]),
    ]
    row_three = [
        ("Most Active Day", performance["most_active_day"]),
        ("Avg Questions / Quiz", performance["average_questions_per_quiz"]),
        ("Avg Flashcard Completion", f"{performance['average_flashcard_completion']}%"),
    ]

    for row in [row_one, row_two, row_three]:
        columns = st.columns(len(row))

        for column, (label, value) in zip(columns, row):
            with column:
                st.metric(label, value)


def _render_charts(data):
    st.subheader("Interactive Charts")

    try:
        chart_one, chart_two = st.columns(2)

        with chart_one:
            st.plotly_chart(
                feature_usage_bar(data["feature_usage"]),
                use_container_width=True,
            )

        with chart_two:
            st.plotly_chart(
                weekly_activity_line(data["weekly_activity"]),
                use_container_width=True,
            )

        chart_three, chart_four = st.columns(2)

        with chart_three:
            st.plotly_chart(
                quiz_performance_line(data["quiz_performance"]),
                use_container_width=True,
            )

        with chart_four:
            st.plotly_chart(
                study_time_pie(data["study_time"]),
                use_container_width=True,
            )

        chart_five, chart_six = st.columns(2)

        with chart_five:
            st.plotly_chart(
                topic_distribution_donut(data["topic_distribution"]),
                use_container_width=True,
            )

        with chart_six:
            st.plotly_chart(
                quiz_difficulty_bar(data["quiz_difficulty"]),
                use_container_width=True,
            )

    except ChartError as error:
        st.warning(
            str(error),
            icon="⚠️",
        )


def _render_recent_activity(activity_rows):
    st.subheader("Recent Activity")

    if not activity_rows:
        st.info("No recent activity found for the selected filters.", icon="💡")
        return

    st.dataframe(
        activity_rows,
        use_container_width=True,
        hide_index=True,
    )


def _render_export_buttons(data):
    export_col1, export_col2 = st.columns(2)

    with export_col1:
        try:
            filename, pdf_bytes = create_pdf_export(
                "Analytics Dashboard",
                "Learning Analytics",
                analytics_to_markdown(data),
            )

            st.download_button(
                "📥 Export Analytics PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                key="analytics_pdf_export",
                on_click=_record_analytics_pdf_export,
                args=(
                    filename,
                ),
            )

        except PDFExportError as error:
            st.warning(
                str(error),
                icon="⚠️",
            )

    with export_col2:
        st.download_button(
            "📥 Export Recent Activity CSV",
            data=activity_to_csv(data["recent_activity"]),
            file_name="AI_Study_Buddy_Analytics.csv",
            mime="text/csv",
            key="analytics_csv_export",
        )


def _record_analytics_pdf_export(file_name):
    try:
        save_pdf_export(
            "Analytics Dashboard",
            "Learning Analytics",
            file_name,
        )

    except DatabaseError:
        pass
