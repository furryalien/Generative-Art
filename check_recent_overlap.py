"""Quick script to check overlap score of the most recent images"""
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import math

def parse_svg_coordinates(svg_file):
    """Extract all coordinate pairs from SVG paths"""
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

def calculate_overlap_score(svg_file):
    """Calculate an overlap score for a gear SVG file"""
    try:
        paths = parse_svg_coordinates(svg_file)
        
        if len(paths) < 2:
            return 999999
        
        overlap_count = 0
        min_valid_distance = 3.0
        
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                sample_size = min(50, len(paths[i]), len(paths[j]))
                
                for k in range(0, len(paths[i]), max(1, len(paths[i])//sample_size)):
                    x1, y1 = paths[i][k]
                    
                    for m in range(0, len(paths[j]), max(1, len(paths[j])//sample_size)):
                        x2, y2 = paths[j][m]
                        
                        dist = math.sqrt((x1-x2)**2 + (y1-y2)**2)
                        
                        if dist < min_valid_distance:
                            overlap_count += 1
        
        return overlap_count
    
    except Exception as e:
        print(f"Error: {e}")
        return 999999

# Get the 3 most recent non-test SVG files
svg_dir = Path("Images/Meshed_Gears/0-svg")
all_svgs = [f for f in svg_dir.glob("*.svg") if not f.name.startswith("test_")]
recent_svgs = sorted(all_svgs, key=lambda p: p.stat().st_mtime, reverse=True)[:3]

print("Checking overlap scores for newly generated images:")
print("=" * 60)

scores = []
for svg in recent_svgs:
    score = calculate_overlap_score(svg)
    scores.append(score)
    print(f"{svg.name}: {score}")

if scores:
    avg = sum(scores) / len(scores)
    print("=" * 60)
    print(f"Average overlap score: {avg:.1f}")
    print(f"\nComparison:")
    print(f"  Previous best formula (D): 494")
    print(f"  New optimized images:       {avg:.1f}")
    
    if avg < 494:
        improvement = ((494 - avg) / 494) * 100
        print(f"  ✓ Improvement: {improvement:.1f}%")
    elif avg > 494:
        decline = ((avg - 494) / 494) * 100
        print(f"  ⚠ Decline: {decline:.1f}%")
    else:
        print(f"  = Same performance")
