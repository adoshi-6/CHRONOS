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


@app.route('/')
def serve_index():
    # Bug fix: send_from_string does not exist in Flask.
    # Replaced with a direct file read — simple and reliable.
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Could not load index.html: {e}", 500


@app.route('/api/command', methods=['POST'])
def handle_command():
    global chat_history
    data    = request.get_json() or {}
    command = data.get('command', '').strip()

    if not command:
        return jsonify({"response": "No command received."})

    if should_trigger_council(command):
        debate_packet = run_council_debate(command)
        threading.Thread(
            target=lambda: [
                speak_text("Contrarian analysis."),
                speak_text(debate_packet['contrarian']),
                speak_text("Synergist strategy."),
                speak_text(debate_packet['synergist']),
                speak_text("Chairman verdict."),
                speak_text(debate_packet['chairman']),
            ],
            daemon=True
        ).start()
        return jsonify({"response": debate_packet})

    else:
        text_lower = command.lower()
        active_model = SMART_MODEL if (
            "think deeply" in text_lower or
            "smart mode"   in text_lower or
            "analyze"      in text_lower
        ) else FAST_MODEL

        messages = [
            {"role": "system",
             "content": f"You are {ASSISTANT_NAME}, a warm, direct, brief personal assistant."}
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

            threading.Thread(target=speak_text, args=(reply,), daemon=True).start()
            return jsonify({"response": reply})

        except Exception as e:
            return jsonify({"response": f"Model error: {e}"})


if __name__ == '__main__':
    print(f"\n{ASSISTANT_NAME} server starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
