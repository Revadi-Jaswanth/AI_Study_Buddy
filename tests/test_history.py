from database import history


def test_save_history_record_uses_insert(monkeypatch):
    captured = {}

    def fake_insert(query, params=None):
        captured["query"] = query
        captured["params"] = params
        return 7

    monkeypatch.setattr(
        history,
        "insert",
        fake_insert,
    )

    record_id = history.save_history_record(
        1,
        "Topic Explainer",
        "DBMS",
        "Generated response",
    )

    assert record_id == 7
    assert "INSERT INTO history" in captured["query"]
    assert captured["params"] == (
        1,
        "Topic Explainer",
        "DBMS",
        "Generated response",
    )
