import asyncio
import edge_tts
import os
import ctypes
import time
import sys

# The massive master directory of all your requested voices organized by region
GLOBAL_VOICES = [
    # --- AUSTRALIA ---
    {"name": "William (Australia - Multilingual)", "tag": "en-AU-WilliamMultilingualNeural"},
    {"name": "Natasha (Australia)", "tag": "en-AU-NatashaNeural"},
    
    # --- CANADA ---
    {"name": "Clara (Canada)", "tag": "en-CA-ClaraNeural"},
    {"name": "Liam (Canada)", "tag": "en-CA-LiamNeural"},
    
    # --- UNITED KINGDOM ---
    {"name": "Libby (UK)", "tag": "en-GB-LibbyNeural"},
    {"name": "Maisie (UK)", "tag": "en-GB-MaisieNeural"},
    {"name": "Ryan (UK - Cinematic)", "tag": "en-GB-RyanNeural"},
    {"name": "Sonia (UK - Elegant)", "tag": "en-GB-SoniaNeural"},
    {"name": "Thomas (UK)", "tag": "en-GB-ThomasNeural"},
    
    # --- HONG KONG ---
    {"name": "Yan (Hong Kong)", "tag": "en-HK-YanNeural"},
    {"name": "Sam (Hong Kong)", "tag": "en-HK-SamNeural"},
    
    # --- IRELAND ---
    {"name": "Connor (Ireland)", "tag": "en-IE-ConnorNeural"},
    {"name": "Emily (Ireland)", "tag": "en-IE-EmilyNeural"},
    
    # --- INDIA ---
    {"name": "Neerja (India - Expressive)", "tag": "en-IN-NeerjaExpressiveNeural"},
    {"name": "Neerja (India)", "tag": "en-IN-NeerjaNeural"},
    {"name": "Prabhat (India)", "tag": "en-IN-PrabhatNeural"},
    
    # --- KENYA ---
    {"name": "Asilia (Kenya)", "tag": "en-KE-AsiliaNeural"},
    {"name": "Chilemba (Kenya)", "tag": "en-KE-ChilembaNeural"},
    
    # --- NIGERIA ---
    {"name": "Abeo (Nigeria)", "tag": "en-NG-AbeoNeural"},
    {"name": "Ezinne (Nigeria)", "tag": "en-NG-EzinneNeural"},
    
    # --- NEW ZEALAND ---
    {"name": "Mitchell (New Zealand)", "tag": "en-NZ-MitchellNeural"},
    {"name": "Molly (New Zealand)", "tag": "en-NZ-MollyNeural"},
    
    # --- PHILIPPINES ---
    {"name": "James (Philippines)", "tag": "en-PH-JamesNeural"},
    {"name": "Rosa (Philippines)", "tag": "en-PH-RosaNeural"},
    
    # --- SINGAPORE ---
    {"name": "Luna (Singapore)", "tag": "en-SG-LunaNeural"},
    {"name": "Wayne (Singapore)", "tag": "en-SG-WayneNeural"},
    
    # --- TANZANIA ---
    {"name": "Elimu (Tanzania)", "tag": "en-TZ-ElimuNeural"},
    {"name": "Imani (Tanzania)", "tag": "en-TZ-ImaniNeural"},
    
    # --- SOUTH AFRICA ---
    {"name": "Leah (South Africa)", "tag": "en-ZA-LeahNeural"},
    {"name": "Luke (South Africa)", "tag": "en-ZA-LukeNeural"},
    
    # --- UNITED STATES ---
    {"name": "Ava (US)", "tag": "en-US-AvaNeural"},
    {"name": "Andrew (US - Deep Casual)", "tag": "en-US-AndrewNeural"},
    {"name": "Emma (US)", "tag": "en-US-EmmaNeural"},
    {"name": "Brian (US - Corporate)", "tag": "en-US-BrianNeural"},
    {"name": "Ana (US)", "tag": "en-US-AnaNeural"},
    {"name": "Andrew (US - Multilingual)", "tag": "en-US-AndrewMultilingualNeural"},
    {"name": "Aria (US)", "tag": "en-US-AriaNeural"},
    {"name": "Ava (US - Multilingual)", "tag": "en-US-AvaMultilingualNeural"},
    {"name": "Brian (US - Multilingual)", "tag": "en-US-BrianMultilingualNeural"},
    {"name": "Christopher (US - Energetic)", "tag": "en-US-ChristopherNeural"},
    {"name": "Emma (US - Multilingual)", "tag": "en-US-EmmaMultilingualNeural"},
    {"name": "Eric (US)", "tag": "en-US-EricNeural"},
    {"name": "Guy (US)", "tag": "en-US-GuyNeural"},
    {"name": "Jenny (US)", "tag": "en-US-JennyNeural"},
    {"name": "Michelle (US)", "tag": "en-US-MichelleNeural"},
    {"name": "Roger (US)", "tag": "en-US-RogerNeural"},
    {"name": "Steffan (US)", "tag": "en-US-SteffanNeural"}
]

def play_audio(file_path):
    """Executes clean native playback and blocks the loop until speaking finishes."""
    abs_path = os.path.abspath(file_path)
    alias = "mega_voice"
    
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
    print("==================================================")
    print("  🌐 CHRONOS MASTER GLOBAL AUDITION LAYER CHASSIS     ")
    print("  Controls: [ENTER] = Play | [S] = Skip | [Q] = Quit")
    print("==================================================")
    
    total = len(GLOBAL_VOICES)
    
    for idx, speaker in enumerate(GLOBAL_VOICES, start=1):
        print(f"\n[🔊 {idx}/{total}] Next up: {speaker['name']}")
        print(f"   Code Identifier: {speaker['tag']}")
        
        choice = input("👉 Press Enter to play (or 's' to skip, 'q' to quit): ").strip().lower()
        
        if choice == 'q':
            print("\nExiting auditions. Gateway closing.")
            break
        elif choice == 's':
            print("Skipped.")
            continue
            
        # Unique safe filenames to avoid internal Windows cache memory traps
        safe_filename = f"mega_sample_{idx}.mp3"
        sample_text = f"Hello Aryan. I am the {speaker['name']} neural voice framework. How does my accent sound for the baseline core build?"
        
        try:
            print("⏳ Generating neural waveform...")
            communicate = edge_tts.Communicate(sample_text, speaker['tag'])
            await communicate.save(safe_filename)
            
            print("▶️ Playing...")
            play_audio(safe_filename)
            
            # Clean up immediately after playback completes
            if os.path.exists(safe_filename):
                os.remove(safe_filename)
                
        except Exception as e:
            print(f"❌ Playback interruption error: {e}")
            
    print("\n==================================================")
    print(" 🎉 Global Auditions Complete! Pipeline Locked. ")
    print("==================================================\n")

if __name__ == "__main__":
    asyncio.run(main())