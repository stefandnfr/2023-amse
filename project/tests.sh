#!/bin/bash

# Get the current working directory
cwd=$(pwd)

echo "You're currently in:"
echo $cwd
# Check if the "test" folder exists in the current working directory
if [ -d "${cwd}/tests" ]; then
  # If it exists, get its absolute path
  test_folder_path=$(realpath "${cwd}/tests")
else
  echo "The 'tests' folder does not exist in the current working directory."
  echo "Make sure you are in the root directory of the project"
  exit 1
fi

# Echo the current working directory and the absolute path of the "test" folder
echo "Current working directory: ${cwd}"
echo "Absolute path of 'tests' folder: ${test_folder_path}"

echo "now testing"
# Check if the script file exists in the "test" folder
script_file="${test_folder_path}/test_data_pipeline.py"
if [ -f "$script_file" ]; then
  # If it exists, save its path to a variable
  script_path="$script_file"
  echo $script_path
else
  echo "The 'test_data_pipeline.py' script does not exist in the 'tests' folder."
  exit 1
fi

pytest $script_path

