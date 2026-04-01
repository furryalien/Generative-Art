"""Quick 20 sample test"""
import subprocess
from pathlib import Path  
import xml.etree.ElementTree as ET
import re
import math

def calc_score(svg_file):
    try:
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
        
        if len(all_coords) < 2:
            return 999999
        
        overlap = 0
        for i in range(len(all_coords)):
            for j in range(i+1, len(all_coords)):
                for k in range(0, len(all_coords[i]), max(1, len(all_coords[i])//50)):
                    x1, y1 = all_coords[i][k]
                    for m in range(0, len(all_coords[j]), max(1, len(all_coords[j])//50)):
                        x2, y2 = all_coords[j][m]
                        if math.sqrt((x1-x2)**2 + (y1-y2)**2) < 3.0:
                            overlap += 1
        return overlap
    except:
        return 999999

scores = []
for i in range(20):
    subprocess.run(['powershell', '-Command', 
        f'.\\venv\\Scripts\\python.exe Meshed_Gears.py False True False a6-landscape random-by-line clustered uniform'],
        capture_output=True, timeout=15)
    
    svg_dir = Path("Images/Meshed_Gears/0-svg")
    latest = max([f for f in svg_dir.glob("*.svg") if not f.name.startswith("test_")], 
                key=lambda p: p.stat().st_mtime)
    
    score = calc_score(latest)
    scores.append(score)
    marker = " ***" if score < 100 else ""
    print(f"[{i+1:2d}/20] {score:4d}{marker}")

print(f"\nBest: {min(scores)}, Avg: {sum(scores)/len(scores):.1f}")
if min(scores) < 100:
    print(f"SUCCESS - {sum(1 for s in scores if s < 100)}/20 under 100!")
