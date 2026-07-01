"""Test 1 (load-bearing): every fixture round-trips AST-equal after formatting.

SemBr soft breaks MUST NOT alter rendered output. mdformat's own ``is_md_equal``
is what gates this; here we assert it directly for each fixture.
"""

from __future__ import annotations

import mdformat
from mdformat._util import is_md_equal

from tests.conftest import fixture_sources


def test_fixtures_are_ast_safe() -> None:
    for name, source in fixture_sources():
        formatted = mdformat.text(source, extensions={"sembr"})
        assert is_md_equal(
            source, formatted, extensions={"sembr"}
        ), f"AST changed for fixture {name!r}"


def test_soft_break_is_ast_safe() -> None:
    src = "First sentence. Second sentence. Third sentence here.\n"
    out = mdformat.text(src, extensions={"sembr"})
    assert "\n" in out.strip()
    assert is_md_equal(src, out, extensions={"sembr"})


def test_no_hard_breaks_emitted() -> None:
    src = "First sentence. Second sentence that is long enough.\n"
    out = mdformat.text(src, extensions={"sembr"})
    # No backslash hard breaks and no two-trailing-space hard breaks.
    assert "\\\n" not in out
    for line in out.splitlines():
        assert not line.endswith("  "), "trailing double space is a hard break"
