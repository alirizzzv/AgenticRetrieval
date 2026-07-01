"""Portable fix for a Chainlit ContextVar bug (Chainlit 2.3.0 on Python 3.9).

Chainlit's ``local_steps`` ContextVar is created without a default and set
imperatively at import time (``local_steps.set(None)``). In any async worker
context created before that import runs, ``local_steps.get()`` raises
``LookupError`` — which breaks every message handler with a traceback.

Newer Chainlit releases fixed this by giving the ContextVar a default, but those
require Python >= 3.10; this project is pinned to Chainlit 2.3.0 on Python 3.9.
So we apply the same fix at runtime: rebind ``local_steps`` to a ContextVar that
carries ``default=None`` in every module that references it.

Importing this module runs the patch. It is idempotent and a harmless no-op on
Chainlit versions that already ship the default.
"""
import importlib
from contextvars import ContextVar

_MODULES = ("chainlit.context", "chainlit.message", "chainlit.step")


def apply() -> None:
    try:
        ctx = importlib.import_module("chainlit.context")
    except Exception:
        return

    # Preserve any value already set, then rebind to a default-carrying var.
    try:
        current = ctx.local_steps.get(None)
    except Exception:
        current = None

    patched: "ContextVar" = ContextVar("local_steps", default=None)
    if current is not None:
        patched.set(current)

    for mod_name in _MODULES:
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "local_steps"):
                mod.local_steps = patched
        except Exception:
            pass


apply()
