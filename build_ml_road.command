#!/bin/bash

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "== ML Road build =="
echo "Project: $SCRIPT_DIR"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found."
  echo
  read -r -p "Press Enter to close..."
  exit 1
fi

if python3 build.py; then
  echo
  echo "== Verification =="
  python3 build.py --check
  echo
  echo "Done."
else
  echo
  echo "Build failed."
fi

echo
read -r -p "Press Enter to close..."
