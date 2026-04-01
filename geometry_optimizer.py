"""
Test different gear geometry parameters to minimize overlap
Tests combinations of: tooth_depth, clearance, tooth_width
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

def modify_geometry(tooth_depth_factor, clearance, tooth_width_factor):
    """Modify Meshed_Gears.py with specific geometry parameters"""
    filepath = Path("Meshed_Gears.py")
    content = filepath.read_text()
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Modify tooth depth
        if 'self.tooth_depth = tooth_size *' in line:
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + f'self.tooth_depth = tooth_size * {tooth_depth_factor}'
        
        # Modify clearance
        if line.strip().startswith('clearance =') and 'Add small clearance' in lines[i-1]:
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + f'clearance = {clearance}'
        
        # Modify tooth width
        if 'tooth_width_angle = tooth_angle *' in line.strip():
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + f'tooth_width_angle = tooth_angle * {tooth_width_factor}'
    
    filepath.write_text('\n'.join(lines))

def generate_and_score():
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
        latest_svg = max(all_svgs, key=lambda p: p.stat().st_mtime)
        return calculate_overlap_score(latest_svg), latest_svg.name
    return 999999, None

def test_geometry(tooth_depth, clearance, tooth_width, num_samples=3):
    modify_geometry(tooth_depth, clearance, tooth_width)
    scores = []
    for _ in range(num_samples):
        score, _ = generate_and_score()
        if score < 999999:
            scores.append(score)
    if not scores:
        return 999999
    return min(scores)

def main():
    print("=" * 70)
    print("GEOMETRY PARAMETER OPTIMIZER")
    print("=" * 70)
    print()
    
    # Save original
    original = Path("Meshed_Gears.py").read_text()
    
    # Test parametercombinations
    tooth_depths = [0.1, 0.12, 0.15, 0.18, 0.20]  # Current is 0.20
    clearances = [1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0]  # Current is 1.0
    tooth_widths = [0.30, 0.32, 0.35, 0.38, 0.40]  # Current is 0.38
    
    best_score = 999999
    best_params = None
    
    total = len(tooth_depths) * len(clearances) * len(tooth_widths)
    tested = 0
    
    print(f"Testing {total} parameter combinations...")
    print()
    
    try:
        for td in tooth_depths:
            for cl in clearances:
                for tw in tooth_widths:
                    tested += 1
                    print(f"[{tested}/{total}] depth={td:.2f}, clear={cl:.1f}, width={tw:.2f} ... ", end="", flush=True)
                    
                    score = test_geometry(td, cl, tw)
                    print(f"Score: {score}")
                    
                    if score < best_score:
                        best_score = score
                        best_params = (td, cl, tw)
                        print(f"    >> NEW BEST: {score}")
                        
                        if score < 100:
                            print()
                            print("=" * 70)
                            print("SUCCESS! Score < 100")
                            print("=" * 70)
                            print(f"tooth_depth={td}, clearance={cl}, tooth_width={tw}")
                            print(f"Score: {score}")
                            
                            # Verify
                            print("\nVerifying with 10 samples...")
                            modify_geometry(td, cl, tw)
                            verify_scores = []
                            for j in range(10):
                                vscore, vfile = generate_and_score()
                                if vscore < 999999:
                                    verify_scores.append(vscore)
                                    print(f"  {j+1}: {vscore}")
                            
                            if verify_scores:
                                avg = sum(verify_scores) / len(verify_scores)
                                vbest = min(verify_scores)
                                print(f"\nVerification: Avg={avg:.1f}, Best={vbest}")
                                
                                if vbest < 100:
                                    print("\nVERIFIED SUCCESS!")
                                    return
                            
                            print("\nContinuing search...")
    
    finally:
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        if best_params:
            td, cl, tw = best_params
            print(f"Best parameters:")
            print(f"  tooth_depth = {td}")
            print(f"  clearance = {cl}")  
            print(f"  tooth_width = {tw}")
            print(f"  Score: {best_score}")
            
            # Apply best
            modify_geometry(td, cl, tw)
            print("\nApplied best geometry parameters to Meshed_Gears.py")
        else:
            Path("Meshed_Gears.py").write_text(original)
            print("No improvement found, restored original")

if __name__ == "__main__":
    main()
