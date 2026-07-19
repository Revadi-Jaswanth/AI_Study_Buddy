import time
from config import GEMINI_CONFIG
from utils.logging_config import get_logger

try:
    from google import genai
    from google.genai import errors as genai_errors
except ModuleNotFoundError:
    genai = None
    genai_errors = None


class GeminiAPIError(Exception):
    """Friendly error that can be shown safely in the Streamlit UI."""


logger = get_logger(__name__)
_client_singleton = None


def get_gemini_client():
    """Retrieve or initialize the reusable GenAI Client (singleton pattern)."""
    global _client_singleton

    if genai is None:
        logger.error("google-genai SDK is not installed.")
        raise GeminiAPIError(
            "google-genai is not installed. Run: pip install -r requirements.txt"
        )

    api_key = GEMINI_CONFIG.api_key
    if not api_key:
        logger.warning("Gemini API key is missing.")
        raise GeminiAPIError(
            "Gemini API key is missing. Please add GEMINI_API_KEY to your .env file and restart the app."
        )

    if _client_singleton is None:
        try:
            _client_singleton = genai.Client(api_key=api_key)
        except Exception as exc:
            logger.exception("Failed to initialize Google GenAI Client.")
            raise GeminiAPIError(
                "Could not initialize Google GenAI Client. Please check your configuration."
            ) from exc

    return _client_singleton


def generate_content(prompt):
    """Generate content using Gemini, with execution timing, error handling, and privacy logging."""
    client = get_gemini_client()
    model_name = GEMINI_CONFIG.model_name
    start_time = time.time()

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        if not response or not response.text:
            raise GeminiAPIError(
                "Gemini did not return any text. Please try again with a clearer input."
            )

        elapsed = time.time() - start_time
        logger.info(
            "Gemini request successful. Model: %s, Duration: %.2f sec, Timestamp: %s",
            model_name,
            elapsed,
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        )

        return response.text

    except genai_errors.APIError as exc:
        elapsed = time.time() - start_time
        status_code = exc.code
        logger.warning(
            "Gemini APIError failure: Status %s, Model: %s, Duration: %.2f sec",
            status_code,
            model_name,
            elapsed
        )

        if status_code == 429:
            raise GeminiAPIError(
                "Gemini API quota has been reached. Please wait and try again later."
            ) from exc
        elif status_code == 403:
            raise GeminiAPIError(
                "Gemini rejected the API key. Please check that your key is valid and has access enabled."
            ) from exc
        elif status_code == 401:
            raise GeminiAPIError(
                "Gemini could not authenticate this request. Please check your API key."
            ) from exc
        elif status_code in (500, 503, 504):
            raise GeminiAPIError(
                "Google Gemini servers are currently busy or down. Please try again in a few moments."
            ) from exc
        else:
            raise GeminiAPIError(
                f"Gemini API Error occurred (HTTP {status_code}). Please try again."
            ) from exc

    except Exception as exc:
        elapsed = time.time() - start_time
        logger.exception("Unexpected Gemini request failure.")

        exc_name = exc.__class__.__name__
        if "Timeout" in exc_name or "Connect" in exc_name or "ConnectionError" in exc_name:
            raise GeminiAPIError(
                "Gemini is temporarily unreachable due to a network connection timeout. Please check your connection."
            ) from exc

        raise GeminiAPIError(
            "Something went wrong while contacting Gemini. Please try again."
        ) from exc
