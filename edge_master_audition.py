print("🚀 [System Diagnostic: Python has successfully opened the file!]")
import asyncio
import edge_tts
import os
import ctypes
import time

# 🛠️ NAME PRONUNCIATION TUNER:
# If any voice says your name wrong, try changing this to "Aaryan" or "Ar-yan"
NAME_SPELLING = "Aryan"

# The master deck of all 47 voices you requested, grouped by region
ALL_REQUESTED_VOICES = [
    # Australia
    {"name": "William (Australia - Multilingual)", "tag": "en-AU-WilliamMultilingualNeural"},
    {"name": "Natasha (Australia)", "tag": "en-AU-NatashaNeural"},
    # Canada
    {"name": "Clara (Canada)", "tag": "en-CA-ClaraNeural"},
    {"name": "Liam (Canada)", "tag": "en-CA-LiamNeural"},
    # Hong Kong
    {"name": "Yan (Hong Kong)", "tag": "en-HK-YanNeural"},
    {"name": "Sam (Hong Kong)", "tag": "en-HK-SamNeural"},
    # India
    {"name": "Neerja (India - Expressive)", "tag": "en-IN-NeerjaExpressiveNeural"},
    {"name": "Neerja (India)", "tag": "en-IN-NeerjaNeural"},
    {"name": "Prabhat (India)", "tag": "en-IN-PrabhatNeural"},
    # Ireland
    {"name": "Connor (Ireland)", "tag": "en-IE-ConnorNeural"},
    {"name": "Emily (Ireland)", "tag": "en-IE-EmilyNeural"},
    # Kenya
    {"name": "Asilia (Kenya)", "tag": "en-KE-AsiliaNeural"},
    {"name": "Chilemba (Kenya)", "tag": "en-KE-ChilembaNeural"},
    # New Zealand
    {"name": "Mitchell (New Zealand)", "tag": "en-NZ-MitchellNeural"},
    {"name": "Molly (New Zealand)", "tag": "en-NZ-MollyNeural"},
    # Nigeria
    {"name": "Abeo (Nigeria)", "tag": "en-NG-AbeoNeural"},
    {"name": "Ezinne (Nigeria)", "tag": "en-NG-EzinneNeural"},
    # Philippines
    {"name": "James (Philippines)", "tag": "en-PH-JamesNeural"},
    {"name": "Rosa (Philippines)", "tag": "en-PH-RosaNeural"},
    # Singapore
    {"name": "Luna (Singapore)", "tag": "en-SG-LunaNeural"},
    {"name": "Wayne (Singapore)", "tag": "en-SG-WayneNeural"},
    # South Africa
    {"name": "Leah (South Africa)", "tag": "en-ZA-LeahNeural"},
    {"name": "Luke (South Africa)", "tag": "en-ZA-LukeNeural"},
    # Tanzania
    {"name": "Elimu (Tanzania)", "tag": "en-TZ-ElimuNeural"},
    {"name": "Imani (Tanzania)", "tag": "en-TZ-ImaniNeural"},
    # United Kingdom
    {"name": "Libby (UK)", "tag": "en-GB-LibbyNeural"},
    {"name": "Maisie (UK)", "tag": "en-GB-MaisieNeural"},
    {"name": "Ryan (UK)", "tag": "en-GB-RyanNeural"},
    {"name": "Sonia (UK)", "tag": "en-GB-SoniaNeural"},
    {"name": "Thomas (UK)", "tag": "en-GB-ThomasNeural"},
    # United States
    {"name": "Ava (US)", "tag": "en-US-AvaNeural"},
    {"name": "Andrew (US)", "tag": "en-US-AndrewNeural"},
    {"name": "Emma (US)", "tag": "en-US-EmmaNeural"},
    {"name": "Brian (US)", "tag": "en-US-BrianNeural"},
    {"name": "Ana (US)", "tag": "en-US-AnaNeural"},
    {"name": "Andrew (US - Multilingual)", "tag": "en-US-AndrewMultilingualNeural"},
    {"name": "Aria (US)", "tag": "en-US-AriaNeural"},
    {"name": "Ava (US - Multilingual)", "tag": "en-US-AvaMultilingualNeural"},
    {"name": "Brian (US - Multilingual)", "tag": "en-US-BrianMultilingualNeural"},
    {"name": "Christopher (US)", "tag": "en-US-ChristopherNeural"},
    {"name": "Emma (US - Multilingual)", "tag": "en-US-EmmaMultilingualNeural"},
    {"name": "Eric (US)", "tag": "en-US-EricNeural"},
    {"name": "Guy (US)", "tag": "en-US-GuyNeural"},
    {"name": "Jenny (US)", "tag": "en-US-JennyNeural"},
    {"name": "Michelle (US)", "tag": "en-US-MichelleNeural"},
    {"name": "Roger (US)", "tag": "en-US-RogerNeural"},
    {"name": "Steffan (US)", "tag": "en-US-SteffanNeural"}
]

def play_audio(file_path):
    """Plays the audio file cleanly and holds system execution until speaking ends."""
    abs_path = os.path.abspath(file_path)
    alias = "master_audition"
    
    ctypes.windll.winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias {alias}', None, 0, 0)
    ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, 0)
    
    status = ctypes.create_unicode_buffer(255)
    while True:
        ctypes.windll.winmm.mciSendStringW(f'status {alias} mode', status, 255, 0)
        if status.value != 'playing':
            break
        time.sleep(0.1)
        
    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, 0)

async def main():
    print("==========================================================")
    print(" 🎙️  CHRONOS MASTER DECK: 47-VOICE GLOBAL INTERACTIVE AUDITION ")
    print(" Controls: [ENTER] = Play/Repeat | [N] = Next | [Q] = Quit")
    print("==========================================================")
    
    total = len(ALL_REQUESTED_VOICES)
    idx = 0
    
    while idx < total:
        speaker = ALL_REQUESTED_VOICES[idx]
        print(f"\n[🗣️ {idx+1}/{total}] Now Reviewing: {speaker['name']}")
        print(f"     Identifier Code: {speaker['tag']}")
        
        sample_text = f"Hello {NAME_SPELLING}. This is the {speaker['name'].split('(')[0].strip()} voice setup. How do I sound for the build?"
        
        # Uses unique filenames dynamically to avoid background cache locks
        safe_filename = f"master_audition_sample_{idx}.mp3"
        
        if not os.path.exists(safe_filename):
            try:
                communicate = edge_tts.Communicate(sample_text, speaker['tag'])
                await communicate.save(safe_filename)
            except Exception as e:
                print(f" ❌ Generation error for {speaker['name']}: {e}")
                idx += 1
                continue
                
        # Play target sound track
        play_audio(safe_filename)