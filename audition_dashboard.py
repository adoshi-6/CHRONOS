import asyncio
import edge_tts
import os
import ctypes
import time
import sys

# 🛠️ NAME PRONUNCIATION TUNER:
# If any voice says your name wrong, try changing this to "Aaryan" or "Ar-yan"
NAME_SPELLING = "Aryan"

# The master collection organized by regional data streams
VOICE_DECK = [
    ("Liam (Canada - Smooth Male)", "en-CA-LiamNeural"),
    ("Clara (Canada - Female)", "en-CA-ClaraNeural"),
    ("William (Australia - Multilingual Male)", "en-AU-WilliamMultilingualNeural"),
    ("Natasha (Australia - Female)", "en-AU-NatashaNeural"),
    ("Ryan (UK - Deep Cinematic Jarvis Male)", "en-GB-RyanNeural"),
    ("Sonia (UK - Elegant & Polished Female)", "en-GB-SoniaNeural"),
    ("Libby (UK - Female)", "en-GB-LibbyNeural"),
    ("Maisie (UK - Female)", "en-GB-MaisieNeural"),
    ("Thomas (UK - Male)", "en-GB-ThomasNeural"),
    ("Yan (Hong Kong - Female)", "en-HK-YanNeural"),
    ("Sam (Hong Kong - Male)", "en-HK-SamNeural"),
    ("Connor (Ireland - Male)", "en-IE-ConnorNeural"),
    ("Emily (Ireland - Female)", "en-IE-EmilyNeural"),
    ("Neerja (India - Expressive Female)", "en-IN-NeerjaExpressiveNeural"),
    ("Neerja (India - Standard Female)", "en-IN-NeerjaNeural"),
    ("Prabhat (India - Male)", "en-IN-PrabhatNeural"),
    ("Asilia (Kenya - Female)", "en-KE-AsiliaNeural"),
    ("Chilemba (Kenya - Male)", "en-KE-ChilembaNeural"),
    ("Abeo (Nigeria - Male)", "en-NG-AbeoNeural"),
    ("Ezinne (Nigeria - Female)", "en-NG-EzinneNeural"),
    ("Mitchell (New Zealand - Male)", "en-NZ-MitchellNeural"),
    ("Molly (New Zealand - Female)", "en-NZ-MollyNeural"),
    ("James (Philippines - Articulate Male)", "en-PH-JamesNeural"),
    ("Rosa (Philippines - Female)", "en-PH-RosaNeural"),
    ("Luna (Singapore - Female)", "en-SG-LunaNeural"),
    ("Wayne (Singapore - Dynamic & Witty Male)", "en-SG-WayneNeural"),
    ("Elimu (Tanzania - Male)", "en-TZ-ElimuNeural"),
    ("Imani (Tanzania - Female)", "en-TZ-ImaniNeural"),
    ("Leah (South Africa - Female)", "en-ZA-LeahNeural"),
    ("Luke (South Africa - Male)", "en-ZA-LukeNeural"),
    ("Ava (US - Modern Female Assistant)", "en-US-AvaNeural"),
    ("Andrew (US - Deep Casual Friend Male)", "en-US-AndrewNeural"),
    ("Emma (US - Soft & Calm Female)", "en-US-EmmaNeural"),
    ("Brian (US - Clear Corporate Male)", "en-US-BrianNeural"),
    ("Ana (US - Female)", "en-US-AnaNeural"),
    ("Andrew (US - Multilingual Male)", "en-US-AndrewMultilingualNeural"),
    ("Aria (US - Female)", "en-US-AriaNeural"),
    ("Ava (US - Multilingual Female)", "en-US-AvaMultilingualNeural"),
    ("Brian (US - Multilingual Male)", "en-US-BrianMultilingualNeural"),
    ("Christopher (US - Energetic Male)", "en-US-ChristopherNeural"),
    ("Emma (US - Multilingual Female)", "en-US-EmmaMultilingualNeural"),
    ("Eric (US - Sharp & Clear Male)", "en-US-EricNeural"),
    ("Guy (US - Male)", "en-US-GuyNeural"),
    {"name": "Jenny (US - Female)", "tag": "en-US-JennyNeural"},
    {"name": "Michelle (US - Female)", "tag": "en-US-MichelleNeural"},
    {"name": "Roger (US - Male)", "tag": "en-US-RogerNeural"},
    {"name": "Steffan (US - Male)", "tag": "en-US-SteffanNeural"}
]

# Quick structure normalizer to ensure completely safe parsing
CLEAN_DECK = []
for item in VOICE_DECK:
    if isinstance(item, tuple):
        CLEAN_DECK.append({"name": item[0], "tag": item[1]})
    else:
        CLEAN_DECK.append(item)

def play_audio(file_path):
    """Feeds the audio tracking stream straight into the native Windows kernel."""
    abs_path = os.path.abspath(file_path)
    alias = "audition_playback"
    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, 0)
    ctypes.windll.winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias {alias}', None, 0, 0)
    ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, 0)
    
    status = ctypes.create_unicode_buffer(255)
    while True:
        ctypes.windll.winmm.mciSendStringW(f'status {alias} mode', status, 255, 0)
        if status.value != 'playing':
            break
        time.sleep(0.1)
    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, 0)

async def run_hub():
    print("\n========================================================")
    print(" 🎙️  CHRONOS SOUNDBOARD: MASTER REGIONAL INTERACTIVE RUNNER")
    print(" [ENTER] = Play/Repeat | [N] = Next Voice | [Q] = Exit ")
    print("========================================================")
    
    total = len(CLEAN_DECK)
    idx = 0
    
    while idx < total:
        speaker = CLEAN_DECK[idx]
        print(f"\n[🗣️  {idx+1}/{total}] Profile: {speaker['name']}")
        print(f"      Code string: {speaker['tag']}")
        
        sample_text = f"Hello {NAME_SPELLING}. This is the {speaker['name'].split('(')[0].strip()} configuration check. How do I sound?"
        filename = f"audition_clip_{idx}.mp3"
        
        # Build file if missing
        if not os.path.exists(filename):
            try:
                communicate = edge_tts.Communicate(sample_text, speaker['tag'])
                await communicate.save(filename)
            except Exception as e:
                print(f"      ⚠️ Waveform generation failed: {e}")
                idx += 1
                continue
        
        # Fire verified native playback
        play_audio(filename)
        
        action = input("👉 Press [ENTER] to replay | Type 'n' for next | Type 'q' to stop: ").strip().lower()
        
        if action == 'q':
            print("\nHub processing suspended.")
            break
        elif action == 'n':
            idx += 1
            
    # Post-session sweep
    print("\n🧹 Cleaning system workspace files...")
    for i in range(total):
        f = f"audition_clip_{i}.mp3"
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass
    print("✨ Cleanup complete.")

if __name__ == "__main__":
    try:
        asyncio.run(run_hub())
    except Exception as e:
        print(f"❌ Structural exception caught: {e}")