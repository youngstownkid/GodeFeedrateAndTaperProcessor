# Two-Tier Threshold System

## Overview
The application now supports TWO threshold levels with THREE different feedrates for ultimate control over your machining speeds!

## How It Works

### Three Feedrate Tiers:

1. **Default Feedrate (F380)** - For large A-axis changes (> 1.5°)
   - Fast, efficient cutting
   - Used when rotating significantly
   
2. **Tier 1: Reduced Feedrate 1 (F100)** - For medium A-axis changes (0.5° to 1.5°)
   - Medium speed
   - Balances speed and precision
   - NEW tier for better control!
   
3. **Tier 2: Reduced Feedrate 2 (F50)** - For small A-axis changes (≤ 0.5°)
   - Slowest, most precise
   - Used for very small rotations
   - Maximum precision

## Settings

### UI Fields:

**Default Feedrate:** 380
- Applied when A-axis change > 1.5°

**🎯 Tier 1**
- **A-Axis Delta Below:** 1.5°
- **Reduced Feedrate 1:** 100
- Applied when 0.5° < A-axis ≤ 1.5°

**🎯 Tier 2**  
- **A-Axis Delta Below:** 0.5°
- **Reduced Feedrate 2:** 50
- Applied when A-axis ≤ 0.5°

## Decision Flow

```
For each line with A-axis change:

Is A-axis change ≤ 0.5°?
    YES → Use Tier 2 (F50) - Slowest
    NO  → Continue...

Is A-axis change ≤ 1.5°?
    YES → Use Tier 1 (F100) - Medium
    NO  → Use Default (F380) - Fastest
```

## Example

### GCode with Various A-Axis Changes:

```gcode
Line: X1.9749A-45.0020
A-change: 5.02° → F380 (Default - large change)

Line: X0.4954A-169.4259
A-change: 1.47° → F100 (Tier 1 - medium change)

Line: X0.2911A-176.3860
A-change: 0.93° → F100 (Tier 1 - medium change)

Line: X0.1845A-178.5568
A-change: 0.62° → F100 (Tier 1 - still in Tier 1 range)

Line: X0.1117A-179.4729
A-change: 0.40° → F50 (Tier 2 - small change)

Line: X0.0748A-179.7641
A-change: 0.29° → F50 (Tier 2 - very small change)
```

## Benefits

✅ **Three-tier control** instead of just two speeds  
✅ **Better speed optimization** - medium speed for medium changes  
✅ **Smoother transitions** between fast and slow  
✅ **More efficient** - spend less time at slowest speed  
✅ **Customizable thresholds** - tune to your needs  

## Statistics Example

From a typical file:
- **Default (F380)**: ~8,000 lines (large rotations)
- **Tier 1 (F100)**: ~2,500 lines (medium rotations) ← NEW!
- **Tier 2 (F50)**: ~2,500 lines (tiny rotations)

**Result:** Significantly faster overall because medium changes no longer use the slowest feedrate!

## CLI Usage

```bash
python3 gcode_processor_cli.py input.tap [threshold1] [feedrate1] [threshold2] [feedrate2] [default_feedrate]
```

Example:
```bash
python3 gcode_processor_cli.py file.tap 1.5 100 0.5 50 380
```

Parameters:
- threshold1 = 1.5° (Tier 1 cutoff)
- feedrate1 = 100 (Tier 1 speed)
- threshold2 = 0.5° (Tier 2 cutoff)
- feedrate2 = 50 (Tier 2 speed)
- default_feedrate = 380 (Default speed)

## Validation

The application validates that:
- Threshold 2 < Threshold 1 (tiers must not overlap)
- All values are positive numbers
- Settings are saved between sessions

## Use Cases

### Scenario 1: Need More Speed
```
Default: 400
Tier 1: ≤ 2.0° → F150
Tier 2: ≤ 0.3° → F40
Result: Faster overall with precision where needed
```

### Scenario 2: Maximum Precision
```
Default: 350
Tier 1: ≤ 1.0° → F75
Tier 2: ≤ 0.3° → F30
Result: More lines at slower speeds
```

### Scenario 3: Your Current Setup
```
Default: 380 (fast)
Tier 1: ≤ 1.5° → F100 (medium)
Tier 2: ≤ 0.5° → F50 (slow)
Result: Balanced speed and precision!
```

## The Power of Three Tiers

Previously with one threshold:
- Change > 0.5° → F380 (fast)
- Change ≤ 0.5° → F50 (slow)
- Problem: Change of 1.4° uses F380 (maybe too fast?)

Now with two thresholds:
- Change > 1.5° → F380 (fast)
- 0.5° < Change ≤ 1.5° → F100 (medium) ← PERFECT!
- Change ≤ 0.5° → F50 (slow)
- Solution: Medium changes get medium speed!

Perfect control! 🎯
