"""Code agent: fence extraction and the self-correcting retry loop.

The retry test uses a fake LLM that returns broken code first, then correct
code, and asserts the agent recovered after exactly one retry — a deterministic
demonstration of the self-correction loop against the real sandbox.
"""
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from app.graph import code_agent


def test_extract_code_strips_fences():
    assert code_agent._extract_code("```python\nx = 1\n```") == "x = 1"
    assert code_agent._extract_code("```\ny = 2\n```") == "y = 2"
    assert code_agent._extract_code("plain code") == "plain code"


def test_self_correcting_retry(monkeypatch):
    # 1st call → code that raises NameError; 2nd call → working code.
    responses = iter([
        "```python\nprint(undefined_var)\n```",
        "```python\nprint('recovered', 2 + 2)\n```",
    ])
    fake_llm = RunnableLambda(lambda _pv: AIMessage(content=next(responses)))
    monkeypatch.setattr(code_agent, "get_llm", lambda *a, **k: fake_llm)

    out = code_agent.run_code_agent({"question": "compute something", "context": []})

    assert out["retries"] == 1            # failed once, fixed on retry
    assert "recovered" in out["answer"]   # the corrected code's output
