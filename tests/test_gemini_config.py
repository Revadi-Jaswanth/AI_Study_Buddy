import pytest
from unittest.mock import patch, MagicMock
from modules.gemini_config import get_gemini_client, GeminiAPIError, generate_content
from google.genai import errors as genai_errors


def test_get_gemini_client_missing_key():
    with patch("modules.gemini_config.GEMINI_CONFIG") as mock_config:
        mock_config.api_key = None
        with pytest.raises(GeminiAPIError) as exc_info:
            # Force singleton cleanup to trigger initialization logic
            with patch("modules.gemini_config._client_singleton", None):
                get_gemini_client()
        assert "API key is missing" in str(exc_info.value)


def test_generate_content_api_error_mapping_quota():
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = genai_errors.APIError(
        code=429,
        response_json={"message": "Quota exceeded"}
    )

    with patch("modules.gemini_config.get_gemini_client", return_value=mock_client):
        with pytest.raises(GeminiAPIError) as exc_info:
            generate_content("Python topic")
        assert "quota" in str(exc_info.value).lower()


def test_generate_content_api_error_mapping_permission():
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = genai_errors.APIError(
        code=403,
        response_json={"message": "Forbidden"}
    )

    with patch("modules.gemini_config.get_gemini_client", return_value=mock_client):
        with pytest.raises(GeminiAPIError) as exc_info:
            generate_content("Python topic")
        assert "rejected the api key" in str(exc_info.value).lower()
