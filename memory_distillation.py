"""
CHRONOS Memory Rule Distillation Engine (claude-mem & MiMo-Code Pattern)
Extracts and distills permanent business rules and user corrections into learned_rules.json.
"""

import os
import json
import datetime

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "CHRONOS_MEMORY")
RULES_FILE = os.path.join(MEMORY_DIR, "learned_rules.json")

def _init_memory_store():
  os.makedirs(MEMORY_DIR, exist_ok=True)
  if not os.path.exists(RULES_FILE):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
      json.dump({"learned_rules": [], "last_updated": datetime.datetime.now().isoformat()}, f, indent=4)

def add_learned_rule(rule_text: str, category: str = "general", source: str = "user_correction") -> dict:
  """Adds a new distilled rule to permanent memory."""
  _init_memory_store()
  now_str = datetime.datetime.now().isoformat()

  with open(RULES_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

  # Check for duplicates
  existing_texts = [r["rule_text"].lower() for r in data["learned_rules"]]
  if rule_text.lower() in existing_texts:
    return {"status": "duplicate", "rule_text": rule_text}

  rule_entry = {
    "id": len(data["learned_rules"]) + 1,
    "rule_text": rule_text,
    "category": category,
    "source": source,
    "created_at": now_str
  }

  data["learned_rules"].append(rule_entry)
  data["last_updated"] = now_str

  with open(RULES_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

  print(f" [MEMORY DISTILLED]: Added new rule -> '{rule_text}'")
  return {"status": "added", "rule": rule_entry}

def get_relevant_learned_rules(profile_name: str = "general") -> list:
  """Retrieves all active distilled rules for system prompt injection."""
  _init_memory_store()
  try:
    with open(RULES_FILE, "r", encoding="utf-8") as f:
      data = json.load(f)
    return [r["rule_text"] for r in data.get("learned_rules", [])]
  except Exception as e:
    print(f"️ [Memory Error]: Could not load learned rules: {e}")
    return []

def get_distilled_rules_system_prompt() -> str:
  """Formats distilled rules for system prompt injection."""
  rules = get_relevant_learned_rules()
  if not rules:
    return ""
  
  prompt = "\n\n[CHRONOS LEARNED BUSINESS & USER RULES]:\n"
  for idx, rule in enumerate(rules, 1):
    prompt += f"- Rule {idx}: {rule}\n"
  return prompt
