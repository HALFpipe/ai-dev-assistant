import ast
from pathlib import Path
from typing import Dict

from .ast_utils import is_overload_function, iter_real_functions

# ============================================================
# HELPERS
# ============================================================


def format_function_signature(func: ast.FunctionDef) -> str:
    """
    Return a human-readable function signature extracted from AST.

    Examples:
    - foo(a, b)
    - bar(path, strict=False)
    """

    parts: list[str] = []

    # Positional arguments (skip self)
    for arg in func.args.args:
        if arg.arg != "self":
            parts.append(arg.arg)

    # *args
    if func.args.vararg:
        parts.append(f"*{func.args.vararg.arg}")

    # **kwargs
    if func.args.kwarg:
        parts.append(f"**{func.args.kwarg.arg}")

    return f"{func.name}({', '.join(parts)})"


def format_package_tree(tree: Dict[str, dict], indent: int = 0) -> list[str]:
    """
    Convert a nested package dictionary into
    a human-readable indented tree.
    """

    lines: list[str] = []

    for name, subtree in tree.items():
        lines.append("  " * indent + f"- {name}")
        if subtree:
            lines.extend(format_package_tree(subtree, indent + 1))

    return lines


# ============================================================
# CONFIGURATION
# ============================================================

IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "tcss",
    "images",
    "tests",
}

MAX_DEPTH = 4


def walk_python_packages(base: Path, depth: int = 0) -> Dict[str, dict]:
    """
    Recursively walk Python package directories and build
    a nested dictionary representing project structure.

    A directory is considered a Python package if it
    contains an __init__.py file.
    """

    if depth > MAX_DEPTH:
        return {}

    if not (base / "__init__.py").exists():
        return {}

    tree: Dict[str, dict] = {}

    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue
        if item.name in IGNORE_DIRS:
            continue

        subtree = walk_python_packages(item, depth + 1)
        tree[item.name] = subtree

    return tree


# ============================================================
# PROJECT-LEVEL CHUNKING (filesystem-based)
# ============================================================


def build_project_overview(repo_root: Path) -> str:
    """
    Build a deep but semantic overview of the project structure.

    This describes WHERE things live, not HOW they work.
    """

    tree = walk_python_packages(repo_root)

    lines: list[str] = [
        f"Project: {repo_root.name}",
        f"Root: {repo_root}",
        "",
        "Package structure:",
        "",
    ]

    lines.extend(format_package_tree(tree))
    return "\n".join(lines).strip()


# ============================================================
# MODULE-LEVEL STRUCTURAL OVERVIEW (AST-based, summary only)
# ============================================================


def build_module_overview(path: Path, tree: ast.Module) -> str:
    """
    Build a compact, human-readable structural overview of a Python module.

    This describes:
    - imports
    - globals
    - classes and methods
    - functions and nested functions
    """

    lines: list[str] = [
        f"File: {path}",
        f"Module: {path.stem}",
        "",
    ]

    module_doc = ast.get_docstring(tree)
    if module_doc:
        lines.extend(["Docstring:", module_doc.strip(), ""])

    # Imports
    imports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(name.name for name in node.names)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports.extend(f"{mod}.{name.name}" for name in node.names)

    if imports:
        lines.append("Imports:")
        for imp in sorted(set(imports)):
            lines.append(f"- {imp}")
        lines.append("")

    # Module variables
    variables: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append(target.id)

    if variables:
        lines.append("Module variables:")
        for var in sorted(set(variables)):
            lines.append(f"- {var}")
        lines.append("")

    # Classes
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    if classes:
        lines.append("Classes:")
        for cls in classes:
            lines.append(f"- {cls.name}")
            for item in cls.body:
                if isinstance(item, ast.FunctionDef):
                    lines.append(f"  - {item.name}()")
        lines.append("")

    # Functions
    functions = iter_real_functions(tree)
    if functions:
        lines.append("Functions:")
        for fn in functions:
            lines.append(f"- {fn.name}()")
            for item in fn.body:
                if isinstance(item, ast.FunctionDef) and not is_overload_function(item):
                    lines.append(f"  - nested: {item.name}()")
        lines.append("")

    return "\n".join(lines).strip()


