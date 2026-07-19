import streamlit as st
import datetime

# Clean, modern vector icons for the welcome dashboard widgets
DASHBOARD_ICONS = {
    "flame": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-flame"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>""",
    "zap": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "target": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-target"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
    "clock": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clock"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>""",
    "sparkles": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sparkles"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"/><path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5.5Z"/><path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1Z"/></svg>""",
    "brain": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-brain"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M12 5v14Z"/><path d="M12 9h4Z"/><path d="M12 13h-4Z"/></svg>""",
    "cap": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-graduation-cap"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.91a2 2 0 0 0 1.66 0z"/><path d="M6 18.8v-4L2 13v6a1 1 0 0 0 1 1h3Z"/><path d="M21.4 10.9v4a2 2 0 0 1-2 2h-3v2.2c0 .4-.3.8-.8.8h-4.8c-.5 0-.8-.4-.8-.8V16.9"/></svg>""",
    "planner": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar-days"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/></svg>""",
    "doubt": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-message-square-text"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M8 9h8"/><path d="M8 13h6"/></svg>""",
    "info": """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-info"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>"""
}


def clean_html(html_str: str) -> str:
    """Removes indentation and newlines to prevent Streamlit from interpreting HTML as preformatted markdown code blocks."""
    return " ".join([line.strip() for line in html_str.split("\n") if line.strip()])


def StatsCard(title: str, value: str, description: str, icon_name: str):
    """Renders a premium KPI metric statistic card."""
    icon_svg = DASHBOARD_ICONS.get(icon_name, DASHBOARD_ICONS["zap"])
    html_payload = clean_html(f"""
    <div class="metric-card" style="padding: 18px; border-radius: 12px; background: var(--surface); border: 1px solid var(--line); box-shadow: var(--shadow); transition: all 0.2s ease;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 11px; text-transform: uppercase; font-weight: 600; color: var(--muted); letter-spacing: 0.05em;">{title}</span>
            <span style="color: var(--accent); display: inline-flex;">{icon_svg}</span>
        </div>
        <strong style="font-size: 24px; font-weight: 700; color: var(--text); display: block; margin-bottom: 4px;">{value}</strong>
        <small style="font-size: 11.5px; color: var(--muted);">{description}</small>
    </div>
    """)
    st.markdown(html_payload, unsafe_allow_html=True)


def QuickActionCard(title: str, description: str, icon_name: str, target_tool: str):
    """Renders an interactive quick-launch action button card."""
    icon_svg = DASHBOARD_ICONS.get(icon_name, DASHBOARD_ICONS["zap"])
    
    st.markdown(
        """
        <div class="quick-actions-wrapper">
        """,
        unsafe_allow_html=True
    )
    
    if st.button(f"Launch {title}", key=f"quick_act_{target_tool}", use_container_width=True):
        st.session_state.selected_tool = target_tool
        st.rerun()

    html_payload = clean_html(f"""
        <div class="quick-action-card-face">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                <span style="color: var(--accent); display: inline-flex;">{icon_svg}</span>
                <strong style="font-size: 14px; color: var(--text); font-weight: 600;">{title}</strong>
            </div>
            <span style="font-size: 12px; color: var(--muted); display: block; line-height: 1.35;">{description}</span>
        </div>
    </div>
    """)
    st.markdown(html_payload, unsafe_allow_html=True)


def ActivityTimeline(recent_activity: list):
    """Renders a chronological timeline listing recent learning events."""
    if not recent_activity:
        html_payload = clean_html("""
        <div style="padding: 20px; text-align: center; color: var(--muted); font-size: 13.5px;">
            No recent study sessions recorded. Choose a Quick Action to get started!
        </div>
        """)
        st.markdown(html_payload, unsafe_allow_html=True)
        return

    timeline_items_html = ""
    for idx, act in enumerate(recent_activity[:5]):
        feature = act.get("feature", "Study Log")
        topic = act.get("topic", "General Topic")
        date_val = act.get("activity_date")
        status = act.get("status", "Completed")

        # Format dates nicely
        formatted_date = ""
        if isinstance(date_val, datetime.datetime):
            formatted_date = date_val.strftime("%b %d, %H:%M")
        else:
            formatted_date = str(date_val)

        # Style indicators based on feature
        bullet_color = "var(--accent)"
        if "Quiz" in feature:
            bullet_color = "var(--accent-3)"
        elif "Flashcard" in feature:
            bullet_color = "var(--accent-2)"

        # Clean and truncate topic to 1-2 lines maximum
        clean_topic = " ".join(str(topic).split())
        if len(clean_topic) > 90:
            clean_topic = clean_topic[:87].strip() + "..."

        timeline_items_html += f"""
        <div style="display: flex; gap: 14px; position: relative; margin-bottom: 16px;">
            {'' if idx == len(recent_activity[:5]) - 1 else f'<div style="position: absolute; left: 6px; top: 18px; bottom: -18px; width: 2px; background-color: var(--line); z-index: 0;"></div>'}
            <div style="width: 14px; height: 14px; border-radius: 50%; background-color: {bullet_color}; border: 3px solid var(--surface); z-index: 1; flex-shrink: 0; margin-top: 3px;"></div>
            <div style="flex-grow: 1;">
                <div style="display: flex; justify-content: space-between; font-size: 13px;">
                    <strong style="color: var(--text); font-weight: 600;">{feature} &bull; <span style='font-weight: 400; color: var(--muted);'>{status}</span></strong>
                    <span style="color: var(--muted); font-size: 11px;">{formatted_date}</span>
                </div>
                <span style="font-size: 12.5px; color: var(--muted); display: block; margin-top: 2px;">{clean_topic}</span>
            </div>
        </div>
        """

    html_payload = clean_html(f"""
    <div class="timeline-container" style="position: relative; padding: 4px 0;">
        {timeline_items_html}
    </div>
    """)
    st.markdown(html_payload, unsafe_allow_html=True)


