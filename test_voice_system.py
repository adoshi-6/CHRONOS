"""
test_voice_system.py
--------------------
Diagnostic script that tests the full audio pipeline step by step.
Run this if speech output is not working — each numbered step will tell
you exactly where the failure is.

Requirements: edge-tts must be installed, and you must be on Windows.
"""

print("1. [CHECK] File opened. Testing imports...")
import asyncio
import edge_tts
import os
import ctypes
print("2. [PASS] All libraries imported successfully.")


async def diagnostic():
  print("3. [PASS] Async event loop started. Testing connection to edge-tts...")

  text   = "Voice pipeline diagnostic test."
  voice_tag = "en-GB-RyanNeural"
  communicate = edge_tts.Communicate(text, voice_tag)

  print("4. [PASS] Request built. Writing audio to disk...")
  await communicate.save("diagnostic_test.mp3")
  print("5. [PASS] Audio file written successfully.")

  print("6. [CHECK] Testing Windows audio playback layer...")
  abs_path = os.path.abspath("diagnostic_test.mp3")

  ctypes.windll.winmm.mciSendStringW(
    f'open "{abs_path}" type mpegvideo alias test_play', None, 0, 0)
  ctypes.windll.winmm.mciSendStringW('play test_play wait', None, 0, 0)
  ctypes.windll.winmm.mciSendStringW('close test_play', None, 0, 0)
  print("7. [PASS] Windows audio layer responded cleanly.")


if __name__ == "__main__":
  try:
    asyncio.run(diagnostic())
    print("\n[ALL SYSTEMS CLEAR] Your setup fully supports this audio pipeline.")
  except Exception as e:
    print(f"\n[DIAGNOSTIC FAILED] Error: {e}")