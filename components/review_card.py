import streamlit as st
import textwrap


def render_review_card(name: str, email: str, college: str, branch: str, year_label: str, style: str, goal: str):
    """Renders the Step 3 verification summary block with clean key-value structures."""
    st.markdown(
        textwrap.dedent(f"""
        <div style='background: var(--surface-soft); padding: 18px; border-radius: 12px; border: 1px solid var(--line); margin-bottom: 24px; font-size: 13.5px; line-height: 1.65;'>
            <div style='display: flex; justify-content: space-between; border-bottom: 1px solid var(--line); padding-bottom: 8px; margin-bottom: 8px;'>
                <span style='color: var(--muted);'>Full Name</span>
                <strong style='color: var(--text);'>{name}</strong>
            </div>
            <div style='display: flex; justify-content: space-between; border-bottom: 1px solid var(--line); padding-bottom: 8px; margin-bottom: 8px;'>
                <span style='color: var(--muted);'>Email Address</span>
                <strong style='color: var(--text);'>{email}</strong>
            </div>
            <div style='display: flex; justify-content: space-between; border-bottom: 1px solid var(--line); padding-bottom: 8px; margin-bottom: 8px;'>
                <span style='color: var(--muted);'>Institution</span>
                <strong style='color: var(--text);'>{college}</strong>
            </div>
            <div style='display: flex; justify-content: space-between; border-bottom: 1px solid var(--line); padding-bottom: 8px; margin-bottom: 8px;'>
                <span style='color: var(--muted);'>Department</span>
                <strong style='color: var(--text);'>{branch}</strong>
            </div>
            <div style='display: flex; justify-content: space-between; border-bottom: 1px solid var(--line); padding-bottom: 8px; margin-bottom: 8px;'>
                <span style='color: var(--muted);'>Academic level</span>
                <strong style='color: var(--text);'>{year_label}</strong>
            </div>
            <div style='display: flex; justify-content: space-between; border-bottom: 1px solid var(--line); padding-bottom: 8px; margin-bottom: 8px;'>
                <span style='color: var(--muted);'>Preferred Learning Style</span>
                <strong style='color: var(--text);'>{style}</strong>
            </div>
            <div style='display: flex; justify-content: space-between;'>
                <span style='color: var(--muted);'>Study Goal</span>
                <strong style='color: var(--text);'>{goal}</strong>
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )
