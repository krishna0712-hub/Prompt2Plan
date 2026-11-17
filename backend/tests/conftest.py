"""
conftest.py — Pytest configuration for Prompt2Plan tests.
"""
import os
import sys

# Ensure repository root is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Ensure local cache path is used for offline sandbox test runs
local_cache = os.path.join(root_dir, ".cache", "huggingface")
if os.path.isdir(local_cache):
    os.environ.setdefault("HF_HOME", local_cache)
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
