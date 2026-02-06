#!/usr/bin/env python3
"""
ONI Demo Video - Female British Voiceover for Finale
Strong, protective, intelligent voice - "Welcome to the OSI of Mind"
"""

import subprocess
import json
import sys
import os
import urllib.request
import urllib.error

SERVICE_NAME = "elevenlabs-api"
ACCOUNT_NAME = "oni-demo"

# British female voices to try (will list available and pick best match)
# Looking for: strong, protective, intelligent, British accent
OUTPUT_DIR = "public/audio"

# The finale text with dramatic pause
# Option 1: "Welcome to the OSI of Mind... This is ONI. Your mind deserves a standard."
# Option 2: "Welcome to the OSI of Mind... This is ONI. The future of neural security starts now."
# Option 3: "Welcome to the OSI of Mind... This is ONI. Because some minds are worth protecting."

FINALE_TEXT = "Welcome to the OSI of Mind. ... This is ONI. The future of neural security... starts now."


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


def list_voices(api_key):
    """List available voices to find British female options"""
    print("\nSearching for British female voices...")

    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key}
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            voices = data.get("voices", [])

            # Filter for potential matches
            british_female = []
            for v in voices:
                labels = v.get("labels", {})
                name = v.get("name", "").lower()
                accent = labels.get("accent", "").lower()
                gender = labels.get("gender", "").lower()
                description = labels.get("description", "").lower()
                use_case = labels.get("use_case", "").lower()

                # Look for British female voices
                is_british = "british" in accent or "english" in accent or "uk" in name
                is_female = gender == "female" or "female" in name

                if is_female:
                    british_female.append({
                        "id": v["voice_id"],
                        "name": v["name"],
                        "accent": accent,
                        "description": description,
                        "use_case": use_case,
                        "is_british": is_british
                    })

            print(f"\nFound {len(british_female)} female voices:")
            print("-" * 60)

            # Sort British voices first
            british_female.sort(key=lambda x: (not x["is_british"], x["name"]))

            for v in british_female[:15]:
                brit_marker = "[BRITISH]" if v["is_british"] else ""
                print(f"  {v['name']} {brit_marker}")
                print(f"    ID: {v['id']}")
                print(f"    Accent: {v['accent']}")
                print(f"    Description: {v['description']}")
                print()

            return british_female

    except urllib.error.HTTPError as e:
        print(f"API error: {e.code} - {e.reason}")
        return []


def generate_voiceover(api_key, voice_id, voice_name, text, output_name):
    """Generate voiceover using ElevenLabs API"""
    output_path = os.path.join(OUTPUT_DIR, f"{output_name}.mp3")

    print(f"\nGenerating finale voiceover...")
    print(f"  Voice: {voice_name}")
    print(f"  Text: {text}")
    print(f"  Output: {output_path}")

    payload = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.6,  # Slightly higher for authoritative tone
            "similarity_boost": 0.75,
            "style": 0.4,  # Less stylized for professional tone
            "use_speaker_boost": True
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
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
            with open(output_path, "wb") as f:
                f.write(response.read())

        size = os.path.getsize(output_path)
        if size > 1000:
            size_kb = size / 1024
            print(f"  Success! Saved to {output_path} ({size_kb:.1f} KB)")

            # Get duration
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", output_path],
                    capture_output=True, text=True
                )
                duration = float(result.stdout.strip())
                print(f"  Duration: {duration:.2f}s ({int(duration * 30)} frames)")
            except:
                pass

            # Play preview
            print("\n  Playing preview...")
            subprocess.Popen(["afplay", output_path])
            return True, output_path
        else:
            print("  Error: Generated file too small")
            return False, None

    except urllib.error.HTTPError as e:
        print(f"  API error: {e.code} - {e.reason}")
        try:
            print(f"  Details: {e.read().decode()}")
        except:
            pass
        return False, None


def main():
    print("\nONI Demo Video - Female British Finale Voiceover")
    print("=" * 55)
    print("\nLooking for: Strong, protective, intelligent British female voice")
    print(f"Text: \"{FINALE_TEXT}\"")

    api_key = get_api_key()
    if not api_key:
        print("\nNo API key found. Run generate-voiceover.py first.")
        sys.exit(1)

    # List available voices
    voices = list_voices(api_key)

    if not voices:
        print("No female voices found!")
        sys.exit(1)

    # Find best British female voice
    # Priority: British accent + authoritative/professional description
    best_voice = None
    for v in voices:
        if v["is_british"]:
            best_voice = v
            break

    # Fallback to any professional-sounding female voice
    if not best_voice:
        for v in voices:
            desc = v.get("description", "").lower()
            if any(word in desc for word in ["authoritative", "professional", "confident", "strong"]):
                best_voice = v
                break

    # Final fallback
    if not best_voice and voices:
        best_voice = voices[0]

    if best_voice:
        print(f"\nSelected voice: {best_voice['name']}")
        print(f"  ID: {best_voice['id']}")

        # Generate the voiceover
        success, path = generate_voiceover(
            api_key,
            best_voice['id'],
            best_voice['name'],
            FINALE_TEXT,
            "vo-finale-welcome"
        )

        if success:
            print("\nSuccess! Now add to ONIDemoVideo.tsx")
    else:
        print("Could not find suitable voice")


if __name__ == "__main__":
    main()
