#!/bin/bash

set -euo pipefail

# Find python in PATH
WHICH_PYTHON=$(which python || echo "")

if [ -z "$WHICH_PYTHON" ] || [ ! -x "$WHICH_PYTHON" ]; then
    echo "Python is not installed or not in PATH"
    exit 1
fi

# Check current python version
PYTHON_VERSION=$("$WHICH_PYTHON" --version 2>&1)

# Set Python path
PYTHON_EXEC="$WHICH_PYTHON"

if [ "$PYTHON_VERSION" != "Python 3.13.9" ]; then
    echo "py-gocd strictly requires Python 3.13.9"
    echo "Current version: $PYTHON_VERSION"
    echo "Please provide the path to Python 3.13.9 (can be a virtual environment):"
    read -r PYTHON_VENV

    # Validate that the user actually entered something
    if [ -z "$PYTHON_VENV" ]; then
        echo "No path provided. Exiting."
        exit 1
    fi

    # Check if the provided python exists and is executable
    if [ ! -x "$PYTHON_VENV" ]; then
        echo "Error: '$PYTHON_VENV' is not executable or does not exist."
        exit 1
    fi

    # Now check the version of the provided Python
    PYTHON_VENV_VERSION=$("$PYTHON_VENV" --version 2>&1)

    if [ "$PYTHON_VENV_VERSION" != "Python 3.13.9" ]; then
        echo "Error: The provided Python is '$PYTHON_VENV_VERSION', but 3.13.9 is required."
        exit 1
    fi

    echo "Using custom Python: $PYTHON_VENV ($PYTHON_VENV_VERSION)"
    PYTHON_EXEC="$PYTHON_VENV"
else
    echo "Using system Python: $PYTHON_EXEC ($PYTHON_VERSION)"
fi

# Now you can safely use "$PYTHON_EXEC" as your Python interpreter

PIP_CMD="$PYTHON_EXEC -m pip"
echo "Using pip: $PIP_CMD"

test_series() {
  echo "=== Recompiling all Python files (before changes) ==="
    "$PYTHON_EXEC" -m compileall . -x '.venv' || {
        echo "compileall failed"
        exit 1
    }

    echo "=== Uninstalling any existing gocd package ==="
    $PIP_CMD uninstall -y gocd || {
        echo "pip uninstall failed (probably not installed, continuing)"
        true
    }

    echo "=== Installing test requirements ==="
    $PIP_CMD install --upgrade -r test-requirements.txt || {
        echo "Failed to install test-requirements.txt"
        exit 1
    }

    echo "=== Recompiling after installing dependencies ==="
    "$PYTHON_EXEC" -m compileall . -x '.venv' || {
        echo "Second compileall failed"
        exit 1
    }

    echo "=== Installing package in editable mode ==="
    $PIP_CMD install -e . || {
        echo "pip install -e . failed"
        exit 1
    }

    echo "=== Running tests with pytest ==="
    "$PYTHON_EXEC" -m pytest -v || {
        echo "Tests failed!"
        exit 1
    }

    echo "All tests passed successfully!"
}

test_series



