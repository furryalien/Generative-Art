import sys
import os
from graphics.PaperSizes import parse_paper_arg
from graphics.LineWidth import parse_line_width_arg

args = sys.argv

# This is our drawing Context
Context = None

# Some default variables
file_format = 'SVG' if eval(args[2]) else 'PNG'
open_file = True if eval(args[1]) else False
image_folder = "/Images"
script_name = args[0]

# Paper size (optional 4th argument)
paper_size = parse_paper_arg(args[4]) if len(args) > 4 else None

# Line width (optional 5th argument)
line_width_mode, line_width_value = parse_line_width_arg(args[5]) if len(args) > 5 else ('fixed', 1.0)

# Shape type (optional 6th argument for Varied_Shapes.py)
shape_type = args[6] if len(args) > 6 else None

# Gear placement mode (optional 6th argument for Meshed_Gears.py: 'clustered' or 'random')
gear_placement = args[6] if len(args) > 6 else 'clustered'

# Gear size mode (optional 7th argument for Meshed_Gears.py: 'uniform' or 'varied')
gear_size_mode = args[7] if len(args) > 7 else 'uniform'

# Variables for posting to Twitter
twitter_post = True if eval(args[3]) else False
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')
tweet_status = '#ADD #YOUR #TWEET #HERE'
