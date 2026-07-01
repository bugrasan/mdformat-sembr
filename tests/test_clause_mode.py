"""Test 7: Iteration-2 clause breaks are off by default and opt-in."""

from __future__ import annotations

import mdformat

from mdformat_sembr._sembr import insert_breaks


def test_clauses_off_by_default() -> None:
    text = "First clause here, second clause follows, and a third clause too."
    # No sentence terminator and clauses disabled -> single line.
    assert "\n" not in insert_breaks(text)


def test_clauses_break_when_enabled() -> None:
    text = "First clause here, second clause follows, and a third clause too."
    out = insert_breaks(text, break_clauses=True)
    assert out == (
        "First clause here,\n"
        "second clause follows,\n"
        "and a third clause too."
    )


def test_clause_respects_min_chars() -> None:
    text = "A, b, this segment is definitely long enough to break here."
    # "A," and "b," are under threshold; only the long segment can break.
    out = insert_breaks(text, break_clauses=True, min_chars=15)
    assert out.startswith("A, b, this segment is definitely long enough to break here.")


def test_clause_chars_configurable() -> None:
    text = "One long segment here; another long segment there for testing."
    # Only semicolon in the set.
    out = insert_breaks(text, break_clauses=True, clause_chars=";", min_chars=5)
    assert out == "One long segment here;\nanother long segment there for testing."


def test_clause_mode_via_api_options() -> None:
    src = "One long clause segment, another long clause segment follows here.\n"
    out = mdformat.text(
        src,
        extensions={"sembr"},
        options={"plugin": {"sembr": {"break_clauses": True}}},
    )
    assert out == (
        "One long clause segment,\n"
        "another long clause segment follows here.\n"
    )
