/**
 * Generate voiceover audio using ElevenLabs API
 *
 * Usage:
 *   export ELEVENLABS_API_KEY="your-api-key"
 *   npx ts-node scripts/generate-audio.ts
 */

import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';

const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;

// Voice IDs from ElevenLabs
const VOICES = {
  adam: 'pNInz6obpgDQGcFmaJgB',      // Deep, authoritative
  rachel: '21m00Tcm4TlvDq8ikWAM',    // Professional female
  josh: 'TxGEqnHWrfWFTfGW9XjX',      // Conversational male
  arnold: 'VR6AewLTigWG4xSOukaG',    // Crisp narrator
};

// Full script for ONI Demo Video
const SCRIPT = `Brain-computer interfaces are no longer science fiction. They're in operating rooms. They're in research labs. They're coming to consumers.

But who's protecting the most sensitive data in existence? Your thoughts.

Today's BCIs lack standardized security frameworks. There's no OSI model for neural interfaces. No common language between neuroscientists, engineers, and security researchers.

Until now.

Introducing the Open Neural Interface Framework.

ONI defines fourteen layers spanning silicon to synapse. Layers one through seven handle the silicon side: physical signals, protocols, and data transport.

Layer eight is the Neural Gateway — the critical bridge between machine and mind.

Layers nine through fourteen map biological processing: from ion channels to cognition to identity.

Each layer has defined security controls, threat models, and verification methods.

But how do you measure neural security?

ONI introduces the Coherence Score — a unified metric combining phase synchronization, timing precision, and frequency response.

It's not a black box. It's fully configurable and mathematically grounded. Explore it yourself in our interactive playground.

For security professionals, there's TARA — the Threat Assessment and Risk Analysis platform.

Real-time brain topology visualization. Attack simulation across all fourteen layers. Neural Signal Assurance Monitoring that flags anomalies before they become breaches.

All open source. All verifiable.

ONI isn't built in a vacuum. It extends the threat models of Kohno and colleagues at the University of Washington. It incorporates neurosecurity research from Columbia, Yale, and the Graz BCI Lab.

Every claim is cited. Every formula is documented.

Ready to secure the neural frontier?

Install ONI with a single command: pip install oni-framework.

Explore the documentation on GitHub. Join us in building the security standards for brain-computer interfaces.

The Open Neural Interface Framework. The OSI of Mind.`;

async function generateVoiceover(text: string, voiceId: string, outputPath: string): Promise<void> {
  if (!ELEVENLABS_API_KEY) {
    throw new Error('ELEVENLABS_API_KEY environment variable is required');
  }

  console.log('Generating voiceover with ElevenLabs...');
  console.log(`Voice ID: ${voiceId}`);
  console.log(`Output: ${outputPath}`);

  const requestData = JSON.stringify({
    text: text,
    model_id: 'eleven_monolingual_v1',
    voice_settings: {
      stability: 0.5,
      similarity_boost: 0.75,
      style: 0.0,
      use_speaker_boost: true,
    },
  });

  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.elevenlabs.io',
      port: 443,
      path: `/v1/text-to-speech/${voiceId}`,
      method: 'POST',
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': ELEVENLABS_API_KEY,
      },
    };

    const req = https.request(options, (res) => {
      if (res.statusCode !== 200) {
        let error = '';
        res.on('data', (chunk) => error += chunk);
        res.on('end', () => {
          reject(new Error(`ElevenLabs API error (${res.statusCode}): ${error}`));
        });
        return;
      }

      const chunks: Buffer[] = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        const buffer = Buffer.concat(chunks);
        fs.writeFileSync(outputPath, buffer);
        console.log(`✓ Voiceover saved to ${outputPath} (${(buffer.length / 1024 / 1024).toFixed(2)} MB)`);
        resolve();
      });
    });

    req.on('error', reject);
    req.write(requestData);
    req.end();
  });
}

async function main() {
  const audioDir = path.join(__dirname, '..', 'public', 'audio');

  // Create audio directory if it doesn't exist
  if (!fs.existsSync(audioDir)) {
    fs.mkdirSync(audioDir, { recursive: true });
  }

  const outputPath = path.join(audioDir, 'voiceover.mp3');

  try {
    // Use Adam voice (deep, authoritative) - good for tech content
    await generateVoiceover(SCRIPT, VOICES.adam, outputPath);
    console.log('\n✓ Audio generation complete!');
    console.log('\nNext steps:');
    console.log('1. Uncomment Audio imports in src/ONIDemoVideo.tsx');
    console.log('2. Run: npm run dev');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();
