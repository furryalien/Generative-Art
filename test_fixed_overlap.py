"""
Fixed overlap detection - properly groups paths by gear
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import math

def get_svg_path_groups(svg_file):
    """Group path coordinates by proximity (each gear should be one group)"""
    tree = ET.parse(svg_file)
    root = tree.getroot()
    
    # Get all paths
    all_paths = []
    for elem in root.iter():
        if elem.tag.endswith('path'):
            d = elem.get('d', '')
            if d:
                numbers = re.findall(r'[-+]?\d*\.?\d+', d)
                coords = [(float(numbers[i]), float(numbers[i+1])) 
                         for i in range(0, len(numbers)-1, 2)]
                if coords:
                    # Calculate center of this path
                    cx = sum(x for x, y in coords) / len(coords)
                    cy = sum(y for x, y in coords) / len(coords)
                    all_paths.append((coords, cx, cy))
    
    # Group paths by proximity (paths within 200px belong to same gear)
    gear_groups = []
    used = [False] * len(all_paths)
    
    for i, (path, cx, cy) in enumerate(all_paths):
        if used[i]:
            continue
        
        # Start new gear group
        group = [path]
        used[i] = True
        
        # Find all paths near this one (same gear)
        for j, (path2, cx2, cy2) in enumerate(all_paths):
            if not used[j]:
                dist = math.sqrt((cx - cx2)**2 + (cy - cy2)**2)
                if dist < 200:  # Same gear
                    group.append(path2)
                    used[j] = True
        
        gear_groups.append(group)
    
    return gear_groups

def calculate_true_overlap(svg_file, threshold=3.0):
    """Calculate overlap between DIFFERENT gears only"""
    try:
        gear_groups = get_svg_path_groups(svg_file)
        
        if len(gear_groups) < 2:
            return 0  # Need at least 2 gears
        
        overlap_count = 0
        
        # Check overlap between different gears
        for i in range(len(gear_groups)):
            for j in range(i+1, len(gear_groups)):
                gear1_paths = gear_groups[i]
                gear2_paths = gear_groups[j]
                
                # Sample points from each gear
                gear1_points = []
                for path in gear1_paths:
                    gear1_points.extend(path[::max(1, len(path)//50)])  # Sample 50 points per path
                
                gear2_points = []
                for path in gear2_paths:
                    gear2_points.extend(path[::max(1, len(path)//50)])
                
                # Check distances
                for x1, y1 in gear1_points:
                    for x2, y2 in gear2_points:
                        dist = math.sqrt((x1-x2)**2 + (y1-y2)**2)
                        if dist < threshold:
                            overlap_count += 1
        
        return overlap_count
    except Exception as e:
        print(f"Error: {e}")
        return 999999

# Test on recent images
svg_dir = Path("Images/Meshed_Gears/0-svg")
recent = sorted([f for f in svg_dir.glob("*.svg") if not f.name.startswith("test_")],
                key=lambda p: p.stat().st_mtime, reverse=True)[:5]

print("FIXED overlap detection - comparing between gears only:")
print("=" * 70)

for svg in recent:
    score = calculate_true_overlap(svg)
    marker = " ***" if score < 100 else ""
    print(f"{svg.name}: {score}{marker}")

print()
print("If these scores are now much lower or 0, the detection was fixed!")
