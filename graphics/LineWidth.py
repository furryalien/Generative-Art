"""
Line width management for generative art scripts
"""
import random
from graphics.Geometry import line_width as set_line_width


# Store the line width mode and value
_line_width_mode = None
_line_width_value = 1.0
_line_width_range = (0.3, 6.0)  # Default range for random widths


def parse_line_width_arg(arg):
    """
    Parse line width argument
    
    Formats:
        - Number (e.g., '2', '2.5') - Fixed width in pixels
        - 'random-by-line' - Each line gets its own random width
        - 'random-all' - All lines share one random width
        - None or 'False' - Use default width (1.0)
    
    Returns:
        Tuple of (mode, value) where mode is 'fixed', 'random-by-line', or 'random-all'
    """
    if not arg or arg.lower() == 'false':
        return ('fixed', 1.0)
    
    arg_lower = arg.lower().strip()
    
    if arg_lower == 'random-by-line':
        return ('random-by-line', None)
    elif arg_lower == 'random-all':
        # Generate one random width to be used for all lines
        width = random.uniform(*_line_width_range)
        return ('random-all', width)
    else:
        # Try to parse as a number
        try:
            width = float(arg)
            return ('fixed', width)
        except ValueError:
            # Default to 1.0 if invalid
            return ('fixed', 1.0)


def set_line_width_range(min_width, max_width):
    """Set the range for random line widths"""
    global _line_width_range
    _line_width_range = (min_width, max_width)


def init_line_width(mode, value):
    """Initialize line width settings"""
    global _line_width_mode, _line_width_value
    _line_width_mode = mode
    _line_width_value = value
    
    # If mode is fixed or random-all, set it once
    if mode == 'fixed':
        set_line_width(value)
    elif mode == 'random-all':
        set_line_width(value)


def apply_line_width():
    """
    Apply line width before drawing a line
    Call this before each stroke() if using random-by-line mode
    """
    if _line_width_mode == 'random-by-line':
        width = random.uniform(*_line_width_range)
        set_line_width(width)
    # For 'fixed' and 'random-all', width is already set in init_line_width


def get_line_width_mode():
    """Get current line width mode"""
    return _line_width_mode


def get_line_width_value():
    """Get current line width value (for fixed/random-all modes)"""
    return _line_width_value
