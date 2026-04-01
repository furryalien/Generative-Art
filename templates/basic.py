import graphics.Config as config
from graphics.Graphics import setup, export
from graphics.Geometry import Circle, background, color, stroke
from graphics.LineWidth import init_line_width, apply_line_width

# Canvas dimensions - can be overridden by paper size argument
width, height = config.paper_size if config.paper_size else (1000, 1000)


def draw():
    # Draw stuff here
    background(0.95, 0.95, 0.95, 1.0)
    color(0, 0, 0, 1.0)
    Circle(width*0.5, height*0.5, 250)
    apply_line_width()
    stroke()


def main():
    setup(width, height)
    init_line_width(config.line_width_mode, config.line_width_value)
    draw()
    export()


if __name__ == '__main__':
    main()
