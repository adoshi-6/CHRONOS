import speech_recognition as sr
import asyncio
import edge_tts
import os
import ctypes
import time

from config import VOICE_TAG

def speak_text(text, voice_mode="standard"):
    """
    Converts text to speech using a single locked voice via edge-tts.
    Dual-voice mode removed — voice is now set once in config.py.
    """
    if not text or not text.strip():
        return

    output_file    = os.path.abspath("assistant_speech.mp3")
    selected_voice = VOICE_TAG

    async def generate_speech():
        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(output_file)

    try:
        asyncio.run(generate_speech())

        ctypes.windll.winmm.mciSendStringW(
            f'open "{output_file}" type mpegvideo alias assistant_audio', None, 0, 0)
        ctypes.windll.winmm.mciSendStringW('play assistant_audio', None, 0, 0)

        status = ctypes.create_unicode_buffer(255)
        while True:
            ctypes.windll.winmm.mciSendStringW(
                'status assistant_audio mode', status, 255, 0)
            if status.value != 'playing':
                break
            time.sleep(0.1)

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
