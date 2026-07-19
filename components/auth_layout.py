import streamlit as st


def render_auth_layout(left_renderer, right_renderer):
    """Establishes the split column grid layout (45% left, 55% right) without any empty wrapping divs."""
    col_left, col_right = st.columns([4.5, 5.5], gap="large")

    with col_left:
        left_renderer()

    with col_right:
        right_renderer()
