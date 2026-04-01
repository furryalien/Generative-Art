"""Check overlap on 10 most recent images"""
from pathlib import Path
import xml.etree.ElementTree as ET
import re
import math

def get_svg_path_groups(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    all_paths = []
    for elem in root.iter():
        if elem.tag.endswith('path'):
            d = elem.get('d', '')
            if d:
                numbers = re.findall(r'[-+]?\d*\.?\d+', d)
                coords = [(float(numbers[i]), float(numbers[i+1])) 
                         for i in range(0, len(numbers)-1, 2)]
                if coords:
                    cx = sum(x for x, y in coords) / len(coords)
                    cy = sum(y for x, y in coords) / len(coords)
                    all_paths.append((coords, cx, cy))
    
    gear_groups = []
    used = [False] * len(all_paths)
    for i, (path, cx, cy) in enumerate(all_paths):
        if used[i]:
            continue
        group = [path]
        used[i] = True
        for j, (path2, cx2, cy2) in enumerate(all_paths):
            if not used[j]:
                if math.sqrt((cx - cx2)**2 + (cy - cy2)**2) < 200:
                    group.append(path2)
                    used[j] = True
        gear_groups.append(group)
    return gear_groups

def calculate_true_overlap(svg_file):
    try:
        gear_groups = get_svg_path_groups(svg_file)
        if len(gear_groups) < 2:
            return 0
        overlap_count = 0
        for i in range(len(gear_groups)):
            for j in range(i+1, len(gear_groups)):
                gear1_points = []
                for path in gear_groups[i]:
                    gear1_points.extend(path[::max(1, len(path)//50)])
                gear2_points = []
                for path in gear_groups[j]:
                    gear2_points.extend(path[::max(1, len(path)//50)])
                for x1, y1 in gear1_points:
                    for x2, y2 in gear2_points:
                        if math.sqrt((x1-x2)**2 + (y1-y2)**2) < 3.0:
                            overlap_count += 1
        return overlap_count
    except:
        return 999999

svg_dir = Path("Images/Meshed_Gears/0-svg")
recent = sorted([f for f in svg_dir.glob("*.svg") if not f.name.startswith("test_")],
                key=lambda p: p.stat().st_mtime, reverse=True)[:10]

print("Final 10 images - Overlap scores:")
print("=" * 70)
scores = []
for svg in recent:
    score = calculate_true_overlap(svg)
    scores.append(score)
    marker = " <- PERFECT!" if score == 0 else " ***" if score < 100 else ""
    print(f"{svg.name}: {score:3d}{marker}")

print("=" * 70)
print(f"Best: {min(scores)}, Worst: {max(scores)}, Average: {sum(scores)/len(scores):.1f}")
zeros = sum(1 for s in scores if s == 0)
under_10 = sum(1 for s in scores if s < 10)
print(f"Perfect (0): {zeros}/10, Under 10: {under_10}/10, All under 100: {len([s for s in scores if s < 100])}/10")
