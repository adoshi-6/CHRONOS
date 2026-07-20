"""
CHRONOS File Lock Conflict Detection Module (1jehuang/jcode Pattern)
Manages thread-safe file locks for parallel sub-agents and concurrent processes.
"""

import os
import time

ACTIVE_LOCKS = {}

def acquire_file_lock(filepath: str, agent_id: str = "main", timeout_seconds: float = 5.0) -> bool:
 """Acquires an exclusive lock on a file path."""
 abs_path = os.path.abspath(filepath)
 start_time = time.time()

 while time.time() - start_time < timeout_seconds:
  if abs_path not in ACTIVE_LOCKS or ACTIVE_LOCKS[abs_path] == agent_id:
   ACTIVE_LOCKS[abs_path] = agent_id
   return True
  time.sleep(0.1)

 print(f" [FILE LOCK CONFLICT]: Agent '{agent_id}' could not acquire lock on '{os.path.basename(abs_path)}' (Locked by '{ACTIVE_LOCKS.get(abs_path)}')")
 return False

def release_file_lock(filepath: str, agent_id: str = "main"):
 """Releases an exclusive lock on a file path."""
 abs_path = os.path.abspath(filepath)
 if abs_path in ACTIVE_LOCKS and ACTIVE_LOCKS[abs_path] == agent_id:
  del ACTIVE_LOCKS[abs_path]
