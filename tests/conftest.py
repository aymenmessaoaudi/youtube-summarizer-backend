import pytest
from app import app as flask_app, limiter
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def reset_limiter():
    """Reset the rate limiter between tests."""
    limiter.reset()

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "RATELIMIT_ENABLED": False  # Désactive le rate limiting pendant les tests
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_openai():
    mock = MagicMock()
    mock.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"summary": "Test summary"}'
                )
            )
        ]
    )
    return mock

@pytest.fixture
def mock_transcript():
    return [
        {
            "text": "Hello world",
            "start": 0.0,
            "duration": 2.5
        },
        {
            "text": "This is a test",
            "start": 2.5,
            "duration": 2.0
        }
    ]

@pytest.fixture
def mock_youtube_transcript_api(mock_transcript):
    def get_transcript(*args, **kwargs):
        return mock_transcript
    return get_transcript