"""Test 2: idempotency — a second formatting pass equals the first."""

from __future__ import annotations

import mdformat

from tests.conftest import fixture_sources


def test_fixtures_idempotent() -> None:
    for name, source in fixture_sources():
        first = mdformat.text(source, extensions={"sembr"})
        second = mdformat.text(first, extensions={"sembr"})
        assert first == second, f"not idempotent for fixture {name!r}"


def test_idempotent_with_clauses() -> None:
    src = "Alpha, then beta, then gamma. Second sentence here, with a clause.\n"
    opts = {"break_clauses": True}
    first = mdformat.text(src, extensions={"sembr"}, options={"plugin": {"sembr": opts}})
    second = mdformat.text(first, extensions={"sembr"}, options={"plugin": {"sembr": opts}})
    assert first == second
