"""Test 8: plugin discovery, config plumbing, and CLI activation."""

from __future__ import annotations

import subprocess
import sys

import mdformat
import mdformat.plugins


def test_entry_point_registered() -> None:
    assert "sembr" in mdformat.plugins.PARSER_EXTENSIONS


def test_interface_surface() -> None:
    ext = mdformat.plugins.PARSER_EXTENSIONS["sembr"]
    assert ext.CHANGES_AST is False
    assert ext.RENDERERS == {}
    assert "paragraph" in ext.POSTPROCESSORS
    assert callable(ext.update_mdit)
    assert callable(ext.add_cli_argument_group)


def test_version_lists_plugin() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mdformat", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "mdformat_sembr" in result.stdout or "mdformat-sembr" in result.stdout


def test_cli_min_chars_option() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mdformat", "-", "--sembr-min-chars", "5"],
        input="One two three. Four five six seven.\n",
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == "One two three.\nFour five six seven.\n"


def test_cli_break_clauses_flag() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mdformat", "-", "--sembr-break-clauses", "--sembr-min-chars", "5"],
        input="One long segment here, another long segment there.\n",
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == "One long segment here,\nanother long segment there.\n"


def test_cli_clause_chars_option() -> None:
    # Override clause chars to only include semicolon; comma should NOT break.
    result = subprocess.run(
        [
            sys.executable, "-m", "mdformat", "-",
            "--sembr-break-clauses",
            "--sembr-clause-chars", ";",
            "--sembr-min-chars", "5",
        ],
        input="One long segment here, another long segment there; and one more.\n",
        capture_output=True,
        text=True,
        check=True,
    )
    # Comma must NOT trigger a break; semicolon must.
    assert ",\n" not in result.stdout
    assert "there;\n" in result.stdout


def test_toml_config(tmp_path) -> None:
    cfg = tmp_path / ".mdformat.toml"
    cfg.write_text("[plugin.sembr]\nmin_chars = 5\n", encoding="utf-8")
    md = tmp_path / "doc.md"
    md.write_text("One two three. Four five six seven.\n", encoding="utf-8")
    subprocess.run(
        [sys.executable, "-m", "mdformat", str(md)],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )
    assert md.read_text(encoding="utf-8") == "One two three.\nFour five six seven.\n"
