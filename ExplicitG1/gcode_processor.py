import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import os
import json


class GCodeProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("GCode A-Axis Feedrate Adjuster")
        self.root.geometry("1100x700")
        self.root.minsize(600, 500)  # Minimum size for usability
        self.root.resizable(True, True)
        
        self.selected_file = None
        self.previous_a_value = None
        self.current_motion_mode = None
        
        # Config file to save settings
        self.config_file = os.path.join(os.path.expanduser("~"), ".gcode_processor_config.json")
        
        self.setup_ui()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.default_feedrate_var.set(config.get('default_feedrate', '380'))
                    self.threshold1_var.set(config.get('threshold1', '1.5'))
                    self.feedrate1_var.set(config.get('feedrate1', '100'))
                    self.threshold2_var.set(config.get('threshold2', '0.5'))
                    self.feedrate2_var.set(config.get('feedrate2', '50'))
                    self.large_diameter_var.set(config.get('large_diameter', ''))
                    self.small_diameter_var.set(config.get('small_diameter', ''))
                    self.length_var.set(config.get('length', ''))
            except:
                pass  # If config file is corrupted, just use defaults
    
    def save_settings(self):
        """Save current settings to config file."""
        try:
            config = {
                'default_feedrate': self.default_feedrate_var.get(),
                'threshold1': self.threshold1_var.get(),
                'feedrate1': self.feedrate1_var.get(),
                'threshold2': self.threshold2_var.get(),
                'feedrate2': self.feedrate2_var.get(),
                'large_diameter': self.large_diameter_var.get(),
                'small_diameter': self.small_diameter_var.get(),
                'length': self.length_var.get()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass  # Don't fail if we can't save settings
    
    def setup_ui(self):
        # Configure modern color scheme
        self.bg_dark = "#1e1e2e"
        self.bg_medium = "#2d2d44"
        self.bg_light = "#3d3d5c"
        self.accent_blue = "#89b4fa"
        self.accent_green = "#a6e3a1"
        self.accent_red = "#f38ba8"
        self.text_color = "#cdd6f4"
        self.text_dim = "#9399b2"
        
        # Configure root window
        self.root.configure(bg=self.bg_dark)
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for ttk widgets
        style.configure('TFrame', background=self.bg_dark)
        style.configure('TLabel', background=self.bg_dark, foreground=self.text_color, font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=self.accent_blue)
        style.configure('Subtitle.TLabel', font=('Segoe UI', 11, 'bold'), foreground=self.accent_green)
        style.configure('Dim.TLabel', foreground=self.text_dim, font=('Segoe UI', 9))
        
        style.configure('TButton', 
                       background=self.accent_blue, 
                       foreground='#1e1e2e',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        style.map('TButton',
                 background=[('active', '#74c7ec'), ('disabled', self.bg_light)],
                 foreground=[('disabled', self.text_dim)])
        
        style.configure('Accent.TButton',
                       background=self.accent_green,
                       foreground='#1e1e2e',
                       font=('Segoe UI', 12, 'bold'),
                       padding=15)
        style.map('Accent.TButton',
                 background=[('active', '#94e2d5')])
        
        style.configure('TEntry',
                       fieldbackground=self.bg_light,
                       foreground=self.text_color,
                       borderwidth=2,
                       relief='flat',
                       insertcolor=self.text_color)
        
        style.configure('TLabelframe',
                       background=self.bg_dark,
                       foreground=self.accent_blue,
                       borderwidth=2,
                       relief='flat')
        style.configure('TLabelframe.Label',
                       background=self.bg_dark,
                       foreground=self.accent_blue,
                       font=('Segoe UI', 11, 'bold'))
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for two-column layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Left column
        main_frame.columnconfigure(1, weight=2)  # Right column (log) - bigger
        main_frame.rowconfigure(0, weight=1)
        
        # LEFT COLUMN - Settings
        left_column = ttk.Frame(main_frame, style='TFrame')
        left_column.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        left_column.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(left_column, text="⚙️ GCode Processor", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.Frame(left_column, style='TFrame')
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        ttk.Label(file_frame, text="📁 File:", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.file_label = ttk.Label(file_frame, text="No file selected", 
                                     style='Dim.TLabel', wraplength=300)
        self.file_label.grid(row=1, column=0, sticky=tk.W)
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=2, column=0, pady=(10, 0), sticky=tk.W)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(left_column, text="⚙️ Settings", padding="15")
        settings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        settings_frame.columnconfigure(1, weight=1)
        
        # Default feedrate
        row = 0
        ttk.Label(settings_frame, text="Default Feedrate:").grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=(0, 15)
        )
        self.default_feedrate_var = tk.StringVar(value="380")
        default_feedrate_entry = ttk.Entry(settings_frame, textvariable=self.default_feedrate_var, width=12)
        default_feedrate_entry.grid(row=row, column=1, sticky=tk.W, pady=8)
        
        # Separator
        row += 1
        separator1 = ttk.Separator(settings_frame, orient=tk.HORIZONTAL)
        separator1.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        # Tier 1 - Below threshold 1
        row += 1
        ttk.Label(settings_frame, text="🎯 Tier 1", 
                  style='Subtitle.TLabel').grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 8)
        )
        
        row += 1
        ttk.Label(settings_frame, text="A-Axis Delta Below:").grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=(0, 15)
        )
        self.threshold1_var = tk.StringVar(value="1.5")
        threshold1_entry = ttk.Entry(settings_frame, textvariable=self.threshold1_var, width=12)
        threshold1_entry.grid(row=row, column=1, sticky=tk.W, pady=8)
        
        row += 1
        ttk.Label(settings_frame, text="Reduced Feedrate 1:").grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=(0, 15)
        )
        self.feedrate1_var = tk.StringVar(value="100")
        feedrate1_entry = ttk.Entry(settings_frame, textvariable=self.feedrate1_var, width=12)
        feedrate1_entry.grid(row=row, column=1, sticky=tk.W, pady=8)
        
        # Separator
        row += 1
        separator2 = ttk.Separator(settings_frame, orient=tk.HORIZONTAL)
        separator2.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        # Tier 2 - Below threshold 2
        row += 1
        ttk.Label(settings_frame, text="🎯 Tier 2", 
                  style='Subtitle.TLabel').grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 8)
        )
        
        row += 1
        ttk.Label(settings_frame, text="A-Axis Delta Below:").grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=(0, 15)
        )
        self.threshold2_var = tk.StringVar(value="0.5")
        threshold2_entry = ttk.Entry(settings_frame, textvariable=self.threshold2_var, width=12)
        threshold2_entry.grid(row=row, column=1, sticky=tk.W, pady=8)
        
        row += 1
        ttk.Label(settings_frame, text="Reduced Feedrate 2:").grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=(0, 15)
        )
        self.feedrate2_var = tk.StringVar(value="50")
        feedrate2_entry = ttk.Entry(settings_frame, textvariable=self.feedrate2_var, width=12)
        feedrate2_entry.grid(row=row, column=1, sticky=tk.W, pady=8)
        
        # Separator
        row += 1
        separator = ttk.Separator(settings_frame, orient=tk.HORIZONTAL)
        separator.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        # Taper settings label
        row += 1
        ttk.Label(settings_frame, text="🔺 Taper (Optional)", 
                  style='Subtitle.TLabel').grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 8)
        )
        
        row += 1
        ttk.Label(settings_frame, text="Large End Diameter:").grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=(0, 15)
        )
        self.large_diameter_var = tk.StringVar(value="")
        large_diameter_entry = ttk.Entry(settings_frame, textvariable=self.large_diameter_var, width=12)
        large_diameter_entry.grid(row=row, column=1, sticky=tk.W, pady=8)
        
        row += 1
        ttk.Label(settings_frame, text="Small End Diameter:").grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=(0, 15)
        )
        self.small_diameter_var = tk.StringVar(value="")
        small_diameter_entry = ttk.Entry(settings_frame, textvariable=self.small_diameter_var, width=12)
        small_diameter_entry.grid(row=row, column=1, sticky=tk.W, pady=8)
        
        row += 1
        ttk.Label(settings_frame, text="Length (X axis):").grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=(0, 15)
        )
        self.length_var = tk.StringVar(value="")
        length_entry = ttk.Entry(settings_frame, textvariable=self.length_var, width=12)
        length_entry.grid(row=row, column=1, sticky=tk.W, pady=8)
        
        row += 1
        ttk.Label(settings_frame, text="Leave blank to disable taper", 
                  style='Dim.TLabel').grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        
        # Run button - big and prominent
        self.run_btn = ttk.Button(left_column, text="🚀 Run Processing", 
                                   command=self.process_file, state=tk.DISABLED,
                                   style='Accent.TButton')
        self.run_btn.grid(row=3, column=0, pady=20, sticky=(tk.W, tk.E))
        
        # RIGHT COLUMN - Processing Log (reading pane style)
        right_column = ttk.Frame(main_frame, style='TFrame')
        right_column.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_column.columnconfigure(0, weight=1)
        right_column.rowconfigure(1, weight=1)
        
        # Log title
        log_title = ttk.Label(right_column, text="📋 Processing Log", style='Title.TLabel')
        log_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # Log frame
        log_frame = ttk.Frame(right_column, style='TFrame')
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD,
                               bg=self.bg_light, fg=self.text_color,
                               insertbackground=self.accent_blue,
                               selectbackground=self.accent_blue,
                               selectforeground=self.bg_dark,
                               font=('Consolas', 9),
                               borderwidth=0,
                               relief='flat',
                               padx=15, pady=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Configure text tags for colored output
        self.log_text.tag_configure('success', foreground=self.accent_green)
        self.log_text.tag_configure('error', foreground=self.accent_red)
        self.log_text.tag_configure('info', foreground=self.accent_blue)
        
        # Store references to columns for responsive layout
        self.left_column = left_column
        self.right_column = right_column
        
        # Bind window resize event for responsive layout
        self.root.bind('<Configure>', self.on_window_resize)
        self.current_layout = 'two-column'  # Track current layout
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select GCode File",
            filetypes=[("TAP files", "*.tap"), ("GCode files", "*.gcode"), ("All files", "*.*")]
        )
        
        if filename:
            self.selected_file = filename
            display_name = os.path.basename(filename)
            self.file_label.config(text=display_name, foreground=self.accent_green, font=('Segoe UI', 10, 'bold'))
            self.run_btn.config(state=tk.NORMAL)
            self.log_message(f"✓ File selected: {display_name}", 'success')
    
    def on_window_resize(self, event):
        """Handle window resize to switch between single and two-column layouts."""
        # Only respond to window resize events, not widget resizes
        if event.widget != self.root:
            return
        
        width = self.root.winfo_width()
        
        # Breakpoint at 900px width
        if width < 900 and self.current_layout == 'two-column':
            # Switch to single column (stacked) layout
            self.current_layout = 'single-column'
            self.left_column.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=0)
            self.right_column.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
            self.root.grid_columnconfigure(0, weight=1)
            
        elif width >= 900 and self.current_layout == 'single-column':
            # Switch to two-column (side-by-side) layout
            self.current_layout = 'two-column'
            self.left_column.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
            self.right_column.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=0)
    
    def log_message(self, message, tag=None):
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
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
    
    def process_file(self):
        if not self.selected_file:
            messagebox.showerror("Error", "No file selected!")
            return
        
        # Save settings for next time
        self.save_settings()
        
        try:
            default_feedrate = float(self.default_feedrate_var.get())
            threshold1 = float(self.threshold1_var.get())
            feedrate1 = float(self.feedrate1_var.get())
            threshold2 = float(self.threshold2_var.get())
            feedrate2 = float(self.feedrate2_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid feedrate or threshold value!")
            return
        
        # Validate that threshold2 < threshold1
        if threshold2 >= threshold1:
            messagebox.showerror("Error", "Tier 2 threshold must be less than Tier 1 threshold!")
            return
        
        # Check taper settings
        apply_taper = False
        large_diameter = 0
        small_diameter = 0
        length = 0
        
        if (self.large_diameter_var.get().strip() and 
            self.small_diameter_var.get().strip() and 
            self.length_var.get().strip()):
            try:
                large_diameter = float(self.large_diameter_var.get())
                small_diameter = float(self.small_diameter_var.get())
                length = float(self.length_var.get())
                
                if large_diameter <= 0 or small_diameter <= 0 or length <= 0:
                    messagebox.showerror("Error", "All taper values must be positive!")
                    return
                
                if small_diameter >= large_diameter:
                    messagebox.showerror("Error", "Small diameter must be less than large diameter!")
                    return
                
                apply_taper = True
                large_radius = large_diameter / 2.0
                small_radius = small_diameter / 2.0
                radius_diff = large_radius - small_radius
                
                self.log_message(f"Taper enabled: {large_diameter} → {small_diameter} over length {length}")
                self.log_message(f"Radius difference: {radius_diff}")
                self.log_message(f"Z adjustment rate: {radius_diff/length:.6f} per X unit")
            except ValueError:
                messagebox.showerror("Error", "Invalid taper values!")
                return
        
        self.log_text.delete(1.0, tk.END)
        self.log_message("=" * 70)
        self.log_message("Starting GCode processing...")
        self.log_message(f"Default Feedrate: F{default_feedrate}")
        self.log_message(f"Tier 1: A-axis ≤ {threshold1}° → F{feedrate1}")
        self.log_message(f"Tier 2: A-axis ≤ {threshold2}° → F{feedrate2}")
        if apply_taper:
            self.log_message(f"Taper: {large_diameter} → {small_diameter} over length {length}")
        self.log_message("=" * 70)
        
        try:
            # Read input file
            with open(self.selected_file, 'r') as f:
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
                        
                        # Check if we should modify
                        if compare_a is not None and a_change <= threshold2:
                            should_modify = True
                        
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
                    elif a_change <= threshold1:
                        # Tier 1: Medium changes, medium feedrate
                        line_to_output = re.sub(r'F[+-]?\d+\.?\d*', '', line_to_output, flags=re.IGNORECASE).strip()
                        line_to_output = f"{line_to_output} F{feedrate1}"
                        modifications_count += 1
                        tier1_count += 1
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
            
            # Generate output filename
            base, ext = os.path.splitext(self.selected_file)
            output_file = f"{base}_modified{ext}"
            
            # Write output file
            with open(output_file, 'w') as f:
                f.writelines(modified_lines)
            
            self.log_message("=" * 70)
            self.log_message(f"✓ Processing complete!", 'success')
            self.log_message(f"Total lines processed: {len(lines)}")
            self.log_message("")
            self.log_message("Feedrate Modifications:", 'info')
            self.log_message(f"  • Tier 2 (≤ {threshold2}°): {tier2_count} lines → F{feedrate2}")
            self.log_message(f"  • Tier 1 (≤ {threshold1}°): {tier1_count} lines → F{feedrate1}")
            self.log_message(f"  • Default (> {threshold1}°): {default_count} lines → F{default_feedrate}")
            self.log_message(f"  • Total feedrate changes: {modifications_count}", 'info')
            if apply_taper:
                self.log_message("")
                self.log_message(f"Taper: {taper_count} X-axis moves adjusted", 'info')
            self.log_message("")
            self.log_message(f"Output file: {os.path.basename(output_file)}", 'success')
            self.log_message("=" * 70)
            
            summary = f"Processing complete!\n\n"
            summary += f"Feedrate Modifications:\n"
            summary += f"  • Tier 2: {tier2_count} lines\n"
            summary += f"  • Tier 1: {tier1_count} lines\n"
            summary += f"  • Default: {default_count} lines\n"
            if apply_taper:
                summary += f"\nTaper: {taper_count} X-axis moves\n"
            summary += f"\nOutput saved to:\n{output_file}"
            
            messagebox.showinfo("Success", summary)
        
        except Exception as e:
            self.log_message(f"✗ ERROR: {str(e)}", 'error')
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")


def main():
    root = tk.Tk()
    app = GCodeProcessor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
