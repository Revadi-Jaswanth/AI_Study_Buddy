import streamlit as st
import textwrap

ICONS = {
    "sparkles": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sparkles"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"/><path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5.5Z"/><path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1Z"/></svg>""",
    "brain": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-brain"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M12 5v14Z"/><path d="M12 9h4Z"/><path d="M12 13h-4Z"/></svg>""",
    "book": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-open"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 1 3-3h7z"/></svg>""",
    "graduation": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-graduation-cap"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.91a2 2 0 0 0 1.66 0z"/><path d="M6 18.8v-4L2 13v6a1 1 0 0 0 1 1h3Z"/><path d="M21.4 10.9v4a2 2 0 0 1-2 2h-3v2.2c0 .4-.3.8-.8.8h-4.8c-.5 0-.8-.4-.8-.8V16.9"/></svg>""",
    "building": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-building-2"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 18H4a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h2Z"/><path d="M18 18h2a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2h-2Z"/><path d="M10 6h4Z"/><path d="M10 10h4Z"/><path d="M10 14h4Z"/><path d="M10 18h4Z"/></svg>""",
    "chart": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-spline"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>""",
    "check": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check"><path d="M20 6 9 17l-5-5"/></svg>"""
}


def render_feature_card(title: str, description: str, icon_name: str):
    """Renders a single premium floating feature card with Lucide vector inline SVG."""
    icon_svg = ICONS.get(icon_name, ICONS["check"])
    
    st.markdown(
        textwrap.dedent(f"""
        <div class="auth-feature-row" style="display: flex; align-items: flex-start; gap: 14px; margin-bottom: 18px; padding: 8px; border-radius: 8px; transition: all 0.2s ease;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 8px; background: rgba(99, 102, 241, 0.1); color: var(--accent); flex-shrink: 0; margin-top: 2px; box-shadow: 0 2px 8px rgba(99, 102, 241, 0.05);">
                {icon_svg}
            </span>
            <div>
                <strong style="display: block; font-size: 14px; color: var(--text); font-weight: 600;">{title}</strong>
                <span style="font-size: 12.5px; color: var(--muted); line-height: 1.4; display: block; margin-top: 2px;">{description}</span>
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )
