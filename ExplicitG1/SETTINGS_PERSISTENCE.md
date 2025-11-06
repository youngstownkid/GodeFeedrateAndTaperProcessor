# Settings Persistence Feature

## Overview
The GCode Processor GUI now automatically remembers your settings between sessions!

## How It Works

### Automatic Save
When you click "Run Processing", the application saves all current settings to a config file:
- A-Axis Threshold
- Reduced Feedrate
- Large End Diameter
- Small End Diameter
- Length

### Automatic Load
When you open the application, it automatically loads the last used settings from the config file.

## Config File Location

The settings are stored in your home directory:
- **Windows**: `C:\Users\YourName\.gcode_processor_config.json`
- **Mac/Linux**: `~/.gcode_processor_config.json`

## Config File Format

The file is a simple JSON file that looks like this:
```json
{
  "threshold": "0.5",
  "feedrate": "50",
  "large_diameter": "2.0",
  "small_diameter": "1.5",
  "length": "2.0"
}
```

## Benefits

- **No need to re-enter settings** every time you use the app
- **Faster workflow** - your typical settings are ready to go
- **Consistent results** - use the same settings across multiple sessions

## Notes

- Settings are saved when you click "Run Processing"
- If the config file doesn't exist (first run), default values are used
- If the config file is corrupted, the app will use defaults and continue working
- You can manually edit the config file if needed (it's just a text file)
- The config file is hidden (starts with a dot) on Mac/Linux

## Default Values

If no config file exists, these defaults are used:
- **Threshold**: 0.5°
- **Feedrate**: 50
- **Taper fields**: Empty (no taper)
