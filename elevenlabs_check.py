import os
import requests

# Reads the ElevenLabs API key from your system environment variables.
# To set it on Windows: search "environment variables" in the Start menu,
# add a new variable named ELEVENLABS_API_KEY with your key as the value.

api_key = os.environ.get("ELEVENLABS_API_KEY")

if not api_key:
    print("[Error: ELEVENLABS_API_KEY is not set in your environment variables]")
else:
    headers = {"xi-api-key": api_key}
    try:
        url = "https://api.elevenlabs.io/v1/user/subscription"
        response = requests.get(url, headers=headers).json()

        used      = response.get("character_count", 0)
        limit     = response.get("character_limit", 0)
        remaining = limit - used

        print("\n========================================")
        print(f"  ElevenLabs Balance: {remaining:,} / {limit:,} credits remaining")
        print("========================================\n")

    except Exception as e:
        print(f"[Failed to fetch ElevenLabs balance: {e}]")