def InsightCard(title: str, description: str, detail: str, insight_type: str = "info"):
    """Renders a card highlighting key learning diagnostic checks and recommendations."""
    border_color = "var(--accent)"
    bg_color = "rgba(99, 102, 241, 0.04)"
    icon_svg = DASHBOARD_ICONS["info"]

    if insight_type == "success":
        border_color = "var(--accent-2)"
        bg_color = "rgba(16, 185, 129, 0.04)"
    elif insight_type == "warning":
        border_color = "var(--accent-3)"
        bg_color = "rgba(217, 119, 6, 0.04)"

    html_payload = clean_html(f"""
    <div style="padding: 16px; border-radius: 10px; border-left: 3px solid {border_color}; background-color: var(--surface-soft); border-top: 1px solid var(--line); border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); margin-bottom: 14px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="color: {border_color}; display: inline-flex;">{icon_svg}</span>
            <strong style="font-size: 13.5px; color: var(--text); font-weight: 600;">{title}</strong>
        </div>
        <span style="font-size: 12.5px; color: var(--muted); display: block; line-height: 1.4;">{description}</span>
        {f"<span style='font-size: 11.5px; color: {border_color}; display: block; margin-top: 6px; font-weight: 500;'>{detail}</span>" if detail else ""}
    </div>
    """)
    st.markdown(html_payload, unsafe_allow_html=True)


def GoalProgress(completed: float, target: float, label: str):
    """Renders a progress tracker detailing study goals."""
    pct = min(100.0, max(0.0, (completed / target) * 100.0)) if target > 0 else 0.0
    html_payload = clean_html(f"""
    <div style="margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; font-size: 12.5px; margin-bottom: 6px;">
            <span style="color: var(--text); font-weight: 500;">{label}</span>
            <strong style="color: var(--accent);">{completed:.1f} / {target:.1f} hrs ({pct:.0f}%)</strong>
        </div>
        <div style="width: 100%; height: 6px; background-color: var(--surface-soft); border-radius: 3px; overflow: hidden; border: 1px solid var(--line);">
            <div style="width: {pct}%; height: 100%; background: var(--accent-gradient); border-radius: 3px;"></div>
        </div>
    </div>
    """)
    st.markdown(html_payload, unsafe_allow_html=True)


def RecommendationCard(topic_name: str, reason: str):
    """Renders recommended revision topic cues."""
    html_payload = clean_html(f"""
    <div style="padding: 12px 14px; border-radius: 8px; background-color: var(--surface); border: 1px solid var(--line); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <strong style="font-size: 13px; color: var(--text); font-weight: 600; display: block;">{topic_name}</strong>
            <span style="font-size: 11.5px; color: var(--muted);">{reason}</span>
        </div>
        <span style="font-size: 11px; font-weight: 600; color: var(--accent); background: rgba(99,102,241,0.08); padding: 4px 8px; border-radius: 4px;">Revise Now</span>
    </div>
    """)
    st.markdown(html_payload, unsafe_allow_html=True)


