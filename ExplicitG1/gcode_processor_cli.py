#!/usr/bin/env python3
"""
Command-line version of GCode processor for testing
Usage: python3 gcode_processor_cli.py input_file.tap [threshold] [feedrate]
"""

import sys
import re
import os


class GCodeProcessorCLI:
    def __init__(self):
        self.previous_a_value = None
        self.current_motion_mode = None
    
    def extract_axis_value(self, line, axis):
        """Extract the value for a specific axis from a GCode line."""
        pattern = rf'{axis}([+-]?\d+\.?\d*)'
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None
    
    def parse_gcode_line(self, line):
        """Parse a GCode line and extract relevant information."""
        # Remove comments
        line = re.sub(r'\(.*?\)', '', line).strip()
        
        # Update motion mode if G command is present
        # G0 or G00 = rapid positioning (not followed by 1-9)
        if re.match(r'G0+(?![1-9])', line, re.IGNORECASE):
            self.current_motion_mode = 'G0'
            return None
        
        # G1 or G01 = linear interpolation
        if re.match(r'G0*1', line, re.IGNORECASE):
            self.current_motion_mode = 'G1'
        
        # Only process lines when in G1 mode
        if self.current_motion_mode != 'G1':
            return None
        
        # Extract axis values
        x = self.extract_axis_value(line, 'X')
        y = self.extract_axis_value(line, 'Y')
        z = self.extract_axis_value(line, 'Z')
        a = self.extract_axis_value(line, 'A')
        f = self.extract_axis_value(line, 'F')
        
        # Only process if there are actual axis moves
        if all(v is None for v in [x, y, z, a]):
            return None
        
        return {'X': x, 'Y': y, 'Z': z, 'A': a, 'F': f, 'original': line}
    
    def process_file(self, input_file, threshold1=1.5, feedrate1=100, threshold2=0.5, feedrate2=50, default_feedrate=380, large_diameter=None, small_diameter=None, length=None):
        """Process the GCode file."""
        print("=" * 80)
        print("GCode A-Axis Feedrate Adjuster - Command Line Version")
        print("=" * 80)
        print(f"Input file: {input_file}")
        print(f"Default Feedrate: F{default_feedrate}")
        print(f"Tier 1: A-axis ≤ {threshold1}° → F{feedrate1}")
        print(f"Tier 2: A-axis ≤ {threshold2}° → F{feedrate2}")
        
        # Check taper settings
        apply_taper = False
        radius_diff = 0
        
        if large_diameter is not None and small_diameter is not None and length is not None:
            if large_diameter <= 0 or small_diameter <= 0 or length <= 0:
                print("ERROR: All taper values must be positive!")
                return None
            
            if small_diameter >= large_diameter:
                print("ERROR: Small diameter must be less than large diameter!")
                return None
            
            apply_taper = True
            large_radius = large_diameter / 2.0
            small_radius = small_diameter / 2.0
            radius_diff = large_radius - small_radius
            
            print(f"Taper enabled: {large_diameter} → {small_diameter} over length {length}")
            print(f"Radius difference: {radius_diff}")
            print(f"Z adjustment rate: {radius_diff/length:.6f} per X unit")
        
        print("=" * 80)
        
        # Read input file
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        # Reset state
        self.previous_a_value = None
        self.current_motion_mode = None
        
        # First pass: parse all lines and extract A-axis values
        parsed_lines = []
        for line in lines:
            original_line = line.rstrip('\n')
            parsed = self.parse_gcode_line(original_line)
            parsed_lines.append({
                'original': line,
                'parsed': parsed,
                'has_explicit_g1': bool(re.match(r'G0*1', original_line.strip(), re.IGNORECASE))
            })
        
        # Second pass: process and modify lines
        modified_lines = []
        modifications_count = 0
        tier1_count = 0
        tier2_count = 0
        default_count = 0
        taper_count = 0
        modification_details = []
        previous_a_for_comparison = None
        current_modal_z = 0.0  # Track the current Z depth from G1Z commands
        
        for i, line_data in enumerate(parsed_lines):
            parsed = line_data['parsed']
            original_line = line_data['original'].rstrip('\n')
            has_explicit_g1 = line_data['has_explicit_g1']
            
            # Update modal Z if this line sets a new Z depth
            if parsed and parsed['Z'] is not None and parsed['X'] is None and parsed['Y'] is None:
                # This is a Z-only move (like G1Z-0.0071), update modal Z
                current_modal_z = parsed['Z']
            
            should_modify = False
            a_change = 0
            
            # Check if this line should be modified
            if parsed:
                # ONLY process lines that have an explicit A-axis value in them
                if parsed['A'] is not None:
                    current_a = parsed['A']
                    compare_a = None
                    
                    # Determine which A value to compare against
                    if has_explicit_g1:
                        # New G1 command - look forward to next A value
                        next_a = None
                        for j in range(i + 1, len(parsed_lines)):
                            if parsed_lines[j]['parsed'] and parsed_lines[j]['parsed']['A'] is not None:
                                next_a = parsed_lines[j]['parsed']['A']
                                break
                        
                        if next_a is not None:
                            a_change = abs(current_a - next_a)
                            compare_a = next_a
                    else:
                        # Modal G1 command - look backward to previous A value
                        if previous_a_for_comparison is not None:
                            a_change = abs(current_a - previous_a_for_comparison)
                            compare_a = previous_a_for_comparison
                    
                    # Update previous A value for next iteration
                    previous_a_for_comparison = current_a
            
            # Apply modification if needed
            line_to_output = original_line
            
            # For lines with A-axis, always set explicit feedrate based on tiers
            if parsed and parsed['A'] is not None and compare_a is not None:
                # Determine which tier this falls into
                if a_change <= threshold2:
                    # Tier 2: Smallest changes, slowest feedrate
                    line_to_output = re.sub(r'F[+-]?\d+\.?\d*', '', line_to_output, flags=re.IGNORECASE).strip()
                    line_to_output = f"{line_to_output} F{feedrate2}"
                    modifications_count += 1
                    tier2_count += 1
                    if modifications_count <= 10:
                        modification_details.append({
                            'line': i + 1,
                            'a_change': a_change,
                            'tier': 2,
                            'feedrate': feedrate2,
                            'original': original_line,
                            'modified': line_to_output
                        })
                elif a_change <= threshold1:
                    # Tier 1: Medium changes, medium feedrate
                    line_to_output = re.sub(r'F[+-]?\d+\.?\d*', '', line_to_output, flags=re.IGNORECASE).strip()
                    line_to_output = f"{line_to_output} F{feedrate1}"
                    modifications_count += 1
                    tier1_count += 1
                    if modifications_count <= 10:
                        modification_details.append({
                            'line': i + 1,
                            'a_change': a_change,
                            'tier': 1,
                            'feedrate': feedrate1,
                            'original': original_line,
                            'modified': line_to_output
                        })
                else:
                    # Above threshold1: Large changes, default feedrate
                    line_to_output = re.sub(r'F[+-]?\d+\.?\d*', '', line_to_output, flags=re.IGNORECASE).strip()
                    line_to_output = f"{line_to_output} F{default_feedrate}"
                    default_count += 1
            
            # Apply taper if needed (can be combined with feedrate modification)
            if apply_taper and parsed and parsed['X'] is not None:
                x_val = parsed['X']
                # Calculate Z adjustment based on X position
                # At X=length (large end): Z adjustment = 0 (no change)
                # At X=0 (small end): Z adjustment = -radius_diff (deeper cut)
                # Formula: as X decreases toward 0, Z goes more negative (deeper)
                z_adjustment = -radius_diff * (1.0 - (x_val / length))
                
                # Calculate the actual Z position: modal Z + taper adjustment
                actual_z = current_modal_z + z_adjustment
                
                # Modify the Z value if present, or add it if not
                if parsed['Z'] is not None:
                    # Line already has Z, add adjustment to it
                    new_z = parsed['Z'] + z_adjustment
                    line_to_output = re.sub(r'Z[+-]?\d+\.?\d*', f'Z{new_z:.4f}', line_to_output, flags=re.IGNORECASE)
                else:
                    # Add Z value after the X value (modal Z + taper adjustment)
                    line_to_output = re.sub(r'(X[+-]?\d+\.?\d*)', rf'\1Z{actual_z:.4f}', line_to_output, flags=re.IGNORECASE)
                
                taper_count += 1
            
            modified_lines.append(line_to_output + '\n' if not line_to_output.endswith('\n') else line_to_output)
        
        # Generate output filename - write to current directory
        input_basename = os.path.basename(input_file)
        base, ext = os.path.splitext(input_basename)
        output_file = f"{base}_modified{ext}"
        
        # Write output file
        with open(output_file, 'w') as f:
            f.writelines(modified_lines)
        
        # Print summary
        print(f"\nProcessing complete!")
        print(f"Total lines: {len(lines)}")
        print(f"\nFeedrate Modifications:")
        print(f"  • Tier 2 (≤ {threshold2}°): {tier2_count} lines → F{feedrate2}")
        print(f"  • Tier 1 (≤ {threshold1}°): {tier1_count} lines → F{feedrate1}")
        print(f"  • Default (> {threshold1}°): {default_count} lines → F{default_feedrate}")
        print(f"  • Total: {modifications_count} feedrate changes")
        if apply_taper:
            print(f"\nTaper: {taper_count} X-axis moves adjusted")
        print(f"\nOutput file: {output_file}")
        
        if modification_details:
            print(f"\nFirst {len(modification_details)} modifications:")
            print("-" * 80)
            for mod in modification_details:
                tier_info = f" (Tier {mod['tier']}) → F{mod['feedrate']}" if 'tier' in mod else ""
                print(f"Line {mod['line']}: A-change = {mod['a_change']:.4f}°{tier_info}")
                print(f"  Before: {mod['original']}")
                print(f"  After:  {mod['modified']}")
        
        print("=" * 80)
        return output_file


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 gcode_processor_cli.py input_file.tap [threshold1] [feedrate1] [threshold2] [feedrate2] [default_feedrate] [large_dia] [small_dia] [length]")
        print("  threshold1: Tier 1 A-axis threshold in degrees (default: 1.5)")
        print("  feedrate1: Tier 1 feedrate (default: 100)")
        print("  threshold2: Tier 2 A-axis threshold in degrees (default: 0.5)")
        print("  feedrate2: Tier 2 feedrate (default: 50)")
        print("  default_feedrate: Default feedrate for large changes (default: 380)")
        print("  large_dia: Large end diameter for taper (optional)")
        print("  small_dia: Small end diameter for taper (optional)")
        print("  length: Length (X axis) for taper (optional)")
        print("\nExample: python3 gcode_processor_cli.py file.tap 1.5 100 0.5 50 380")
        sys.exit(1)
    
    input_file = sys.argv[1]
    threshold1 = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    feedrate1 = float(sys.argv[3]) if len(sys.argv) > 3 else 100
    threshold2 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    feedrate2 = float(sys.argv[5]) if len(sys.argv) > 5 else 50
    default_feedrate = float(sys.argv[6]) if len(sys.argv) > 6 else 380
    
    # Taper parameters (all three must be provided together)
    large_dia = float(sys.argv[7]) if len(sys.argv) > 7 else None
    small_dia = float(sys.argv[8]) if len(sys.argv) > 8 else None
    length = float(sys.argv[9]) if len(sys.argv) > 9 else None
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found!")
        sys.exit(1)
    
    processor = GCodeProcessorCLI()
    processor.process_file(input_file, threshold1, feedrate1, threshold2, feedrate2, default_feedrate, large_dia, small_dia, length)


if __name__ == "__main__":
    main()
