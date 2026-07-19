import streamlit as st
import time
import textwrap
from profile.preferences import get_preferred_theme
from components.progress_stepper import render_progress_stepper
from components.review_card import render_review_card
from components.success_animation import render_success_animation


def render_login_form(authenticate_user):
    """Renders the premium sign in form, validates inputs, and authenticates user credentials."""
    st.markdown(
        textwrap.dedent("""
        <div style='margin-bottom: 24px;'>
            <h3 style='margin: 0; font-size: 22px; font-weight: 700; color: var(--text);'>Welcome back 👋</h3>
            <p style='margin: 4px 0 0 0; font-size: 13px; color: var(--muted);'>Log in to continue your personalized AI learning journey.</p>
        </div>
        """),
        unsafe_allow_html=True
    )

    login_email = st.text_input("Email", placeholder="", key="auth_login_email")
    st.markdown(
        '<input type="text" style="display:none;" name="dummy_username" autocomplete="off">'
        '<input type="password" style="display:none;" name="dummy_password" autocomplete="new-password">',
        unsafe_allow_html=True
    )
    login_password = st.text_input("Password", type="password", placeholder="", key="auth_login_password")

    col_rem, col_forg = st.columns([1, 1])
    with col_rem:
        st.checkbox("Remember me", key="auth_remember_me")
    with col_forg:
        st.markdown(
            textwrap.dedent("<div style='text-align: right; margin-top: 4px;'><a href='#' style='color: var(--accent); font-size: 0.85rem; text-decoration: none; font-weight: 500;'>Forgot password?</a></div>"),
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    if st.button("Continue", type="primary", use_container_width=True, key="btn_login_submit"):
        with st.spinner("Authenticating..."):
            user = authenticate_user(login_email, login_password)
            if user:
                st.session_state.user_id = user["id"]
                st.session_state.user_name = user["full_name"]
                st.session_state.user_email = user["email"]
                pref_theme = get_preferred_theme(user["id"], "Dark")
                st.session_state.theme = "light" if pref_theme == "Light" else "dark"
                
                # Show premium welcome loading sequence
                render_success_animation(user["full_name"])
                st.rerun()
            else:
                st.error("Invalid email or password. Please verify your credentials and try again.", icon="❌")


def render_signup_form(register_user, authenticate_user):
    """Renders the multi-step onboarding wizard for new user registration with persistent data backup."""
    # Ensure current onboarding step is initialized
    if "auth_step" not in st.session_state:
        st.session_state.auth_step = 1

    # Initialize non-widget persistent registration dict in session state
    if "reg_data" not in st.session_state:
        st.session_state.reg_data = {
            "name": "",
            "email": "",
            "password": "",
            "college": "",
            "branch": "",
            "year_label": "1st Year",
            "style": "Mixed Study Guide",
            "goal": ""
        }

    render_progress_stepper(st.session_state.auth_step)

    # STEP 1: Personal Information
    if st.session_state.auth_step == 1:
        st.markdown(
            textwrap.dedent("""
            <div style='margin-bottom: 20px;'>
                <h3 style='margin: 0; font-size: 18px; font-weight: 600; color: var(--text);'>Personal Information</h3>
                <p style='margin: 2px 0 0 0; font-size: 12px; color: var(--muted);'>Tell us who you are and secure your account.</p>
            </div>
            """),
            unsafe_allow_html=True
        )

        reg_name = st.text_input("Full Name", value=st.session_state.reg_data["name"], placeholder="", key="auth_reg_name")
        reg_email = st.text_input("Email Address", value=st.session_state.reg_data["email"], placeholder="", key="auth_reg_email")
        st.markdown(
            '<input type="text" style="display:none;" name="dummy_username" autocomplete="off">'
            '<input type="password" style="display:none;" name="dummy_password" autocomplete="new-password">',
            unsafe_allow_html=True
        )
        reg_password = st.text_input("Password (min 6 characters)", type="password", value=st.session_state.reg_data["password"], placeholder="", key="auth_reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", value=st.session_state.reg_data["password"], placeholder="", key="auth_reg_confirm")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        if st.button("Next Step", type="primary", use_container_width=True, key="btn_reg_step1_next"):
            reg_name = reg_name.strip()
            reg_email = reg_email.strip()
            reg_password = reg_password.strip()
            reg_confirm = reg_confirm.strip()

            if not reg_name or not reg_email or not reg_password:
                st.warning("All fields are required to proceed.", icon="⚠️")
            elif reg_password != reg_confirm:
                st.warning("Passwords do not match.", icon="⚠️")
            elif len(reg_password) < 6:
                st.warning("Password must be at least 6 characters long.", icon="⚠️")
            else:
                # Save values to persistent non-widget state dict
                st.session_state.reg_data["name"] = reg_name
                st.session_state.reg_data["email"] = reg_email
                st.session_state.reg_data["password"] = reg_password
                st.session_state.auth_step = 2
                st.rerun()

    # STEP 2: Academic Profile
    elif st.session_state.auth_step == 2:
        st.markdown(
            textwrap.dedent("""
            <div style='margin-bottom: 20px;'>
                <h3 style='margin: 0; font-size: 18px; font-weight: 600; color: var(--text);'>Academic Profile</h3>
                <p style='margin: 2px 0 0 0; font-size: 12px; color: var(--muted);'>Configure your studies to calibrate the AI model.</p>
            </div>
            """),
            unsafe_allow_html=True
        )

        reg_college = st.text_input("College / University", value=st.session_state.reg_data["college"], placeholder="", key="auth_reg_college")
        reg_branch = st.text_input("Branch / Department", value=st.session_state.reg_data["branch"], placeholder="", key="auth_reg_branch")
        
        # Load index selections safely
        dropdown_options = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"]
        year_idx = dropdown_options.index(st.session_state.reg_data["year_label"]) if st.session_state.reg_data["year_label"] in dropdown_options else 0
        
        year_label = st.selectbox(
            "Current Academic Year",
            dropdown_options,
            index=year_idx,
            key="auth_reg_year_label"
        )
        
        styles_options = ["Visual Notes", "Practical Coding Scenarios", "Reading Bulletins", "Mixed Study Guide"]
        style_idx = styles_options.index(st.session_state.reg_data["style"]) if st.session_state.reg_data["style"] in styles_options else 3
        
        reg_style = st.selectbox(
            "Preferred Study Style",
            styles_options,
            index=style_idx,
            key="auth_reg_style"
        )

        reg_goal = st.text_input("Weekly Study Goal (e.g. Pass OS exam, Learn Python)", value=st.session_state.reg_data["goal"], placeholder="", key="auth_reg_goal")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("Back", key="btn_reg_step2_back", use_container_width=True):
                # Save input values persistently before stepping back
                st.session_state.reg_data["college"] = reg_college
                st.session_state.reg_data["branch"] = reg_branch
                st.session_state.reg_data["year_label"] = year_label
                st.session_state.reg_data["style"] = reg_style
                st.session_state.reg_data["goal"] = reg_goal
                st.session_state.auth_step = 1
                st.rerun()
        with col_b2:
            if st.button("Next Step", type="primary", key="btn_reg_step2_next", use_container_width=True):
                if not reg_college.strip() or not reg_branch.strip():
                    st.warning("Institution and branch details are required.", icon="⚠️")
                else:
                    # Save input values persistently before stepping forward
                    st.session_state.reg_data["college"] = reg_college
                    st.session_state.reg_data["branch"] = reg_branch
                    st.session_state.reg_data["year_label"] = year_label
                    st.session_state.reg_data["style"] = reg_style
                    st.session_state.reg_data["goal"] = reg_goal
                    st.session_state.auth_step = 3
                    st.rerun()

    # STEP 3: Review Details
    elif st.session_state.auth_step == 3:
        st.markdown(
            textwrap.dedent("""
            <div style='margin-bottom: 20px;'>
                <h3 style='margin: 0; font-size: 18px; font-weight: 600; color: var(--text);'>Review Profile</h3>
                <p style='margin: 2px 0 0 0; font-size: 12px; color: var(--muted);'>Verify your configurations before entering the workspace.</p>
            </div>
            """),
            unsafe_allow_html=True
        )

        name = st.session_state.reg_data["name"]
        email = st.session_state.reg_data["email"]
        college = st.session_state.reg_data["college"]
        branch = st.session_state.reg_data["branch"]
        year_label = st.session_state.reg_data["year_label"]
        style = st.session_state.reg_data["style"]
        goal = st.session_state.reg_data["goal"]

        # Render summary card
        render_review_card(name, email, college, branch, year_label, style, goal)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("Back", key="btn_reg_step3_back", use_container_width=True):
                st.session_state.auth_step = 2
                st.rerun()
        with col_c2:
            if st.button("Create Workspace", type="primary", key="btn_reg_step3_submit", use_container_width=True):
                # Map displayed year labels to DB strings
                year_mapping = {
                    "1st Year": "First Year",
                    "2nd Year": "Second Year",
                    "3rd Year": "Third Year",
                    "4th Year": "Final Year",
                    "Graduated": "Graduate"
                }
                db_year = year_mapping.get(year_label, "First Year")
                password = st.session_state.reg_data["password"]

                # Map study style display strings to database preference styles
                style_mapping = {
                    "Visual Notes": "Visual",
                    "Practical Coding Scenarios": "Practical",
                    "Reading Bulletins": "Reading",
                    "Mixed Study Guide": "Mixed"
                }
                db_style = style_mapping.get(style, "Mixed")

                try:
                    # Register user and initialize preferences
                    user_id = register_user(
                        name.strip(),
                        email.strip().lower(),
                        password.strip(),
                        college.strip(),
                        branch.strip(),
                        db_year
                    )
                    
                    # Update preferences with study style and goals from onboarding wizard
                    from profile.profile_database import update_profile
                    preferences = {
                        "education_level": "Undergraduate" if year_label != "Graduated" else "Graduate",
                        "preferred_language": "English",
                        "learning_style": db_style,
                        "exam_type": "Semester",
                        "weak_subjects": "",
                        "daily_study_time": 2.0,  # default daily study time
                        "preferred_quiz_difficulty": "Medium",
                        "preferred_flashcard_count": 10,
                        "preferred_theme": "Dark",
                        "current_study_goal": goal.strip() if goal.strip() else "Semester Success",
                        "exam_date": None,
                        "preferred_explanation_level": "Intermediate" if year_label != "1st Year" else "Beginner"
                    }
                    
                    user_data = {
                        "full_name": name.strip(),
                        "email": email.strip().lower(),
                        "college_name": college.strip(),
                        "branch_department": branch.strip(),
                        "current_year": db_year
                    }
                    
                    update_profile(user_id, user_data, preferences)

                    # Auto-login upon success
                    st.session_state.user_id = user_id
                    st.session_state.user_name = name.strip()
                    st.session_state.user_email = email.strip().lower()
                    st.session_state.auth_step = 1
                    
                    # Clear temporary registration storage dict
                    if "reg_data" in st.session_state:
                        del st.session_state.reg_data
                    
                    # Show premium loading sequence
                    render_success_animation(name.strip())
                    st.rerun()

                except Exception as error:
                    st.error(f"Failed to create workspace: {error}", icon="❌")
