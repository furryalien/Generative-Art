"""
Iterative gear meshing formula tester
Inspects SVG files for overlaps, adjusts formulas, and repeats until optimal
"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import math

def parse_svg_coordinates(svg_file):
    """Extract all coordinate pairs from SVG paths"""
    tree = ET.parse(svg_file)
    root = tree.getroot()
    
    all_coords = []
    
    # Find all path elements
    for elem in root.iter():
        if elem.tag.endswith('path'):
            d = elem.get('d', '')
            if d:
                # Extract all numbers from the path
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
            return 999999  # Bad - not enough gears
        
        overlap_count = 0
        min_valid_distance = 3.0  # Pixels - anything closer is considered overlap
        
        # Check proximity between different gears' coordinates
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                # Sample some points from each path (not all, too slow)
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
        print(f"    Error analyzing {svg_file.name}: {e}")
        return 999999

def modify_formula(formula_code):
    """Modify Meshed_Gears.py with a specific formula"""
    filepath = Path("Meshed_Gears.py")
    content = filepath.read_text()
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('new_rotation =') and 'existing_gear.rotation' in line:
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + f'new_rotation = {formula_code}'
            break
    
    filepath.write_text('\n'.join(lines))

def generate_image():
    """Generate one test image"""
    result = subprocess.run(
        ['powershell', '-Command', 
         f'.\\venv\\Scripts\\python.exe Meshed_Gears.py False True False a6-landscape random-by-line clustered uniform'],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    if result.returncode != 0:
        return None
    
    # Find the latest SVG
    svg_dir = Path("Images/Meshed_Gears/0-svg")
    latest_svg = max(svg_dir.glob("*.svg"), key=lambda p: p.stat().st_mtime)
    
    return latest_svg

def test_formula(formula_name, formula_code, num_samples=3):
    """Test a formula by generating multiple images and averaging overlap score"""
    print(f"  Testing: {formula_name}")
    print(f"    Formula: {formula_code}")
    
    modify_formula(formula_code)
    
    scores = []
    for i in range(num_samples):
        img = generate_image()
        if img:
            score = calculate_overlap_score(img)
            scores.append(score)
            print(f"    Sample {i+1}: overlap score = {score}")
        else:
            print(f"    Sample {i+1}: generation failed")
    
    if not scores:
        return 999999
    
    avg_score = sum(scores) / len(scores)
    print(f"    Average overlap: {avg_score:.1f}")
    return avg_score

def main():
    print("=" * 70)
    print("ITERATIVE GEAR MESHING FORMULA OPTIMIZER")
    print("=" * 70)
    print()
    
    # Save original file
    original_file = Path("Meshed_Gears.py").read_text()
    
    # First, evaluate the existing test images
    print("STEP 1: Analyzing existing test images...")
    print("-" * 70)
    
    test_files = sorted(Path("Images/Meshed_Gears/0-svg").glob("test_*.svg"))
    results = []
    
    for test_file in test_files:
        score = calculate_overlap_score(test_file)
        formula_name = test_file.stem.replace("test_", "").split("_20262403")[0]
        print(f"  {formula_name}: {score}")
        results.append((formula_name, score, test_file))
    
    if results:
        results.sort(key=lambda x: x[1])
        print()
        print("Best existing formula:")
        print(f"  🏆 {results[0][0]} - Score: {results[0][1]}")
        best_score = results[0][1]
    else:
        best_score = 999999
    
    print()
    print("STEP 2: Testing additional formulas...")
    print("-" * 70)
    
    # Additional formulas to try
    additional_formulas = [
        ("F_neg_rot_minus_angle", "-existing_gear.rotation - angle"),
        ("G_neg_rot_plus_pi", "-existing_gear.rotation + math.pi"),
        ("H_neg_rot_minus_2angle_plus_pi", "-existing_gear.rotation - 2*angle + math.pi"),
        ("I_neg_rot", "-existing_gear.rotation"),
        ("J_neg_rot_plus_angle", "-existing_gear.rotation + angle"),
    ]
    
    try:
        new_results = []
        
        for formula_name, formula_code in additional_formulas:
            avg_score = test_formula(formula_name, formula_code, num_samples=2)
            new_results.append((formula_name, formula_code, avg_score))
            print()
        
        # Combine all results
        all_results = [(r[0], r[1], None) for r in results]  # existing
        all_results.extend([(r[0], r[2], r[1]) for r in new_results])  # new
        
        all_results.sort(key=lambda x: x[1])
        
        print()
        print("=" * 70)
        print("FINAL RESULTS (lower score is better)")
        print("=" * 70)
        
        for i, (name, score, formula) in enumerate(all_results[:10], 1):
            marker = "🏆" if i == 1 else f"{i:2d}."
            print(f"{marker} {name:40s} - Score: {score}")
        
        print()
        print("=" * 70)
        
        best = all_results[0]
        if best[2]:  # Has formula code (new result)
            print(f"✓ BEST FORMULA: {best[0]}")
            print(f"  Score: {best[1]:.1f}")
            print(f"  Code: {best[2]}")
            print()
            
            # Apply the best formula
            if best[1] < best_score * 0.8:  # At least 20% improvement
                modify_formula(best[2])
                print("✓ Applied best formula to Meshed_Gears.py")
            else:
                # Restore original
                Path("Meshed_Gears.py").write_text(original_file)
                print("⚠ No significant improvement found, kept original formula")
        else:
            print(f"✓ BEST FORMULA: {best[0]} (from existing tests)")
            print(f"  Score: {best[1]:.1f}")
            Path("Meshed_Gears.py").write_text(original_file)
            print("✓ Restored original Meshed_Gears.py")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        Path("Meshed_Gears.py").write_text(original_file)
        print("✓ Restored original Meshed_Gears.py due to error")

if __name__ == "__main__":
    main()
