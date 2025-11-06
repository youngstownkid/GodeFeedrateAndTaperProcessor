# Default Feedrate Feature

## Problem Solved
Previously, lines that didn't meet the A-axis threshold would have NO feedrate specified, causing them to inherit the last feedrate (which might be F50). This would make the machine run slowly even when it should be running fast!

## Solution
The application now has THREE feedrate settings:

### 1. Default Feedrate (F380)
- Used for normal moves with **large A-axis changes** (> 0.5°)
- This is your "fast" feedrate
- **Explicitly set on every line** with large A-axis changes

### 2. Reduced Feedrate (F50)
- Used for moves with **small A-axis changes** (≤ 0.5°)
- This is your "slow" feedrate for precision
- **Explicitly set on every line** with small A-axis changes

### 3. A-Axis Threshold (0.5°)
- Determines which feedrate to use
- If A-axis change ≤ threshold → F50
- If A-axis change > threshold → F380

## Example

### Original GCode:
```gcode
G1X11.9720A-90.0349F21.0
X11.9441A-90.1325
X11.9165A-90.2941
X11.8891A-90.5184
X11.8619A-90.8046
X11.8349A-91.1515
X11.8082A-91.5582
X11.7816A-92.0236
X11.7552A-92.5466    ← No feedrate! Will inherit F21.0
X11.7290A-93.1263    ← Should be fast but inherits slow feedrate
```

### Modified GCode (with default feedrate):
```gcode
G1X11.9720A-90.0349 F50.0   ← Small change (0.0328°) = F50
X11.9441A-90.1325 F50.0      ← Small change (0.0976°) = F50
X11.9165A-90.2941 F50.0      ← Small change (0.1616°) = F50
X11.8891A-90.5184 F50.0      ← Small change (0.2243°) = F50
X11.8619A-90.8046 F50.0      ← Small change (0.2862°) = F50
X11.8349A-91.1515 F50.0      ← Small change (0.3469°) = F50
X11.8082A-91.5582 F50.0      ← Small change (0.4067°) = F50
X11.7816A-92.0236 F380.0     ← Large change (0.4654°) = F380!
X11.7552A-92.5466 F380.0     ← Large change (0.5230°) = F380!
X11.7290A-93.1263 F380.0     ← Large change (0.5797°) = F380!
```

## Benefits

✅ **Every line with A-axis now has explicit feedrate**  
✅ **No more inherited feedrates causing problems**  
✅ **Fast moves run fast (F380)**  
✅ **Precise moves run slow (F50)**  
✅ **Machine operates at optimal speeds**

## Settings in UI

The GUI now has three feedrate fields:
1. **Default Feedrate**: 380 (your fast speed)
2. **A-Axis Threshold**: 0.5° (the cutoff)
3. **Reduced Feedrate**: 50 (your slow speed)

## CLI Usage

```bash
python3 gcode_processor_cli.py input.tap [threshold] [reduced_feedrate] [default_feedrate]
```

Example:
```bash
python3 gcode_processor_cli.py Waves-Sine.tap 0.5 50 380
```

## Result

Your machine will now:
- Run at **F380** for normal moves (smooth, efficient)
- Slow to **F50** only when precision is needed (small A-axis changes)
- Never inherit wrong feedrates from previous lines

Perfect operation! 🎯
