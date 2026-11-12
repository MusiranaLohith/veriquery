
import pytest

from veriquery.llm.config import get_api_key


def test_get_gemini_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")

    assert get_api_key("gemini") == "test-gemini-key"


def test_get_groq_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")

    assert get_api_key("groq") == "test-groq-key"


def test_missing_gemini_api_key_raises_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
        get_api_key("gemini")


def test_missing_groq_api_key_raises_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GROQ_API_KEY is missing"):
        get_api_key("groq")
