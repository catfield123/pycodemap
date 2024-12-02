"""
The command line interface of the pycodemap tool.

This module provides the command line interface for the pycodemap tool.
"""

import argparse
import fnmatch
import os

from pycodemap.analyzer import analyze_file
from pycodemap.formatter import format_output

DEFAULT_IGNORES = {".git", ".venv*", "__pycache__", "*.egg-info", "build", "dist"}
"""
A set of default ignores for the --ignore option.

This set includes some common directory and file names that are usually
not relevant for the structure of a Python project, such as version control
directories, virtual environments, Python bytecode cache directories,
package build directories, and egg-info directories.
"""


def run():
    """
    The main entry point of the script.

    Parses the command line arguments, analyzes all Python files in the given directory,
    and formats the output.

    :param directory: Path to the project directory.
    :param functions_only: Include only functions in the output.
    :param classes_only: Include only classes in the output.
    :param no_attributes: Exclude attributes from the output.
    :param minimalistic: Minimalistic output mode.
    :param output: Path to save the output to a file.
    :param ignore: Pattern of directories or files to ignore (e.g., '.git|__pycache__').
    """
    parser = argparse.ArgumentParser(
        description="A tool to extract and outline the structure of Python code."
    )
    parser.add_argument("directory", type=str, help="Path to the project directory.")
    parser.add_argument(
        "--functions-only",
        "-f",
        action="store_true",
        help="Include only functions in the output.",
    )
    parser.add_argument(
        "--classes-only",
        "-c",
        action="store_true",
        help="Include only classes in the output.",
    )
    parser.add_argument(
        "--no-attributes",
        "-a",
        action="store_true",
        help="Exclude attributes from the output.",
    )
    parser.add_argument(
        "--minimalistic", "-m", action="store_true", help="Minimalistic output mode."
    )
    parser.add_argument(
        "--output", "-o", type=str, help="Path to save the output to a file."
    )
    parser.add_argument(
        "--ignore",
        "-I",
        type=str,
        help="Pattern of directories or files to ignore (e.g., '.git|__pycache__').",
    )
    args = parser.parse_args()

    directory = args.directory
    ignore_patterns = set(DEFAULT_IGNORES)
    if args.ignore:
        ignore_patterns.update(args.ignore.split("|"))

    include_classes = not args.functions_only
    include_functions = not args.classes_only

    if args.functions_only and args.classes_only:
        print("You can't use both --functions-only and --classes-only.")
        return

    output_file = open(args.output, "w", encoding="utf-8") if args.output else None

    for root, dirs, files in os.walk(directory):
        dirs[:] = [
            d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in ignore_patterns)
        ]
        for file in files:
            if file.endswith(".py") and not any(
                fnmatch.fnmatch(file, p) for p in ignore_patterns
            ):
                filepath = os.path.join(root, file)
                classes, functions = analyze_file(
                    filepath, include_classes, include_functions
                )
                result = format_output(
                    filepath,
                    classes,
                    functions,
                    include_classes,
                    include_functions,
                    args.minimalistic,
                    args.no_attributes,
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
