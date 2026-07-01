import speech_recognition as sr
import asyncio
import edge_tts
import os
import ctypes
import time
import threading

from config import VOICE_TAG

# Global speaking lock — prevents two TTS calls from overlapping.
# speak_text blocks until audio finishes, so the caller always knows
# when the assistant has stopped speaking before doing anything else.
_speak_lock = threading.Lock()


def speak_text(text, voice_mode="standard"):
    """
    Converts text to speech using edge-tts and plays via Windows native audio.
    Blocks until playback is fully complete.

    Switched back from Piper (offline) to edge-tts (cloud) for better voice
    quality and lower setup complexity. Voice is set in config.py under VOICE_TAG.
    """
    if not text or not text.strip():
        return

    output_file    = os.path.abspath("assistant_speech.mp3")
    selected_voice = VOICE_TAG

    async def generate_speech():
        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(output_file)

    with _speak_lock:
        try:
            asyncio.run(generate_speech())

            ctypes.windll.winmm.mciSendStringW(
                f'open "{output_file}" type mpegvideo alias assistant_audio', None, 0, 0)
            # "play wait" blocks until playback finishes — no polling loop needed
            ctypes.windll.winmm.mciSendStringW('play assistant_audio wait', None, 0, 0)
            ctypes.windll.winmm.mciSendStringW('close assistant_audio', None, 0, 0)

        except Exception as e:
            print(f"[Audio error: {e}]")


def listen_to_user():
    """
    Captures microphone audio and returns it as transcribed text.
    Uses a 3.5-second pause threshold so the speaker is never cut off.
    """
    recognizer = sr.Recognizer()
    recognizer.pause_threshold          = 3.5
    recognizer.dynamic_energy_threshold = False

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        recognizer.energy_threshold = 300

        print("\n[Listening... Speak now]")
        try:
            audio_data = recognizer.listen(source, timeout=7, phrase_time_limit=None)
            print("Processing...")
            text = recognizer.recognize_google(audio_data)
            print(f'You said: "{text}"')
            return text
        except sr.UnknownValueError:
            print("[Could not understand audio]")
            return None
        except sr.RequestError as e:
            print(f"[Speech recognition error: {e}]")
            return None
        except Exception:
            print("[Listening timed out]")
            return None
