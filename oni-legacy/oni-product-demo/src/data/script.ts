/**
 * ONI Framework Demo Video Script
 * SYNCED TO VIDEO TIMESTAMPS - Total: 3:30 (6300 frames @ 30fps)
 *
 * Voice: ElevenLabs "Jay Wayne - Wise University Professor"
 * Voice ID: 8Ln42OXYupYsag45MAUy
 * Duration: ~3:11
 * Last Updated: 2026-01-29
 */

export interface ScriptLine {
  text: string;
  startFrame: number;
  endFrame: number;
  scene: string;
  startTime: string; // MM:SS for reference
}

export const script: ScriptLine[] = [
  // ═══════════════════════════════════════════════════════════════
  // COLD OPEN: 0:00-0:08 (frames 0-240)
  // ═══════════════════════════════════════════════════════════════
  {
    scene: 'coldOpen',
    text: "The next era of computing won't happen on a screen.",
    startFrame: 0,
    endFrame: 120,
    startTime: '0:00',
  },
  {
    scene: 'coldOpen',
    text: "It will happen inside your mind.",
    startFrame: 120,
    endFrame: 240,
    startTime: '0:04',
  },

  // ═══════════════════════════════════════════════════════════════
  // TITLE: 0:08-0:15 (frames 240-450)
  // ═══════════════════════════════════════════════════════════════
  {
    scene: 'title',
    text: "Brain-computer interfaces are here. But who protects your thoughts?",
    startFrame: 240,
    endFrame: 450,
    startTime: '0:08',
  },

  // ═══════════════════════════════════════════════════════════════
  // PROBLEM: 0:15-0:40 (frames 450-1200)
  // SYNCED TO VISUAL PHASES in ProblemScene.tsx
  // ═══════════════════════════════════════════════════════════════
  {
    scene: 'problem',
    // Visual: "Brain-computer interfaces are here." + "FDA approved. In clinical trials. Shipping to consumers."
    text: "Brain-computer interfaces are here. FDA approved. In clinical trials. Shipping to consumers.",
    startFrame: 470,  // Phase 1 starts at scene-relative frame 20
    endFrame: 570,
    startTime: '0:15',
  },
  {
    scene: 'problem',
    // Visual: "Neurosecurity today is..."
    text: "But neurosecurity today is...",
    startFrame: 570,
    endFrame: 670,
    startTime: '0:19',
  },
  {
    scene: 'problem',
    // Visual: "Fragmented." (delay 0) "Complex." (delay 35) "Inaccessible." (delay 70)
    // Speak slowly to match staggered visual reveal
    text: "Fragmented. Complex. Inaccessible.",
    startFrame: 670,
    endFrame: 850,
    startTime: '0:22',
  },
  {
    scene: 'problem',
    // Visual: "Until now." (big, center screen)
    text: "Until now.",
    startFrame: 870,
    endFrame: 960,
    startTime: '0:29',
  },
  {
    scene: 'problem',
    // Visual: "Introducing" + "ONI Framework" with animated gradient
    text: "Introducing ONI. The Open Neurosecurity Interoperability framework.",
    startFrame: 990,
    endFrame: 1100,
    startTime: '0:33',
  },
  {
    scene: 'problem',
    // Visual: Typing effect "A unified neurosecurity stack for the next era of computing"
    text: "A unified neurosecurity stack for the next era of computing.",
    startFrame: 1100,
    endFrame: 1200,
    startTime: '0:36',
  },

  // ═══════════════════════════════════════════════════════════════
  // LAYERS: 0:40-1:20 (frames 1200-2400)
  // SYNCED TO VISUAL PHASES in ONILayersAnimation.tsx
  // Phase 1: 0-150 (intro), Phase 2: 150-450 (L1-L7), Phase 3: 450-750 (L8)
  // Phase 4: 750-1050 (L9-L14), Phase 5: 1050-1200 (full stack)
  // ═══════════════════════════════════════════════════════════════
  {
    scene: 'layers',
    // Visual: "14 layers spanning silicon to synapse" (Phase 1: frames 1200-1350)
    text: "Fourteen layers spanning silicon to synapse.",
    startFrame: 1200,
    endFrame: 1350,
    startTime: '0:40',
  },
  {
    scene: 'layers',
    // Visual: L1-L7 silicon layers revealing with OSI labels (Phase 2: frames 1350-1650)
    text: "Layers one through seven extend the classical OSI model. Physical signals, protocols, transport, applications.",
    startFrame: 1350,
    endFrame: 1620,
    startTime: '0:45',
  },
  {
    scene: 'layers',
    // Transition to L8
    text: "But here's where everything changes.",
    startFrame: 1620,
    endFrame: 1700,
    startTime: '0:54',
  },
  {
    scene: 'layers',
    // Visual: L8 zooms in, glows amber (Phase 3 start: frame 1650)
    text: "Layer Eight. The Neural Gateway.",
    startFrame: 1700,
    endFrame: 1820,
    startTime: '0:56',
  },
  {
    scene: 'layers',
    // Visual: "The critical bridge between machine and mind" text appears below L8
    text: "The critical bridge between machine and mind. Where cybersecurity ends, and neurosecurity begins.",
    startFrame: 1820,
    endFrame: 1980,
    startTime: '1:00',
  },
  {
    scene: 'layers',
    // Visual: L9-L14 biology layers revealing (Phase 4: frames 1950-2250)
    text: "Layers nine through fourteen map the living brain. Ion channels, spike trains, neural populations, cognitive function, and identity.",
    startFrame: 1980,
    endFrame: 2280,
    startTime: '1:06',
  },
  {
    scene: 'layers',
    // Visual: Full stack view (Phase 5: frames 2250-2400)
    text: "The complete ONI stack. From silicon to self.",
    startFrame: 2280,
    endFrame: 2400,
    startTime: '1:16',
  },

  // ═══════════════════════════════════════════════════════════════
  // COHERENCE: 1:20-1:50 (frames 2400-3300)
  // SYNCED TO VISUAL PHASES in CoherenceScene.tsx
  // Phase 1: 0-280 (intro), Phase 2: 280-500 (threshold demo), Phase 3: 500+ (scale-freq)
  // ═══════════════════════════════════════════════════════════════
  {
    scene: 'coherence',
    // Visual: "The Coherence Score" title with animated gauge building up
    text: "The Coherence Score. A unified metric for neural security.",
    startFrame: 2400,
    endFrame: 2550,
    startTime: '1:20',
  },
  {
    scene: 'coherence',
    // Visual: Component cards appear (σ²φ, σ²τ, σ²γ)
    text: "Phase variance. Timing variance. Frequency variance.",
    startFrame: 2550,
    endFrame: 2700,
    startTime: '1:25',
  },
  {
    scene: 'coherence',
    // Visual: "When coherence drops below threshold..." + gauge drops + breach alert
    text: "When coherence drops below threshold, defenses activate instantly.",
    startFrame: 2700,
    endFrame: 2900,
    startTime: '1:30',
  },
  {
    scene: 'coherence',
    // Visual: Attack types appear (MRI, Injection) and recovery
    text: "MRI interference. Injection attacks. Detected and neutralized.",
    startFrame: 2900,
    endFrame: 3100,
    startTime: '1:36',
  },
  {
    scene: 'coherence',
    // Visual: Scale-Frequency section with formula
    text: "The scale-frequency invariant ensures neural patterns stay consistent across all scales.",
    startFrame: 3100,
    endFrame: 3300,
    startTime: '1:43',
  },

  // ═══════════════════════════════════════════════════════════════
  // TARA: 1:50-2:25 (frames 3300-4350)
  // SYNCED TO VISUAL PHASES in TARAScene.tsx
  // Phase 1: 0-500 (TARA intro + features), Phase 2: 500+ (anomaly detection)
  // ═══════════════════════════════════════════════════════════════
  {
    scene: 'tara',
    // Visual: "TARA" title + "Telemetry Analysis & Response Automation" + brain viz
    text: "For security teams, there's TARA. Telemetry Analysis and Response Automation.",
    startFrame: 3300,
    endFrame: 3550,
    startTime: '1:50',
  },
  {
    scene: 'tara',
    // Visual: Feature cards appear (Brain Topology, Attack Simulator, NSAM Monitor)
    text: "Brain topology. Attack simulation. Real-time monitoring.",
    startFrame: 3550,
    endFrame: 3750,
    startTime: '1:58',
  },
  {
    scene: 'tara',
    // Visual: Privacy-First card appears with lock-in-shield icon
    text: "Privacy-first by design. Only coherence scores are transmitted. Raw neural data never leaves your device.",
    startFrame: 3750,
    endFrame: 4000,
    startTime: '2:05',
  },
  {
    scene: 'tara',
    // Visual: "How TARA Detects Threats" title + statistical visualization
    text: "How does TARA detect threats? Statistical baselines. Z-score thresholds. Automated response in milliseconds.",
    startFrame: 4000,
    endFrame: 4350,
    startTime: '2:13',
  },

  // ═══════════════════════════════════════════════════════════════
  // ACADEMIC: 2:25-2:50 (frames 4350-5100)
  // Research foundation and audience (shortened for timing)
  // ═══════════════════════════════════════════════════════════════
  {
    scene: 'academic',
    text: "Built on peer-reviewed research. Grounded in Shannon's information theory.",
    startFrame: 4350,
    endFrame: 4600,
    startTime: '2:25',
  },
  {
    scene: 'academic',
    text: "Every formula documented. Every claim cited. Open source and verifiable.",
    startFrame: 4600,
    endFrame: 4850,
    startTime: '2:33',
  },
  {
    scene: 'academic',
    text: "Built for researchers. Developers. Regulators. And you.",
    startFrame: 4850,
    endFrame: 5100,
    startTime: '2:41',
  },

  // ═══════════════════════════════════════════════════════════════
  // CTA: 2:50-3:15 (frames 5100-5850)
  // Call to action
  // ═══════════════════════════════════════════════════════════════
  {
    scene: 'cta',
    text: "The neural frontier is here. The only question is, who secures it?",
    startFrame: 5100,
    endFrame: 5340,
    startTime: '2:50',
  },
  {
    scene: 'cta',
    text: "The standard is being written. Researchers, builders, visionaries.",
    startFrame: 5340,
    endFrame: 5550,
    startTime: '2:58',
  },
  {
    scene: 'cta',
    text: "Let's write it together. Join us in building the security standards for brain-computer interfaces.",
    startFrame: 5550,
    endFrame: 5850,
    startTime: '3:05',
  },

  // ═══════════════════════════════════════════════════════════════
  // CREDITS: 3:09-3:34 (frames 5670-6420) - extended for finale
  // SYNCED TO VISUAL PHASES in CreditsScene.tsx
  // ═══════════════════════════════════════════════════════════════
  {
    scene: 'credits',
    // Visual: "Your Mind. Your Privacy. Our Future." in white
    text: "Your mind. Your privacy. Our future.",
    startFrame: 5670,
    endFrame: 5820,
    startTime: '3:09',
  },
  {
    scene: 'credits',
    // Visual: "ONI. The bridge between worlds." (transition)
    text: "ONI. The bridge between worlds.",
    startFrame: 5820,
    endFrame: 5970,
    startTime: '3:14',
  },
  {
    scene: 'credits',
    // Visual: "Because only life's most important connections deserve the most thought."
    text: "Because only life's most important connections deserve the most thought.",
    startFrame: 5970,
    endFrame: 6130,
    startTime: '3:19',
  },
  {
    scene: 'credits',
    // Visual: "Welcome to" + "The OSI of Mind" door opening effect
    // Voice: Female British (Lily) - strong, protective, intelligent
    text: "Welcome to the OSI of Mind. This is ONI. The future of neural security starts now.",
    startFrame: 6130,
    endFrame: 6335,
    startTime: '3:24',
  },
  // Orchestrated closing: ding (6340) → ding2 (6370) → chime (6395-6420)
];

// Full script for voiceover generation
export const fullScript = script.map(line => line.text).join(' ');

// Scene-by-scene script for segmented generation
export const sceneScripts = {
  coldOpen: script.filter(l => l.scene === 'coldOpen').map(l => l.text).join(' '),
  title: script.filter(l => l.scene === 'title').map(l => l.text).join(' '),
  problem: script.filter(l => l.scene === 'problem').map(l => l.text).join(' '),
  layers: script.filter(l => l.scene === 'layers').map(l => l.text).join(' '),
  coherence: script.filter(l => l.scene === 'coherence').map(l => l.text).join(' '),
  tara: script.filter(l => l.scene === 'tara').map(l => l.text).join(' '),
  academic: script.filter(l => l.scene === 'academic').map(l => l.text).join(' '),
  cta: script.filter(l => l.scene === 'cta').map(l => l.text).join(' '),
  credits: script.filter(l => l.scene === 'credits').map(l => l.text).join(' '),
};

// Metadata
export const scriptMeta = {
  totalDuration: '3:30',
  totalFrames: 6300,
  fps: 30,
  wordCount: fullScript.split(' ').length,
  sceneCount: 9,
};
