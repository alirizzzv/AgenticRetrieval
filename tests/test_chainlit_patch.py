"""Regression test for the Chainlit ContextVar fix (app/chainlit_patch.py).

Without the patch, `local_steps.get()` raises LookupError in any context where
it was never set — which is every server worker context, breaking chat. After
the patch, it returns None safely in a fresh context.
"""
import contextvars
import importlib


def test_local_steps_safe_in_fresh_context():
    import chainlit  # noqa: F401  — load the modules first
    import app.chainlit_patch  # noqa: F401  — apply the fix

    for name in ("chainlit.context", "chainlit.message", "chainlit.step"):
        mod = importlib.import_module(name)
        # Must not raise LookupError in a brand-new (empty) context.
        assert contextvars.Context().run(mod.local_steps.get) is None
