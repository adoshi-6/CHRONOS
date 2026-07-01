import speech_recognition as sr
import os
import ctypes
import time
import requests
import wave
from piper.voice import PiperVoice

# ── Piper Voice Configuration ──────────────────────────────────────────────
# Change these three variables to swap voices without touching anything else.
# Run piper_mega.py to browse and audition all available options first.
#
# VOICE_NAME    — voice identity  (e.g. "ryan", "alan", "lessac", "amy")
# VOICE_QUALITY — audio quality   ("low", "medium", or "high")
# VOICE_CODE    — language region ("en_US" for American, "en_GB" for British)
# ──────────────────────────────────────────────────────────────────────────
VOICE_NAME    = "ryan"
VOICE_QUALITY = "medium"
VOICE_CODE    = "en_US"

# Derived file paths — no need to edit these
MODEL_DIR   = os.path.abspath("piper_voices")
FILE_PREFIX = f"{VOICE_CODE}-{VOICE_NAME}-{VOICE_QUALITY}"
MODEL_PATH  = os.path.join(MODEL_DIR, f"{FILE_PREFIX}.onnx")
CONFIG_PATH = os.path.join(MODEL_DIR, f"{FILE_PREFIX}.onnx.json")


def download_piper_model() -> bool:
    """
    Downloads the ONNX model and config files from HuggingFace on first run.
    Files are cached locally in piper_voices/ — only downloaded once.
    Returns True if the model is ready, False if the download failed.
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    region_folder = "en_US" if VOICE_CODE == "en_US" else "en_GB"
    base_url = (
        f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
        f"en/{region_folder}/{VOICE_NAME}/{VOICE_QUALITY}/"
    )

    if not os.path.exists(MODEL_PATH):
        print(f"\n[Downloading voice model: {FILE_PREFIX}.onnx (~15-50MB)...]")
        r = requests.get(base_url + f"{FILE_PREFIX}.onnx", stream=True)
        if r.status_code != 200:
            print(f"[Error: Voice '{VOICE_NAME}' ({VOICE_QUALITY}) not found for region '{VOICE_CODE}']")
            return False
        with open(MODEL_PATH, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    if not os.path.exists(CONFIG_PATH):
        print("[Downloading voice configuration...]")
        r = requests.get(base_url + f"{FILE_PREFIX}.onnx.json", stream=True)
        with open(CONFIG_PATH, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return True


# Load the voice engine on import — downloads files if this is the first run
_engine_ready = download_piper_model()
if _engine_ready:
    print(f"[Piper voice engine loaded: {VOICE_NAME.upper()} ({VOICE_CODE})]")
    voice_engine = PiperVoice.load(MODEL_PATH)
else:
    voice_engine = None
    print("[Warning: Piper failed to load. speak_text will not produce audio.]")


def speak_text(text, voice_mode="standard"):
    """
    Synthesizes speech completely offline using the local Piper ONNX engine.
    No internet connection needed after the first-run model download.
    """
    if not text or not text.strip() or not voice_engine:
        return

    output_file = os.path.abspath("assistant_speech.wav")

    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except Exception:
            pass

    try:
        with wave.open(output_file, 'wb') as wav_file:
            voice_engine.synthesize(text, wav_file)

        ctypes.windll.winmm.mciSendStringW(
            f'open "{output_file}" type waveaudio alias assistant_audio', None, 0, 0)
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
