#!/usr/bin/env python3
"""
ONI Demo Video - Finale Sound Effects Generator

Creates sound effects matching the established harmonic pattern:
- Perfect 4th (4:3 ratio) - ding-tone.mp3
- Perfect 5th (3:2 ratio) - ding-tone-2.mp3
- Major resolution - boot-chime.mp3

For the finale, we continue the progression:
1. "finale-dawn.mp3" - Ascending major chord, opens like a door to light
   (Futuristic yet simple, elegant, beginning of a journey)

Uses ElevenLabs Sound Effects API
"""

import subprocess
import json
import sys
import os
import urllib.request
import urllib.error

SERVICE_NAME = "elevenlabs-api"
ACCOUNT_NAME = "oni-demo"
OUTPUT_DIR = "public/audio"

# Sound effects prompts - designed to match the established tonal pattern
# and evoke "beginning of a journey, new chapter, futuristic yet elegant"
SOUND_EFFECTS = [
    {
        "name": "finale-ascend",
        "prompt": "Soft ascending synthesizer chord progression, starting low and rising to a bright, hopeful major chord. Crystal clear, futuristic, elegant, minimal. Like dawn breaking through a window. 3 seconds.",
        "duration_seconds": 3.0,
    },
    {
        "name": "finale-shimmer",
        "prompt": "Gentle shimmering bells and soft synth pad, major key, warm and inviting. Futuristic yet organic. Creates sense of opening, new beginnings. Simple and elegant. 4 seconds.",
        "duration_seconds": 4.0,
    },
    {
        "name": "finale-resolve",
        "prompt": "Resolving synthesizer tone, perfect fifth interval ascending to octave. Clean, pure, hopeful. Like the first light of a new day. Minimal, elegant, futuristic. 2 seconds.",
        "duration_seconds": 2.0,
    },
]


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


def generate_sound_effect(api_key, sfx):
    """Generate sound effect using ElevenLabs Sound Effects API"""
    name = sfx["name"]
    prompt = sfx["prompt"]
    duration = sfx.get("duration_seconds", 5.0)
    output_path = os.path.join(OUTPUT_DIR, f"{name}.mp3")

    print(f"\nGenerating: {name}")
    print(f"  Prompt: {prompt[:80]}...")
    print(f"  Duration: {duration}s")

    payload = json.dumps({
        "text": prompt,
        "duration_seconds": duration,
        "prompt_influence": 0.7  # Higher = more faithful to prompt
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/sound-generation",
        data=payload,
        headers={
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(output_path, "wb") as f:
                f.write(response.read())

        # Check file size
        size = os.path.getsize(output_path)
        if size > 1000:
            size_kb = size / 1024
            print(f"  Success! Saved to {output_path} ({size_kb:.1f} KB)")
            return True, output_path
        else:
            print(f"  Error: Generated file is too small")
            return False, None

    except urllib.error.HTTPError as e:
        print(f"  API error: {e.code} - {e.reason}")
        try:
            error_body = e.read().decode()
            print(f"  Details: {error_body}")
        except:
            pass
        return False, None
    except Exception as e:
        print(f"  Error: {e}")
        return False, None


def main():
    print("\nONI Demo Video - Finale Sound Effects Generator")
    print("=" * 50)
    print("\nCreating sounds that match the established harmonic pattern:")
    print("  - Perfect 4th → Perfect 5th → Major Resolution")
    print("  - Theme: Beginning of a journey, new chapter")
    print("  - Style: Futuristic yet simple, elegant, exciting")

    # Get API key from Keychain
    api_key = get_api_key()

    if not api_key:
        print("\nNo API key found in Keychain.")
        print("Run the main generate-voiceover.py first to set up API key.")
        sys.exit(1)
    else:
        print("\nAPI key found in Keychain")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate each sound effect
    generated = []
    for sfx in SOUND_EFFECTS:
        success, path = generate_sound_effect(api_key, sfx)
        if success:
            generated.append(path)

    print(f"\n{'='*50}")
    print(f"Generated {len(generated)}/{len(SOUND_EFFECTS)} sound effects")

    if generated:
        print("\nPlaying generated sounds...")
        for path in generated:
            print(f"  Playing: {path}")
            proc = subprocess.Popen(["afplay", path])
            proc.wait()  # Wait for each to finish

    print("\nNext steps:")
    print("1. Review the generated sounds")
    print("2. Add to ONIDemoVideo.tsx in the credits sequence")
    print("3. Time them to sync with the door-opening visual effect")


if __name__ == "__main__":
    main()
