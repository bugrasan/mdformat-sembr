"""mdformat-sembr: Semantic Line Breaks as CommonMark soft breaks.

The entry point ``mdformat.parser_extension`` -> ``sembr`` resolves to the
``_plugin`` attribute of this package (see ``pyproject.toml``). Importing it here
exposes the interface object as ``mdformat_sembr._plugin``.
"""

from __future__ import annotations

from mdformat_sembr import _plugin
from mdformat_sembr._sembr import insert_breaks

__all__ = ["_plugin", "insert_breaks"]
__version__ = "0.1.0"
