"""
CHRONOS Seed Skill: System Diagnostics (system_info_skill.py)
"""

import platform
import os
import psutil

SKILL_NAME = "System Diagnostics"
SKILL_DESCRIPTION = "Provides real-time CPU, RAM, Disk, and OS metrics."
SKILL_TRIGGERS = ["system info", "cpu usage", "ram usage", "disk space", "system status"]

def run_skill(**kwargs):
    """Gathers system health metrics."""
    cpu_pct = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    return {
        "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "cpu_usage_percent": f"{cpu_pct}%",
        "memory_total_gb": round(mem.total / (1024**3), 2),
        "memory_used_gb": round(mem.used / (1024**3), 2),
        "memory_percent": f"{mem.percent}%",
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "disk_percent": f"{disk.percent}%"
    }
