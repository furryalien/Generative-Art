"""
Paper size definitions with DPI settings for print-quality artwork
"""

# DPI (dots per inch) settings for different quality levels
DPI_HIGH = 300      # High quality print
DPI_MEDIUM = 200    # Medium quality print
DPI_DRAFT = 150     # Draft quality

# Paper sizes in millimeters (width, height) - portrait orientation
PAPER_SIZES_MM = {
    'a6': (105, 148),
    'a5': (148, 210),
    'a4': (210, 297),
    'a3': (297, 420),
    'letter': (216, 279),    # US Letter
    'legal': (216, 356),     # US Legal
    'square-small': (100, 100),
    'square-medium': (200, 200),
    'square-large': (300, 300),
}


def mm_to_pixels(mm, dpi=DPI_HIGH):
    """Convert millimeters to pixels at given DPI"""
    return int((mm / 25.4) * dpi)


def get_paper_size(size_name, dpi=DPI_HIGH, landscape=False):
    """
    Get pixel dimensions for a paper size
    
    Args:
        size_name: Paper size name (e.g., 'a6', 'a4', 'letter')
        dpi: Dots per inch (default: 300 for high quality)
        landscape: If True, swap width and height
    
    Returns:
        Tuple of (width, height) in pixels
    """
    size_name = size_name.lower()
    
    if size_name not in PAPER_SIZES_MM:
        raise ValueError(f"Unknown paper size: {size_name}. Available sizes: {', '.join(PAPER_SIZES_MM.keys())}")
    
    width_mm, height_mm = PAPER_SIZES_MM[size_name]
    
    if landscape:
        width_mm, height_mm = height_mm, width_mm
    
    width_px = mm_to_pixels(width_mm, dpi)
    height_px = mm_to_pixels(height_mm, dpi)
    
    return (width_px, height_px)


def list_paper_sizes():
    """List all available paper sizes"""
    return sorted(PAPER_SIZES_MM.keys())


def parse_paper_arg(paper_arg):
    """
    Parse paper size argument string
    
    Formats:
        'a6' - A6 paper at 300 DPI portrait
        'a6-landscape' - A6 paper at 300 DPI landscape
        'a6-200' - A6 paper at 200 DPI portrait
        'a6-landscape-200' - A6 paper at 200 DPI landscape
    
    Returns:
        Tuple of (width, height) in pixels or None if invalid
    """
    if not paper_arg or paper_arg.lower() == 'false':
        return None
    
    parts = paper_arg.lower().split('-')
    size_name = parts[0]
    landscape = 'landscape' in parts
    
    # Find DPI value if specified
    dpi = DPI_HIGH
    for part in parts:
        if part.isdigit():
            dpi = int(part)
            break
    
    try:
        return get_paper_size(size_name, dpi, landscape)
    except ValueError:
        return None
