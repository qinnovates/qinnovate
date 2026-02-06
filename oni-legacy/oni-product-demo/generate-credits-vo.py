#!/usr/bin/env python3
"""
ONI Demo Video - Credits Scene Voiceover Generator
Generates vo-credits.mp3 with the updated text including "only"
"""

import subprocess
import json
import sys
import os
import urllib.request
import urllib.error

SERVICE_NAME = "elevenlabs-api"
ACCOUNT_NAME = "oni-demo"
VOICE_NAME = "Jay Wayne"  # Wise University Professor
VOICE_ID = "8Ln42OXYupYsag45MAUy"
OUTPUT_PATH = "public/audio/vo-credits.mp3"

# Updated credits text - includes "only"
CREDITS_TEXT = """Your mind. Your privacy. Our future. ONI. The bridge between worlds. Because only life's most important connections deserve the most thought."""


def get_api_key():
    """Retrieve API key from macOS Keychain"""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", SERVICE_NAME, "-a", ACCOUNT_NAME, "-w"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def generate_voiceover(api_key):
    """Generate voiceover using ElevenLabs API"""
    print("\nGenerating credits voiceover with ElevenLabs...")
    print(f"  Voice: {VOICE_NAME}")
    print(f"  Output: {OUTPUT_PATH}")
    print(f"\nScript: {CREDITS_TEXT}")
    print("\nGenerating...\n")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    payload = json.dumps({
        "text": CREDITS_TEXT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        data=payload,
        headers={
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            with open(OUTPUT_PATH, "wb") as f:
                f.write(response.read())

        # Check file size
        size = os.path.getsize(OUTPUT_PATH)
        if size > 1000:
            size_kb = size / 1024
            print(f"Success! Credits voiceover saved to {OUTPUT_PATH} ({size_kb:.1f} KB)")

            # Get duration using ffprobe
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", OUTPUT_PATH],
                    capture_output=True, text=True
                )
                duration = float(result.stdout.strip())
                print(f"Duration: {duration:.2f}s ({int(duration * 30)} frames at 30fps)")
            except:
                pass

            # Play audio preview
            print("\nPlaying audio preview...")
            subprocess.Popen(["afplay", OUTPUT_PATH])
            return True
        else:
            print("Error: Generated file is too small. Check API response.")
            return False

    except urllib.error.HTTPError as e:
        print(f"API error: {e.code} - {e.reason}")
        try:
            error_body = e.read().decode()
            print(f"Details: {error_body}")
        except:
            pass
        return False


def main():
    print("\nONI Demo Video - Credits Scene Voiceover Generator")
    print("=" * 55)

    # Get API key from Keychain
    api_key = get_api_key()

    if not api_key:
        print("\nNo API key found in Keychain.")
        print("Run the main generate-voiceover.py first to set up API key.")
        sys.exit(1)
    else:
        print("API key found in Keychain")

    # Generate voiceover
    success = generate_voiceover(api_key)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
