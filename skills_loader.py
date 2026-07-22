"""
CHRONOS Modular Skills Library Framework (skills_loader.py)
------------------------------------------------------------
Dynamic plugin loader and skill registry engine for CHRONOS.
Scans the skills/ directory, dynamically imports python skill modules,
registers skill metadata, and provides intent matching and execution sandbox.
"""

import os
import sys
import importlib.util
import traceback
import time

CHRONOS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(CHRONOS_DIR, "skills")

class SkillsManager:
    """Registry and execution orchestrator for CHRONOS skills plugins."""

    def __init__(self, skills_dir=SKILLS_DIR):
        self.skills_dir = skills_dir
        self.registry = {}
        self.ensure_skills_dir()
        self.load_all_skills()

    def ensure_skills_dir(self):
        """Ensure the skills/ folder exists."""
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir, exist_ok=True)
            print(f"[SKILLS] Created skills directory: {self.skills_dir}")

    def load_all_skills(self):
        """Scans skills_dir for .py files and loads them into the registry."""
        self.registry.clear()
        if not os.path.exists(self.skills_dir):
            return

        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                skill_path = os.path.join(self.skills_dir, filename)
                self.load_skill_file(skill_path)

        print(f"[SKILLS] Loaded {len(self.registry)} skill plugin(s) successfully.")

    def load_skill_file(self, filepath):
        """Dynamically imports a single python skill module."""
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Validate skill contract
            name = getattr(module, "SKILL_NAME", module_name)
            desc = getattr(module, "SKILL_DESCRIPTION", "No description provided.")
            triggers = getattr(module, "SKILL_TRIGGERS", [])
            handler = getattr(module, "run_skill", None)

            if handler is None or not callable(handler):
                print(f"[SKILLS WARNING] Skill '{module_name}' skipped: missing callable run_skill() function.")
                return

            self.registry[name.lower()] = {
                "name": name,
                "description": desc,
                "triggers": [t.lower() for t in triggers],
                "handler": handler,
                "module_path": filepath,
                "loaded_at": time.time()
            }
            print(f"[SKILLS] Registered skill: '{name}' ({len(triggers)} triggers)")
        except Exception as e:
            print(f"[SKILLS ERROR] Failed to load skill file '{filepath}': {e}")
            traceback.print_exc()

    def list_skills(self):
        """Returns metadata for all registered skills."""
        output = []
        for key, info in self.registry.items():
            output.append({
                "name": info["name"],
                "description": info["description"],
                "triggers": info["triggers"]
            })
        return output

    def match_skill(self, user_query):
        """Finds the best matching skill for a user prompt based on keyword triggers."""
        query_lower = user_query.lower()
        matched = []

        for key, info in self.registry.items():
            for trigger in info["triggers"]:
                if trigger in query_lower:
                    matched.append((info, len(trigger)))

        if not matched:
            return None

        # Sort by trigger length (longer/more specific matches first)
        matched.sort(key=lambda x: x[1], reverse=True)
        return matched[0][0]

    def execute_skill(self, skill_name_or_info, **kwargs):
        """Safely executes a registered skill in an isolated exception handler."""
        if isinstance(skill_name_or_info, str):
            info = self.registry.get(skill_name_or_info.lower())
        else:
            info = skill_name_or_info

        if not info:
            return {"success": False, "error": f"Skill '{skill_name_or_info}' not found in registry."}

        start_time = time.time()
        try:
            handler = info["handler"]
            result = handler(**kwargs)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": True,
                "skill": info["name"],
                "result": result,
                "duration_ms": duration_ms
            }
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "skill": info["name"],
                "error": str(e),
                "duration_ms": duration_ms
            }


# Singleton instance for server integration
skills_manager = SkillsManager()


if __name__ == "__main__":
    print("\n--- CHRONOS Skills Loader Diagnostics ---")
    skills = skills_manager.list_skills()
    print("Registered Skills List:")
    for s in skills:
        print(f" - {s['name']}: {s['description']} (Triggers: {s['triggers']})")
