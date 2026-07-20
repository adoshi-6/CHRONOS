"""
CHRONOS Trust Level Auto-Escalation Engine (Fable 5 & 6 / BALL Setup Pattern)
Tracks tool execution history in trust_ledger.db and automatically escalates
routine tools from NEEDS_APPROVAL to AUTO_APPROVED after verified successes.
"""

import os
import sqlite3
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "CHRONOS_SECURITY", "trust_ledger.db")

# Default approval thresholds and daily budget caps
SUCCESS_THRESHOLD_FOR_ESCALATION = 5
DEFAULT_DAILY_AUTO_BUDGET = 50

# Global in-memory overrides for current session
TRUST_LEVEL_CACHE = {}
DAILY_USAGE_COUNTER = {}

def _get_connection():
 os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
 conn = sqlite3.connect(DB_PATH, check_same_thread=False)
 conn.execute("PRAGMA journal_mode=WAL;")
 return conn

def init_trust_escalation_tables():
 """Initializes the trust escalation policy table in trust_ledger.db."""
 conn = _get_connection()
 cursor = conn.cursor()
 cursor.execute("""
  CREATE TABLE IF NOT EXISTS trust_policy (
   tool_name TEXT PRIMARY KEY,
   trust_level TEXT DEFAULT 'NEEDS_APPROVAL',
   consecutive_successes INTEGER DEFAULT 0,
   total_approvals INTEGER DEFAULT 0,
   total_rejections INTEGER DEFAULT 0,
   daily_budget INTEGER DEFAULT 50,
   last_updated TEXT
  )
 """)
 conn.commit()
 conn.close()

def get_tool_trust_status(tool_name: str) -> dict:
 """Retrieves current trust level, daily budget, and consecutive success count for a tool."""
 init_trust_escalation_tables()
 conn = _get_connection()
 cursor = conn.cursor()
 cursor.execute("SELECT trust_level, consecutive_successes, total_approvals, total_rejections, daily_budget FROM trust_policy WHERE tool_name = ?", (tool_name,))
 row = cursor.fetchone()
 conn.close()

 if not row:
  return {
   "tool_name": tool_name,
   "trust_level": "NEEDS_APPROVAL",
   "consecutive_successes": 0,
   "total_approvals": 0,
   "total_rejections": 0,
   "daily_budget": DEFAULT_DAILY_AUTO_BUDGET,
   "auto_approved": False
  }

 trust_level, consecutive_successes, total_approvals, total_rejections, daily_budget = row
 today_str = datetime.date.today().isoformat()
 usage_key = f"{tool_name}_{today_str}"
 used_today = DAILY_USAGE_COUNTER.get(usage_key, 0)

 auto_approved = (trust_level == "AUTO_APPROVED") and (used_today < daily_budget)

 return {
  "tool_name": tool_name,
  "trust_level": trust_level,
  "consecutive_successes": consecutive_successes,
  "total_approvals": total_approvals,
  "total_rejections": total_rejections,
  "daily_budget": daily_budget,
  "used_today": used_today,
  "auto_approved": auto_approved
 }

def record_tool_verdict(tool_name: str, approved: bool) -> dict:
 """
 Logs user approval/rejection verdict for a tool call.
 Escalates to AUTO_APPROVED if consecutive_successes >= 5.
 Demotes to NEEDS_APPROVAL immediately on any rejection.
 """
 init_trust_escalation_tables()
 now_str = datetime.datetime.now().isoformat()
 conn = _get_connection()
 cursor = conn.cursor()

 cursor.execute("SELECT trust_level, consecutive_successes, total_approvals, total_rejections, daily_budget FROM trust_policy WHERE tool_name = ?", (tool_name,))
 row = cursor.fetchone()

 if not row:
  trust_level = "NEEDS_APPROVAL"
  consecutive_successes = 0
  total_approvals = 0
  total_rejections = 0
  daily_budget = DEFAULT_DAILY_AUTO_BUDGET
 else:
  trust_level, consecutive_successes, total_approvals, total_rejections, daily_budget = row

 if approved:
  total_approvals += 1
  consecutive_successes += 1
  if consecutive_successes >= SUCCESS_THRESHOLD_FOR_ESCALATION and trust_level != "AUTO_APPROVED":
   trust_level = "AUTO_APPROVED"
   print(f" [TRUST ESCALATED]: Tool '{tool_name}' auto-escalated to AUTO_APPROVED after {consecutive_successes} consecutive successes!")
 else:
  total_rejections += 1
  consecutive_successes = 0
  if trust_level == "AUTO_APPROVED":
   trust_level = "NEEDS_APPROVAL"
   print(f"️ [TRUST DEMOTED]: Tool '{tool_name}' demoted to NEEDS_APPROVAL due to user rejection!")

 cursor.execute("""
  INSERT INTO trust_policy (tool_name, trust_level, consecutive_successes, total_approvals, total_rejections, daily_budget, last_updated)
  VALUES (?, ?, ?, ?, ?, ?, ?)
  ON CONFLICT(tool_name) DO UPDATE SET
   trust_level = excluded.trust_level,
   consecutive_successes = excluded.consecutive_successes,
   total_approvals = excluded.total_approvals,
   total_rejections = excluded.total_rejections,
   daily_budget = excluded.daily_budget,
   last_updated = excluded.last_updated
 """, (tool_name, trust_level, consecutive_successes, total_approvals, total_rejections, daily_budget, now_str))

 conn.commit()
 conn.close()

 return get_tool_trust_status(tool_name)

def increment_daily_auto_usage(tool_name: str):
 """Increments the daily execution count for an auto-approved tool call."""
 today_str = datetime.date.today().isoformat()
 usage_key = f"{tool_name}_{today_str}"
 DAILY_USAGE_COUNTER[usage_key] = DAILY_USAGE_COUNTER.get(usage_key, 0) + 1

# Initialize tables on import
init_trust_escalation_tables()
