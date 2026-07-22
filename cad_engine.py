"""
CHRONOS OpenSCAD & 2D DXF CAD Engine (cad_engine.py)
---------------------------------------------------
Generates OpenSCAD (.scad) 3D parametric models and 2D DXF CAD wireframe entities.
Saves CAD files to cad_exports/ directory.
"""

import os
import json
import time

CHRONOS_DIR = os.path.dirname(os.path.abspath(__file__))
CAD_EXPORTS_DIR = os.path.join(CHRONOS_DIR, "cad_exports")

class CADEngine:
    """Generates 3D OpenSCAD models and 2D DXF wireframes."""

    def __init__(self, output_dir=CAD_EXPORTS_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_scad_model(self, part_name="bracket", length=50, width=30, height=15, hole_r=4):
        """Generates 3D OpenSCAD parametric code for a mechanical part."""
        scad_code = f"""// CHRONOS Parametric 3D CAD Model: {part_name}
// Generated automatically on {time.strftime('%Y-%m-%d %H:%M:%S')}

$fn = 100;

module main_bracket() {{
    difference() {{
        // Base Block
        cube([{length}], [{width}], [{height}], center = true);
        
        # Center Mounting Hole
        cylinder(h = {height} + 2, r = {hole_r}, center = true);
        
        // Corner Fillets / Cutouts
        translate([{length}/2 - 5], [{width}/2 - 5], 0)
            cylinder(h = {height} + 2, r = 2, center = true);
    }}
}}

main_bracket();
"""
        filename = f"{part_name}_{int(time.time())}.scad"
        save_path = os.path.join(self.output_dir, filename)

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(scad_code)

        print(f"[CAD ENGINE] Saved OpenSCAD model: {save_path}")

        return {
            "success": True,
            "filename": filename,
            "filepath": save_path,
            "scad_code": scad_code
        }

    def generate_dxf_wireframe(self, part_name="plate_2d", width=100.0, height=60.0):
        """Generates minimal 2D DXF ASCII wireframe content."""
        dxf_content = f"""0
SECTION
2
HEADER
0
ENDSEC
0
SECTION
2
ENTITIES
0
LINE
8
0
10
0.0
20
0.0
11
{width}
21
0.0
0
LINE
8
0
10
{width}
20
0.0
11
{width}
21
{height}
0
LINE
8
0
10
{width}
20
{height}
11
0.0
21
{height}
0
LINE
8
0
10
0.0
20
{height}
11
0.0
21
0.0
0
ENDSEC
0
EOF
"""
        filename = f"{part_name}_{int(time.time())}.dxf"
        save_path = os.path.join(self.output_dir, filename)

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(dxf_content)

        print(f"[CAD ENGINE] Saved 2D DXF wireframe: {save_path}")

        return {
            "success": True,
            "filename": filename,
            "filepath": save_path,
            "dxf_content": dxf_content
        }


# Singleton Instance
cad_engine = CADEngine()


if __name__ == "__main__":
    print("\n--- CHRONOS CAD Engine Diagnostics ---")
    scad_res = cad_engine.generate_scad_model("flange_mount", 60, 40, 20, 6)
    dxf_res = cad_engine.generate_dxf_wireframe("base_plate", 120.0, 80.0)
    print(f"Generated SCAD: {scad_res['filename']} | Generated DXF: {dxf_res['filename']}")
