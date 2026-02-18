"""
chunking.py

Convert repository structure and Python source files
into semantic CodeChunk objects.

IMPORTANT:
- This file does NOT use AI.
- This file does NOT understand code behavior.
- This file ONLY extracts structure and text boundaries.

Sources of structure:
- filesystem (project overview)
- AST (modules, classes, functions, methods)
"""

import ast
from pathlib import Path
from typing import Iterable

from .schema import CodeChunk
from .ast_utils import iter_real_functions, is_overload_function

from .overviews import (
    build_project_overview,
    build_module_overview,
    build_class_overview,
    build_function_overview,
    build_method_overview,
)






def chunk_project_overview(repo_root: Path) -> CodeChunk:
    """
    Produce a CodeChunk describing the high-level project structure.
    """

    return CodeChunk(
        id="PROJECT::overview",
        file=str(repo_root),
        type="project",
        symbol=repo_root.name,
        text=build_project_overview(repo_root),
    )





# ============================================================
# FILE-LEVEL CHUNKING (AST-based, code-bearing)
# ============================================================

def chunk_python_file(path: Path) -> Iterable[CodeChunk]:
    code = path.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return

    # --------------------------------------------------
    # MODULE OVERVIEW (embedded)
    # --------------------------------------------------
    yield CodeChunk(
        id=f"{path}::module::overview",
        file=str(path),
        type="module_overview",
        symbol=path.stem,
        text=build_module_overview(path, tree),
    )

    # --------------------------------------------------
    # MODULE FULL CODE (not embedded)
    # --------------------------------------------------
    yield CodeChunk(
        id=f"{path}::module",
        file=str(path),
        type="module",
        symbol=path.stem,
        text=code,
    )

    # --------------------------------------------------
    # CLASSES
    # --------------------------------------------------
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        yield CodeChunk(
            id=f"{path}::{node.name}::overview",
            file=str(path),
            type="class_overview",
            symbol=node.name,
            text=build_class_overview(path, node),
        )

        yield CodeChunk(
            id=f"{path}::{node.name}",
            file=str(path),
            type="class",
            symbol=node.name,
            text=ast.get_source_segment(code, node),
        )

        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue

            if is_overload_function(item):
                continue

            yield CodeChunk(
                id=f"{path}::{node.name}.{item.name}::overview",
                file=str(path),
                type="method_overview",
                symbol=f"{node.name}.{item.name}",
                text=build_method_overview(path, node.name, item),
            )

            yield CodeChunk(
                id=f"{path}::{node.name}.{item.name}",
                file=str(path),
                type="method",
                symbol=f"{node.name}.{item.name}",
                text=ast.get_source_segment(code, item),
            )

    # --------------------------------------------------
    # STANDALONE FUNCTIONS (IMPORTANT PART)
    # --------------------------------------------------
    for func in iter_real_functions(tree):

        yield CodeChunk(
            id=f"{path}::{func.name}::overview",
            file=str(path),
            type="function_overview",
            symbol=func.name,
            text=build_function_overview(path, func),
        )

        yield CodeChunk(
            id=f"{path}::{func.name}",
            file=str(path),
            type="function",
            symbol=func.name,
            text=ast.get_source_segment(code, func),
        )

