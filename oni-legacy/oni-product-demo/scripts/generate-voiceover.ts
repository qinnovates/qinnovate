/**
 * ElevenLabs Voiceover Generator for ONI Demo Video
 *
 * Usage:
 *   ELEVENLABS_API_KEY=your_key npx ts-node scripts/generate-voiceover.ts
 *
 * Or set ELEVENLABS_API_KEY in .env file
 */

import fs from 'fs';
import path from 'path';
import { script, fullScript, scriptMeta } from '../src/data/script';

const ELEVENLABS_API_URL = 'https://api.elevenlabs.io/v1';

// Voice IDs from ElevenLabs
const VOICES = {
  // Recommended for cinematic narration
  Antoni: '21m00Tcm4TlvDq8ikWAM',  // Deep, authoritative, cinematic
  Adam: 'pNInz6obpgDQGcFmaJgB',    // Clear, professional
  Marcus: '2EiwWnXFnvU5JabPnv8n',  // Deep narrator voice
  // Alternative voices
  Josh: 'TxGEqnHWrfWFTfGW9XjX',    // Young, energetic
  Sam: 'yoZ06aMxZJJ28mfd3POQ',     // Neutral, clear
};

interface VoiceSettings {
  stability: number;
  similarity_boost: number;
  style?: number;
  use_speaker_boost?: boolean;
}

interface GenerationConfig {
  voiceId: string;
  modelId: string;
  voiceSettings: VoiceSettings;
  outputFormat: string;
}

// Optimized settings for dramatic narration
const CINEMATIC_CONFIG: GenerationConfig = {
  voiceId: VOICES.Antoni,
  modelId: 'eleven_multilingual_v2',
  voiceSettings: {
    stability: 0.5,        // Lower = more expressive
    similarity_boost: 0.8, // Higher = more consistent
    style: 0.7,            // More dramatic style
    use_speaker_boost: true,
  },
  outputFormat: 'mp3_44100_128',
};

async function generateVoiceover(
  text: string,
  config: GenerationConfig,
  apiKey: string
): Promise<Buffer> {
  const response = await fetch(
    `${ELEVENLABS_API_URL}/text-to-speech/${config.voiceId}`,
    {
      method: 'POST',
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': apiKey,
      },
      body: JSON.stringify({
        text,
        model_id: config.modelId,
        voice_settings: config.voiceSettings,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`ElevenLabs API error: ${response.status} - ${error}`);
  }

  const arrayBuffer = await response.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

async function generateWithTimestamps(
  text: string,
  config: GenerationConfig,
  apiKey: string
): Promise<{ audio: Buffer; timestamps: any }> {
  const response = await fetch(
    `${ELEVENLABS_API_URL}/text-to-speech/${config.voiceId}/with-timestamps`,
    {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'xi-api-key': apiKey,
      },
      body: JSON.stringify({
        text,
        model_id: config.modelId,
        voice_settings: config.voiceSettings,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`ElevenLabs API error: ${response.status} - ${error}`);
  }

  return await response.json();
}

async function main() {
  const apiKey = process.env.ELEVENLABS_API_KEY;

  if (!apiKey) {
    console.error('❌ ELEVENLABS_API_KEY environment variable not set');
    console.log('\nUsage:');
    console.log('  ELEVENLABS_API_KEY=your_key npx ts-node scripts/generate-voiceover.ts');
    console.log('\nOr create a .env file with:');
    console.log('  ELEVENLABS_API_KEY=your_key');
    process.exit(1);
  }

  console.log('🎙️  ONI Demo Video - Voiceover Generator');
  console.log('=========================================');
  console.log(`📝 Script: ${scriptMeta.wordCount} words`);
  console.log(`⏱️  Estimated duration: ${scriptMeta.estimatedDuration}`);
  console.log(`🎤 Voice: ${scriptMeta.voice.recommended}`);
  console.log('');

  // Output paths
  const outputDir = path.join(__dirname, '../public/audio');
  const outputPath = path.join(outputDir, 'voiceover.mp3');
  const timestampsPath = path.join(outputDir, 'timestamps.json');

  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log('🔄 Generating voiceover with ElevenLabs...');
  console.log(`   Voice ID: ${CINEMATIC_CONFIG.voiceId}`);
  console.log(`   Model: ${CINEMATIC_CONFIG.modelId}`);
  console.log('');

  try {
    // Generate full audio
    const audioBuffer = await generateVoiceover(
      fullScript,
      CINEMATIC_CONFIG,
      apiKey
    );

    // Save audio file
    fs.writeFileSync(outputPath, audioBuffer);
    console.log(`✅ Audio saved to: ${outputPath}`);
    console.log(`   Size: ${(audioBuffer.length / 1024 / 1024).toFixed(2)} MB`);

    // Save script with frame mappings for manual sync
    const syncData = {
      script: script.map(line => ({
        text: line.text,
        scene: line.scene,
        startFrame: line.startFrame,
        endFrame: line.endFrame,
        startTime: line.startFrame / 30, // seconds at 30fps
        endTime: line.endFrame / 30,
        emphasis: line.emphasis,
      })),
      meta: scriptMeta,
      generatedAt: new Date().toISOString(),
      voice: scriptMeta.voice.recommended,
    };

    fs.writeFileSync(timestampsPath, JSON.stringify(syncData, null, 2));
    console.log(`✅ Sync data saved to: ${timestampsPath}`);

    console.log('');
    console.log('🎬 Next steps:');
    console.log('   1. Listen to public/audio/voiceover.mp3');
    console.log('   2. Fine-tune timing in src/data/script.ts if needed');
    console.log('   3. Uncomment audio lines in src/ONIDemoVideo.tsx');
    console.log('   4. Render final video with: npm run build');

  } catch (error) {
    console.error('❌ Generation failed:', error);
    process.exit(1);
  }
}

// Also export for programmatic use
export { generateVoiceover, generateWithTimestamps, VOICES, CINEMATIC_CONFIG };

// Run if called directly
main();
