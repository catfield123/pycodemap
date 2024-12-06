"""
Formats the outline of a Python file as a string.

This module contains functions for formatting the outline of a Python file as a string.
The outline is determined by the classes and functions found in the file.

"""


def format_class(
    class_data: dict, minimalistic: bool, no_attributes: bool
) -> list[str]:
    class_output = []

    class_name = class_data["name"]
    class_decorators = class_data["decorators"]
    class_attributes = class_data["attributes"]
    class_base_classes = class_data["base_classes"]

    if class_decorators:
        for decorator in class_decorators:
            class_output.append(f"  @{decorator}")

    class_full_name = f"  Class: {class_name}"
    if class_base_classes:
        class_full_name += " (" + ", ".join(class_base_classes) + ")"
    class_output.append(class_full_name)
    class_output.append("")

    if not no_attributes and class_attributes:
        for attribute in class_attributes:
            attr_type = f": {attribute['type']}" if attribute["type"] else ""
            class_output.append(f"    {attribute['name']}{attr_type}")
        class_output.append("")

    for method in class_data["methods"]:
        decorators_output = []
        if method["decorators"]:
            for i, decorator in enumerate(method["decorators"]):
                prefix = "    " if i == 0 else "    |"
                decorators_output.append(f"{prefix}@{decorator}")
        args = ", ".join(
            f"{name}: {hint}" if hint else name for name, hint in method["args"]
        )
        return_type = f" -> {method['return_type']}" if method["return_type"] else ""
        method_output = (
            f"    {method['name']}({args}){return_type}"
            if minimalistic
            else f"    Method: {method['name']}({args}){return_type}"
        )
        if decorators_output:
            class_output.append("\n".join(decorators_output))
        class_output.append(method_output)
        class_output.append("")
    return class_output


def format_function(function_data: dict, minimalistic: bool) -> list[str]:
    function_output = []
    decorators_output = []
    if function_data["decorators"]:
        for i, decorator in enumerate(function_data["decorators"]):
            prefix = "   " if i == 0 else "  |"
            decorators_output.append(f"{prefix}@{decorator}")
    args = ", ".join(
        f"{name}: {hint}" if hint else name for name, hint in function_data["args"]
    )
    return_type = (
        f" -> {function_data['return_type']}" if function_data["return_type"] else ""
    )
    function_string = (
        f"    {function_data['name']}({args}){return_type}"
        if minimalistic
        else f"  Function: {function_data['name']}({args}){return_type}"
    )
    if decorators_output:
        function_output.append("\n".join(decorators_output))
    function_output.append(function_string)
    function_output.append("")
    return function_output


def format_output(
    filepath: str,
    classes: list,
    functions: list,
    include_classes: bool,
    include_functions: bool,
    minimalistic: bool,
    no_attributes: bool,
):
    """
    Formats the given classes and functions into a string that represents the outline of the given file.

    Args:
        filepath (str): The path to the file being outlined.
        classes (list): A list of dictionaries containing information about the classes
            in the file. Each dictionary should contain the keys "name", "decorators", "attributes",
            and "methods".
        functions (list): A list of dictionaries containing information about the functions
            in the file. Each dictionary should contain the keys "name", "decorators", and "args".
        include_classes (bool): Whether or not to include classes in the output.
        include_functions (bool): Whether or not to include functions in the output.
        minimalistic (bool): Whether to use a minimalistic output style or not.
        no_attributes (bool): Whether to ignore class attributes from the output.

    Returns:
        str: The formatted string representing the outline of the file.
    """
    output = []
    if (include_classes and classes) or (include_functions and functions):
        output.append(f"=== {filepath}: ===")
        output.append("")

        if include_classes and classes:
            for class_data in classes:
                class_output = format_class(class_data, minimalistic, no_attributes)
                output.extend(class_output)

        if include_functions and functions:
            if minimalistic:
                output.append("  Functions:\n")
            for function_data in functions:
                function_output = format_function(function_data, minimalistic)
                output.extend(function_output)
            output.append("")
        output.append("")
    return "\n".join(output)
