"""Shared fixtures and helpers for the mdformat-sembr test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def fixture_sources() -> list[tuple[str, str]]:
    """Return (name, source_text) for every ``*.md`` file under fixtures/."""
    return [(p.name, p.read_text(encoding="utf-8")) for p in sorted(FIXTURES_DIR.glob("*.md"))]


@pytest.fixture(params=fixture_sources(), ids=lambda pair: pair[0])
def fixture(request: pytest.FixtureRequest) -> tuple[str, str]:
    """Parametrized fixture yielding (name, source) for each fixture file."""
    return request.param
