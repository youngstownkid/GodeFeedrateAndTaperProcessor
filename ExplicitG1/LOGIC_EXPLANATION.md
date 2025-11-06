# Processing Logic - Forward vs Backward Looking

## The Rule

The application uses different comparison logic depending on whether a line has an **explicit G1 command** or is using **modal G1**:

### Explicit G1 Commands → Look FORWARD
When a line starts with `G1` or `G01`, compare its A-axis value with the **next** A-axis value.

**Example:**
```gcode
Line 51: X0.0000A89.9993         (modal G1, A = 89.9993°)
Line 52: G1Z-0.0143F6.5          (explicit G1, no A)
Line 53: G1X0.0377A89.9399F21.0  (explicit G1, A = 89.9399°) → Compare with next
Line 54: X0.0751A89.7634         (modal G1, A = 89.7634°)    ← Next A value
```

**Line 53 comparison:**
- Current A: 89.9399°
- Next A (line 54): 89.7634°
- Change: 0.1765° ✓ Modified because ≤ 0.5°

### Modal G1 Commands → Look BACKWARD
When a line doesn't start with `G1` but is in G1 mode (inherits from previous G1), compare with the **previous** A-axis value.

**Example:**
```gcode
Line 53: G1X0.0377A89.9399F21.0  (explicit G1, A = 89.9399°)
Line 54: X0.0751A89.7634         (modal G1, A = 89.7634°) → Compare with previous
```

**Line 54 comparison:**
- Current A: 89.7634°
- Previous A (line 53): 89.9399°
- Change: 0.1765° ✓ Modified because ≤ 0.5°

## Why This Matters

This approach correctly handles **G1 commands that start new motion sequences**, ensuring that:

1. When a new explicit G1 starts, we look at where it's **going** (forward)
2. For modal moves continuing a sequence, we look at where we **came from** (backward)

## Lines Without A-Axis

When a line has no A-axis value (like `G1Z-0.0143F6.5`):
- The A-axis maintains its last commanded position
- It doesn't reset the tracking
- The previous A value persists for the next comparison

## Results

With this logic:
- **Total lines modified**: 2,518
- Correctly handles both explicit and modal G1 commands
- Properly tracks A-axis position through moves that don't command A

## Visual Example

```gcode
G1X1.0A10.0F100   ← Explicit G1: Compare A10.0 with NEXT (A10.3)
X2.0A10.3         ← Modal: Compare A10.3 with PREVIOUS (A10.0)
X3.0A10.4         ← Modal: Compare A10.4 with PREVIOUS (A10.3)
G1Z-1.0F50        ← G1 with no A (A stays at 10.4)
G1X4.0A10.6F100   ← Explicit G1: Compare A10.6 with NEXT (A10.8)
X5.0A10.8         ← Modal: Compare A10.8 with PREVIOUS (A10.6)
```

All lines with A-axis changes ≤ 0.5° will have feedrate changed to F50.
