#!/usr/bin/env python3
"""
Generate test images with different gear meshing formulas
Creates a visual comparison to manually inspect which formula works best
"""

import math
import random
import sys

# Set up fake command line args before importing graphics modules  
sys.argv = ['test_gear_formulas.py', 'False', 'True', 'False', 'a6-landscape', '1.0', 'clustered', 'uniform']

from graphics.Graphics import setup, export
from graphics.LineWidth import init_line_width, apply_line_width
from graphics.PaperSizes import parse_paper_arg

# Test formulas to try
TEST_FORMULAS = [
    ("A: -rot + pi + half", lambda rot, angle, ta: -rot + math.pi + ta/2),
    ("B: -rot - 2*angle + half", lambda rot, angle, ta: -rot - 2*angle + ta/2),
    ("C: -rot + pi - 2*angle + half", lambda rot, angle, ta: -rot + math.pi - 2*angle + ta/2),
    ("D: -rot - angle + half", lambda rot, angle, ta: -rot - angle + ta/2),
    ("E: -rot + pi - angle + half", lambda rot, angle, ta: -rot + math.pi - angle + ta/2),
]

class Gear:
    def __init__(self, x, y, num_teeth, tooth_size, width, rotation=0, formula_func=None):
        self.x = x
        self.y = y
        self.num_teeth = num_teeth
        self.tooth_size = tooth_size  # Size of one tooth
        self.width = width
        self.rotation = rotation
        self.formula_func = formula_func  # Custom formula function
        
        # Calculate radii
        self.tooth_depth = tooth_size * 0.2
        self.inner_radius = tooth_size
        self.outer_radius = tooth_size + self.tooth_depth
        self.pitch_radius = (self.inner_radius + self.outer_radius) / 2
        self.total_radius = self.outer_radius
        
    def get_tooth_angle(self):
        """Angle covered by one tooth"""
        return 2 * math.pi / self.num_teeth
    
    def overlaps(self, other_gear):
        """Check if this gear overlaps with another"""
        distance = math.sqrt((self.x - other_gear.x)**2 + (self.y - other_gear.y)**2)
        return distance < (self.total_radius + other_gear.total_radius)
    
    def get_mesh_position_and_rotation(self, existing_gear, preferred_angle=None):
        """Calculate position and rotation to mesh with an existing gear"""
        clearance = 1.0
        ideal_distance = self.pitch_radius + existing_gear.pitch_radius + clearance
        
        if preferred_angle is None:
            angle = random.uniform(0, 2 * math.pi)
        else:
            angle = preferred_angle
            
        new_x = existing_gear.x + ideal_distance * math.cos(angle)
        new_y = existing_gear.y + ideal_distance * math.sin(angle)
        
        tooth_angle = 2 * math.pi / self.num_teeth
        
        # Use the formula function if provided
        if self.formula_func:
            new_rotation = self.formula_func(existing_gear.rotation, angle, tooth_angle)
        else:
            # Default formula
            new_rotation = -existing_gear.rotation + math.pi + tooth_angle / 2
        
        return new_x, new_y, new_rotation
    
    def draw(self):
        """Draw the gear with teeth"""
        from graphics.Geometry import color, move_to, line_to, close_path, stroke
        from graphics.LineWidth import apply_line_width, set_line_width
        
        color(0.0, 0.0, 0.0, 1.0)
        set_line_width(self.width)
        
        tooth_angle = self.get_tooth_angle()
        tooth_width_angle = tooth_angle * 0.38
        
        points = []
        
        for i in range(self.num_teeth):
            center_angle = i * tooth_angle + self.rotation
            
            tip_left = center_angle - tooth_width_angle / 2
            tip_right = center_angle + tooth_width_angle / 2
            
            base_width_angle = tooth_width_angle * 0.85
            base_left = center_angle - base_width_angle / 2
            base_right = center_angle + base_width_angle / 2
            
            next_center = (i + 1) * tooth_angle + self.rotation
            next_base_left = next_center - (tooth_width_angle * 0.85) / 2
            
            points.append((
                self.x + self.inner_radius * math.cos(base_left),
                self.y + self.inner_radius * math.sin(base_left)
            ))
            points.append((
                self.x + self.outer_radius * math.cos(tip_left),
                self.y + self.outer_radius * math.sin(tip_left)
            ))
            points.append((
                self.x + self.outer_radius * math.cos(tip_right),
                self.y + self.outer_radius * math.sin(tip_right)
            ))
            points.append((
                self.x + self.inner_radius * math.cos(base_right),
                self.y + self.inner_radius * math.sin(base_right)
            ))
            
            gap_segments = 3
            for j in range(1, gap_segments + 1):
                gap_angle = base_right + (next_base_left - base_right) * j / gap_segments
                points.append((
                    self.x + self.inner_radius * math.cos(gap_angle),
                    self.y + self.inner_radius * math.sin(gap_angle)
                ))
        
        if points:
            move_to(points[0][0], points[0][1])
            for point in points[1:]:
                line_to(point[0], point[1])
            close_path()
            apply_line_width()
            stroke()


def generate_test_image(formula_name, formula_func, width, height, filename):
    """Generate one test image with a specific formula"""
    setup(width, height)
    init_line_width(1.0, "fixed")
    
    # Simple test: 2 gears meshing
    random.seed(42)  # Fixed seed for consistency
    
    num_teeth = 14
    tooth_size = 80
    
    # First gear in center
    gear1 = Gear(
        x=width / 2,
        y=height / 2,
        num_teeth=num_teeth,
        tooth_size=tooth_size,
        width=1.0,
        rotation=0,
        formula_func=formula_func
    )
    
    # Second gear meshed to the right
    gear2 = Gear(
        x=0, y=0,
        num_teeth=num_teeth,
        tooth_size=tooth_size,
        width=1.0,
        formula_func=formula_func
    )
    
    angle = 0  # Place to the right
    x2, y2, rot2 = gear2.get_mesh_position_and_rotation(gear1, angle)
    gear2.x = x2
    gear2.y = y2
    gear2.rotation = rot2
    
    # Draw gears
    gear1.draw()
    gear2.draw()
    
    export(filename, open_file=False)
    print(f"✓ Generated: {formula_name}")


def main():
    # Get paper size (use A6 landscape for testing)
    width, height = parse_paper_arg("a6-landscape")
    
    print("Generating test images for gear meshing formulas...")
    print(f"Image size: {width}x{height}")
    print()
    
    for formula_name, formula_func in TEST_FORMULAS:
        safe_name = formula_name.replace(":", "").replace(" ", "_").replace("*", "x")
        filename = f"Images/Meshed_Gears/0-svg/test_{safe_name}.svg"
        
        try:
            generate_test_image(formula_name, formula_func, width, height, filename)
        except Exception as e:
            print(f"❌ Error with {formula_name}: {e}")
    
    print()
    print("✓ Test images generated!")
    print("  Check Images/Meshed_Gears/0-svg/test_*.svg")
    print("  Look for gears where teeth align properly at the mesh point")


if __name__ == "__main__":
    main()
