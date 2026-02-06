# Claude AI Instructions for ONI Video Production

> This file provides instructions for Claude when working on ONI demo videos using Remotion.
> **Read this file at the start of any video production session.**

---

## Quick Reference

| Resource | Location | Purpose |
|----------|----------|---------|
| **Main Video Component** | `src/ONIDemoVideo.tsx` | Video composition with all scenes and audio |
| **Scene Timestamps** | `src/data/oni-theme.ts` | Frame timing for all scenes |
| **Script Data** | `src/data/script.ts` | Voiceover text synced to frames |
| **Sound Design Doc** | `MAIN/legacy-core/resources/sound-engineering/ONI_VIDEO_SOUND_DESIGN.md` | Audio psychology and specs |
| **Audio Files** | `public/audio/` | All voiceovers and sound effects |
| **Scene Components** | `src/scenes/` | Individual scene React components |

---

## Video Configuration

```typescript
// From src/data/oni-theme.ts
export const videoConfig = {
  fps: 30,
  width: 1920,
  height: 1080,
  durationInSeconds: 236, // 3:56
  durationInFrames: 7080, // 3:56 at 30fps
};
```

**Frame-Time Conversion:**
- `frame = seconds * 30`
- `seconds = frame / 30`
- Example: 3:44 = 224 seconds = 6720 frames

---

## Video-Audio Sync Guidelines (CRITICAL)

> **The most important aspect of video production is keeping visuals synchronized with audio.**

### 1. Frame-Based Timing System

All timing in Remotion uses frames, not seconds. Always convert:

```typescript
// Converting time to frames
const fps = 30;
const timeInSeconds = 15;
const frame = timeInSeconds * fps; // 450

// Scene timestamps define when each scene starts/ends
export const sceneTimestamps = {
  coldOpen: { start: 0, end: 8 * 30 },      // 0:00-0:08
  title: { start: 8 * 30, end: 15 * 30 },   // 0:08-0:15
  // ... etc
};
```

### 2. Voiceover Sync Strategy

**Step 1: Generate voiceover audio files**
```bash
# Use ElevenLabs API to generate voiceover
# Save to public/audio/vo-[scene].mp3
```

**Step 2: Measure actual audio duration**
```bash
# Get duration of audio file
ffprobe -i public/audio/vo-scene.mp3 -show_entries format=duration -v quiet -of csv="p=0"
```

**Step 3: Sync audio to scene**
```typescript
// Audio starts relative to scene start
<Sequence from={scene.start + offsetFrames}>
  <Audio src={staticFile("audio/vo-scene.mp3")} />
</Sequence>
```

**Step 4: Match visual animations to voiceover timing**
```typescript
// In scene component, use frame-based phases
const frame = useCurrentFrame();

// Phase 1: First line of voiceover (frames 0-100)
const showPhase1 = frame >= 0 && frame < 100;

// Phase 2: Second line of voiceover (frames 100-200)
const showPhase2 = frame >= 100 && frame < 200;
```

### 3. Audio Layering Rules

**Volume Hierarchy (loudest to quietest):**
1. Voiceover: 85-100%
2. Sound effects: 40-60%
3. Ambient/music: 25-40%

**Ducking:** When voiceover plays, reduce ambient by 25%:
```typescript
<Audio
  src={staticFile("audio/ambient.mp3")}
  volume={(f) => {
    const voiceoverActive = f >= voStart && f <= voEnd;
    return voiceoverActive ? 0.26 : 0.35; // 25% reduction
  }}
/>
```

### 4. Visual-Audio Phase Matching

**Document phases in script.ts:**
```typescript
export const script: ScriptLine[] = [
  {
    scene: 'problem',
    text: "Brain-computer interfaces are here.",
    startFrame: 470,  // When this line starts
    endFrame: 570,    // When this line ends
    startTime: '0:15',
  },
  // ...
];
```

**Match scene animations to script phases:**
```typescript
// In ProblemScene.tsx
const phase = frame < 100 ? 1 :
              frame < 200 ? 2 :
              frame < 420 ? 3 :
              frame < 540 ? 4 : 5;

// Phase 1 text appears when voiceover says "BCIs are here"
{phase >= 1 && <Text>Brain-computer interfaces are here.</Text>}
```

### 5. Fade Transitions

**Prevent audio bleed between scenes:**
```typescript
<Sequence from={scene.start} durationInFrames={scene.end - scene.start}>
  <Audio
    src={staticFile("audio/vo-scene.mp3")}
    volume={(f) => {
      const duration = scene.end - scene.start;
      // Fade out over last 30 frames (1 second)
      return interpolate(f, [duration - 30, duration], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
    }}
  />
</Sequence>
```

### 6. Testing Sync

**Preview specific frames:**
```bash
# Preview at specific frame
npx remotion preview --frame=450

# Render specific frame range
npx remotion render ONIDemoVideo out.mp4 --frames=400-500
```

**Check audio timing:**
1. Render a short section
2. Watch with audio
3. Note any visual-audio misalignment
4. Adjust frame offsets in code

---

## Scene Structure Pattern

Each scene follows this pattern:

