# rag/ast_utils.py

import ast


def is_overload_function(func: ast.FunctionDef) -> bool:
    for decorator in func.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "overload":
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr == "overload":
            return True
    return False


def iter_real_functions(tree: ast.Module) -> list[ast.FunctionDef]:
    """
    Return semantic (runtime-real) top-level functions.

    - overload stubs are ignored
    - last definition wins
    """
    functions: dict[str, ast.FunctionDef] = {}

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue

        if is_overload_function(node):
            continue

        functions[node.name] = node

    return list(functions.values())
