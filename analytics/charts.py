try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    go = None


class ChartError(Exception):
    """Raised when chart rendering dependencies are unavailable."""


COLORS = [
    "#6366f1",  # Indigo
    "#10b981",  # Emerald
    "#f59e0b",  # Amber
    "#f43f5e",  # Rose
    "#8b5cf6",  # Violet
    "#06b6d4",  # Cyan
]


def _require_plotly():
    if go is None:
        raise ChartError(
            "Plotly is not installed. Run: pip install plotly"
        )


def feature_usage_bar(rows):
    _require_plotly()
    figure = go.Figure(
        data=[
            go.Bar(
                x=[row["feature"] for row in rows],
                y=[row["usage_count"] for row in rows],
                marker_color=COLORS,
                hovertemplate="%{x}<br>Requests: %{y}<extra></extra>",
            )
        ]
    )
    return _style_figure(
        figure,
        "Feature Usage"
    )


def weekly_activity_line(rows):
    _require_plotly()
    figure = go.Figure(
        data=[
            go.Scatter(
                x=[row["activity_date"] for row in rows],
                y=[row["request_count"] for row in rows],
                mode="lines+markers",
                line={
                    "color": "#6366f1",
                    "width": 3,
                },
                hovertemplate="%{x}<br>Requests: %{y}<extra></extra>",
            )
        ]
    )
    return _style_figure(
        figure,
        "Weekly Activity"
    )


def quiz_performance_line(rows):
    _require_plotly()
    figure = go.Figure(
        data=[
            go.Scatter(
                x=[row["created_at"] for row in rows],
                y=[row["percentage"] for row in rows],
                text=[row["topic"] for row in rows],
                mode="lines+markers",
                line={
                    "color": "#10b981",
                    "width": 3,
                },
                hovertemplate="%{text}<br>Score: %{y}%<extra></extra>",
            )
        ]
    )
    return _style_figure(
        figure,
        "Quiz Performance"
    )


def study_time_pie(rows):
    _require_plotly()
    figure = go.Figure(
        data=[
            go.Pie(
                labels=[row["feature"] for row in rows],
                values=[row["study_time_seconds"] for row in rows],
                hole=0.35,
                marker={
                    "colors": COLORS,
                },
                hovertemplate="%{label}<br>Seconds: %{value}<extra></extra>",
            )
        ]
    )
    return _style_figure(
        figure,
        "Study Time"
    )


def topic_distribution_donut(rows):
    _require_plotly()
    figure = go.Figure(
        data=[
            go.Pie(
                labels=[row["topic"] for row in rows],
                values=[row["topic_count"] for row in rows],
                hole=0.55,
                marker={
                    "colors": COLORS,
                },
                hovertemplate="%{label}<br>Count: %{value}<extra></extra>",
            )
        ]
    )
    return _style_figure(
        figure,
        "Topic Distribution"
    )


def quiz_difficulty_bar(rows):
    _require_plotly()
    difficulty_map = {
        row["difficulty"]: row["attempt_count"]
        for row in rows
    }
    figure = go.Figure()

    for index, difficulty in enumerate(["Easy", "Medium", "Hard"]):
        figure.add_trace(
            go.Bar(
                x=["Quiz Difficulty"],
                y=[difficulty_map.get(difficulty, 0)],
                name=difficulty,
                marker_color=COLORS[index],
                hovertemplate=f"{difficulty}<br>Attempts: %{{y}}<extra></extra>",
            )
        )

    figure.update_layout(
        barmode="stack"
    )
    return _style_figure(
        figure,
        "Quiz Difficulty"
    )


def _style_figure(figure, title):
    import streamlit as st

    theme = st.session_state.get("theme", "dark")
    if theme == "light":
        font_color = "#09090b"
        grid_color = "rgba(9, 9, 11, 0.06)"
        hover_bg = "#ffffff"
    else:
        font_color = "#f4f4f5"
        grid_color = "rgba(255, 255, 255, 0.08)"
        hover_bg = "#18181b"

    figure.update_layout(
        title={
            "text": title,
            "font": {
                "size": 15,
                "weight": "bold"
            }
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "color": font_color,
            "family": "Inter, sans-serif",
        },
        margin={
            "l": 16,
            "r": 16,
            "t": 48,
            "b": 32,
        },
        hoverlabel={
            "bgcolor": hover_bg,
            "font_size": 12,
            "font_color": font_color,
        },
        legend={
            "font": {
                "size": 11
            }
        }
    )
    figure.update_xaxes(
        gridcolor=grid_color,
        zerolinecolor=grid_color,
    )
    figure.update_yaxes(
        gridcolor=grid_color,
        zerolinecolor=grid_color,
    )

    return figure
