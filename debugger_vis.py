"""
CHRONOS CS Code Debugger & Pointer Visualizer (debugger_vis.py)
----------------------------------------------------------------
Renders memory stack/heap allocations, C/C++ pointer addresses,
array index highlights, and linked list node chains.
"""

import os
import json

class DebuggerVisualizerEngine:
    """Generates CS memory diagrams, stack frames, and pointer maps."""

    def render_pointer_memory_map(self, variables=None):
        """Renders a memory stack table with hex addresses and pointer references."""
        variables = variables or [
            {"name": "ptr_a", "type": "int*", "address": "0x7fff5fbff7c0", "value": "0x7fff5fbff7c8"},
            {"name": "val", "type": "int", "address": "0x7fff5fbff7c8", "value": "42"}
        ]

        rows_html = ""
        for v in variables:
            rows_html += f"""
            <tr style="border-bottom:1px solid #334155;">
                <td style="padding:10px; font-family:monospace; color:#38bdf8;">{v['address']}</td>
                <td style="padding:10px; font-weight:bold; color:#f8fafc;">{v['name']}</td>
                <td style="padding:10px; color:#cbd5e1;">{v['type']}</td>
                <td style="padding:10px; font-family:monospace; color:#f43f5e; font-weight:bold;">{v['value']}</td>
            </tr>
            """

        html = f"""
        <div class="debugger-vis-container" style="background:#0f172a; border-radius:12px; padding:20px; color:#fff; font-family:sans-serif; border:1px solid #1e293b;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h3 style="margin:0; color:#38bdf8;">CS Pointer & Stack Memory Map</h3>
                <span style="background:#1e293b; color:#94a3b8; padding:4px 12px; border-radius:16px; font-size:12px;">Stack Frame [main()]</span>
            </div>
            <table style="width:100%; border-collapse:collapse; background:#1e293b; border-radius:8px; overflow:hidden;">
                <thead>
                    <tr style="background:#334155; text-align:left; color:#94a3b8; font-size:12px; text-transform:uppercase;">
                        <th style="padding:10px;">Memory Address</th>
                        <th style="padding:10px;">Variable</th>
                        <th style="padding:10px;">Type</th>
                        <th style="padding:10px;">Stored Value / Target</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        return html.strip()

    def render_linked_list(self, nodes=None):
        """Renders linked list node chain diagram."""
        nodes = nodes or [10, 20, 30, 40]
        chain_html = ""
        for idx, val in enumerate(nodes):
            chain_html += f"""
            <div style="background:#1e293b; border:2px solid #38bdf8; border-radius:8px; padding:12px 20px; text-align:center; min-width:70px;">
                <div style="font-size:10px; color:#94a3b8;">NODE {idx}</div>
                <div style="font-size:18px; font-weight:bold; color:#38bdf8;">{val}</div>
            </div>
            """
            if idx < len(nodes) - 1:
                chain_html += f'<div style="font-size:24px; color:#64748b; font-weight:bold; align-self:center;">→</div>'
            else:
                chain_html += f'<div style="font-size:24px; color:#f43f5e; font-weight:bold; align-self:center;">→ NULL</div>'

        html = f"""
        <div class="debugger-vis-container" style="background:#0f172a; border-radius:12px; padding:20px; color:#fff; font-family:sans-serif; border:1px solid #1e293b;">
            <h3 style="margin:0 0 16px 0; color:#38bdf8;">Linked List Memory Pointer Chain</h3>
            <div style="display:flex; gap:12px; align-items:center; overflow-x:auto; padding-bottom:8px;">
                {chain_html}
            </div>
        </div>
        """
        return html.strip()


# Singleton Instance
debugger_vis = DebuggerVisualizerEngine()


if __name__ == "__main__":
    print("\n--- CHRONOS CS Debugger & Pointer Visualizer Diagnostics ---")
    mem_map = debugger_vis.render_pointer_memory_map()
    ll_map = debugger_vis.render_linked_list()
    print(f"Generated Memory Map ({len(mem_map)} chars) | Linked List ({len(ll_map)} chars)")
