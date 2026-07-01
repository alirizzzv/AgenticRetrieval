"""Per-session conversation memory."""
from app.memory import SessionMemory


def test_add_and_trim_to_max():
    m = SessionMemory(max_turns=2)
    m.add("q1", "a1", "retrieval")
    m.add("q2", "a2", "code")
    m.add("q3", "a3", "retrieval")
    assert len(m.turns) == 2
    assert m.turns[0].question == "q2"   # oldest dropped


def test_empty_memory_has_no_prompt_block():
    assert SessionMemory().as_prompt_block() is None


def test_prompt_block_includes_prior_turns():
    m = SessionMemory()
    m.add("What is revenue?", "It was $425M", "retrieval")
    block = m.as_prompt_block()
    assert "What is revenue?" in block
    assert "$425M" in block
