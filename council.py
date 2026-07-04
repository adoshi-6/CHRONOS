import ollama
import re

from config import SMART_MODEL

LOCAL_MODEL = SMART_MODEL


def _chat(system: str, user: str) -> str:
    """Single model call. Strips reasoning blocks from thinking models."""
    try:
        response = ollama.chat(
            model=LOCAL_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ]
        )
        raw = response['message']['content']
        return re.sub(r'<think>[\s\S]*?</think>', '', raw).strip()
    except Exception as e:
        return f"[Agent unavailable: {e}]"


def run_council_debate(user_idea: str) -> dict:
    """
    Full 6-seat council debate.

    Expanded from 3 agents (Contrarian, Synergist, Chairman) to 6:
      1. Contrarian       — risks and flaws
      2. First Principles — rebuild from axioms
      3. Expansionist     — hidden upside and scale
      4. Outsider         — objective, no jargon
      5. Executor         — one concrete next action
      6. Chairman         — synthesises all five

    Returns a dict with all six agent keys.
    """
    print("\n==================================================")
    print("  Council Chamber Active — 6 Agents")
    print("==================================================")

    print("[1/6] Contrarian...")
    text1 = _chat(
        "You are The Contrarian. Identify every risk, flaw, and reason this will fail. "
        "Be direct. Maximum 2 sentences.",
        f"Identify vulnerabilities: {user_idea}"
    )
    print("  done.")

    print("[2/6] First Principles Thinker...")
    text2 = _chat(
        "You are the First Principles Thinker. Strip all assumptions. "
        "Rebuild the core logic from raw axioms. Maximum 2 sentences.",
        f"Deconstruct and rebuild: {user_idea}"
    )
    print("  done.")

    print("[3/6] Expansionist...")
    text3 = _chat(
        "You are The Expansionist. Uncover hidden upside, scale plays, "
        "and opportunities being missed. Maximum 2 sentences.",
        f"Maximize scale and upside: {user_idea}"
    )
    print("  done.")

    print("[4/6] Outsider...")
    text4 = _chat(
        "You are The Outsider. Evaluate with complete objectivity and zero jargon. "
        "Maximum 2 sentences.",
        f"Evaluate neutrally: {user_idea}"
    )
    print("  done.")

    print("[5/6] Executor...")
    text5 = _chat(
        "You are The Executor. Focus only on what to do next. "
        "Give one concrete, actionable next step. Maximum 2 sentences.",
        f"What is the immediate next action? {user_idea}"
    )
    print("  done.")

    print("[6/6] Chairman...")
    chairman_context = (
        f"Objective: {user_idea}\n\n"
        f"Contrarian: {text1}\n\n"
        f"First Principles: {text2}\n\n"
        f"Expansionist: {text3}\n\n"
        f"Outsider: {text4}\n\n"
        f"Executor: {text5}"
    )
    text6 = _chat(
        "You are The Chairman. Read all five agent briefs and deliver one clear, "
        "unified recommendation — the single best path forward. Maximum 3 sentences.",
        chairman_context
    )
    print("  done.")

    print("\n==================================================")
    print("  Debate complete.")
    print("==================================================\n")

    return {
        "contrarian":       text1,
        "first_principles": text2,
        "expansionist":     text3,
        "outsider":         text4,
        "executor":         text5,
        "chairman":         text6,
    }
