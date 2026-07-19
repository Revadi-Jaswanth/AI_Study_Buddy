import streamlit as st
from components.feature_card import render_feature_card


def clean_html(html_str):
    """Minifies HTML strings by stripping leading/trailing whitespace and removing comments to prevent Markdown code block formatting."""
    lines = []
    for line in html_str.split("\n"):
        line_clean = line.strip()
        if line_clean and not line_clean.startswith("<!--"):
            lines.append(line_clean)
    return " ".join(lines)


def render_hero_section():
    """Renders the left panel's typography header, glowing ambient shapes, and interactive mock KPI preview cards."""
    html_content = clean_html("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 28px;">
            <span style="font-size: 38px; display: inline-block; filter: drop-shadow(0 4px 12px rgba(99,102,241,0.25));">📚</span>
            <h1 style="font-size: 26px; font-weight: 700; margin: 0; background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.01em;">AI Study Buddy</h1>
        </div>
        
        <h2 style="font-size: 40px; font-weight: 800; line-height: 1.15; margin: 0 0 12px 0; color: var(--text); letter-spacing: -0.03em;">
            Learn Smarter.<br/>Learn Faster.
        </h2>
        <p style="font-size: 15px; color: var(--muted); line-height: 1.55; margin: 0 0 32px 0; font-weight: 400; max-width: 90%;">
            Your personalized AI-powered learning workspace built for students, developers, and lifelong learners.
        </p>
        
        <!-- Premium visual preview: Study Streak, AI Requests, Quiz Accuracy, Daily Goal cards -->
        <div class="auth-illustration-container" style="position: relative; padding: 24px; border-radius: 16px; background: rgba(255, 255, 255, 0.01); border: 1px solid var(--line); margin-bottom: 34px; overflow: visible;">
            <!-- Subtle moving light effect & blurred glow nodes -->
            <div style="position: absolute; width: 160px; height: 160px; border-radius: 50%; background: #6366f1; filter: blur(55px); opacity: 0.16; top: -30px; left: -20px; z-index: 0;"></div>
            <div style="position: absolute; width: 160px; height: 160px; border-radius: 50%; background: #10b981; filter: blur(55px); opacity: 0.12; bottom: -30px; right: -20px; z-index: 0;"></div>
            
            <div style="position: relative; z-index: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
                <!-- Streak Card -->
                <div style="background: var(--surface); border: 1px solid var(--line); padding: 14px; border-radius: 12px; box-shadow: var(--shadow); transform: rotate(-1.5deg);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 10px; text-transform: uppercase; font-weight: 700; color: var(--muted); letter-spacing: 0.05em;">Study Streak</span>
                        <span style="font-size: 16px;">🔥</span>
                    </div>
                    <div style="font-size: 20px; font-weight: 700; color: var(--text);">7 Days</div>
                    <span style="font-size: 10.5px; color: var(--accent-2); font-weight: 500;">✓ Weekly goal complete</span>
                </div>
                
                <!-- AI Requests -->
                <div style="background: var(--surface); border: 1px solid var(--line); padding: 14px; border-radius: 12px; box-shadow: var(--shadow); transform: rotate(1.2deg);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 10px; text-transform: uppercase; font-weight: 700; color: var(--muted); letter-spacing: 0.05em;">AI Requests</span>
                        <span style="font-size: 14px; color: var(--accent);">⚡</span>
                    </div>
                    <div style="font-size: 20px; font-weight: 700; color: var(--text);">142</div>
                    <span style="font-size: 10.5px; color: var(--muted);">This semester</span>
                </div>
                
                <!-- Quiz Accuracy -->
                <div style="background: var(--surface); border: 1px solid var(--line); padding: 14px; border-radius: 12px; box-shadow: var(--shadow); transform: rotate(1deg);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 10px; text-transform: uppercase; font-weight: 700; color: var(--muted); letter-spacing: 0.05em;">Quiz Accuracy</span>
                        <span style="font-size: 14px; color: var(--accent-3);">🎯</span>
                    </div>
                    <div style="font-size: 20px; font-weight: 700; color: var(--text);">88.4%</div>
                    <span style="font-size: 10.5px; color: var(--accent-2); font-weight: 500;">+2.4% vs last week</span>
                </div>

                <!-- Daily Goal -->
                <div style="background: var(--surface); border: 1px solid var(--line); padding: 14px; border-radius: 12px; box-shadow: var(--shadow); transform: rotate(-1deg);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 10px; text-transform: uppercase; font-weight: 700; color: var(--muted); letter-spacing: 0.05em;">Daily Goal</span>
                        <span style="font-size: 14px; color: var(--accent-2);">⏳</span>
                    </div>
                    <div style="font-size: 20px; font-weight: 700; color: var(--text);">2.5 Hours</div>
                    <span style="font-size: 10.5px; color: var(--muted);">Target: 3.0 Hours</span>
                </div>
            </div>
        </div>
    """)

    st.markdown(html_content, unsafe_allow_html=True)

    # Render floating feature cards below the illustration
    render_feature_card(
        title="AI Topic Explainer",
        description="Deconstruct complex technical concepts using adaptive explanation levels.",
        icon_name="sparkles"
    )
    render_feature_card(
        title="Smart Repetitive Flashcards",
        description="Verify recall progress using custom repetitions with no manual cards creation.",
        icon_name="brain"
    )
    render_feature_card(
        title="Interactive Quiz Generator",
        description="Test syllabus accuracy with customized questions generated from your study topics.",
        icon_name="graduation"
    )
    render_feature_card(
        title="Personalized Study Planner",
        description="Create calendar plans and subject breakdowns to track your exams preparation.",
        icon_name="book"
    )
    render_feature_card(
        title="Learning Analytics Dashboard",
        description="Track score averages, subject focus percentages, and study streaks.",
        icon_name="chart"
    )
