#!/usr/bin/env python3
"""
Test gear meshing formulas by generating images and checking for overlaps
"""

import math
import random
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Test different rotation formulas
FORMULAS = [
    ("pi + half", lambda rot, angle, ta: -rot + math.pi + ta/2),
    ("2*angle + half", lambda rot, angle, ta: -rot - 2*angle + ta/2),
    ("pi - 2*angle + half", lambda rot, angle, ta: -rot + math.pi - 2*angle + ta/2),
    ("2*angle + pi + half", lambda rot, angle, ta: -rot - 2*angle + math.pi + ta/2),
    ("angle + half", lambda rot, angle, ta: -rot - angle + ta/2),
    ("pi + angle + half", lambda rot, angle, ta: -rot + math.pi - angle + ta/2),
    ("-pi - 2*angle + half", lambda rot, angle, ta: -rot - math.pi - 2*angle + ta/2),
    ("just -rot", lambda rot, angle, ta: -rot),
    ("just -rot + half", lambda rot, angle, ta: -rot + ta/2),
]

def parse_svg_paths(svg_file):
    """Extract path data from SVG"""
    tree = ET.parse(svg_file)
    root = tree.getroot()
    
    # Find all path elements
    paths = []
    for elem in root.iter():
        if elem.tag.endswith('path'):
            d = elem.get('d', '')
            if d:
                paths.append(d)
    
    return paths

def check_path_overlap(path1, path2):
    """Simple check: count how many path segments might overlap"""
    # This is a simplified check - just look at coordinate proximity
    # Extract numbers from path data
    import re
    
    coords1 = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', path1)]
    coords2 = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', path2)]
    
    overlap_count = 0
    threshold = 5.0  # pixels
    
    # Check pairs of coordinates
    for i in range(0, len(coords1)-1, 2):
        x1, y1 = coords1[i], coords1[i+1]
        for j in range(0, len(coords2)-1, 2):
            x2, y2 = coords2[j], coords2[j+1]
            dist = math.sqrt((x1-x2)**2 + (y1-y2)**2)
            if dist < threshold:
                overlap_count += 1
    
    return overlap_count

def test_formula(formula_name, formula_func):
    """Test a specific rotation formula"""
    print(f"\n{'='*60}")
    print(f"Testing formula: {formula_name}")
    print(f"{'='*60}")
    
    # Modify Meshed_Gears.py temporarily
    meshed_gears_path = Path("Meshed_Gears.py")
    original_content = meshed_gears_path.read_text()
    
    # Find and replace the rotation formula line
    import re
    pattern = r'new_rotation = .*'
    replacement = f'new_rotation = formula_func(existing_gear.rotation, angle, tooth_angle)  # TEST: {formula_name}'
    
    # Actually, we need to inject our formula differently
    # Let's create a test version
    test_content = original_content.replace(
        'new_rotation = -existing_gear.rotation + math.pi + tooth_angle / 2',
        f'new_rotation = {generate_formula_code(formula_func, formula_name)}'
    )
    
    # Write test version
    test_path = Path("Meshed_Gears_Test.py")
    test_path.write_text(test_content)
    
    # Generate one image using venv python
    import subprocess
    import os
    
    # Use the virtual environment's python
    venv_python = os.path.join('venv', 'Scripts', 'python.exe')
    result = subprocess.run(
        [venv_python, 'Meshed_Gears_Test.py', 'False', 'True', 'False', 'a6-landscape', 'random-by-line', 'clustered', 'uniform'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode != 0:
        print(f"❌ Generation failed: {result.stderr}")
        test_path.unlink()
        return None
    
    # Find the generated SVG
    svg_dir = Path("Images/Meshed_Gears/0-svg")
    latest_svg = max(svg_dir.glob("*.svg"), key=lambda p: p.stat().st_mtime)
    
    print(f"✓ Generated: {latest_svg.name}")
    
    # Parse and check overlaps
    paths = parse_svg_paths(latest_svg)
    print(f"  Found {len(paths)} paths (gears)")
    
    total_overlaps = 0
    for i in range(len(paths)):
        for j in range(i+1, len(paths)):
            overlaps = check_path_overlap(paths[i], paths[j])
            total_overlaps += overlaps
    
    print(f"  Overlap score: {total_overlaps}")
    
    # Cleanup
    test_path.unlink()
    
    return total_overlaps

def generate_formula_code(formula_func, name):
    """Generate inline formula code based on the name"""
    formulas_code = {
        "pi + half": "-existing_gear.rotation + math.pi + tooth_angle / 2",
        "2*angle + half": "-existing_gear.rotation - 2*angle + tooth_angle / 2",
        "pi - 2*angle + half": "-existing_gear.rotation + math.pi - 2*angle + tooth_angle / 2",
        "2*angle + pi + half": "-existing_gear.rotation - 2*angle + math.pi + tooth_angle / 2",
        "angle + half": "-existing_gear.rotation - angle + tooth_angle / 2",
        "pi + angle + half": "-existing_gear.rotation + math.pi - angle + tooth_angle / 2",
        "-pi - 2*angle + half": "-existing_gear.rotation - math.pi - 2*angle + tooth_angle / 2",
        "just -rot": "-existing_gear.rotation",
        "just -rot + half": "-existing_gear.rotation + tooth_angle / 2",
    }
    return formulas_code.get(name, formulas_code["pi + half"])

def main():
    print("=" * 60)
    print("GEAR MESHING FORMULA TESTER")
    print("=" * 60)
    print("Testing different rotation formulas...")
    
    results = []
    
    for formula_name, formula_func in FORMULAS:
        try:
            overlap_score = test_formula(formula_name, formula_func)
            if overlap_score is not None:
                results.append((formula_name, overlap_score))
        except Exception as e:
            print(f"❌ Error testing {formula_name}: {e}")
    
    # Report results
    print("\n" + "=" * 60)
    print("RESULTS (lower overlap score is better)")
    print("=" * 60)
    
    results.sort(key=lambda x: x[1])
    
    for i, (name, score) in enumerate(results, 1):
        marker = "🏆" if i == 1 else "  "
        print(f"{marker} {i}. {name:25s} - Overlap: {score}")
    
    if results:
        print(f"\n✓ Best formula: {results[0][0]} (score: {results[0][1]})")

if __name__ == "__main__":
    main()
