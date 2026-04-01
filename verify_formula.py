"""
Generate multiple samples with the best formula to verify performance
"""
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import re
import math

def parse_svg_coordinates(svg_file):
    """Extract all coordinate pairs from SVG paths"""
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
    """Calculate an overlap score for a gear SVG file"""
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
    
    except Exception as e:
        return 999999

def generate_and_test(num_samples=10):
    """Generate multiple samples and calculate average overlap"""
    print(f"Generating {num_samples} samples to verify formula performance...")
    print("=" * 70)
    
    scores = []
    
    for i in range(num_samples):
        # Generate one image
        result = subprocess.run(
            ['powershell', '-Command', 
             f'.\\venv\\Scripts\\python.exe Meshed_Gears.py False True False a6-landscape random-by-line clustered uniform'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            # Find the latest SVG
            svg_dir = Path("Images/Meshed_Gears/0-svg")
            all_svgs = [f for f in svg_dir.glob("*.svg") if not f.name.startswith("test_")]
            latest_svg = max(all_svgs, key=lambda p: p.stat().st_mtime)
            
            # Calculate score
            score = calculate_overlap_score(latest_svg)
            scores.append(score)
            print(f"Sample {i+1:2d}: {latest_svg.name} - Score: {score}")
        else:
            print(f"Sample {i+1:2d}: Generation failed")
    
    print("=" * 70)
    if scores:
        avg = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        
        print(f"Results ({len(scores)} samples):")
        print(f"  Average: {avg:.1f}")
        print(f"  Best:    {min_score}")
        print(f"  Worst:   {max_score}")
        print()
        print(f"Comparison to test formula D: 494")
        
        if avg < 494:
            improvement = ((494 - avg) / 494) * 100
            print(f"  ✓ Current formula is {improvement:.1f}% better on average")
        else:
            decline = ((avg - 494) / 494) * 100
            print(f"  ⚠ Current formula is {decline:.1f}% worse on average")
            print(f"  ⚠ Consider trying formula B: -rot - 2*angle + half (score: 516)")
    
    return scores

if __name__ == "__main__":
    generate_and_test(10)
