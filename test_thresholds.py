"""
Test with different overlap detection thresholds
Maybe 3.0 pixels is too small and catching intended mesh points
"""
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import re
import math

def parse_svg_coordinates(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    all_coords = []
    for elem in root.iter():
        if elem.tag.endswith('path'):
            d = elem.get('d', '')
            if d:
                numbers = re.findall(r'[-+]?\d*\.?\d+', d)
                coords = [(float(numbers[i]), float(numbers[i+1])) 
                         for i in range(0, len(numbers)-1, 2)]
                all_coords.append(coords)
    return all_coords

def calculate_overlap_score(svg_file, threshold):
    """Calculate overlap with configurable threshold"""
    try:
        paths = parse_svg_coordinates(svg_file)
        if len(paths) < 2:
            return 999999
        
        overlap_count = 0
        
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                sample_size = min(50, len(paths[i]), len(paths[j]))
                for k in range(0, len(paths[i]), max(1, len(paths[i])//sample_size)):
                    x1, y1 = paths[i][k]
                    for m in range(0, len(paths[j]), max(1, len(paths[j])//sample_size)):
                        x2, y2 = paths[j][m]
                        dist = math.sqrt((x1-x2)**2 + (y1-y2)**2)
                        if dist < threshold:
                            overlap_count += 1
        return overlap_count
    except:
        return 999999

# Test with several recent images
svg_dir = Path("Images/Meshed_Gears/0-svg")
all_svgs = [f for f in svg_dir.glob("*.svg") if not f.name.startswith("test_")]
recent = sorted(all_svgs, key=lambda p: p.stat().st_mtime, reverse=True)[:5]

print("Testing overlap detection with different thresholds")
print("=" * 70)
print()

thresholds = [1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]

for svg in recent:
    print(f"{svg.name}:")
    for thresh in thresholds:
        score = calculate_overlap_score(svg, thresh)
        print(f"  threshold={thresh:4.1f}: overlap={score:4d}")
    print()

print("=" * 70)
print("Analysis:")
print("If threshold=3.0 gives ~456 and threshold=1.0 gives much lower,")
print("then gears are meshing correctly and 3.0 is catching valid contacts.")
print()
print("If threshold=1.0 still gives high scores, gears are truly overlapping.")
