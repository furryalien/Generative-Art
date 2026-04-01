from graphics.Graphics import setup, export
from graphics.Geometry import background, color, stroke, Line
from graphics.Vector import Vector as vec2
from graphics.LineWidth import init_line_width, set_line_width
import graphics.Config as config
import math
import random
import numpy as np

# Canvas dimensions - can be overridden by paper size argument
width, height = config.paper_size if config.paper_size else (1000, 1000)


class Gear:
    def __init__(self, x, y, num_teeth, tooth_size, width, rotation=0):
        """Create a gear with specified number of teeth"""
        self.x = x
        self.y = y
        self.num_teeth = num_teeth
        self.tooth_size = tooth_size
        self.width = width
        self.rotation = rotation  # Starting rotation angle
        
        # Calculate gear dimensions
        self.tooth_depth = tooth_size * 0.08
        self.inner_radius = tooth_size
        self.outer_radius = tooth_size + self.tooth_depth
        self.pitch_radius = tooth_size + self.tooth_depth / 2
        
        # Calculate total radius for collision detection
        self.total_radius = self.outer_radius + 80  # Maximum margin for zero overlap
        
    def get_tooth_angle(self):
        """Get the angle of each tooth"""
        return 2 * math.pi / self.num_teeth
    
    def overlaps(self, other_gear):
        """Check if this gear overlaps with another gear"""
        distance = math.sqrt((self.x - other_gear.x)**2 + (self.y - other_gear.y)**2)
        return distance < (self.total_radius + other_gear.total_radius)
    
    def get_mesh_position_and_rotation(self, existing_gear, preferred_angle=None):
        """Calculate position and rotation to mesh with an existing gear"""
        # Add clearance to prevent tooth overlap
        clearance = 80.0  # Maximum clearance for zero overlap
        ideal_distance = self.pitch_radius + existing_gear.pitch_radius + clearance
        
        # If no preferred angle, choose random
        if preferred_angle is None:
            angle = random.uniform(0, 2 * math.pi)
        else:
            angle = preferred_angle
            
        new_x = existing_gear.x + ideal_distance * math.cos(angle)
        new_y = existing_gear.y + ideal_distance * math.sin(angle)
        
        # Calculate proper rotation for meshing identical gears
        # 
        # For two gears to mesh:
        # - At contact point, one gear's tooth must fit into other's gap
        # - The gears must counter-rotate for proper meshing
        # 
        # Optimal formula found through iterative testing:
        # - Counter-rotation: -existing_rotation
        # - Position adjustment: -2*angle (double the placement angle)
        # - Tooth offset: +tooth_angle/2 (ensures tooth-to-gap alignment)
        
        tooth_angle = 2 * math.pi / self.num_teeth
        
        #Geometric derivation for identical gears:
        # Contact point at angle θ from existing gear's center
        # Same contact at angle θ+π from new gear's center
        # For tooth-to-gap alignment:
        #   existing_rotation + θ = new_rotation + (θ+π) +(tooth_angle/2)
        # Solving: new_rotation = existing_rotation - π - tooth_angle/2
        
        tooth_angle = 2 * math.pi / self.num_teeth
        
        # Derived meshing formula
        new_rotation = existing_gear.rotation - math.pi - tooth_angle / 2
        
        return new_x, new_y, new_rotation
    
    def draw(self):
        """Draw the gear with teeth"""
        color(0.0, 0.0, 0.0, 1.0)
        set_line_width(self.width)
        
        tooth_angle = self.get_tooth_angle()
        tooth_width_angle = tooth_angle * 0.25  # Thinner teeth to reduce overlap
        
        points = []
        
        # Generate gear outline with teeth (more precise geometry)
        for i in range(self.num_teeth):
            # Center angle for this tooth
            center_angle = i * tooth_angle + self.rotation
            
            # Tooth tip angles (at outer radius)
            tip_left = center_angle - tooth_width_angle / 2
            tip_right = center_angle + tooth_width_angle / 2
            
            # Tooth base angles (at inner radius) - slightly wider  
            base_width_angle = tooth_width_angle * 0.85  # Slight taper
            base_left = center_angle - base_width_angle / 2
            base_right = center_angle + base_width_angle / 2
            
            # Gap extends to next tooth
            next_center = (i + 1) * tooth_angle + self.rotation
            next_base_left = next_center - (tooth_width_angle * 0.85) / 2
            
            # Tooth profile: base_left -> tip_left -> tip_right -> base_right
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
            
            # Gap arc at inner radius to next tooth
            # Use a few points to approximate the arc
            gap_segments = 3
            for j in range(1, gap_segments + 1):
                gap_angle = base_right + (next_base_left - base_right) * j / gap_segments
                points.append((
                    self.x + self.inner_radius * math.cos(gap_angle),
                    self.y + self.inner_radius * math.sin(gap_angle)
                ))
        
        # Draw the gear outline
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]
            Line(x1, y1, x2, y2)
            stroke()
        
        # Draw center circle
        center_radius = self.inner_radius * 0.3
        num_segments = 32
        for i in range(num_segments):
            angle1 = i * 2 * math.pi / num_segments
            angle2 = (i + 1) * 2 * math.pi / num_segments
            x1 = self.x + center_radius * math.cos(angle1)
            y1 = self.y + center_radius * math.sin(angle1)
            x2 = self.x + center_radius * math.cos(angle2)
            y2 = self.y + center_radius * math.sin(angle2)
            Line(x1, y1, x2, y2)
            stroke()


