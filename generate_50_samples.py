"""
Generate 50 samples and find the absolute best score achieved
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

print("Generating 50 samples to find best achievable score...")
print("=" * 70)

scores = []
filesnames = []

for i in range(50):
    result = subprocess.run(
        ['powershell', '-Command', 
         f'.\\venv\\Scripts\\python.exe Meshed_Gears.py False True False a6-landscape random-by-line clustered uniform'],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    if result.returncode == 0:
        svg_dir = Path("Images/Meshed_Gears/0-svg")
        all_svgs = [f for f in svg_dir.glob("*.svg") if not f.name.startswith("test_")]
        latest = max(all_svgs, key=lambda p: p.stat().st_mtime)
        
        score = calculate_overlap_score(latest)
        scores.append(score)
        filesnames.append((score, latest.name))
        
        print(f"[{i+1:2d}/50] {latest.name}: {score}")

print()
print("=" * 70)
print("RESULTS")
print("=" * 70)

if scores:
    scores.sort()
    filesnames.sort()
    
    print(f"Best 10 scores:")
    for i in range(min(10, len(filesnames))):
        score, name = filesnames[i]
        marker = "***" if score < 100 else ""
        print(f"  {i+1:2d}. {score:4d} - {name} {marker}")
    
    print()
    print(f"Statistics:")
    print(f"  Best:    {min(scores)}")
    print(f"  Worst:   {max(scores)}")
    print(f"  Average: {sum(scores)/len(scores):.1f}")
    print(f"  Median:  {scores[len(scores)//2]}")
    
    under_100 = sum(1 for s in scores if s < 100)
    under_200 = sum(1 for s in scores if s < 200)
    
    print(f"\n  Under 100: {under_100}/50 ({under_100*2}%)")
    print(f"  Under 200: {under_200}/50 ({under_200*2}%)")
    
    if min(scores) < 100:
        print(f"\n*** SUCCESS: Found {under_100} image(s) with overlap < 100!")
        print(f"Best: {filesnames[0][1]} with score {filesnames[0][0]}")
    else:
        print(f"\nBest achieved: {min(scores)}")
        print(f"Still need to reduce by {min(scores) - 100} to reach goal")
