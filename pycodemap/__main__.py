import ast
import os
import argparse
import fnmatch


DEFAULT_EXCLUDES = {".git", ".venv*", ".venv_test", "__pycache__", "*.egg-info", "build", "dist"}


def get_arguments_and_hints(node):
    """Получает аргументы и их типы из FunctionDef."""
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


def get_decorators(node):
    """Извлекает декораторы из функции или метода."""
    decorators = []
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            decorators.append(decorator.id)
        elif isinstance(decorator, ast.Call):
            func_name = ast.unparse(decorator.func)
            args = ", ".join(ast.unparse(arg) for arg in decorator.args)
            decorators.append(f"{func_name}({args})" if args else func_name)
        else:
            decorators.append(ast.unparse(decorator))
    return decorators


def analyze_file(filepath, include_classes, include_functions):
    """Анализирует Python-файл, извлекая классы, функции и атрибуты."""
    with open(filepath, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())
    
    classes = []
    functions = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and include_classes:
            # Сбор декораторов класса
            class_decorators = get_decorators(node)

            class_methods = []
            class_attributes = []
            
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    args, return_type = get_arguments_and_hints(child)
                    method_decorators = get_decorators(child)
                    class_methods.append({
                        "name": child.name,
                        "args": args,
                        "return_type": return_type,
                        "decorators": method_decorators,
                    })
                elif isinstance(child, (ast.Assign, ast.AnnAssign)):
                    # Извлекаем атрибуты (переменные класса)
                    if isinstance(child, ast.AnnAssign):
                        name = child.target.id if isinstance(child.target, ast.Name) else None
                        annotation = ast.unparse(child.annotation) if child.annotation else None
                    elif isinstance(child, ast.Assign):
                        name = child.targets[0].id if isinstance(child.targets[0], ast.Name) else None
                        annotation = None
                    else:
                        continue
                    if name:
                        class_attributes.append({
                            "name": name,
                            "type": annotation,
                        })

            classes.append({
                "name": node.name,
                "decorators": class_decorators,
                "methods": class_methods,
                "attributes": class_attributes,
            })
        elif isinstance(node, ast.FunctionDef) and include_functions:
            args, return_type = get_arguments_and_hints(node)
            function_decorators = get_decorators(node)
            functions.append({
                "name": node.name,
                "args": args,
                "return_type": return_type,
                "decorators": function_decorators,
            })
    
    return classes, functions


def format_output(filepath, classes, functions, include_classes, include_functions, minimalistic, no_attributes):
    """Форматирует вывод для одного файла."""
    output = []
    if (include_classes and classes) or (include_functions and functions):
        output.append(f"=== {filepath}: ===")
        output.append("")  # Отступ после пути

        if include_classes and classes:
            for class_data in classes:
                class_name = class_data["name"]
                class_decorators = class_data["decorators"]
                class_attributes = class_data["attributes"]

                # Декораторы класса
                if class_decorators:
                    for decorator in class_decorators:
                        output.append(f"  @{decorator}")

                output.append(f"  Class: {class_name}")
                output.append("")  # Отступ после класса

                # Атрибуты класса
                if not no_attributes and class_attributes:
                    for attribute in class_attributes:
                        attr_type = f": {attribute['type']}" if attribute["type"] else ""
                        output.append(f"    {attribute['name']}{attr_type}")
                    output.append("")  # Отступ после атрибутов

                # Методы класса
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
                    method_output = f"    {method['name']}({args}){return_type}" if minimalistic else f"    Method: {method['name']}({args}){return_type}"
                    if decorators_output:
                        output.append("\n".join(decorators_output))
                    output.append(method_output)
                    output.append("")  # Пустая строка между методами

        if include_functions and functions:
            if minimalistic:
                output.append("  Functions:\n")
            for function in functions:
                decorators_output = []
                if function["decorators"]:
                    for i, decorator in enumerate(function["decorators"]):
                        prefix = "   " if i == 0 else "  |"
                        decorators_output.append(f"{prefix}@{decorator}")
                args = ", ".join(
                    f"{name}: {hint}" if hint else name for name, hint in function["args"]
                )
                return_type = f" -> {function['return_type']}" if function["return_type"] else ""
                function_output = f"    {function['name']}({args}){return_type}" if minimalistic else f"  Function: {function['name']}({args}){return_type}"
                if decorators_output:
                    output.append("\n".join(decorators_output))
                output.append(function_output)
                output.append("")  # Пустая строка между функциями
            output.append("")  # Пустая строка после блока Functions

        output.append("")  # Пустая строка между файлами
    return "\n".join(output)


def run():
    parser = argparse.ArgumentParser(description="Analyze Python project structure.")
    parser.add_argument("directory", type=str, help="Path to the project directory.")
    parser.add_argument(
        "--functions-only", "-f", action="store_true", help="Include only functions in the output."
    )
    parser.add_argument(
        "--classes-only", "-c", action="store_true", help="Include only classes in the output."
    )
    parser.add_argument(
        "--no-attributes", "-a", action="store_true", help="Exclude attributes from the output."
    )
    parser.add_argument(
        "--minimalistic", action="store_true", help="Minimalistic output mode."
    )
    parser.add_argument(
        "--output", "-o", type=str, help="Path to save the output to a file."
    )
    parser.add_argument(
        "--exclude", "-I", type=str, help="Pattern of directories or files to exclude (e.g., '.git|__pycache__')."
    )
    
    args = parser.parse_args()

    directory = args.directory
    exclude_patterns = set(DEFAULT_EXCLUDES)
    if args.exclude:
        exclude_patterns.update(args.exclude.split("|"))

    # Логика включения классов и функций
    include_classes = not args.functions_only
    include_functions = not args.classes_only

    # Проверка конфликтов
    if args.functions_only and args.classes_only:
        print("You can't use both --functions-only and --classes-only.")
        return

    # Открытие файла для записи, если указан --output
    output_file = open(args.output, "w", encoding="utf-8") if args.output else None

    # Анализируем файлы по одному
    for root, dirs, files in os.walk(directory):
        # Фильтрация директорий
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in exclude_patterns)]
        for file in files:
            if file.endswith(".py") and not any(fnmatch.fnmatch(file, p) for p in exclude_patterns):
                filepath = os.path.join(root, file)
                classes, functions = analyze_file(filepath, include_classes, include_functions)
                result = format_output(
                    filepath, classes, functions,
                    include_classes, include_functions,
                    args.minimalistic, args.no_attributes
                )
                if result.strip():
                    if output_file:
                        output_file.write(result)
                    else:
                        print(result)

    if output_file:
        output_file.close()


if __name__ == "__main__":
    run()