def draw():
    background(0.95, 0.95, 0.95, 1.0)
    
    # Configuration parameters
    min_teeth = 8
    max_teeth = 24
    min_tooth_size = 60  # Even larger gears
    max_tooth_size = 120  # Even larger gears
    
    min_width = 0.5
    max_width = 3.0
    
    margin = 100
    
    # Get placement mode and size mode from config
    placement_mode = config.gear_placement if hasattr(config, 'gear_placement') else 'clustered'
    size_mode = config.gear_size_mode if hasattr(config, 'gear_size_mode') else 'uniform'
    
    gears = []
    max_attempts = 2000
    target_gears = random.randint(3, 5)  # 3-5 gears per image
    
    # Clustering parameters
    if placement_mode == 'clustered':
        mesh_probability = 0.85  # High probability of meshing with existing gear
        prefer_recent = 0.7  # Probability of choosing from last 5 gears
    else:  # random mode
        mesh_probability = 0.3  # Lower probability of meshing
        prefer_recent = 0.0
    
    # Uniform gear parameters (used when size_mode is 'uniform')
    if size_mode == 'uniform':
        uniform_teeth = random.randint(12, 16)  # All gears have same tooth count
        uniform_tooth_size = random.uniform(80, 100)  # Much larger gears
    
    # Place first gear at center with some randomness
    if size_mode == 'uniform':
        first_gear = Gear(
            x=width / 2 + random.uniform(-100, 100),
            y=height / 2 + random.uniform(-100, 100),
            num_teeth=uniform_teeth,
            tooth_size=uniform_tooth_size,
            width=random.uniform(min_width, max_width),
            rotation=random.uniform(0, 2 * math.pi)
        )
    else:
        first_tooth_size = random.uniform(min_tooth_size, max_tooth_size)
        first_gear = Gear(
            x=width / 2 + random.uniform(-100, 100),
            y=height / 2 + random.uniform(-100, 100),
            num_teeth=random.randint(min_teeth, max_teeth),
            tooth_size=first_tooth_size,
            width=random.uniform(min_width, max_width),
            rotation=random.uniform(0, 2 * math.pi)
        )
    gears.append(first_gear)
    
    attempts = 0
    while len(gears) < target_gears and attempts < max_attempts:
        attempts += 1
        
        # Try to mesh with an existing gear
        if len(gears) > 0 and random.random() < mesh_probability:
            # Choose gear to mesh with
            if placement_mode == 'clustered' and len(gears) > 5 and random.random() < prefer_recent:
                # Prefer recent gears for clustering
                existing_gear = random.choice(gears[-5:])
            else:
                existing_gear = random.choice(gears)
            
            # Try multiple angles for placement
            angles_to_try = 8
            for attempt in range(angles_to_try):
                # Try different angles around the existing gear
                angle = (2 * math.pi / angles_to_try) * attempt + random.uniform(-0.3, 0.3)
                
                # Create new gear with appropriate size parameters
                if size_mode == 'uniform':
                    new_gear = Gear(0, 0, uniform_teeth, uniform_tooth_size, random.uniform(min_width, max_width))
                else:
                    num_teeth = random.randint(min_teeth, max_teeth)
                    tooth_size = random.uniform(min_tooth_size, max_tooth_size)
                    new_gear = Gear(0, 0, num_teeth, tooth_size, random.uniform(min_width, max_width))
                
                new_x, new_y, new_rotation = new_gear.get_mesh_position_and_rotation(existing_gear, angle)
                
                # Update position and rotation
                new_gear.x = new_x
                new_gear.y = new_y
                new_gear.rotation = new_rotation
                
                # Check if in bounds
                if not (margin < new_x < width - margin and margin < new_y < height - margin):
                    continue
                
                # Check for overlaps
                overlaps = False
                for existing in gears:
                    if new_gear.overlaps(existing) and existing != existing_gear:
                        overlaps = True
                        break
                
                if not overlaps:
                    gears.append(new_gear)
                    attempts = 0  # Reset attempts on success
                    break
        else:
            # Place randomly without meshing (for random mode or spacing)
            x = random.uniform(margin, width - margin)
            y = random.uniform(margin, height - margin)
            
            if size_mode == 'uniform':
                new_gear = Gear(
                    x, y, uniform_teeth, uniform_tooth_size,
                    random.uniform(min_width, max_width),
                    rotation=random.uniform(0, 2 * math.pi)
                )
            else:
                num_teeth = random.randint(min_teeth, max_teeth)
                tooth_size = random.uniform(min_tooth_size, max_tooth_size)
                new_gear = Gear(
                    x, y, num_teeth, tooth_size,
                    random.uniform(min_width, max_width),
                    rotation=random.uniform(0, 2 * math.pi)
                )
            
            # Check if it overlaps with any existing gear
            overlaps = False
            for existing in gears:
                if new_gear.overlaps(existing):
                    overlaps = True
                    break
            
            if not overlaps:
                gears.append(new_gear)
                attempts = 0  # Reset attempts on success
    
    # Draw all gears
    for gear in gears:
        gear.draw()


def main():
    setup(width, height)
    init_line_width(config.line_width_mode, config.line_width_value)
    draw()
    export()


# Call the main function
if __name__ == '__main__':
    main()
