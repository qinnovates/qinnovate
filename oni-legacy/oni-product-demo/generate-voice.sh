#!/bin/bash
cd "$(dirname "$0")"

echo "🎙️  ONI Demo Video - ElevenLabs Voiceover Generator"
echo "=================================================="
echo ""

# Prompt for API key (hidden input)
read -s -p "Paste your ElevenLabs API key and press Enter: " API_KEY
echo ""
echo ""

if [ -z "$API_KEY" ]; then
    echo "❌ No API key entered. Exiting."
    exit 1
fi

echo "🔍 Looking up 'Hale' voice..."

# Get voice ID for "Hale"
VOICE_ID=$(curl -s "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: $API_KEY" | \
  python3 -c "import sys, json; voices = json.load(sys.stdin).get('voices', []); hale = next((v for v in voices if 'hale' in v['name'].lower()), None); print(hale['voice_id'] if hale else '')")

if [ -z "$VOICE_ID" ]; then
    echo "❌ Could not find 'Hale' voice. Available voices:"
    curl -s "https://api.elevenlabs.io/v1/voices" \
      -H "xi-api-key: $API_KEY" | \
      python3 -c "import sys, json; voices = json.load(sys.stdin).get('voices', []); [print(f\"  - {v['name']}\") for v in voices[:15]]"
    exit 1
fi

echo "✅ Found Hale voice: $VOICE_ID"
echo ""
echo "🔄 Generating voiceover with ElevenLabs..."
echo "   Voice: Hale"
echo "   Duration: ~3:30"
echo ""

# The full script text
SCRIPT_TEXT="The next era of computing won't happen on a screen. It will happen inside your mind. Brain-computer interfaces are here. But who protects your thoughts? Today's neural interfaces are racing to market without standardized security. No common framework. No universal language. Until now. Introducing ONI. The Open Neurosecurity Interoperability framework. The world's first security architecture for the bio-digital interface. Security by design. Privacy by default. ONI bridges two worlds with fourteen layers, spanning silicon to synapse. Layers one through seven extend the classical OSI model. Physical signals, protocols, transport, applications. But here's where everything changes. Layer Eight. The Neural Gateway. The critical bridge where silicon meets synapse. Where traditional cybersecurity ends, and neurosecurity begins. Layers nine through fourteen map the living brain. Ion channels, spike trains, neural populations, cognitive function, and identity itself. How do you secure a brain-computer interface? ONI introduces the Coherence Score. A unified metric measuring the integrity of every neural signal in real-time. Phase alignment. Timing precision. Frequency stability. When coherence drops below threshold, defense mechanisms activate instantly. MRI interference. Electromagnetic disruption. Injection attacks. Detected and neutralized. For security teams, there's TARA. Telemetry Analysis and Response Automation. Real-time visualization. Attack simulation. Anomaly detection across all fourteen layers. And here's what makes it revolutionary. TARA never sees your raw neural data. Ever. Only mathematical scores. Coherence values. Your thoughts never leave your device. Privacy-preserving security at scale. Built on peer-reviewed research from the University of Washington, Columbia, Yale, and the Graz BCI Lab. Every formula documented. Every claim cited. Open source and verifiable. Built for researchers. Developers. Regulators. Security teams. And you. The neural frontier is here. The only question is, who secures it? Get started in seconds. pip install oni-framework. Join us in building the security standards for brain-computer interfaces. Your mind. Your privacy. Our future. ONI. The bridge between worlds."

# Create output directory
mkdir -p public/audio

# Call ElevenLabs API with Hale voice
curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID" \
  -H "Accept: audio/mpeg" \
  -H "Content-Type: application/json" \
  -H "xi-api-key: $API_KEY" \
  -d "{
    \"text\": \"$SCRIPT_TEXT\",
    \"model_id\": \"eleven_multilingual_v2\",
    \"voice_settings\": {
      \"stability\": 0.5,
      \"similarity_boost\": 0.75,
      \"style\": 0.5,
      \"use_speaker_boost\": true
    }
  }" \
  --output public/audio/voiceover.mp3

# Check if successful
if [ -f "public/audio/voiceover.mp3" ] && [ -s "public/audio/voiceover.mp3" ]; then
    SIZE=$(ls -lh public/audio/voiceover.mp3 | awk '{print $5}')
    echo ""
    echo "✅ Success! Voiceover saved to public/audio/voiceover.mp3 ($SIZE)"
    echo ""
    echo "🎬 Preview in Remotion: npm run dev"
    echo ""
    echo "🔊 Playing audio preview..."
    afplay public/audio/voiceover.mp3 &
else
    echo "❌ Generation failed. Response:"
    cat public/audio/voiceover.mp3 2>/dev/null
fi
