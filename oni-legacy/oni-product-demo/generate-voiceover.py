#!/usr/bin/env python3
"""
ONI Demo Video - ElevenLabs Voiceover Generator
Stores API key securely in macOS Keychain
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
VOICE_ID_OVERRIDE = "8Ln42OXYupYsag45MAUy"  # Shared voice - use ID directly
OUTPUT_PATH = "public/audio/voiceover.mp3"

# The full script synced to video timestamps (3:11 duration)
# Last updated: 2026-01-29
SCRIPT_TEXT = """The next era of computing won't happen on a screen. It will happen inside your mind. Brain-computer interfaces are here. But who protects your thoughts? Today's neural interfaces are racing to market without standardized security. No common framework. No universal language. Until now. Introducing ONI. The Open Neurosecurity Interoperability framework. The world's first security architecture for the bio-digital interface. Security by design. Privacy by default. ONI bridges two worlds with fourteen layers, spanning silicon to synapse. Layers one through seven extend the classical OSI model. Physical signals, protocols, transport, applications. But here's where everything changes. Layer Eight. The Neural Gateway. The critical bridge where silicon meets synapse. Where traditional cybersecurity ends, and neurosecurity begins. Layers nine through fourteen map the living brain. Ion channels, spike trains, neural populations, cognitive function, and identity itself. How do you secure a brain-computer interface? ONI introduces the Coherence Score. A unified metric measuring the integrity of every neural signal in real-time. Phase alignment. Timing precision. Frequency stability. When coherence drops below threshold, defense mechanisms activate instantly. MRI interference. Electromagnetic disruption. Injection attacks. Detected and neutralized. For security teams, there's TARA. Telemetry Analysis and Response Automation. Real-time visualization. Attack simulation. Anomaly detection across all fourteen layers. And here's what makes it revolutionary. TARA never sees your raw neural data. Ever. Only mathematical scores. Coherence values. Your thoughts never leave your device. Privacy-preserving security at scale. Built on peer-reviewed research from top universities around the world. Grounded in Shannon's information theory. The mathematics of uncertainty, transformed into a real-time detection algorithm that protects what matters most. Every formula documented. Every claim cited. Open source and verifiable. Built for researchers. Developers. Regulators. Security teams. And you. The neural frontier is here. The only question is, who secures it? The standard is being written. Researchers, builders, visionaries. Let's write it together. Join us in building the security standards for brain-computer interfaces. Your mind. Your privacy. Our future. ONI. The bridge between worlds. Only life's most important connections deserves the most thought."""


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


def store_api_key():
    """Prompt for API key and store in macOS Keychain"""
    import getpass

    print("\n" + "=" * 60)
    print("  ElevenLabs API Key Setup")
    print("=" * 60)
    print("\nYour API key will be stored securely in macOS Keychain.")
    print(f"Service: {SERVICE_NAME}")
    print(f"Account: {ACCOUNT_NAME}")
    print("")

    # Prompt for key securely (hidden input)
    api_key = getpass.getpass("Paste your ElevenLabs API key: ")

    if not api_key.strip():
        print("No API key entered. Exiting.")
        sys.exit(1)

    api_key = api_key.strip()

    # Delete existing entry if present (ignore errors)
    subprocess.run(
        ["security", "delete-generic-password", "-s", SERVICE_NAME, "-a", ACCOUNT_NAME],
        capture_output=True
    )

    # Store in Keychain
    result = subprocess.run(
        ["security", "add-generic-password", "-s", SERVICE_NAME, "-a", ACCOUNT_NAME, "-w", api_key],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("API key saved to Keychain successfully!")
        return api_key
    else:
        print(f"Failed to save to Keychain: {result.stderr}")
        sys.exit(1)


def get_voice_id(api_key):
    """Get voice ID for the specified voice name"""
    # Use override ID if set (for shared voices not in user library)
    if VOICE_ID_OVERRIDE:
        print(f"Using voice: {VOICE_NAME} ({VOICE_ID_OVERRIDE})")
        return VOICE_ID_OVERRIDE, VOICE_NAME

    print(f"Looking up '{VOICE_NAME}' voice...")

    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key}
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            voices = data.get("voices", [])

            for voice in voices:
                if VOICE_NAME.lower() in voice["name"].lower():
                    return voice["voice_id"], voice["name"]

            # Voice not found - show available voices
            print(f"\nCould not find '{VOICE_NAME}' voice. Available voices:")
            for v in voices[:15]:
                print(f"  - {v['name']}")
            return None, None

    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("Invalid API key. Please update your Keychain entry.")
        else:
            print(f"API error: {e.code} - {e.reason}")
        return None, None


def generate_voiceover(api_key, voice_id):
    """Generate voiceover using ElevenLabs API"""
    print("\nGenerating voiceover with ElevenLabs...")
    print(f"  Voice: {VOICE_NAME}")
    print(f"  Model: eleven_multilingual_v2")
    print(f"  Output: {OUTPUT_PATH}")
    print("\nThis may take a minute...\n")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    payload = json.dumps({
        "text": SCRIPT_TEXT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.5,
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
            with open(OUTPUT_PATH, "wb") as f:
                f.write(response.read())

        # Check file size
        size = os.path.getsize(OUTPUT_PATH)
        if size > 1000:
            size_mb = size / (1024 * 1024)
            print(f"Success! Voiceover saved to {OUTPUT_PATH} ({size_mb:.1f} MB)")
            print("\nPreview in Remotion: npm run dev")

            # Play audio preview
            print("\nPlaying audio preview...")
            subprocess.Popen(["afplay", OUTPUT_PATH])
            return True
        else:
            print("Error: Generated file is too small. Check API response.")
            with open(OUTPUT_PATH, "r") as f:
                print(f.read())
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
    print("\nONI Demo Video - ElevenLabs Voiceover Generator")
    print("=" * 50)

    # Get API key from Keychain
    api_key = get_api_key()

    if not api_key:
        print("\nNo API key found in Keychain.")
        api_key = store_api_key()
    else:
        print("API key found in Keychain")

    # Get voice ID
    voice_id, voice_name = get_voice_id(api_key)

    if not voice_id:
        print("\nFailed to get voice ID. Exiting.")
        sys.exit(1)

    print(f"Found voice: {voice_name} ({voice_id})")

    # Generate voiceover
    success = generate_voiceover(api_key, voice_id)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
