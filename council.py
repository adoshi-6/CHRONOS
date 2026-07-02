import ollama

from config import SMART_MODEL

# The council uses the smart model defined in config.py.
# This first version has three agents: Contrarian, Synergist, Chairman.
# Note: this version returns a plain string (the Chairman's verdict only).
# A later version fixes this to return a full dict with all agents.
LOCAL_MODEL = SMART_MODEL


def run_council_debate(user_idea: str) -> str:
    """
    Runs a 3-agent strategic debate on the user's idea.
    Returns the Chairman's final verdict as a plain string.

    Agents:
      1. The Contrarian  — identifies every flaw and risk
      2. The Synergist   — re-engineers the idea to bypass those flaws
      3. The Chairman    — synthesizes both into a final verdict

    Note: This version returned a plain string. This caused a bug when
    callers tried to access debate_packet['contrarian'] etc. Fixed in v2.
    """
    print("\n==================================================")
    print("  Council Chamber Active")
    print("==================================================")

    # Phase 1: The Contrarian
    print("\n[1/3] The Contrarian...")
    prompt_contrarian = (
        f"You are 'The Contrarian', a ruthless risk analyst. "
        f"Point out every flaw, risk, and hidden assumption in this idea. "
        f"Be brief and direct.\n\nIdea: {user_idea}"
    )
    try:
        response          = ollama.chat(model=LOCAL_MODEL,
                                        messages=[{"role": "user", "content": prompt_contrarian}])
        contrarian_verdict = response['message']['content']
        print("  done.")
    except Exception as e:
        contrarian_verdict = f"[Contrarian failed: {e}]"

    # Phase 2: The Synergist
    print("[2/3] The Synergist...")
    prompt_synergist = (
        f"You are 'The Synergist', a venture strategist. "
        f"Review this idea: '{user_idea}' and the criticisms: '{contrarian_verdict}'. "
        f"Re-engineer the idea to bypass those flaws and maximize its value. Be concise."
    )
    try:
        response          = ollama.chat(model=LOCAL_MODEL,
                                        messages=[{"role": "user", "content": prompt_synergist}])
        synergist_verdict = response['message']['content']
        print("  done.")
    except Exception as e:
        synergist_verdict = f"[Synergist failed: {e}]"

    # Phase 3: The Chairman
    print("[3/3] The Chairman...")
    prompt_chairman = (
        f"You are 'The Chairman'. Synthesize a final verdict based on the debate. "
        f"Original idea: '{user_idea}'. "
        f"Risks identified: '{contrarian_verdict}'. "
        f"Strategic optimization: '{synergist_verdict}'. "
        f"Deliver a clear, authoritative summary in 3 to 4 sentences."
    )
    try:
        response      = ollama.chat(model=LOCAL_MODEL,
                                    messages=[{"role": "user", "content": prompt_chairman}])
        final_verdict = response['message']['content']
        print("  done.")
    except Exception as e:
        final_verdict = f"[Chairman failed: {e}]"

    print("\n==================================================")
    print("  Debate complete.")
    print("==================================================\n")

    return final_verdict