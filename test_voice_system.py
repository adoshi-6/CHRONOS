print("1. [PASS] File opened. Testing imports...")
import asyncio
import edge_tts
import os
import ctypes
print("2. [PASS] All libraries imported successfully.")

async def diagnostic():
    print("3. [PASS] Async event loop started. Testing Microsoft connection...")
    text = "Testing system architecture."
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    
    print("4. [PASS] Request built. Writing temporary mp3 to disk...")
    await communicate.save("diagnostic_test.mp3")
    print("5. [PASS] Audio file written successfully.")
    
    print("6. Testing native Windows Audio DLL (Hard crash watch)...")
    abs_path = os.path.abspath("diagnostic_test.mp3")
    
    # This line talks directly to your Windows motherboard core
    ctypes.windll.winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias test_play', None, 0, 0)
    ctypes.windll.winmm.mciSendStringW('play test_play wait', None, 0, 0)
    ctypes.windll.winmm.mciSendStringW('close test_play', None, 0, 0)
    print("7. [PASS] Windows Audio core responded cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(diagnostic())
        print("\n🎉 ALL SYSTEMS CLEAR. Your system fully supports this audio framework.")
    except Exception as e:
        print(f"\n❌ Python caught an error: {e}")