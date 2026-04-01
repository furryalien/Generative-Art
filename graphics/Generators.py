from .Vector import Vector as vec2
try:
    # Try the original noise module (requires C++ compilation)
    from noise import pnoise2
except ImportError:
    # Fall back to pure Python perlin-noise module
    from perlin_noise import PerlinNoise
    # Create a wrapper function to match pnoise2 API
    _perlin = PerlinNoise(octaves=4, seed=0)
    def pnoise2(x, y):
        return _perlin([x, y])
from random import randint, choices
from math import cos
from math import sin
from math import radians


# Noise loop generator
class NoiseLoop:
    def __init__(self, diameter, _min, _max):
        self.diameter = diameter
        self.min = _min
        self.max = _max
        self.noise_seed = randint(0, 10000)

    def get_value(self, a):
        x = self.map(cos(radians(a)), -1, 1, 0, self.diameter)
        y = self.map(sin(radians(a)), -1, 1, 0, self.diameter)
        r = pnoise2(x+self.noise_seed, y+self.noise_seed)
        return self.map(r, -1, 1, self.min, self.max)

    def map(self, value, left_min, left_max, right_min, right_max):
        left_span = left_max - left_min
        right_span = right_max - right_min
        value_scaled = float(value - left_min) / float(left_span)
        return right_min + (value_scaled * right_span)

    def set_noise_seed(self, _offset):
        self.noise_seed = _offset


# Random walker
class RandomWalker:
    def __init__(self, x, y, size):
        self.pos = vec2([x, y])
        self.prev_pos = vec2([x, y])
        self.size = size
        self.direction = vec2([0, 0])

    def walk(self, d, w):
        self.set_direction(d, w)
        self.pos.x += self.direction.x * self.size
        self.pos.y += self.direction.y * self.size

    def set_direction(self, d, w):
        directions = d
        weights = w
        self.direction = choices(directions, weights=weights, k=1)[0]

    def step_size(self, s, r=None):
        if r is None:
            self.size = s
        else:
            self.size = randint(s, r)
