# GCode A-Axis Feedrate Adjuster

A desktop application that processes GCode (.tap) files and automatically adjusts feedrates for multi-axis moves with small A-axis changes.

## Features

- Browse and select GCode/TAP files via file dialog
- Automatically detects G1 commands with multiple axes
- Adjusts feedrate to 50 (configurable) when A-axis change is ≤ 0.5 degrees (configurable)
- Real-time processing log showing all modifications
- Saves modified GCode to a new file with "_modified" suffix

## Requirements

- Python 3.x
- tkinter (usually included with Python, or install via: `apt-get install python3-tk` on Linux)

## Usage

1. Run the application:
   ```bash
   python gcode_processor.py
   ```

2. Click "Browse File" and select your GCode (.tap) file

3. (Optional) Adjust settings:
   - **A-Axis Change Threshold**: Maximum A-axis change in degrees (default: 0.5)
   - **Reduced Feedrate**: New feedrate value to apply (default: 50)

4. Click "Run Processing" to process the file

5. The modified file will be saved with "_modified" added to the filename

## How It Works

The application:
1. Reads each line of the GCode file
2. Tracks the current motion mode (G0 for rapid moves, G1 for linear interpolation)
3. Identifies G1 commands (explicit or modal) with multiple axes (X, Y, Z, A)
4. Tracks the A-axis value between consecutive moves
5. When a multi-axis move has an A-axis change of ≤ 0.5° (threshold):
   - Removes any existing feedrate (F) value
   - Adds the new feedrate (F50 by default)
6. Logs all modifications for review

**Note**: The application properly handles modal G-code commands. Once a G1 command is issued, subsequent lines with axis coordinates are treated as G1 moves until a different G-code is encountered.

## Test Results

Testing with real GCode files shows:
- **DisconnectedEndWaves-Cosine.tap**: 2,566 lines modified (19.9% of G1 moves)
- **DisconnectedEndWaves-Sine.tap**: 2,567 lines modified (19.9% of G1 moves)
- Average A-axis change in modified lines: ~0.22°
- A-axis changes range from 0° to 0.47°

## Example

**Before:**
```gcode
G1 X10.0 Y5.0 A0.3 F200
G1 X15.0 Y10.0 A0.6 F200
```

**After:**
```gcode
G1 X10.0 Y5.0 A0.3 F200
G1 X15.0 Y10.0 A0.6 F50
```
*(A-axis changed by 0.3°, which is ≤ 0.5°, so feedrate reduced to 50)*

## Notes

- Single-axis A moves are NOT modified
- Moves without an A-axis value are NOT modified
- The original file is preserved; a new "_modified" file is created
- All modifications are logged in the processing window

## Test File

A sample test file (`sample_gcode.tap`) is included for testing the application.