def render_welcome_dashboard(profile: dict, analytics: dict):
    """Main renderer for the premium Welcome Dashboard Workspace home screen."""
    user_name = profile.get("full_name") or "Student"
    
    # Compute greeting based on time of day
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    html_payload = clean_html(f"""
    <div style="margin-bottom: 28px;">
        <h2 style="font-size: 28px; font-weight: 800; margin: 0; color: var(--text); letter-spacing: -0.02em;">
            {greeting}, {user_name} 👋
        </h2>
        <p style="font-size: 14px; color: var(--muted); margin: 4px 0 0 0;">
            Welcome back to AI Study Buddy. Ready to expand your knowledge today?
        </p>
    </div>
    """)
    st.markdown(html_payload, unsafe_allow_html=True)

    # 1. KPI Statistic Cards Grid
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    
    accuracy = analytics.get("performance", {}).get("overall_accuracy", 0)
    streak = analytics.get("performance", {}).get("weekly_learning_streak", 0)
    ai_requests = analytics.get("summary", {}).get("total_ai_requests", 0)
    study_mins = analytics.get("performance", {}).get("average_study_session_duration", 0) or 0
    study_hrs = (study_mins * ai_requests) / 3600.0  # approximate active study hours

    with col_kpi1:
        StatsCard("Study Streak", f"{streak} Days", "🔥 Learning streak active", "flame")
    with col_kpi2:
        StatsCard("AI Requests", f"{ai_requests}", "⚡ Dynamic prompts run", "zap")
    with col_kpi3:
        StatsCard("Quiz Accuracy", f"{accuracy:.1f}%", "🎯 Overall syllabus accuracy", "target")
    with col_kpi4:
        StatsCard("Active Study", f"{study_hrs:.1f} hrs", "⏳ Accumulated study time", "clock")

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # 2. Main content split columns
    col_left_main, col_right_main = st.columns([6, 4], gap="large")

    with col_left_main:
        # Quick Actions Section
        st.markdown("<h3 style='font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.04em;'>Quick Actions</h3>", unsafe_allow_html=True)
        
        col_qa1, col_qa2 = st.columns(2)
        with col_qa1:
            QuickActionCard("Explain Topic", "Generate clear explanations on new terms.", "sparkles", "📖 Topic Explainer")
            QuickActionCard("Flashcards Cues", "Test your memory with repetition card decks.", "brain", "🃏 Flashcards")
        with col_qa2:
            QuickActionCard("Generate Quiz", "Take custom testing to assess syllabus knowledge.", "cap", "❓ Quiz Generator")
            QuickActionCard("Study Planner", "Create structured timetables in seconds.", "planner", "🎯 Study Planner")

        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

        # Recent Activity Timeline Section
        st.markdown("<h3 style='font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.04em;'>Recent Activity</h3>", unsafe_allow_html=True)
        recent_activity = analytics.get("recent_activity", [])
        ActivityTimeline(recent_activity)

    with col_right_main:
        # Goal Progress Widget
        st.markdown("<h3 style='font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.04em;'>Goal Progress</h3>", unsafe_allow_html=True)
        
        target_hours = float(profile.get("daily_study_time") or 1.0)
        GoalProgress(min(study_hrs, target_hours), target_hours, "Daily Study Goal")
        
        target_box_payload = clean_html(f"""
        <div style="background-color: var(--surface-soft); padding: 12px; border-radius: 8px; border: 1px solid var(--line); font-size: 12.5px; margin-bottom: 24px;">
            <span style="color: var(--muted); display: block;">Active Learning Target</span>
            <strong style="color: var(--text); display: block; font-size: 14px; margin-top: 2px;">{profile.get("current_study_goal") or "Semester Success"}</strong>
            <span style="color: var(--muted); font-size: 11px; display: block; margin-top: 4px;">Exam Target Date: {profile.get("exam_date") or "Not configured"}</span>
        </div>
        """)
        st.markdown(target_box_payload, unsafe_allow_html=True)

        # AI Learning Insights Section
        st.markdown("<h3 style='font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.04em;'>Learning Insights</h3>", unsafe_allow_html=True)
        
        most_studied = analytics.get("performance", {}).get("most_studied_topic")
        best_topic = analytics.get("performance", {}).get("best_topic")

        if accuracy >= 75:
            InsightCard("Superb Quiz Accuracy", "Your average scores are looking strong. You are ready for exam repetitions.", "Keep it up!", "success")
        else:
            InsightCard("Recall Practice Recommended", "Try generating more flashcard decks or topic quizzes to boost retention.", "Focus on revision", "warning")

        if most_studied and most_studied != "None":
            clean_most_studied = " ".join(str(most_studied).split())
            if len(clean_most_studied) > 90:
                clean_most_studied = clean_most_studied[:87].strip() + "..."
            InsightCard("Topic Concentration", f"You have spent the most sessions reviewing '{clean_most_studied}' this week.", "", "info")

        # Recommended Topics Widget
        st.markdown("<h3 style='font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.04em;'>Recommended Revisions</h3>", unsafe_allow_html=True)
        
        weak_subjects = profile.get("weak_subjects")
        if weak_subjects:
            for sub in weak_subjects.split(",")[:2]:
                RecommendationCard(sub.strip(), "Weakness flagged in settings")
        else:
            if best_topic and best_topic != "None":
                RecommendationCard(best_topic, "Reinforce your strongest topic")
            else:
                RecommendationCard("Operating Systems", "Recommended baseline review topic")
