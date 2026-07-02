"""Tests 3, 4, 5: sentence breaks, abbreviation guard, min-char threshold."""

from __future__ import annotations

import mdformat

from mdformat_sembr._sembr import insert_breaks


def _fmt(src: str, **plugin_opts: object) -> str:
    options = {"plugin": {"sembr": plugin_opts}} if plugin_opts else {}
    return mdformat.text(src, extensions={"sembr"}, options=options)


# --- Test 3: sentence breaks ------------------------------------------------

def test_multi_sentence_one_per_line() -> None:
    src = "This is one sentence. This is another sentence. And a third here.\n"
    out = _fmt(src)
    assert out == (
        "This is one sentence.\n"
        "This is another sentence.\n"
        "And a third here.\n"
    )


def test_interrobang_runs_break() -> None:
    # "Really?!" is short, so use a low threshold to isolate boundary detection.
    assert insert_breaks("Really?! I did not know that at all.", min_chars=5) == (
        "Really?!\nI did not know that at all."
    )


def test_single_sentence_unchanged() -> None:
    assert insert_breaks("Just one single sentence here.") == (
        "Just one single sentence here."
    )


# --- Test 4: abbreviation guard ---------------------------------------------

def test_abbreviation_eg_no_break() -> None:
    text = "Use a tool, e.g. the reference parser, for this task."
    assert "\n" not in insert_breaks(text)


def test_abbreviation_dr_no_break() -> None:
    text = "We asked Dr. Smith about the results of the experiment."
    assert "\n" not in insert_breaks(text)


def test_abbreviation_etc_no_break() -> None:
    text = "Bring pens, paper, etc. and meet us at the front entrance."
    assert "\n" not in insert_breaks(text)


def test_real_sentence_end_still_breaks_after_abbrev_clause() -> None:
    text = "See the guide, e.g. chapter two here. Then start the real work now."
    assert insert_breaks(text) == (
        "See the guide, e.g. chapter two here.\nThen start the real work now."
    )


# --- Test 5: min-char threshold ---------------------------------------------

def test_short_fragments_stay_joined() -> None:
    # Each fragment ("Yes.", "No.", "Go.") is under the default 15-char minimum.
    assert insert_breaks("Yes. No. Go.") == "Yes. No. Go."


def test_threshold_is_configurable() -> None:
    text = "One two three. Four five six seven."
    # Default 15 keeps "One two three." (14 chars) joined.
    assert insert_breaks(text, min_chars=15) == text
    # A low threshold allows the break.
    assert insert_breaks(text, min_chars=5) == "One two three.\nFour five six seven."


# --- Closing-punctuation regression tests -----------------------------------
# These only apply when closing_punct=True (American-English punctuation style).

def test_closing_quote_stays_on_first_line() -> None:
    # Regression: closing `"` must not be orphaned on the next line.
    text = 'He said "goodbye." The next sentence follows here now.'
    out = insert_breaks(text, min_chars=5, closing_punct=True)
    lines = out.splitlines()
    assert lines[0].endswith('"'), f"closing quote orphaned: {lines!r}"
    assert lines[1][0].isupper()


def test_closing_quote_no_break_by_default() -> None:
    # Without closing_punct, a sentence ending inside quotes is not broken.
    text = 'He said "goodbye." The next sentence follows here now.'
    out = insert_breaks(text, min_chars=5)
    assert "\n" not in out


def test_closing_single_quote_stays_on_first_line() -> None:
    text = "She replied 'of course.' Then she walked away from them."
    out = insert_breaks(text, min_chars=5, closing_punct=True)
    lines = out.splitlines()
    assert lines[0].endswith("'"), f"closing single-quote orphaned: {lines!r}"


def test_closing_paren_stays_on_first_line() -> None:
    text = "See the appendix (p. 42.) The proof follows from that result."
    out = insert_breaks(text, min_chars=5, closing_punct=True)
    lines = out.splitlines()
    assert lines[0].endswith(")"), f"closing paren orphaned: {lines!r}"


def test_closing_bracket_stays_on_first_line() -> None:
    text = "The author confirmed [sic.] The record stands as written here."
    out = insert_breaks(text, min_chars=5, closing_punct=True)
    lines = out.splitlines()
    assert lines[0].endswith("]"), f"closing bracket orphaned: {lines!r}"
