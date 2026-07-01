"""Pydantic schema validation at the API boundary."""
import pytest
from pydantic import ValidationError

from app.models.schemas import ChatRequest, ChatResponse, Intent


def test_chatrequest_rejects_empty_question():
    with pytest.raises(ValidationError):
        ChatRequest(question="")


def test_chatrequest_accepts_valid():
    r = ChatRequest(question="hello")
    assert r.question == "hello"
    assert r.session_id is None


def test_intent_enum_parsing():
    assert Intent("code") == Intent.CODE
    assert Intent("retrieval") == Intent.RETRIEVAL


def test_response_defaults():
    r = ChatResponse(answer="a", intent=Intent.RETRIEVAL)
    assert r.citations == []
    assert r.retries == 0
    assert r.artifact_path is None
