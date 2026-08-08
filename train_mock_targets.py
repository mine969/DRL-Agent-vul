"""
DEPRECATED -- this root-level copy is stale (pre-dates the fast in-process
transport, crash-safe checkpointing, real logging, and the 3,000-episode
default). The real, actively-maintained trainer is training/train_mock_targets.py.

This file could not be deleted automatically (filesystem lock in the build
environment) -- delete it manually once that clears:
    del train_mock_targets.py
"""

raise SystemExit(
    "train_mock_targets.py (root) is deprecated and stale -- use the real one:\n"
    "  python training/train_mock_targets.py\n"
    "This file is safe to delete; it's kept only as a pointer since it couldn't "
    "be removed automatically."
)
