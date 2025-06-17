#!/usr/bin/env bash

# Recursively find Python files importing numpy and matplotlib
find . -type f -name "*.py" | while IFS= read -r file; do
  if grep -qE '^\s*(import|from)\s+numpy' "$file" && grep -qE '^\s*(import|from)\s+matplotlib' "$file"; then
    echo "$file"
  fi
done