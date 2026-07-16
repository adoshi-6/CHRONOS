import asyncio
import edge_tts

async def main():
    try:
        # Fetch the master voice list directly from Microsoft
        voices = await edge_tts.list_voices()
        
        print("\n==================================================")
        print(" 🎙️  Available English Neural Voices (Edge-TTS) ")
        print("==================================================")
        
        # Filter and print only the English voice profiles
        for v in voices:
            if v['ShortName'].startswith("en-"):
                print(f"🔹 Code: {v['ShortName']:<30} | Gender: {v['Gender']:<6}")
                
        print("==================================================\n")
        print("💡 Copy your favorite Code string (e.g., en-US-AndrewNeural)")
        print("   and paste it into audio_provider.py!")
        
    except Exception as e:
        print(f"❌ [Failed to gather voice list: {e}]")

if __name__ == "__main__":
    asyncio.run(main())