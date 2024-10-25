#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_file> <destination_directory>"
    exit 1
fi

# Assign arguments to variables
SOURCE_FILE="$1"
DESTINATION_DIR="$2"

# Check if the source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file '$SOURCE_FILE' does not exist."
    exit 1
fi

# Create the destination directory if it doesn't exist
mkdir -p "$DESTINATION_DIR"

# Copy the file while preserving permissions
cp -p "$SOURCE_FILE" "$DESTINATION_DIR"

# Check if the copy was successful
if [ $? -eq 0 ]; then
    echo "Successfully copied '$SOURCE_FILE' to '$DESTINATION_DIR'."
else
    echo "Error: Failed to copy '$SOURCE_FILE'."
    exit 1
fi
