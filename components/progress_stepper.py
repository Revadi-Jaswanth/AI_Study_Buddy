import streamlit as st
import textwrap


def render_progress_stepper(current_step: int):
    """Renders a premium progress indicator showing step milestones (Personal -> Academic -> Review) with precise bounding lines."""
    steps = [
        (1, "Personal", "Basic Details"),
        (2, "Academic", "Study Profile"),
        (3, "Review", "Confirmation")
    ]

    check_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check"><path d="M20 6 9 17l-5-5"/></svg>"""

    stepper_html = ""
    for step_num, title, desc in steps:
        circle_style = ""
        label_style = ""
        status_class = ""

        if current_step == step_num:
            status_class = "active"
            circle_style = "background: var(--accent-gradient); border-color: var(--accent); color: #ffffff; box-shadow: 0 0 12px rgba(99, 102, 241, 0.35);"
            label_style = "color: var(--text); font-weight: 600;"
        elif current_step > step_num:
            status_class = "completed"
            circle_style = "background: var(--accent-2); border-color: var(--accent-2); color: #ffffff;"
            label_style = "color: var(--text);"
        else:
            status_class = "pending"
            circle_style = "background-color: var(--surface-soft); border-color: var(--line); color: var(--muted);"
            label_style = "color: var(--muted);"

        step_content = check_svg if current_step > step_num else str(step_num)

        stepper_html += f"""
        <div class="step-node {status_class}" style="display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; text-align: center; position: relative; z-index: 1;">
            <div class="step-circle" style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid var(--line); display: grid; place-items: center; font-size: 11.5px; font-weight: 600; transition: all 0.3s ease; {circle_style}">
                {step_content}
            </div>
            <span class="step-label" style="font-size: 11px; {label_style}">{title}</span>
        </div>
        """

    # Active bar endpoint boundary calculations (bounds line between 15% and 85%)
    right_pct = "85%"
    if current_step == 2:
        right_pct = "50%"
    elif current_step >= 3:
        right_pct = "15%"

    st.markdown(
        textwrap.dedent(f"""
        <div class="stepper-wrapper" style="position: relative; display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; padding: 0 10px;">
            <div class="stepper-line" style="position: absolute; top: 15px; left: 15%; right: 15%; height: 2px; background-color: var(--line); z-index: 0;"></div>
            <div class="stepper-line-active" style="position: absolute; top: 15px; left: 15%; right: {right_pct}; height: 2px; background: var(--accent-gradient); z-index: 0; transition: right 0.3s ease;"></div>
            {stepper_html}
        </div>
        """),
        unsafe_allow_html=True
    )
