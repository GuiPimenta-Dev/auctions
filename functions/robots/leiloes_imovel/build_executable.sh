#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Ensure Python is installed with tkinter
python3 -c "import tkinter" 2>/dev/null || {
    echo "Installing Python with tkinter support..."
    brew install python-tk@3.11
}

# Build executable using the spec file
pyinstaller LeiloesImovelRobot.spec

# Move executable to current directory
mv dist/LeiloesImovelRobot .
rm -rf build dist __pycache__ *.spec 