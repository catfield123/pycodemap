# PyCodeMap

Version: 1.0.3


## Description

PyCodeMap is a command-line tool to extract and outline the structure of Python code. It helps developers visualize the organization of classes, methods, functions, and attributes in their projects, providing a clear and detailed overview.

## Installation

You can install PyCodeMap directly from PyPI:

```bash
pip install pycodemap
```

## Usage

After installation, you can run the tool using the `pycodemap` command.

You can also use `python -m pycodemap` to run the tool from the command line.

Note that if pip installs the package into directory that is not in the PATH, you will need to add the directory to the PATH or use `python -m pycodemap`.

To add the directory to the PATH, you can run the following command or add it to your `.bashrc` or `.zshrc` file:

```bash
export PATH="$PATH:/path/to/pycodemap/directory"
```

### Basic Commands

- Analyze the current directory:
  ```bash
  pycodemap .
  python -m pycodemap .
  ```

- Save the output to a file:
  ```bash
  pycodemap . -o structure.txt
  pycodemap . --output structure.txt
  ```

- Show only functions:
  ```bash
  pycodemap . -c
  pycodemap . --functions-only
  ```

- Show only classes:
  ```bash
  pycodemap . -c
  pycodemap . --classes-only
  ```

- Exclude attributes from the output:
  ```bash
  pycodemap . -a
  pycodemap . --no-attributes
  ```

- Minimalistic output:
  ```bash
  pycodemap . -m
  pycodemap . --minimalistic
  ```

- Exclude specific directories or files:
  ```bash
  pycodemap . -i "dir_to_ignore|file_to_ignore"
  pycodemap . --ignore "dir_to_ignore|file_to_ignore"
  ```

You can combine multiple options to get the desired output.

```bash
pycodemap . -cam -i "dir_to_ignore|file_to_ignore"
pycodemap . --classes-only --no-attributes --minimalistic --ignore "dir_to_ignore|file_to_ignore"
```

## Contributing

### How to contribute

Follow these steps to set up your development environment and submit your changes:

1. Fork the repository:
   - Go to the [PyCodeMap repository on GitHub](https://github.com/catfield123/PyCodeMap).
   - Click the "Fork" button in the top-right corner to create your own copy of the repository.

2. Clone your forked repository:
   ```bash
   git clone https://github.com/your_username/PyCodeMap.git
   cd PyCodeMap
   ```

3. Install pycodemap in editable mode from source code:
   ```bash
   pip install -e .
   ```

    Now you can develop and test your changes locally by running `pycodemap`. All changes will be automatically reflected in your local installation.

4. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b your-feature-branch
   ```

5. Set up `pre-commit` to ensure code quality:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

    Before committing your changes, `pre-commit` checks your code for formatting. If issues are found, the commit process halts, and `pre-commit` automatically resolves them. You'll need to stage these changes and try to commit again.


5. Make your changes and write tests.

6. Run all tests:
   ```bash
   pytest
   ```

7. Commit your changes and push them to your forked repository:
   ```bash
   git push origin your-feature-branch
   ```

8. Create a pull request:
   - Go to the original [PyCodeMap repository](https://github.com/catfield123/PyCodeMap).
   - Click "Pull Requests" and then "New Pull Request."
   - Select your branch from your forked repository and create the pull request.


### Guidelines

- Ensure your code is formatted with `black`.
- Use `isort` for imports and `autoflake` to remove unused imports.
- Check your code with `pylint` using configuration from `.pylintrc`.
- Write tests for any new features or bug fixes.
- Provide a clear description of the changes in your pull request.
