"""Unified test harness for the study planner project."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


def main() -> int:
    """Run all tests in the tests directory."""
    project_root = Path(__file__).resolve().parents[1]
    return pytest.main([str(project_root / "tests"), "-q"])


if __name__ == "__main__":
    raise SystemExit(main())
