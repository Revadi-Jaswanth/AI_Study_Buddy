import streamlit as st


def render_glass_card(content_renderer):
    """Wraps authentication forms inside a premium glassmorphism card container."""
    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
    content_renderer()
    st.markdown('</div>', unsafe_allow_html=True)
