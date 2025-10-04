from __future__ import annotations

from typing import Dict


def classify(message: str) -> str:
    m = message or ""
    if "ZeroDivisionError" in m:
        return "ZeroDivision"
    if "ImportError" in m or "ModuleNotFoundError" in m:
        return "ImportError"
    if "NameError" in m:
        return "NameError"
    if "AttributeError" in m:
        return "AttributeError"
    if "AssertionError" in m or "assert" in m:
        return "Assertion"
    return "Unknown"

