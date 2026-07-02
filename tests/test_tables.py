"""Tests for table preservation — these currently FAIL (bug: table parsed as paragraph).

Root cause: markdown-it's table rule is disabled; tables fall through to the
paragraph postprocessor where ``_collapse_whitespace`` destroys row-separator
newlines and ``_apply_breaks`` may inject ``\\n`` inside a cell.
"""

from __future__ import annotations

import mdformat


def _fmt(src: str) -> str:
    return mdformat.text(src, extensions={"sembr"})


# ---------------------------------------------------------------------------
# Basic structure preservation
# ---------------------------------------------------------------------------

TABLE_SIMPLE = (
    "| A | B |\n"
    "| --- | --- |\n"
    "| one | two |\n"
)

TABLE_WITH_SENTENCES = (
    "| Option | Meaning |\n"
    "| --- | --- |\n"
    "| `min_chars` | Minimum length of the segment before a break is allowed. |\n"
    "| `break_clauses` | Enable clause-level breaks (SemBr \"SHOULD\"). Off by default. |\n"
)

TABLE_FROM_README = (
    "| Option | Type | Default | Meaning |\n"
    "| --------------- | ----------- | --------- | -------------------------------------------------------------- |\n"
    "| `min_chars` | int | `15` | Minimum length of the segment before a break is allowed. |\n"
    "| `abbreviations` | list[str] | see below | Tokens after which no sentence break is inserted. |\n"
    "| `break_clauses` | bool | `false` | Enable clause-level breaks (SemBr \"SHOULD\"). Off by default. |\n"
    "| `clause_chars` | str | `\",;:—\"` | Clause punctuation set (only used when `break_clauses` true). |\n"
)


def test_table_row_count_preserved() -> None:
    """Each table row must remain on its own line — no rows collapsed."""
    out = _fmt(TABLE_SIMPLE)
    # Input has 3 rows; output must still have 3 pipe-prefixed lines.
    pipe_lines = [ln for ln in out.splitlines() if ln.lstrip().startswith("|")]
    assert len(pipe_lines) == 3, (
        f"Expected 3 table rows, got {len(pipe_lines)}:\n{out!r}"
    )


def test_table_separator_row_preserved() -> None:
    """The ``| --- |`` alignment row must be on its own line."""
    out = _fmt(TABLE_SIMPLE)
    # The separator must appear as a standalone line, not collapsed into a single-line soup
    lines = out.splitlines()
    assert any(ln.strip() == "| --- | --- |" for ln in lines), (
        f"Separator row missing or not on its own line:\n{out!r}"
    )


def test_no_newline_injected_inside_cell() -> None:
    """No ``\\n`` must appear mid-row (inside a cell)."""
    out = _fmt(TABLE_WITH_SENTENCES)
    for line in out.splitlines():
        if line.lstrip().startswith("|") and line.rstrip().endswith("|"):
            # A well-formed table row — must not contain embedded newlines
            # (this can't happen on a single line, so verify row integrity instead)
            assert "|" in line, f"Malformed table row: {line!r}"
    # More directly: count rows — if a newline was injected inside a cell the
    # row count increases beyond the original 4 lines.
    pipe_lines = [ln for ln in out.splitlines() if ln.lstrip().startswith("|")]
    assert len(pipe_lines) == 4, (
        f"Expected 4 table rows, got {len(pipe_lines)} — a cell was broken:\n{out!r}"
    )


def test_table_structure_identical_to_base_mdformat() -> None:
    """sembr must produce the same table structure as plain mdformat."""
    import mdformat as _mdf

    plain = _mdf.text(TABLE_FROM_README)
    with_sembr = _fmt(TABLE_FROM_README)

    plain_rows = [ln for ln in plain.splitlines() if ln.lstrip().startswith("|")]
    sembr_rows = [ln for ln in with_sembr.splitlines() if ln.lstrip().startswith("|")]

    assert len(plain_rows) == len(sembr_rows), (
        f"Row count differs: plain={len(plain_rows)}, sembr={len(sembr_rows)}\n"
        f"plain:\n{plain}\nsembr:\n{with_sembr}"
    )


def test_table_idempotent() -> None:
    """A second sembr pass on a table must equal the first pass AND be valid."""
    # First confirm the table is not destroyed (this is the real bug assertion)
    first = _fmt(TABLE_FROM_README)
    pipe_lines = [ln for ln in first.splitlines() if ln.lstrip().startswith("|")]
    assert len(pipe_lines) == 6, (
        f"Table was destroyed on first pass ({len(pipe_lines)} rows instead of 6):\n{first!r}"
    )
    second = _fmt(first)
    assert first == second, (
        f"Not idempotent.\nFirst:\n{first}\nSecond:\n{second}"
    )


def test_table_followed_by_paragraph() -> None:
    """A table followed by normal prose: table rows intact, prose still broken."""
    src = (
        "| Col | Value |\n"
        "| --- | ----- |\n"
        "| foo | bar   |\n"
        "\n"
        "First sentence here. Second sentence follows it.\n"
    )
    out = _fmt(src)
    pipe_lines = [ln for ln in out.splitlines() if ln.lstrip().startswith("|")]
    assert len(pipe_lines) == 3, (
        f"Expected 3 table rows, got {len(pipe_lines)}:\n{out!r}"
    )
    # Prose after the table should still get a SemBr break
    assert "First sentence here.\n" in out, (
        f"Prose after table was not SemBr-broken:\n{out!r}"
    )
