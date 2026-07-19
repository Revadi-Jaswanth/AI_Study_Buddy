from database.history import get_recent_history, save_history_record


def save_history(feature, content):
    return save_history_record(
        feature,
        "",
        content
    )


def load_history():
    rows = get_recent_history(
        20
    )

    return [
        (
            row["feature_name"],
            row["ai_response"]
        )
        for row in rows
    ]
