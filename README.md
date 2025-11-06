This program was designed to update TAP (GCODE) files that were created in VCarve.

VCarve doesn't support tapering, so this program adds the ability to cut tapered files, such as cue parts.

When setting up VCarve to cut using 4th Axis (A Axis), the actual rate of cutting really slows down a lot, 
except when  the A axis change is slight, so this program rewrites commands and tracks the change in the A axis,
so that the feedrate can be modified accordingly to speed up the process.

For example, if the normal output from VCarve has the feedrate set at F21...
on the UI for this program, 
you can specify what you want the faster feedrate to be (the Default Feedrate field)
and you can specify what you want the feedrate to be when the a axis change gets below two different tiers,
so what seems to work well is to change the feedrate to 100 when it's less than 1.5 degrees,
then change the feedrate again to 50 when the a axis change is less than half a degree.

If we don't to the tiered feedrates, then the default feedrate could be too fast when cutting straight it really close to straight, and we can break a bit.
