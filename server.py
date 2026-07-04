from flask import Flask, request, jsonify
import os
import threading
import time
import ollama

from audio_provider import speak_text
from council import run_council_debate
from config import ASSISTANT_NAME, USER_NAME, FAST_MODEL, SMART_MODEL, COUNCIL_TRIGGERS

app = Flask(__name__)

chat_history = []


def should_trigger_council(text: str) -> bool:
    text_lower = text.lower()
    negations  = ["don't", "dont", "do not", "never", "without", "skip", "stop"]
    if not any(kw in text_lower for kw in COUNCIL_TRIGGERS):
        return False
    for neg in negations:
        if neg in text_lower:
            for kw in COUNCIL_TRIGGERS:
                if kw in text_lower and text_lower.find(neg) < text_lower.find(kw):
                    return False
    return True


def execute_audio_playback(text_to_speak: str):
    """
    Runs TTS in a background thread.
    Initialises Windows COM on the thread if needed.
    """
    try:
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except ImportError:
            pass
        speak_text(text_to_speak)
    except Exception as e:
        print(f"[Audio error: {e}]")


@app.route('/')
def serve_index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Could not load index.html: {e}", 500


@app.route('/api/command', methods=['POST'])
def handle_command():
    """
    Main routing endpoint.
    Added 'source' field tracking — voice responses trigger TTS,
    text responses are silent. Council narration also respects source.
    """
    global chat_history
    data    = request.get_json() or {}
    command = data.get('command', '').strip()
    source  = data.get('source', 'text')   # 'voice' or 'text'

    if not command:
        return jsonify({"response": "No command received."})

    print(f"\n[{source.upper()}]: \"{command}\"")

    if should_trigger_council(command):
        debate_packet = run_council_debate(command)

        # Only narrate council over voice — text source stays silent
        if source == 'voice':
            def narrate():
                execute_audio_playback("Contrarian analysis.")
                execute_audio_playback(debate_packet['contrarian'])
                time.sleep(0.3)
                execute_audio_playback("Synergist strategy.")
                execute_audio_playback(debate_packet['synergist'])
                time.sleep(0.3)
                execute_audio_playback("Chairman verdict.")
                execute_audio_playback(debate_packet['chairman'])
            threading.Thread(target=narrate, daemon=True).start()

        return jsonify({"response": debate_packet})

    else:
        text_lower   = command.lower()
        active_model = SMART_MODEL if (
            "think deeply" in text_lower or
            "smart mode"   in text_lower or
            "analyze"      in text_lower
        ) else FAST_MODEL

        print(f"[Model: {active_model}]")

        messages = [
            {"role": "system", "content": (
                f"You are {ASSISTANT_NAME}, a warm, direct, brief personal assistant. "
                f"Keep responses to 1 or 2 sentences. No filler."
            )}
        ]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": command})

        try:
            response = ollama.chat(model=active_model, messages=messages)
            reply    = response['message']['content']

            chat_history.append({"role": "user",      "content": command})
            chat_history.append({"role": "assistant",  "content": reply})
            if len(chat_history) > 20:
                chat_history = chat_history[-20:]

            if source == 'voice':
                threading.Thread(
                    target=execute_audio_playback, args=(reply,), daemon=True
                ).start()

            return jsonify({"response": reply})

        except Exception as e:
            return jsonify({"response": f"Model error: {e}"})


if __name__ == '__main__':
    print(f"\n{ASSISTANT_NAME} server running at http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
