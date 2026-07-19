import streamlit as st
import time


def clean_html(html_str: str) -> str:
    """Removes indentation and newlines to prevent Streamlit from interpreting HTML as preformatted markdown code blocks."""
    return " ".join([line.strip() for line in html_str.split("\n") if line.strip()])


def render_success_animation(user_name: str):
    """Renders a premium sequential onboarding success log before taking the user to the dashboard."""
    placeholder = st.empty()
    
    logs = [
        ("✓ Account Created Successfully", "green"),
        ("Creating your personalized AI workspace...", "blue"),
        ("Preparing your dashboard...", "blue"),
        ("Loading your profile...", "blue"),
        ("Loading AI preferences...", "blue")
    ]
    
    combined_log_html = ""
    for message, color in logs:
        text_color = "var(--accent-2)" if color == "green" else "var(--muted)"
        glow_dot = """<span class="pulse-dot" style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: var(--accent); margin-right: 8px;"></span>""" if color == "blue" else ""
        
        combined_log_html += f"""
        <div style="display: flex; align-items: center; gap: 4px; font-size: 13px; color: {text_color}; margin-bottom: 8px;">
            {glow_dot}
            <span>{message}</span>
        </div>
        """
        
        html_payload = clean_html(f"""
        <div class="auth-wrapper" style="text-align: left; padding: 2.5rem; max-width: 480px; margin: 40px auto; border-radius: 16px; border: 1px solid var(--line); background: var(--surface);">
            <h3 style="font-size: 20px; font-weight: 600; color: var(--text); margin: 0 0 8px 0;">Setting up workspace</h3>
            <p style="font-size: 13px; color: var(--muted); margin: 0 0 24px 0;">Please wait while we initialize your study assistant, {user_name}.</p>
            <div style="margin-bottom: 24px;">
                {combined_log_html}
            </div>
            <div class="loading-bar-wrapper" style="width: 100%; height: 4px; background: var(--surface-soft); border-radius: 2px; overflow: hidden; position: relative;">
                <div class="loading-bar-active" style="width: 70%; height: 100%; background: var(--accent-gradient); border-radius: 2px; position: absolute; left: 0; top: 0; animation: loadingPulse 1.2s infinite ease-in-out;"></div>
            </div>
            <style>
                @keyframes loadingPulse {{
                    0% {{ left: -100%; width: 50%; }}
                    50% {{ left: 25%; width: 60%; }}
                    100% {{ left: 100%; width: 50%; }}
                }}
            </style>
        </div>
        """)
        
        placeholder.markdown(html_payload, unsafe_allow_html=True)
        time.sleep(0.4)