# ============================================================
# CLASS-LEVEL STRUCTURAL OVERVIEW (AST-based, summary only)
# ============================================================


def build_class_overview(
    module_path: Path,
    class_node: ast.ClassDef,
) -> str:
    """
    Build a compact structural overview of a class.

    This describes:
    - inheritance
    - class docstring
    - class-level attributes
    - methods and their signatures

    It does NOT include method bodies.
    """

    lines: list[str] = []

    # --------------------------------------------------
    # Identity
    # --------------------------------------------------
    lines.append(f"Class: {class_node.name}")
    lines.append(f"Defined in: {module_path}")
    lines.append("")

    # --------------------------------------------------
    # Base classes (inheritance)
    # --------------------------------------------------
    bases: list[str] = []
    for base_expr in class_node.bases:
        if isinstance(base_expr, ast.Name):
            bases.append(base_expr.id)
        elif isinstance(base_expr, ast.Attribute):
            bases.append(ast.unparse(base_expr))

    if bases:
        lines.append("Inherits from:")
        for base_name in bases:
            lines.append(f"- {base_name}")
        lines.append("")

    # --------------------------------------------------
    # Class docstring
    # --------------------------------------------------
    docstring = ast.get_docstring(class_node)
    if docstring:
        lines.append("Docstring:")
        lines.append(docstring.strip())
        lines.append("")

    # --------------------------------------------------
    # Class-level attributes
    # --------------------------------------------------
    attributes: list[str] = []

    for item in class_node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    attributes.append(target.id)

    if attributes:
        lines.append("Class attributes:")
        for attr in sorted(set(attributes)):
            lines.append(f"- {attr}")
        lines.append("")

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------
    methods: list[str] = []

    for item in class_node.body:
        if isinstance(item, ast.FunctionDef):
            methods.append(format_function_signature(item))

    if methods:
        lines.append("Methods:")
        for method in methods:
            lines.append(f"- {method}")
        lines.append("")

    return "\n".join(lines).strip()


# ============================================================
# METHOD-LEVEL STRUCTURAL OVERVIEW (AST-based, summary only)
# ============================================================


def build_method_overview(
    path: Path,
    class_name: str,
    func: ast.FunctionDef,
) -> str:
    """
    Build a short semantic description of a class method.

    Same idea as function_overview, but with class context.
    """

    lines: list[str] = []

    lines.append(f"Method: {class_name}.{format_function_signature(func)}")
    lines.append(f"Defined in: {path}")
    lines.append(f"Class: {class_name}")
    lines.append("")

    doc = ast.get_docstring(func)
    if doc:
        lines.append("Docstring:")
        lines.append(doc.strip())
        lines.append("")

    if func.returns:
        try:
            returns = ast.unparse(func.returns)
        except Exception:
            returns = "unknown"
    else:
        returns = "unknown"

    lines.append(f"Returns: {returns}")

    if any(isinstance(n, ast.Yield) for n in ast.walk(func)):
        lines.append("Type: generator")

    return "\n".join(lines)


# ============================================================
# FUNCTION-LEVEL STRUCTURAL OVERVIEW (AST-based, summary only)
# ============================================================


def build_function_overview(
    path: Path,
    func: ast.FunctionDef,
) -> str:
    """
    Build a short semantic description of a standalone function.

    This is EMBEDDED.
    It must remain stable even if the function body changes.
    """

    lines: list[str] = []

    lines.append(f"Function: {format_function_signature(func)}")
    lines.append(f"Defined in: {path}")
    lines.append("")

    # Docstring (if present)
    doc = ast.get_docstring(func)
    if doc:
        lines.append("Docstring:")
        lines.append(doc.strip())
        lines.append("")

    # Return annotation
    if func.returns:
        try:
            returns = ast.unparse(func.returns)
        except Exception:
            returns = "unknown"
    else:
        returns = "unknown"

    lines.append(f"Returns: {returns}")

    # Generator hint (semantic signal)
    if any(isinstance(n, ast.Yield) for n in ast.walk(func)):
        lines.append("Type: generator")

    return "\n".join(lines)
