"""
CHRONOS Clarity Gate Engine (Varun Mayya Pattern)
Evaluates high-impact ambiguous requests and prompts for targeted clarification before executing.
"""

AMBIGUOUS_KEYWORDS = [
 "delete all", "cancel all", "wipe everything", "reset system",
 "send to everyone", "change all prices", "reconfigure"
]

def evaluate_clarity(user_prompt: str) -> dict:
 """
 Evaluates whether a request contains high ambiguity or destructive scope.
 Returns dict with needs_clarification boolean and suggested questions.
 """
 prompt_lower = user_prompt.lower().strip()

 # Check for destructive/broad ambiguity keywords
 matched_keywords = [kw for kw in AMBIGUOUS_KEYWORDS if kw in prompt_lower]

 if matched_keywords:
  return {
   "needs_clarification": True,
   "matched_keyword": matched_keywords[0],
   "clarifying_questions": [
    f"You requested an action matching '{matched_keywords[0]}'. Could you specify the exact targets or timeframes?",
    "Would you like me to run a dry-run preview before executing this across all records?"
   ]
  }

 return {
  "needs_clarification": False,
  "matched_keyword": None,
  "clarifying_questions": []
 }
