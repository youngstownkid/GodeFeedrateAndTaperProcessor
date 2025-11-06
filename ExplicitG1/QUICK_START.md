# Quick Start Guide

## Run the GUI Application
```bash
python3 gcode_processor.py
```

## Files Included
- **gcode_processor.py** - Main GUI application
- **gcode_processor_cli.py** - Command-line version
- **README.md** - Complete documentation
- **TEST_RESULTS.md** - Results from your test files
- **DisconnectedEndWaves-Cosine_modified.tap** - Example output
- **sample_gcode.tap** - Simple test file
- **run_gcode_processor.sh** - Launcher script

## What It Does
Reduces feedrate to F50 on G1 moves where:
- Multiple axes are moving (X, Y, Z, A)
- A-axis change is ≤ 0.5 degrees

## Your Test Results
- **Cosine file**: 2,458 lines modified (19.1%)
- **Sine file**: 2,567 lines modified (19.9%)

## Settings You Can Change
- A-axis threshold: 0.5° (default)
- New feedrate: 50 (default)

## Important Notes
- Original files are never overwritten
- Output files have "_modified" suffix
- All changes are logged in the GUI
- Properly handles modal G-code (G1 commands that apply to following lines)
