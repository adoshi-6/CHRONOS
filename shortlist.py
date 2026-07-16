import asyncio
import edge_tts
import os
import ctypes
import time

# 🛠️ NAME PRONUNCIATION TUNER:
# If a voice mispronounces your name, try changing this to "Aaryan" or "Ar-yan"
NAME_SPELLING = "Aryan"

SHORTLIST_VOICES = [
    {"name": "Liam (Canada - Smooth & Grounded)", "tag": "en-CA-LiamNeural"},
    {"name": "Ryan (UK - Deep Cinematic)", "tag": "en-GB-RyanNeural"},
    {"name": "James (Philippines - Clear & Articulate)", "tag": "en-PH-JamesNeural"},
    {"name": "Wayne (Singapore - Professional / Dynamic)", "tag": "en-SG-WayneNeural"},
    {"name": "Andrew (US - Deep Casual Friend)", "tag": "en-US-AndrewNeural"},
    {"name": "Eric (US - Sharp & Clear)", "tag": "en-US-EricNeural"}
]

def play_audio(file_path):
    abs_path = os.path.abspath(file_path)
    alias = "shortlist_voice"
    
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
    print(" 🎯  CHRONOS VOICE FINALS: THE SHORTLIST DECK         ")
    print(" Controls: [ENTER] = Play/Repeat | [N] = Next | [Q] = Quit")
    print("==================================================")
    
    idx = 0
    while idx < len(SHORTLIST_VOICES):
        speaker = SHORTLIST_VOICES[idx]
        print(f"\n▶️ Finalist [{idx+1}/{len(SHORTLIST_VOICES)}]: {speaker['name']}")
        print(f"   Identifier: {speaker['tag']}")
        
        # Build the script utilizing the phonetic pronunciation variable
        sample_text = f"Hello {NAME_SPELLING}. Testing the {speaker['name'].split('(')[0].strip()} neural engine config. How do I sound for the master build, Aryan?"
        safe_filename = f"shortlist_sample_{idx}.mp3"
        
        # Generate the file if it doesn't exist yet
        if not os.path.exists(safe_filename):
            communicate = edge_tts.Communicate(sample_text, speaker['tag'])
            await communicate.save(safe_filename)
            
        play_audio(safe_filename)
        
        # Give you the choice to repeat the exact same voice or advance
        action = input("👉 Press [ENTER] to replay | Type 'n' for next voice | Type 'q' to quit: ").strip().lower()
        
        if action == 'q':
            break
        elif action == 'n':
            idx += 1
            
    # Comprehensive post-audition file cleanup routine
    print("\n🧹 Clearing temporary final audio blocks...")
    for i in range(len(SHORTLIST_VOICES)):
        f = f"shortlist_sample_{i}.mp3"
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass
                
    print("\n==================================================")
    print(" 🎉 Shortlist review complete. Select your anchor! ")
    print("==================================================\n")

if __name__ == "__main__":
    asyncio.run(main())