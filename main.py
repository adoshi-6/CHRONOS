import sys
import json
import re
import os
from model_provider import generate_response
from tools import execute_tool, get_current_time, get_calendar_events
from audio_provider import listen_to_user, speak_text
from council import run_council_debate
from config import ASSISTANT_NAME, USER_NAME, HISTORY_FILE, COUNCIL_TRIGGERS

# Load the system prompt from AGENT.md if it exists.
# This file defines the assistant's personality and behaviour.
try:
    with open("AGENT.md", "r", encoding="utf-8") as file:
        system_prompt = file.read()
except FileNotFoundError:
    system_prompt = (
        f"You are {ASSISTANT_NAME}, a warm, plain-spoken, and brief personal assistant."
    )

conversation_history = []


def load_conversation_history():
    """Loads past conversations from the local history file if it exists."""
    global conversation_history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                conversation_history = json.load(file)
            print("[Loaded conversation history from disk]")
        except Exception as e:
            print(f"[Warning: Failed to load history: {e}]")
            conversation_history = []
    else:
        conversation_history = []


def save_conversation_history():
    """Saves the current conversation to disk."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(conversation_history, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[Warning: Failed to save history: {e}]")


def parse_text_for_json_tool(text):
    """Tries to extract a tool call from plain text if the model didn't use native tool calling."""
    cleaned = text.strip()
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if "name" in data:
                return data.get("name"), data.get("arguments", {})
        except json.JSONDecodeError:
            pass
    return None, None


def run_agent_turn():
    """
    Sends the current conversation to the model and processes the response.
    Handles both streaming text replies and tool calls.
    """
    global conversation_history

    response_stream = generate_response(conversation_history, system_prompt)
    if not response_stream:
        print(f"{ASSISTANT_NAME}: [Local connection failed. Is Ollama running?]\n")
        return

    full_reply = ""
    tool_calls_accumulated = {}
    is_streaming_text = False

    for chunk in response_stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta

        if delta.tool_calls:
            for tool_call in delta.tool_calls:
                idx = tool_call.index
                if idx not in tool_calls_accumulated:
                    tool_calls_accumulated[idx] = {
                        "id": tool_call.id, "name": "", "arguments": ""
                    }
                if tool_call.function:
                    if tool_call.function.name:
                        tool_calls_accumulated[idx]["name"] = tool_call.function.name
                    if tool_call.function.arguments:
                        tool_calls_accumulated[idx]["arguments"] += tool_call.function.arguments

        elif delta.content:
            if not is_streaming_text and not delta.content.strip().startswith("{"):
                print(f"{ASSISTANT_NAME}: ", end="", flush=True)
                is_streaming_text = True

            if is_streaming_text:
                sys.stdout.write(delta.content)
                sys.stdout.flush()

            full_reply += delta.content

    if is_streaming_text:
        print("\n")
        # Only speak the reply if it is not a raw JSON tool block
        clean_check = full_reply.strip()
        if not clean_check.startswith("{") and '"name":' not in clean_check:
            speak_text(full_reply)

    tool_name, tool_args = None, {}
    tool_id = "text_fallback_id"

    if tool_calls_accumulated:
        first_tc = list(tool_calls_accumulated.values())[0]
        tool_name = first_tc["name"]
        tool_args = first_tc["arguments"]
        tool_id = first_tc["id"]
    else:
        tool_name, tool_args = parse_text_for_json_tool(full_reply)

    if tool_name:
        if isinstance(tool_args, dict):
            tool_args = json.dumps(tool_args)

        print(f"[Tool called: '{tool_name}']")
        conversation_history.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": tool_id,
                "type": "function",
                "function": {"name": tool_name, "arguments": tool_args}
            }]
        })

        tool_result = execute_tool(tool_name, tool_args)
        print(f"[Tool result: {tool_result}]")

        conversation_history.append({
            "role": "tool",
            "tool_call_id": tool_id,
            "name": tool_name,
            "content": tool_result
        })

        save_conversation_history()
        run_agent_turn()
    else:
        if full_reply and is_streaming_text:
            conversation_history.append({"role": "assistant", "content": full_reply})
            save_conversation_history()


def run_autonomous_wakeup():
    """Runs on first boot. Gives the assistant current time and calendar context for its greeting."""
    global conversation_history
    print("[Initializing autonomous wake-up sequence...]")

    current_time_data = get_current_time()
    calendar_data    = get_calendar_events()

    wakeup_prompt = (
        f"SYSTEM NOTIFICATION (BOOT COMPLETE): The user has initialized your interface. "
        f"Context: {current_time_data} Schedule: {calendar_data}. "
        f"Provide a brief, warm greeting addressing the user as {USER_NAME} "
        f"and let them know you are online and ready."
    )

    conversation_history.append({"role": "user", "content": wakeup_prompt})
    run_agent_turn()


def main():
    global conversation_history

    print("=" * 52)
    print(f" {ASSISTANT_NAME} — Voice Agent")
    print(f" Press [ENTER] to speak.")
    print(f" Say 'council', 'debate', or 'evaluate' to run the council.")
    print(f" Type 'clear' to wipe conversation history.")
    print(f" Type 'exit' to quit.")
    print("=" * 52 + "\n")

    load_conversation_history()

    if not conversation_history:
        run_autonomous_wakeup()
    else:
        msg = f"Welcome back, {USER_NAME}. Ready when you are."
        print(f"\n{ASSISTANT_NAME}: [{msg}]")
        speak_text(msg)

    while True:
        try:
            mode = input("[Press Enter to Talk / Type your command]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if mode.lower() in ["exit", "quit"]:
            print("Goodbye.")
            break

        if mode.lower() == "clear":
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            conversation_history = []
            print("[Memory cleared. Restart for a clean session.]")
            continue

        if not mode:
            user_input = listen_to_user()
            if not user_input:
                continue
        else:
            user_input = mode

        # Route to council if trigger keywords are detected
        if any(kw in user_input.lower() for kw in COUNCIL_TRIGGERS):
            print("\n[Intent Gateway: Council triggered. Assembling agents...]")

            clean_idea = user_input
            for kw in COUNCIL_TRIGGERS:
                clean_idea = re.sub(rf'\b{kw}\b', '', clean_idea, flags=re.IGNORECASE)
            clean_idea = " ".join(clean_idea.split()).strip()

            verdict = run_council_debate(clean_idea)

            print(f"\n{ASSISTANT_NAME} (Chairman Verdict):\n{verdict}\n")

            conversation_history.append({"role": "user",      "content": user_input})
            conversation_history.append({"role": "assistant", "content": verdict})
            save_conversation_history()

            speak_text(verdict)

        else:
            conversation_history.append({"role": "user", "content": user_input})
            save_conversation_history()
            run_agent_turn()


if __name__ == "__main__":
    main()