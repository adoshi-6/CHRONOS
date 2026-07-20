"""
CHRONOS AgentShield Security Guardrails (ECC Pattern)
Enforces constitutional guardrails, policy checks, and secret redactions across all sub-agents.
"""

import re

CONSTITUTIONAL_RULES = [
  "NEVER reveal private API keys, tokens, or PIN credentials in responses.",
  "NEVER perform hard data deletions without explicit PIN gate authorization.",
  "NEVER dispatch outbound communications without user approval or drafts-first verification.",
  "ALWAYS log execution events to trust_ledger.py for auditing.",
  "ALWAYS enforce token efficiency and brief executive responses in Business Mode."
]

SECRET_PATTERNS = [
  r"AIzaSy[A-Za-z0-9_-]{33}",     # Gemini API Keys
  r"sk-proj-[A-Za-z0-9_-]{48}",    # OpenAI API Keys
  r"sk-ant-[A-Za-z0-9_-]{48}",     # Anthropic API Keys
  r"100\.\d{1,3}\.\d{1,3}\.\d{1,3}"  # Tailscale IP pattern
]

def sanitize_response(text: str) -> str:
  """Scans and redacts sensitive API keys, tokens, or IP patterns from LLM output."""
  if not text:
    return ""
  sanitized = text
  for pattern in SECRET_PATTERNS:
    sanitized = re.sub(pattern, "[REDACTED_SECRET]", sanitized)
  return sanitized

def validate_action_policy(action_name: str, parameters: dict = None) -> tuple[bool, str]:
  """
  Evaluates proposed action against AgentShield constitutional guardrails.
  Returns (is_allowed, policy_reason).
  """
  parameters = parameters or {}

  # Hard-coded protected actions
  if action_name in ["delete_file", "format_disk", "wipe_database"]:
    return False, "Action violates AgentShield Constitutional Policy: Hard data deletion requires PIN gate."

  if action_name in ["send_email", "post_social_media"] and not parameters.get("user_approved", False):
    return False, "Action requires user approval before dispatching outbound communications."

  return True, "Policy check passed."

def get_agent_shield_system_instructions() -> str:
  """Returns formatted AgentShield constitutional guardrails for injection into system prompts."""
  instructions = "\n\n[AGENTSHIELD CONSTITUTIONAL SECURITY GUARDRAILS]:\n"
  for idx, rule in enumerate(CONSTITUTIONAL_RULES, 1):
    instructions += f"{idx}. {rule}\n"
  return instructions
