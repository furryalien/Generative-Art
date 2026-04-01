"""
Temporarily disable meshing to create baseline non-overlapping gears
"""
from pathlib import Path

# Read current file
filepath = Path("Meshed_Gears.py")
content = filepath.read_text()

# Save backup
Path("Meshed_Gears_backup.py").write_text(content)

# Find the meshing section and comment it out
lines = content.split('\n')
new_lines = []
in_mesh_section = False

for i, line in enumerate(lines):
    # Look for the mesh probability check
    if 'if len(gears) > 0 and random.random() < mesh_probability:' in line:
        in_mesh_section = True
        # Comment out this whole section and replace with simple random placement
        new_lines.append(line)
        new_lines.append("        # MESHING DISABLED FOR BASELINE TEST")
        new_lines.append("        pass")
        new_lines.append("    if True:  # Always do random placement instead")
        continue
    
    # Skip the meshing logic until we get to random placement
    if in_mesh_section:
        if 'else:  # Random placement without meshing' in line or'else:' in line and i > 200:
            in_mesh_section = False
            new_lines.append("    # Random placement")
            continue
    
    if not in_mesh_section:
        new_lines.append(line)

Path("Meshed_Gears.py").write_text('\n'.join(new_lines))
print("Disabled meshing logic")
print("Generating 5 non-meshed images...")

# Generate some images
import subprocess
for i in range(5):
    result = subprocess.run(
        ['powershell', '-Command', 
         f'.\\venv\\Scripts\\python.exe Meshed_Gears.py False True False a6-landscape random-by-line clustered uniform'],
        capture_output=True,
        text=True,
        timeout=15
    )
    if result.returncode == 0:
        print(f"  {i+1}/5 generated")

print("\nNow testing overlap scores...")

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

def calculate_overlap_score(svg_file):
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
    except:
        return 999999

svg_dir = Path("Images/Meshed_Gears/0-svg")
all_svgs = [f for f in svg_dir.glob("*.svg") if not f.name.startswith("test_")]
recent = sorted(all_svgs, key=lambda p: p.stat().st_mtime, reverse=True)[:5]

print("\nNon-meshed gear overlap scores:")
scores = []
for svg in recent:
    score = calculate_overlap_score(svg)
    scores.append(score)
    print(f"  {svg.name}: {score}")

if scores:
    avg = sum(scores) / len(scores)
    print(f"\nAverage: {avg:.1f}")
    print(f"\nThis is the baseline for non-overlapping gears.")
    print(f"Meshed gears will naturally have higher scores due to contact points.")

# Restore original
Path("Meshed_Gears.py").write_text(Path("Meshed_Gears_backup.py").read_text())
Path("Meshed_Gears_backup.py").unlink()
print("\nRestored original Meshed_Gears.py")
