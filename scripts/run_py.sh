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

# Iterate over each Python file in the specified directory
for file in "$DIRECTORY"/*.py; do
    echo "Running $file..."
    python -m "$file"
    # Check if the script exited with a non-zero status
    if [ $? -ne 0 ]; then
        echo "$file encountered an error."
    fi
done
