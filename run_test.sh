#!/bin/bash

if [ -x "venv/Scripts/python.exe" ]; then
  ./venv/Scripts/python.exe -m unittest discover -v tests
elif [ -x ".venv/Scripts/python.exe" ]; then
  ./.venv/Scripts/python.exe -m unittest discover -v tests
elif [ -x "venv/bin/python" ]; then
  ./venv/bin/python -m unittest discover -v tests
elif [ -x ".venv/bin/python" ]; then
  ./.venv/bin/python -m unittest discover -v tests
elif command -v python3 >/dev/null 2>&1; then
  python3 -m unittest discover -v tests
else
  python -m unittest discover -v tests
fi
