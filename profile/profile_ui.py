import streamlit as st

from analytics.queries import get_dashboard_data
from database.connection import DatabaseError
from profile.profile_manager import (
    ProfileValidationError,
    delete_profile,
    export_profile_json,
    import_profile_json,
    load_profile,
    save_profile,
)


def render_student_profile():
    st.markdown(
        """
        <div class="tool-header">
            <span>👤</span>
            <div>
                <h2>Student Profile</h2>
                <p>Personalize AI Study Buddy around your goals, learning style, and exam needs.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        user_id = st.session_state.get("user_id")
        profile = load_profile(user_id)

    except DatabaseError as error:
        st.warning(f"Profile is temporarily unavailable: {error}", icon="⚠️")
        return

    _render_notifications(profile)

    dashboard_tab, profile_tab, settings_tab = st.tabs(
        [
            "Profile Dashboard",
            "Update Profile",
            "Settings",
        ]
    )

    with dashboard_tab:
        _render_profile_dashboard(profile)

    with profile_tab:
        _render_profile_form(profile)

    with settings_tab:
        _render_settings(profile)


def _render_profile_dashboard(profile):
    if not profile:
        st.info("No student profile saved yet. Add your profile to unlock personalization.", icon="💡")
        return

    try:
        user_id = st.session_state.get("user_id")
        analytics = get_dashboard_data(user_id)

    except DatabaseError:
        analytics = None

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Student Name", profile["full_name"])

    with col2:
        st.metric("Study Streak", _safe_metric(analytics, "weekly_learning_streak", "performance"))

    with col3:
        st.metric("Quiz Accuracy", f"{_safe_metric(analytics, 'overall_accuracy', 'performance')}%")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Learning Style", profile["learning_style"])

    with col5:
        st.metric("Total AI Sessions", _safe_metric(analytics, "total_ai_requests", "summary"))

    with col6:
        st.metric("Daily Study Time", f"{profile['daily_study_time']} hr")

    st.markdown("### Current Study Goal")
    st.write(profile.get("current_study_goal") or "No current goal saved.")

    st.markdown("### Weak Subjects")
    st.write(profile.get("weak_subjects") or "No weak subjects saved.")


def _render_profile_form(profile):
    with st.form("student_profile_form"):
        st.subheader("Personal Information")
        full_name = st.text_input("Full Name", value=_value(profile, "full_name"))
        email = st.text_input("Email (optional)", value=_value(profile, "email"))
        college_name = st.text_input("College Name", value=_value(profile, "college_name"))
        branch_department = st.text_input("Branch / Department", value=_value(profile, "branch_department"))
        current_year = st.selectbox(
            "Current Year of Study",
            ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate", "Other"],
            index=_index(["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate", "Other"], _value(profile, "current_year")),
        )

        st.subheader("Learning Preferences")
        education_level = st.selectbox(
            "Education Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=_index(["Beginner", "Intermediate", "Advanced"], _value(profile, "education_level", "Beginner")),
        )
        preferred_language = st.text_input("Preferred Language", value=_value(profile, "preferred_language", "English"))
        learning_style = st.selectbox(
            "Learning Style",
            ["Visual", "Reading", "Practical", "Mixed"],
            index=_index(["Visual", "Reading", "Practical", "Mixed"], _value(profile, "learning_style", "Mixed")),
        )
        exam_type = st.selectbox(
            "Exam Type",
            ["Semester", "Placement", "Competitive", "Interview"],
            index=_index(["Semester", "Placement", "Competitive", "Interview"], _value(profile, "exam_type", "Semester")),
        )
        weak_subjects = st.text_area("Weak Subjects", value=_value(profile, "weak_subjects"))
        current_study_goal = st.text_input("Current Study Goal", value=_value(profile, "current_study_goal"))
        exam_date = st.date_input("Exam Date", value=profile.get("exam_date") if profile and profile.get("exam_date") else None)
        daily_study_time = st.number_input(
            "Daily Study Time (hours)",
            min_value=0.25,
            max_value=24.0,
            value=float(_value(profile, "daily_study_time", 1.0)),
            step=0.25,
        )
        preferred_quiz_difficulty = st.selectbox(
            "Preferred Quiz Difficulty",
            ["Easy", "Medium", "Hard"],
            index=_index(["Easy", "Medium", "Hard"], _value(profile, "preferred_quiz_difficulty", "Medium")),
        )
        preferred_flashcard_count = st.selectbox(
            "Preferred Flashcard Count",
            [5, 10, 15, 20],
            index=_index([5, 10, 15, 20], int(_value(profile, "preferred_flashcard_count", 10))),
        )
        preferred_theme = "Light"
        preferred_explanation_level = st.selectbox(
            "Preferred Explanation Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=_index(["Beginner", "Intermediate", "Advanced"], _value(profile, "preferred_explanation_level", "Beginner")),
        )

        submitted = st.form_submit_button("Save Profile", type="primary")

    if submitted:
        user_data = {
            "full_name": full_name.strip(),
            "email": email.strip(),
            "college_name": college_name.strip(),
            "branch_department": branch_department.strip(),
            "current_year": current_year,
        }
        preferences = {
            "education_level": education_level,
            "preferred_language": preferred_language.strip() or "English",
            "learning_style": learning_style,
            "exam_type": exam_type,
            "weak_subjects": weak_subjects.strip(),
            "daily_study_time": daily_study_time,
            "preferred_quiz_difficulty": preferred_quiz_difficulty,
            "preferred_flashcard_count": preferred_flashcard_count,
            "preferred_theme": preferred_theme,
            "current_study_goal": current_study_goal.strip(),
            "exam_date": exam_date,
            "preferred_explanation_level": preferred_explanation_level,
        }

        try:
            user_id = st.session_state.get("user_id")
            save_profile(user_id, user_data, preferences)
            st.success("Profile saved successfully.", icon="✅")
            st.rerun()

        except (ProfileValidationError, DatabaseError) as error:
            st.error(str(error), icon="⚠️")


def _render_settings(profile):
    st.subheader("Export Profile")

    st.download_button(
        "Export Profile JSON",
        data=export_profile_json(profile),
        file_name="AI_Study_Buddy_Profile.json",
        mime="application/json",
        disabled=not profile,
    )

    st.subheader("Import Profile")
    uploaded_file = st.file_uploader("Import Profile JSON", type=["json"])

    if uploaded_file and st.button("Import Profile"):
        try:
            import_profile_json(uploaded_file.getvalue().decode("utf-8"))
            st.success("Profile imported successfully.", icon="✅")
            st.rerun()

        except (ProfileValidationError, DatabaseError) as error:
            st.error(str(error), icon="⚠️")

    st.subheader("Security Settings")
    with st.expander("Change Password"):
        old_password = st.text_input("Current Password", type="password", key="sec_old_pass")
        new_password = st.text_input("New Password (min 6 characters)", type="password", key="sec_new_pass")
        confirm_password = st.text_input("Confirm New Password", type="password", key="sec_confirm_pass")

        if st.button("Update Password"):
            if new_password != confirm_password:
                st.error("New passwords do not match.", icon="❌")
            elif len(new_password) < 6:
                st.error("New password must be at least 6 characters.", icon="❌")
            else:
                try:
                    from database.auth import change_user_password
                    user_id = st.session_state.get("user_id")
                    if change_user_password(user_id, old_password, new_password):
                        st.success("Password updated successfully.", icon="✅")
                    else:
                        st.error("Failed to update password. Please check your current password.", icon="❌")
                except Exception as exc:
                    st.error(f"Error: {exc}", icon="❌")

    st.subheader("Reset Profile")

    if st.button("Reset Profile"):
        st.session_state.confirm_profile_reset = True
        st.rerun()

    if st.session_state.get("confirm_profile_reset"):
        st.warning("This will permanently remove your saved profile.", icon="⚠️")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Confirm Reset", type="primary"):
                try:
                    user_id = st.session_state.get("user_id")
                    delete_profile(user_id)
                    st.session_state.clear()
                    st.success("Account deleted successfully.", icon="✅")
                    st.rerun()

                except DatabaseError as error:
                    st.error(str(error), icon="⚠️")

        with col2:
            if st.button("Cancel Reset"):
                st.session_state.confirm_profile_reset = False
                st.rerun()


def _render_notifications(profile):
    if not profile:
        return

    try:
        user_id = st.session_state.get("user_id")
        analytics = get_dashboard_data(user_id)

    except DatabaseError:
        return

    recent_activity = analytics.get("recent_activity", [])
    accuracy = analytics["performance"]["overall_accuracy"]
    weak_subjects = profile.get("weak_subjects")

    if not recent_activity:
        st.info("You have not studied yet. Start with your weakest subject today.", icon="💡")
    elif accuracy >= 75:
        st.success("Your quiz accuracy is looking strong. Keep the streak going.", icon="✅")

    if weak_subjects:
        first_subject = weak_subjects.split(",")[0].strip()
        st.info(f"Time to revise {first_subject}. A short flashcard session would help.", icon="💡")


def _safe_metric(analytics, key, section):
    if not analytics:
        return 0

    return analytics.get(section, {}).get(key, 0)


def _value(profile, key, default=""):
    if not profile:
        return default

    value = profile.get(key)

    return value if value not in [None, ""] else default


def _index(options, value):
    return options.index(value) if value in options else 0
