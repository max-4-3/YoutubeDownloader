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

# Generate new random file names
NEW_NAME1=$(shuf -i 1-200000 -n 1)$(basename "$SOURCE_FILE")
NEW_NAME2=$(shuf -i 1-2000000000 -n 1)$(basename "$SOURCE_FILE")

# Rename the source file to a new name
echo "Renaming '$SOURCE_FILE' to '$NEW_NAME1'."
mv "$SOURCE_FILE" "$NEW_NAME1"

# Create an empty file in the destination directory
EMPTY_FILE="$DESTINATION_DIR/$NEW_NAME2"
echo "Making an empty file: '$EMPTY_FILE'."
touch "$EMPTY_FILE"

# Copy the contents using dd
echo "Data copying from '$NEW_NAME1' to '$NEW_NAME2'."
dd if="$NEW_NAME1" of="$EMPTY_FILE" bs=4M status=progress

# Check if the copy was successful
if [ $? -eq 0 ]; then
    echo "Successfully copied data from '$NEW_NAME1' to '$EMPTY_FILE'."
    # Rename the empty file back to the original file name
    echo "Renaming '$EMPTY_FILE' back to '$SOURCE_FILE'."
    mv "$EMPTY_FILE" "$(dirname "$SOURCE_FILE")/$(basename "$SOURCE_FILE")"
    echo "Completed!"
else
    echo "Error: Failed to copy '$NEW_NAME1'."
    exit 1
fi
