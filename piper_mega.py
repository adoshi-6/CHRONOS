import asyncio
import os
import ctypes
import time
import requests
import wave
import sys
from piper.voice import PiperVoice

# A massive curated collection of top-tier local Piper voices across the repository
PIPER_GLOBAL_VOICES = [
    # --- AMERICAN VOICES ---
    {"name": "Ryan (US - Balanced Conversational Male)", "voice": "ryan", "code": "en_US", "quality": "medium"},
    {"name": "Ryan (US - High Definition Core Male)", "voice": "ryan", "code": "en_US", "quality": "high"},
    {"name": "Lessac (US - Clear & Articulate Male)", "voice": "lessac", "code": "en_US", "quality": "medium"},
    {"name": "Lessac (US - High Definition Academic Male)", "voice": "lessac", "code": "en_US", "quality": "high"},
    {"name": "Amy (US - Natural Fluid Female)", "voice": "amy", "code": "en_US", "quality": "medium"},
    {"name": "Joe (US - Smooth Friendly Male)", "voice": "joe", "code": "en_US", "quality": "medium"},
    {"name": "Kristin (US - Crisp Assistant Female)", "voice": "kristin", "code": "en_US", "quality": "medium"},
    {"name": "Linda (US - Clear Narrative Female)", "voice": "linda", "code": "en_US", "quality": "medium"},
    
    # --- BRITISH VOICES ---
    {"name": "Alan (UK - Sophisticated Gentleman)", "voice": "alan", "code": "en_GB", "quality": "medium"},
    {"name": "Alba (UK - Clear Modern Female)", "voice": "alba", "code": "en_GB", "quality": "medium"},
    {"name": "Jenny (UK - Warm Conversational Female)", "voice": "jenny", "code": "en_GB", "quality": "medium"},
    {"name": "Northern English Male (UK - Regional Dialect)", "voice": "northern_english_male", "code": "en_GB", "quality": "medium"},
    {"name": "VCTK (UK - Corporate Delivery Profile)", "voice": "vctk", "code": "en_GB", "quality": "medium"}
]

MODEL_DIR = os.path.abspath("piper_voices")

def play_audio(file_path):
    """Plays the local WAV file using native Windows audio architecture cleanly."""
    abs_path = os.path.abspath(file_path)
    alias = "piper_mega_voice"
    
    ctypes.windll.winmm.mciSendStringW(f'open "{abs_path}" type waveaudio alias {alias}', None, 0, 0)
    ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, 0)
    
    status = ctypes.create_unicode_buffer(255)
    while True:
        ctypes.windll.winmm.mciSendStringW(f'status {alias} mode', status, 255, 0)
        if status.value != 'playing':
            break
        time.sleep(0.1)
        
    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, 0)

def fetch_model(prefix, code, voice, quality):
    """Dynamically pulls down the ONNX files on-demand if not already cached."""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    model_path = os.path.join(MODEL_DIR, f"{prefix}.onnx")
    config_path = os.path.join(MODEL_DIR, f"{prefix}.onnx.json")
    
    base_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/{code}/{voice}/{quality}/"
    
    if not os.path.exists(model_path):
        print(f"   ⏳ Downloading ONNX neural model (~15-60MB)...")
        r = requests.get(base_url + f"{prefix}.onnx", stream=True)
        if r.status_code != 200:
            print("   ❌ System Error: This specific combination isn't available in the remote pool.")
            return None, None
        with open(model_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
    if not os.path.exists(config_path):
        print(f"   ⏳ Downloading configuration blueprint...")
        r = requests.get(base_url + f"{prefix}.onnx.json", stream=True)
        with open(config_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
    return model_path, config_path

def main():
    print("==================================================")
    print(" 🧠  PIPER LOCAL NEURAL MEGA AUDITION PLATFORM   ")
    print(" Controls: [ENTER] = Download & Play | [S] = Skip | [Q] = Quit")
    print("==================================================")
    
    total = len(PIPER_GLOBAL_VOICES)
    output_file = os.path.abspath("mega_piper_test.wav")
    
    for idx, speaker in enumerate(PIPER_GLOBAL_VOICES, start=1):
        file_prefix = f"{speaker['code']}-{speaker['voice']}-{speaker['quality']}"
        print(f"\n[🔊 {idx}/{total}] Up Next: {speaker['name']}")
        print(f"   Model Target: {file_prefix}")
        
        user_choice = input("👉 Press Enter to test (or 's' to skip, 'q' to quit): ").strip().lower()
        
        if user_choice == 'q':
            print("\nAudition matrix closing down.")
            break
        elif user_choice == 's':
            print("Skipped.")
            continue
            
        # Download files on-demand
        m_path, _ = fetch_model(file_prefix, speaker['code'], speaker['voice'], speaker['quality'])
        
        if not m_path:
            continue
            
        try:
            print("   🧠 Compiling local speech synthesis...")
            voice_engine = PiperVoice.load(m_path)
            
            sample_text = f"Hello Aryan. This is the local offline {speaker['name'].split('(')[0].strip()} voice engine running on Piper. How do I sound?"
            
            # Write out the temporary audio wave
            with wave.open(output_file, 'wb') as wav_file:
                voice_engine.synthesize(sample_text, wav_file)
                
            print("   ▶️ Playing offline wave structure...")
            play_audio(output_file)
            
        except Exception as e:
            print(f"   ❌ Synthesis Failure: {e}")
            
    # Clean up the singular temporary test sentence playback file
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except:
            pass
            
    print("\n==================================================")
    print(" 🎉 Offline Auditions Complete! Pick your engine. ")
    print("==================================================\n")

if __name__ == "__main__":
    main()