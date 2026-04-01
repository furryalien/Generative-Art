from graphics.Graphics import setup, export
from graphics.Geometry import background, color, stroke
from graphics.Geometry import Circle, Line
from graphics.Vector import Vector as vec2
from graphics.LineWidth import init_line_width, set_line_width
import graphics.Config as config
import math
import random
import numpy as np

# Canvas dimensions - can be overridden by paper size argument
width, height = config.paper_size if config.paper_size else (1000, 1000)


class Shape:
    def __init__(self, x, y, size, width, shape_type):
        """Create a shape with variable size and line width"""
        self.x = x
        self.y = y
        self.size = size
        self.width = width
        self.shape_type = shape_type
    
    def draw(self):
        """Draw the shape with its specific width"""
        color(0.0, 0.0, 0.0, 1.0)
        set_line_width(self.width)
        
        if self.shape_type == 'circle':
            self.draw_circle()
        elif self.shape_type == 'square':
            self.draw_square()
        elif self.shape_type == 'triangle':
            self.draw_triangle()
        elif self.shape_type == 'star':
            self.draw_star()
        elif self.shape_type == 'heart':
            self.draw_heart()
        elif self.shape_type == 'moon':
            self.draw_moon()
        elif self.shape_type == 'clover':
            self.draw_clover()
        elif self.shape_type == 'diamond':
            self.draw_diamond()
        elif self.shape_type == 'hexagon':
            self.draw_hexagon()
        elif self.shape_type == 'pentagon':
            self.draw_pentagon()
    
    def draw_circle(self):
        """Draw a circle"""
        Circle(self.x, self.y, self.size)
        stroke()
    
    def draw_square(self):
        """Draw a square"""
        half = self.size / 2
        points = [
            (self.x - half, self.y - half),
            (self.x + half, self.y - half),
            (self.x + half, self.y + half),
            (self.x - half, self.y + half)
        ]
        self.draw_polygon(points, closed=True)
    
    def draw_triangle(self):
        """Draw a triangle"""
        h = self.size * 0.866  # height of equilateral triangle
        points = [
            (self.x, self.y - self.size * 0.577),
            (self.x + self.size / 2, self.y + h / 2 - self.size * 0.577),
            (self.x - self.size / 2, self.y + h / 2 - self.size * 0.577)
        ]
        self.draw_polygon(points, closed=True)
    
    def draw_star(self, points=5):
        """Draw a star with specified number of points"""
        outer_radius = self.size
        inner_radius = self.size * 0.4
        angle_step = math.pi / points
        
        star_points = []
        for i in range(points * 2):
            angle = i * angle_step - math.pi / 2
            if i % 2 == 0:
                r = outer_radius
            else:
                r = inner_radius
            star_points.append((
                self.x + r * math.cos(angle),
                self.y + r * math.sin(angle)
            ))
        self.draw_polygon(star_points, closed=True)
    
    def draw_heart(self):
        """Draw a heart shape"""
        # Heart shape using parametric equations
        t_values = np.linspace(0, 2 * math.pi, 100)
        points = []
        for t in t_values:
            x = self.size * 16 * math.sin(t)**3
            y = -self.size * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            points.append((self.x + x / 16, self.y + y / 16))
        self.draw_polygon(points, closed=True)
    
    def draw_moon(self):
        """Draw a crescent moon"""
        # Draw outer circle
        Circle(self.x, self.y, self.size)
        stroke()
        # Draw inner circle offset to create crescent
        offset = self.size * 0.3
        Circle(self.x + offset, self.y, self.size * 0.8)
        stroke()
    
    def draw_clover(self):
        """Draw a four-leaf clover"""
        # Four circles arranged in clover pattern
        offset = self.size * 0.5
        positions = [
            (0, -offset),
            (offset, 0),
            (0, offset),
            (-offset, 0)
        ]
        for dx, dy in positions:
            Circle(self.x + dx, self.y + dy, self.size * 0.4)
            stroke()
    
    def draw_diamond(self):
        """Draw a diamond"""
        points = [
            (self.x, self.y - self.size),
            (self.x + self.size * 0.6, self.y),
            (self.x, self.y + self.size),
            (self.x - self.size * 0.6, self.y)
        ]
        self.draw_polygon(points, closed=True)
    
    def draw_hexagon(self):
        """Draw a hexagon"""
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            points.append((
                self.x + self.size * math.cos(angle),
                self.y + self.size * math.sin(angle)
            ))
        self.draw_polygon(points, closed=True)
    
    def draw_pentagon(self):
        """Draw a pentagon"""
        points = []
        for i in range(5):
            angle = i * 2 * math.pi / 5 - math.pi / 2
            points.append((
                self.x + self.size * math.cos(angle),
                self.y + self.size * math.sin(angle)
            ))
        self.draw_polygon(points, closed=True)
    
    def draw_polygon(self, points, closed=True):
        """Draw a polygon from a list of points"""
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)] if closed else points[i + 1] if i < len(points) - 1 else points[i]
            if closed or i < len(points) - 1:
                Line(x1, y1, x2, y2)
                stroke()


def draw():
    background(0.95, 0.95, 0.95, 1.0)
    
    # Configuration parameters
    num_shapes = random.randint(200, 500)
    
    # Size range (in pixels)
    min_size = 5
    max_size = min(width, height) * 0.08
    
    # Width range (in pixels)
    min_width = 0.3
    max_width = 6.0
    
    # Shape mode selection
    shape_modes = {
        'circles': ['circle'],
        'squares': ['square'],
        'triangles': ['triangle'],
        'stars': ['star'],
        'hearts': ['heart'],
        'moons': ['moon'],
        'clovers': ['clover'],
        'diamonds': ['diamond'],
        'hexagons': ['hexagon'],
        'pentagons': ['pentagon'],
        'lucky_charms': ['circle', 'star', 'heart', 'moon', 'clover', 'diamond'],
        'geometric': ['circle', 'square', 'triangle', 'hexagon', 'pentagon', 'diamond'],
        'all': ['circle', 'square', 'triangle', 'star', 'heart', 'moon', 'clover', 'diamond', 'hexagon', 'pentagon']
    }
    
    # Use shape_type parameter if provided, otherwise randomly select
    if config.shape_type and config.shape_type in shape_modes:
        mode = config.shape_type
    else:
        mode = random.choice(list(shape_modes.keys()))
    available_shapes = shape_modes[mode]
    
    shapes = []
    
    for i in range(num_shapes):
        # Random position
        x = random.uniform(max_size, width - max_size)
        y = random.uniform(max_size, height - max_size)
        
        # Variable size
        size = random.uniform(min_size, max_size)
        
        # Variable width
        shape_width = random.uniform(min_width, max_width)
        
        # Select shape type
        shape_type = random.choice(available_shapes)
        
        shapes.append(Shape(x, y, size, shape_width, shape_type))
    
    # Draw all shapes
    for shape in shapes:
        shape.draw()


def main():
    setup(width, height)
    init_line_width(config.line_width_mode, config.line_width_value)
    draw()
    export()


# Call the main function
if __name__ == '__main__':
    main()
