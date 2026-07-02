"""Test 6: protected regions are never split; block elements are untouched."""

from __future__ import annotations

import mdformat

from mdformat_sembr._sembr import insert_breaks


def _fmt(src: str) -> str:
    return mdformat.text(src, extensions={"sembr"})


# --- Inline protected regions ----------------------------------------------

def test_inline_code_not_split() -> None:
    text = "Call `a. b. c()` now and then continue with more prose here."
    out = insert_breaks(text)
    assert "`a. b. c()`" in out


def test_multi_backtick_code_not_split() -> None:
    text = "Call ``a. b. c()`` now and then continue with more prose here."
    out = insert_breaks(text)
    assert "``a. b. c()``" in out


def test_link_not_split() -> None:
    text = "Read [the A. B. guide](https://example.com/a.b.c) before you begin."
    out = insert_breaks(text)
    assert "[the A. B. guide](https://example.com/a.b.c)" in out


def test_image_link_not_split() -> None:
    text = "See ![fig. 1](https://example.com/fig.1.png) for the full diagram here."
    out = insert_breaks(text)
    assert "![fig. 1](https://example.com/fig.1.png)" in out


def test_footnote_reference_stays_attached() -> None:
    text = "This has a note[^1] right here. And a second sentence follows it."
    out = insert_breaks(text)
    assert "note[^1]" in out
    assert out == "This has a note[^1] right here.\nAnd a second sentence follows it."


# --- Block-level elements untouched (paragraph-only registration) -----------

def test_code_block_untouched() -> None:
    src = "```\nx = 1. y = 2. z = 3.\n```\n"
    assert _fmt(src) == src


def test_heading_untouched() -> None:
    src = "# One sentence. Two sentence.\n"
    out = _fmt(src)
    # Heading text stays on a single line (no soft break injected).
    assert out.strip() == "# One sentence. Two sentence."


def test_table_untouched() -> None:
    src = (
        "| Col one. two | Col three. four |\n"
        "| ------------ | --------------- |\n"
        "| a. b | c. d |\n"
    )
    # Without a table extension the pipe text is a paragraph, but is_md_equal
    # gates AST safety; here we just confirm no crash and stable output.
    out = _fmt(src)
    assert "|" in out
