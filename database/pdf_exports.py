from database.queries import insert


def save_pdf_export(user_id, feature_name, topic, file_name):
    return insert(
        """
        INSERT INTO pdf_exports
        (user_id, feature_name, topic, file_name)
        VALUES (%s, %s, %s, %s)
        """,
        (
            user_id,
            feature_name,
            topic,
            file_name
        )
    )
