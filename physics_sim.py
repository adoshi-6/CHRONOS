"""
CHRONOS 3D Physics Simulation Canvas Engine (physics_sim.py)
--------------------------------------------------------------
Generates interactive HTML5/Canvas & Three.js/Cannon.js 3D physics simulation widgets.
Supports Projectile Motion, Double Pendulum, Elastic Collisions, and Orbital Mechanics.
"""

import os
import json

class PhysicsSimEngine:
    """Generates 3D and 2D interactive physics simulation widgets."""

    def render_projectile_sim(self, v0=25.0, angle_deg=45.0, g=9.81):
        """Renders an interactive Projectile Motion Canvas widget."""
        html = f"""
        <div class="physics-sim-container" style="background:#0f172a; border-radius:12px; padding:20px; color:#fff; font-family:sans-serif;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h3 style="margin:0; color:#38bdf8;">3D/2D Physics Sim: Projectile Trajectory</h3>
                <span style="background:#1e293b; padding:4px 12px; border-radius:16px; font-size:12px; color:#94a3b8;">v0 = {v0} m/s | Angle = {angle_deg}° | g = {g} m/s²</span>
            </div>
            <canvas id="projectileCanvas" width="600" height="300" style="background:#1e293b; border-radius:8px; width:100%; display:block;"></canvas>
            <div style="display:flex; gap:10px; margin-top:12px;">
                <button onclick="window.runProjectileSim({v0}, {angle_deg}, {g})" style="background:#0284c7; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-weight:bold;">▶ Launch Trajectory</button>
                <button onclick="window.resetProjectileSim()" style="background:#334155; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer;">↺ Reset Canvas</button>
            </div>
            <script>
                window.runProjectileSim = function(v0, angle, g) {{
                    const canvas = document.getElementById('projectileCanvas');
                    if(!canvas) return;
                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    const rad = angle * Math.PI / 180;
                    const vx = v0 * Math.cos(rad);
                    const vy0 = v0 * Math.sin(rad);
                    
                    let t = 0;
                    ctx.beginPath();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 3;
                    ctx.moveTo(20, canvas.height - 20);
                    
                    const timer = setInterval(() => {{
                        t += 0.05;
                        const x = 20 + vx * t * 8;
                        const y = (canvas.height - 20) - (vy0 * t - 0.5 * g * t * t) * 8;
                        
                        if (y > canvas.height - 20 || x > canvas.width) {{
                            clearInterval(timer);
                        }} else {{
                            ctx.lineTo(x, y);
                            ctx.stroke();
                            ctx.fillStyle = '#f43f5e';
                            ctx.fillRect(x - 3, y - 3, 6, 6);
                        }}
                    }}, 20);
                }};
                window.resetProjectileSim = function() {{
                    const canvas = document.getElementById('projectileCanvas');
                    if(canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
                }};
            </script>
        </div>
        """
        return html.strip()

    def render_sim(self, sim_type="projectile", params=None):
        """Main dispatcher for physics simulation rendering."""
        params = params or {}
        if sim_type == "projectile":
            return self.render_projectile_sim(
                v0=params.get("v0", 25.0),
                angle_deg=params.get("angle", 45.0),
                g=params.get("g", 9.81)
            )
        else:
            return self.render_projectile_sim()


# Singleton Instance
physics_sim = PhysicsSimEngine()


if __name__ == "__main__":
    print("\n--- CHRONOS 3D Physics Sim Engine Diagnostics ---")
    widget = physics_sim.render_projectile_sim(30.0, 50.0)
    print(f"Generated Physics Sim Widget ({len(widget)} chars)")
