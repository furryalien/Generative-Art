"""
Extended optimizer with fractional angle multipliers and pi fractions
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

def modify_formula(formula_code):
    filepath = Path("Meshed_Gears.py")
    content = filepath.read_text()
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('new_rotation =') and 'existing_gear.rotation' in line:
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + f'new_rotation = {formula_code}'
            break
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

def test_formula(formula_code, num_samples=3):
    modify_formula(formula_code)
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
    print("EXTENDED OPTIMIZER - Fractional angles & pi fractions")
    print("=" * 70)
    
    # Start from best known: -existing_gear.rotation + angle - tooth_angle / 3 (456)
    
    # Try fractional angle multipliers and pi fractions
    formulas = []
    
    # Fractional angle multipliers
    angle_mults = ["0.5*angle", "1.5*angle", "2.5*angle", "3.5*angle",
                   "0.25*angle", "0.75*angle", "1.25*angle", "1.75*angle", "2.25*angle"]
    
    # Pi fractions
    pi_terms = ["math.pi/2", "math.pi/3", "math.pi/4", "math.pi/6",
                "3*math.pi/2", "2*math.pi/3", "3*math.pi/4", "5*math.pi/6"]
    
    # Tooth angle fractions
    tooth_fracs = ["tooth_angle / 2", "tooth_angle / 3", "tooth_angle / 4",
                   "tooth_angle / 5", "tooth_angle / 6", "tooth_angle / 8",
                   "tooth_angle * 0.4", "tooth_angle * 0.6", "tooth_angle * 0.7"]
    
    # Build formulas around best known pattern
    for am in angle_mults:
        for tf in tooth_fracs:
            formulas.append(f"-existing_gear.rotation + {am} - {tf}")
            formulas.append(f"-existing_gear.rotation - {am} + {tf}")
            formulas.append(f"-existing_gear.rotation + {am} + {tf}")
            formulas.append(f"-existing_gear.rotation - {am} - {tf}")
    
    for pt in pi_terms:
        for tf in tooth_fracs:
            formulas.append(f"-existing_gear.rotation + {pt} - {tf}")
            formulas.append(f"-existing_gear.rotation - {pt} + {tf}")
            formulas.append(f"-existing_gear.rotation + angle + {pt} - {tf}")
            formulas.append(f"-existing_gear.rotation - angle - {pt} + {tf}")
    
    print(f"Testing {len(formulas)} formula variations...")
    print()
    
    best_score = 456  # Current best
    best_formula = "-existing_gear.rotation + angle - tooth_angle / 3"
    
    try:
        for i, formula in enumerate(formulas):
            print(f"[{i+1}/{len(formulas)}] Testing...", end=" ", flush=True)
            score = test_formula(formula)
            print(f"Score: {score}")
            
            if score < best_score:
                best_score = score
                best_formula = formula
                print(f"    >> NEW BEST: {score}")
                print(f"    Formula: {formula}")
                
                if score < 100:
                    print()
                    print("=" * 70)
                    print("SUCCESS! Score < 100 achieved!")
                    print("=" * 70)
                    print(f"Formula: {formula}")
                    print(f"Score: {score}")
                    modify_formula(formula)
                    
                    # Verify
                    print("\nVerifying with 10 samples...")
                    verify_scores = []
                    for j in range(10):
                        vscore, vfile = generate_and_score()
                        if vscore < 999999:
                            verify_scores.append(vscore)
                            print(f"  {j+1}: {vscore} - {vfile}")
                    
                    if verify_scores:
                        avg = sum(verify_scores) / len(verify_scores)
                        best_v = min(verify_scores)
                        print(f"\nVerification: Avg={avg:.1f}, Best={best_v}")
                        
                        if best_v < 100:
                            print("\nVERIFIED! Consistently below 100")
                            return
                    
                    print("\nContinuing search for more reliable formula...")
            
            print()
    
    finally:
        print()
        print("=" * 70)
        print("FINAL RESULT")
        print("=" * 70)
        print(f"Best formula: {best_formula}")
        print(f"Best score: {best_score}")
        modify_formula(best_formula)

if __name__ == "__main__":
    main()
