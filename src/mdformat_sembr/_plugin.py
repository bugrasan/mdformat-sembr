"""mdformat parser-extension interface for the SemBr plugin.

This module *is* the plugin interface object referenced by the entry point
``mdformat_sembr:_plugin``. It exposes the members required by
``mdformat.plugins.ParserExtensionInterface`` at module level.

We do not change the parser or override any renderer; all work happens in a
postprocessor registered on the ``paragraph`` node type. At that point inline
formatting is already resolved into the rendered string, so we operate on final
text and protect a few inline constructs by regex.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from mdformat_sembr._sembr import (
    DEFAULT_ABBREVIATIONS,
    DEFAULT_CLAUSE_CHARS,
    DEFAULT_MIN_CHARS,
    insert_breaks,
)

if TYPE_CHECKING:
    from markdown_it import MarkdownIt
    from mdformat.renderer import RenderContext, RenderTreeNode

#: SemBr soft breaks never alter the rendered output, so the AST is unchanged.
#: This lets mdformat's built-in ``is_md_equal`` validator gate correctness.
CHANGES_AST = False


def update_mdit(mdit: "MarkdownIt") -> None:
    """No parser change is needed for SemBr."""
    # Intentionally a no-op.
    pass


def _plugin_options(context: "RenderContext") -> Mapping[str, Any]:
    """Return the merged ``[plugin.sembr]`` / CLI options mapping."""
    mdformat_opts = context.options.get("mdformat", {})
    plugin_opts = mdformat_opts.get("plugin", {})
    return plugin_opts.get("sembr", {}) or {}


def _postprocess_paragraph(
    text: str,
    node: "RenderTreeNode",
    context: "RenderContext",
) -> str:
    """Insert SemBr soft breaks into an already-rendered paragraph string."""
    opts = _plugin_options(context)

    min_chars = opts.get("min_chars", DEFAULT_MIN_CHARS)
    abbreviations = opts.get("abbreviations", None)
    break_clauses = bool(opts.get("break_clauses", False))
    clause_chars = opts.get("clause_chars", DEFAULT_CLAUSE_CHARS)

    return insert_breaks(
        text,
        min_chars=int(min_chars),
        abbreviations=abbreviations,
        break_clauses=break_clauses,
        clause_chars=clause_chars,
    )


def add_cli_argument_group(group: argparse._ArgumentGroup) -> None:
    """Register CLI options, mirrored to TOML ``[plugin.sembr]``.

    Values are stored under ``mdit.options["mdformat"]["plugin"]["sembr"]`` and
    merged with the TOML config. ``dest`` names deliberately match the TOML keys
    so CLI values merge cleanly over TOML.
    """
    group.add_argument(
        "--sembr-min-chars",
        dest="min_chars",
        type=int,
        default=None,
        metavar="N",
        help=(
            "minimum length of the segment before a break is allowed "
            f"(default: {DEFAULT_MIN_CHARS})"
        ),
    )
    group.add_argument(
        "--sembr-abbreviations",
        dest="abbreviations",
        action="append",
        default=None,
        metavar="ABBR",
        help=(
            "abbreviation after which no sentence break is inserted; "
            "repeat to add several (replaces the default list)"
        ),
    )
    group.add_argument(
        "--sembr-break-clauses",
        dest="break_clauses",
        action="store_true",
        default=None,
        help="also break after clause punctuation (Iteration 2; off by default)",
    )
    group.add_argument(
        "--sembr-clause-chars",
        dest="clause_chars",
        default=None,
        metavar="CHARS",
        help=(
            "clause punctuation set used when --sembr-break-clauses is on "
            f"(default: {DEFAULT_CLAUSE_CHARS!r})"
        ),
    )


#: A mapping from ``RenderTreeNode.type`` to a ``Render`` function. Empty: we do
#: not override rendering.
RENDERERS: Mapping[str, Any] = {}

#: A mapping from ``RenderTreeNode.type`` to a collaborative ``Postprocess``.
POSTPROCESSORS: Mapping[str, Any] = {"paragraph": _postprocess_paragraph}


__all__ = [
    "CHANGES_AST",
    "RENDERERS",
    "POSTPROCESSORS",
    "update_mdit",
    "add_cli_argument_group",
    "DEFAULT_ABBREVIATIONS",
]