```typescript
// src/scenes/[SceneName].tsx
export const SceneName: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase timing (synced to voiceover)
  const phase = frame < 100 ? 1 : frame < 200 ? 2 : 3;

  // Animations using spring/interpolate
  const opacity = spring({ frame, fps, config: { damping: 20 } });

  return (
    <AbsoluteFill style={{ background: colors.gradients.background }}>
      {/* Phase-based content */}
      {phase >= 1 && <Element1 />}
      {phase >= 2 && <Element2 />}
    </AbsoluteFill>
  );
};
```

---

## Audio File Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Voiceover | `vo-[scene].mp3` | `vo-problem.mp3` |
| Voiceover (character) | `vo-[scene]-[voice].mp3` | `vo-finale-lily.mp3` |
| Sound effect | `[description].mp3` | `boot-chime.mp3` |
| Ambient | `ambient-[type].mp3` | `ambient-tech.mp3` |

---

## ElevenLabs Voice Reference

### Primary Narrator: Jay Wayne
- **Voice ID:** `8Ln42OXYupYsag45MAUy`
- **Settings:** `{ stability: 0.5, similarity_boost: 0.75, style: 0.5, use_speaker_boost: true }`
- **Character:** Authoritative, professorial

### Finale Voice: Lily (British)
- **Voice ID:** `pFZP5JQG7iQjIQuC4Bku`
- **Bold Settings:** `{ stability: 0.35, similarity_boost: 0.85, style: 0.6, use_speaker_boost: true }`
- **Encouraging Settings:** `{ stability: 0.45, similarity_boost: 0.75, style: 0.5, use_speaker_boost: true }`
- **Character:** Strong, protective, intelligent

---

## Sound Design Principles

### Harmonic Progression (4th → 5th → Major)

Used at intro and closing for bookend effect:

```
Ding 1 (Perfect 4th) → Ding 2 (Perfect 5th) → Boot Chime (Major)
     "Question"            "Answer coming"         "Resolution"
```

### 60 BPM Pulse

Matches resting heart rate for calm focus:
- Activates parasympathetic nervous system
- Creates receptive state for information

### Frequency-Emotion Mapping

| Frequency | Feeling | Use |
|-----------|---------|-----|
| 20-80Hz | Presence, power | Pulse base |
| 80-250Hz | Warmth, safety | Ambient |
| 500Hz-2kHz | Clarity | Voiceover |
| 2-6kHz | Excitement | Chimes |

---

## Common Tasks

### Add New Voiceover

1. Generate audio with ElevenLabs
2. Save to `public/audio/vo-[scene].mp3`
3. Measure duration: `ffprobe -i file.mp3 -show_entries format=duration`
4. Add Sequence in `ONIDemoVideo.tsx`:
   ```typescript
   <Sequence from={scene.start + offset}>
     <Audio src={staticFile("audio/vo-scene.mp3")} />
   </Sequence>
   ```
5. Update `script.ts` with text and frame timing
6. Sync scene animations to voiceover phases

### Extend Video Duration

1. Update `videoConfig.durationInSeconds` and `durationInFrames` in `oni-theme.ts`
2. Adjust final scene's `end` timestamp
3. Update `Root.tsx` composition duration
4. Verify all audio fades complete before new end

### Add Voice-Reactive Elements

```typescript
// Calculate voice intensity based on frame timing
const voiceIntensity = (() => {
  const voiceActive = frame >= voStart && frame <= voEnd;
  if (voiceActive) {
    const t = (frame - voStart) / (voEnd - voStart);
    const pulse = Math.sin(frame * 0.3) * 0.3 + 0.7;
    const envelope = Math.sin(t * Math.PI);
    return pulse * envelope;
  }
  return 0;
})();

// Apply to visual element
<div style={{ transform: `scale(${1 + voiceIntensity * 0.15})` }} />
```

---

## Troubleshooting

### Audio Not Playing
- Check file exists in `public/audio/`
- Verify `staticFile()` path is correct
- Check volume is > 0

### Visual-Audio Out of Sync
- Verify scene timestamps in `oni-theme.ts`
- Check Sequence `from` values
- Measure actual audio duration vs expected

### Choppy Playback
- Reduce concurrent audio tracks
- Simplify animations
- Render instead of preview for accurate timing

---

## File Structure

```
MAIN/legacy-core/oni-product-demo/
├── CLAUDE.md                 # This file
├── public/
│   └── audio/                # All audio files
│       ├── vo-*.mp3          # Voiceovers
│       ├── ambient-*.mp3     # Ambient sounds
│       └── *.mp3             # Sound effects
├── src/
│   ├── ONIDemoVideo.tsx      # Main composition
│   ├── Root.tsx              # Remotion root
│   ├── data/
│   │   ├── oni-theme.ts      # Config, colors, timestamps
│   │   └── script.ts         # Voiceover text/timing
│   ├── scenes/               # Scene components
│   │   ├── ColdOpenScene.tsx
│   │   ├── TitleScene.tsx
│   │   ├── ProblemScene.tsx
│   │   ├── ONILayersAnimation.tsx
│   │   ├── CoherenceScene.tsx
│   │   ├── TARAScene.tsx
│   │   ├── AcademicScene.tsx
│   │   ├── CTAScene.tsx
│   │   └── CreditsScene.tsx
│   └── components/           # Shared components
│       ├── Particles.tsx
│       └── Watermark.tsx
└── package.json
```

---

*Version: 1.0*
*Last Updated: 2026-01-29*
*Created for: ONI Framework Demo Video Production*
