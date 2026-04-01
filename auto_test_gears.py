"""
Automated gear meshing formula tester
Modifies Meshed_Gears.py, generates images with different formulas, compares results
"""

import subprocess
from pathlib import Path

TEST_FORMULAS = [
    ("A_neg_rot_plus_pi_plus_half", "-existing_gear.rotation + math.pi + tooth_angle / 2"),
    ("B_neg_rot_minus_2angle_plus_half", "-existing_gear.rotation - 2*angle + tooth_angle / 2"),
    ("C_neg_rot_plus_pi_minus_2angle_plus_half", "-existing_gear.rotation + math.pi - 2*angle + tooth_angle / 2"),
    ("D_neg_rot_minus_angle_plus_half", "-existing_gear.rotation - angle + tooth_angle / 2"),
    ("E_neg_rot_plus_pi_minus_angle_plus_half", "-existing_gear.rotation + math.pi - angle + tooth_angle / 2"),
]

def modify_formula(formula_code):
    """Modify Meshed_Gears.py with a specific formula"""
    filepath = Path("Meshed_Gears.py")
    content = filepath.read_text()
    
    # Find the line starting with "new_rotation ="
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('new_rotation =') and 'existing_gear.rotation' in line:
            # Replace this line
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + f'new_rotation = {formula_code}'
            break
    
    filepath.write_text('\n'.join(lines))

def generate_image(formula_name):
    """Generate one test image"""
    result = subprocess.run(
        ['powershell', '-Command', 
         f'.\\venv\\Scripts\\python.exe Meshed_Gears.py False True False a6-landscape random-by-line clustered uniform'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode != 0:
        print(f"  ❌ Generation failed")
        return None
    
    # Find the latest SVG
    svg_dir = Path("Images/Meshed_Gears/0-svg")
    latest_svg = max(svg_dir.glob("*.svg"), key=lambda p: p.stat().st_mtime)
    
    # Rename it to include the formula name
    new_name = svg_dir / f"test_{formula_name}_{latest_svg.name}"
    latest_svg.rename(new_name)
    
    return new_name

def main():
    print("=" * 70)
    print("AUTOMATED GEAR MESHING FORMULA TESTER")
    print("=" * 70)
    print()
    
    # Save original file
    original_file = Path("Meshed_Gears.py").read_text()
    
    try:
        for formula_name, formula_code in TEST_FORMULAS:
            print(f"Testing: {formula_name}")
            print(f"  Formula: {formula_code}")
            
            # Modify the file
            modify_formula(formula_code)
            
            # Generate image
            output_file = generate_image(formula_name)
            
            if output_file:
                print(f"  ✓ Generated: {output_file.name}")
            print()
    
    finally:
        # Restore original file
        Path("Meshed_Gears.py").write_text(original_file)
        print("✓ Restored original Meshed_Gears.py")
    
    print()
    print("=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
    print("Check Images/Meshed_Gears/0-svg/test_*.svg files")
    print("Look for gears where teeth mesh properly at contact points")

if __name__ == "__main__":
    main()
