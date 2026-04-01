from graphics.Graphics import setup, export
from graphics.Geometry import background, color, stroke
from graphics.Geometry import Line as draw_line
from graphics.Vector import Vector as vec2
from graphics.LineWidth import init_line_width, set_line_width
import graphics.Config as config
import math
import random
import numpy as np

# Canvas dimensions - can be overridden by paper size argument
width, height = config.paper_size if config.paper_size else (1000, 1000)


class LineSegment:
    def __init__(self, x, y, angle, length, width):
        """Create a line segment with variable length and width"""
        self.x = x
        self.y = y
        self.angle = angle
        self.length = length
        self.width = width
        
        # Calculate end point based on angle and length
        self.x2 = x + length * math.cos(angle)
        self.y2 = y + length * math.sin(angle)
    
    def draw(self):
        """Draw the line segment with its specific width"""
        color(0.0, 0.0, 0.0, 1.0)
        set_line_width(self.width)
        draw_line(self.x, self.y, self.x2, self.y2)
        stroke()


def draw():
    background(0.95, 0.95, 0.95, 1.0)
    
    # Configuration parameters
    num_segments = random.randint(800, 1500)
    
    # Length range (in pixels)
    min_length = 10
    max_length = min(width, height) * 0.15
    
    # Width range (in pixels)
    min_width = 0.3
    max_width = 6.0
    
    # Angle options
    angle_mode = random.choice(['random', 'horizontal', 'vertical', 'diagonal', 'mixed'])
    
    segments = []
    
    for i in range(num_segments):
        # Random position
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        
        # Variable length
        length = random.uniform(min_length, max_length)
        
        # Variable width
        segment_width = random.uniform(min_width, max_width)
        
        # Angle based on mode
        if angle_mode == 'random':
            angle = random.uniform(0, 2 * math.pi)
        elif angle_mode == 'horizontal':
            angle = random.uniform(-math.pi/12, math.pi/12)  # Nearly horizontal
        elif angle_mode == 'vertical':
            angle = random.uniform(math.pi/2 - math.pi/12, math.pi/2 + math.pi/12)  # Nearly vertical
        elif angle_mode == 'diagonal':
            base = random.choice([math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4])
            angle = base + random.uniform(-math.pi/12, math.pi/12)
        else:  # mixed
            angle = random.choice([0, math.pi/4, math.pi/2, 3*math.pi/4]) + random.uniform(-math.pi/8, math.pi/8)
        
        segments.append(LineSegment(x, y, angle, length, segment_width))
    
    # Draw all segments
    for segment in segments:
        segment.draw()


def main():
    setup(width, height)
    init_line_width(config.line_width_mode, config.line_width_value)
    draw()
    export()


# Call the main function
if __name__ == '__main__':
    main()
