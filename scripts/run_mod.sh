#!/bin/bash

# Check if a directory argument was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the first argument to a variable
DIRECTORY=$1

# Check if the specified directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Directory does not exist: $DIRECTORY"
    exit 1
fi

# Convert the directory path to a Python module path
MOD_PATH=$(echo "$DIRECTORY" | sed 's#/#.#g')

# Iterate over each Python file in the specified directory
for file in "$DIRECTORY"/*.py; do
    # Extract the base filename without the extension
    MODULE=$(basename "$file" .py)

    # Skip __init__.py files
    if [ "$MODULE" == "__init__" ]; then
        continue
    fi

    echo "Running $MODULE as a module..."
    python -m "$MOD_PATH.$MODULE"
    # Check if the script exited with a non-zero status
    if [ $? -ne 0 ]; then
        echo "$MODULE encountered an error."
    fi
done

