"""
Analyzes a Python file and extracts information about the classes and functions
it contains.

This module contains functions for analyzing a Python file and extracting
information about the classes and functions it contains.

"""

import ast

DEFAULT_IGNORES = {".git", ".venv*", "__pycache__", "*.egg-info", "build", "dist"}


def get_arguments_and_hints(node: ast.FunctionDef) -> tuple:
    """
    Extracts the argument names and their type hints from a function
    or method node, as well as the return type hint.

    Args:
        node (ast.FunctionDef): The AST node representing a function or method.

    Returns:
        tuple: A tuple containing a list of tuples with argument names
               and their type hints, and the return type hint.
               The argument list includes positional, *args, and **kwargs.
    """
    args_info = []
    for arg in node.args.args:
        arg_name = arg.arg
        arg_type = None
        if arg.annotation:
            arg_type = ast.unparse(arg.annotation)
        args_info.append((arg_name, arg_type))

    if node.args.vararg:
        args_info.append((f"*{node.args.vararg.arg}", None))
    if node.args.kwarg:
        args_info.append((f"**{node.args.kwarg.arg}", None))

    return_type = None
    if node.returns:
        return_type = ast.unparse(node.returns)

    return args_info, return_type


def get_decorators(node: ast.FunctionDef) -> list:
    """
    Extracts decorators from a function or method node.

    Args:
        node (ast.FunctionDef): The AST node representing a function or method.

    Returns:
        list: A list containing the decorators as strings.
    """
    decorators = []
    for decorator in node.decorator_list:
        decorators.append(ast.unparse(decorator))
    return decorators


def analyze_file(
    filepath: str, include_classes: bool = True, include_functions: bool = True
) -> tuple:
    """
    Analyzes a Python file and extracts information about the classes and functions
    it contains.

    Args:
        filepath (str): The path to the Python file to analyze.
        include_classes (bool): Whether to include classes in the output.
        include_functions (bool): Whether to include functions in the output.

    Returns:
        tuple: A tuple containing two lists: the first list contains dictionaries
            with information about the classes, and the second list contains
            dictionaries with information about the functions.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())

    classes = []
    functions = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and include_classes:
            class_decorators = get_decorators(node)
            class_methods = []
            base_classes = [ast.unparse(base) for base in node.bases]
            class_attributes = []

            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    args, return_type = get_arguments_and_hints(child)
                    method_decorators = get_decorators(child)
                    class_methods.append(
                        {
                            "name": child.name,
                            "args": args,
                            "return_type": return_type,
                            "decorators": method_decorators,
                        }
                    )
                elif isinstance(child, (ast.Assign, ast.AnnAssign)):
                    name = (
                        child.target.id if isinstance(child.target, ast.Name) else None
                    )
                    annotation = (
                        ast.unparse(child.annotation) if child.annotation else None
                    )
                    class_attributes.append({"name": name, "type": annotation})

            classes.append(
                {
                    "name": node.name,
                    "decorators": class_decorators,
                    "base_classes": base_classes,
                    "methods": class_methods,
                    "attributes": class_attributes,
                }
            )
        elif isinstance(node, ast.FunctionDef) and include_functions:
            args, return_type = get_arguments_and_hints(node)
            function_decorators = get_decorators(node)
            functions.append(
                {
                    "name": node.name,
                    "args": args,
                    "return_type": return_type,
                    "decorators": function_decorators,
                }
            )

    return classes, functions
