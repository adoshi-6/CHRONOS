import asyncio
import edge_tts
import os
import ctypes
import time

# The curated lineup of premium neural profiles
TEST_VOICES = {
    "Brian (US - Corporate & Crisp)": "en-US-BrianNeural",
    "Andrew (US - Deep & Casual Friend)": "en-US-AndrewNeural",
    "Christopher (US - Young & Articulate)": "en-US-ChristopherNeural",
    "Ava (US - Modern Intelligent Female)": "en-US-AvaNeural",
    "Emma (US - Soft & Calm Female)": "en-US-EmmaNeural",
    "Ryan (UK - Cinematic Deep British)": "en-GB-RyanNeural",
    "Sonia (UK - Elegant & Polished British)": "en-GB-SoniaNeural"
}

def play_audio(file_path):
    """Plays the audio file using native Windows audio architecture cleanly."""
    abs_path = os.path.abspath(file_path)
    alias = os.path.basename(file_path).split('.')[0]
    
    ctypes.windll.winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias {alias}', None, 0, 0)
    ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, 0)
    
    status = ctypes.create_unicode_buffer(255)
    while True:
        ctypes.windll.winmm.mciSendStringW(f'status {alias} mode', status, 255, 0)
        if status.value != 'playing':
            break
        time.sleep(0.1)
        
    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, 0)

async def run_audition():
    print("\n==================================================")
    print(" 🎙️  CHRONOS Core Voice Auditions: Unique Scope Active ")
    print("==================================================\n")
    
    generated_files = []
    
    for nickname, voice_tag in TEST_VOICES.items():
        name_key = nickname.split('(')[0].strip().lower()
        unique_file = f"voice_sample_{name_key}.mp3"
        generated_files.append(unique_file)
        
        print(f"▶️ Generating and playing: {nickname}...")
        sample_text = f"Hello Aryan. This is the {nickname.split('(')[0].strip()} neural voice profile. How do I sound as the voice of CHRONOS?"
        
        try:
            # Save to its own dedicated unique file to prevent collisions
            communicate = edge_tts.Communicate(sample_text, voice_tag)
            await communicate.save(unique_file)
            
            # Fire the playback
            play_audio(unique_file)
            time.sleep(0.8) # Cushion room between clips
            
        except Exception as e:
            print(f"❌ Failed to process {nickname}: {e}")
            
    # Clean up all created files once the whole lineup is finished playing
    print("\n🧹 Cleaning up test audio configurations...")
    for f in generated_files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass
                
    print("\n==================================================")
    print(" 🎉 Auditions Complete! Choose your favorite.     ")
    print("==================================================\n")

if __name__ == "__main__":
    asyncio.run(run_audition())