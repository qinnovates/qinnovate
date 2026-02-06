# ONI Framework Product Demo

<video src="ONIDemoVideo.mp4" controls width="100%"></video>

A 3:30 professional marketing video for the ONI (Open Neurosecurity Interoperability) Framework, built with [Remotion](https://www.remotion.dev/) — video as code.

## Quick Start

```bash
# Install dependencies
npm install

# Start Remotion Studio (development preview)
npm run dev

# Render full video (1080p)
npx remotion render ONIDemoVideo out/ONI-Demo-1080p.mp4

# Render 720p for web
npx remotion render ONIDemoVideo out/ONI-Demo-720p.mp4 --scale=0.67
```

## Project Structure

```
oni-demo-video/
├── src/
│   ├── Root.tsx                # Remotion composition config
│   ├── ONIDemoVideo.tsx        # Main video composition
│   ├── components/             # Reusable animation components
│   │   ├── TextReveal.tsx      # Text fade-in animations
│   │   ├── TitleCard.tsx       # ONI logo title card
│   │   ├── LayerStack.tsx      # 14-layer visualization
│   │   └── CoherenceGauge.tsx  # Coherence metric display
│   ├── scenes/                 # Video scenes (9 total)
│   │   ├── ColdOpenScene.tsx   # 0:00-0:08
│   │   ├── TitleScene.tsx      # 0:08-0:15
│   │   ├── ProblemScene.tsx    # 0:15-0:40
│   │   ├── LayersScene.tsx     # 0:40-1:20
│   │   ├── CoherenceScene.tsx  # 1:20-1:50
│   │   ├── TARAScene.tsx       # 1:50-2:25
│   │   ├── AcademicScene.tsx   # 2:25-2:50
│   │   ├── CTAScene.tsx        # 2:50-3:15
│   │   └── CreditsScene.tsx    # 3:15-3:30
│   └── data/
│       ├── oni-theme.ts        # Colors, typography, timing
│       └── script.ts           # Voiceover script with timestamps
├── public/
│   ├── assets/                 # ONI logos and diagrams
│   ├── recordings/             # Screen recordings (to add)
│   └── audio/                  # Voiceover and music (to add)
└── output/                     # Rendered videos
```

## Video Scenes

| Scene | Time | Duration | Description |
|-------|------|----------|-------------|
| Cold Open | 0:00-0:08 | 8s | BCI headlines montage |
| Title | 0:08-0:15 | 7s | ONI Banner reveal |
| Problem | 0:15-0:40 | 25s | "BCIs exist, no standards" |
| 14-Layer Model | 0:40-1:20 | 40s | Hourglass + layer stack |
| Coherence Metric | 1:20-1:50 | 30s | Formula + gauge |
| TARA Stack | 1:50-2:25 | 35s | Dashboard features |
| Academic | 2:25-2:50 | 25s | Citations |
| Call to Action | 2:50-3:15 | 25s | pip install, GitHub |
| Credits | 3:15-3:30 | 15s | Author, license |

## Adding Audio

### Voiceover (ElevenLabs)
1. Generate audio from `src/data/script.ts`
2. Request word-level timestamps
3. Save to `public/audio/voiceover.mp3`
4. Uncomment Audio import in `ONIDemoVideo.tsx`

### Background Music (SOUNDRAW)
1. Generate tech/ambient track
2. Save to `public/audio/background.mp3`
3. Uncomment Audio with volume={0.3}

## Adding Screen Recordings

Record these demos at 1080p, 30fps:
- `public/recordings/coherence-playground.mp4` - Drag sliders
- `public/recordings/layer-explorer.mp4` - Click layers
- `public/recordings/tara-dashboard.mp4` - Overview
- `public/recordings/tara-topology.mp4` - 3D brain
- `public/recordings/tara-attack-sim.mp4` - Pew-pew

## Theme Colors

```typescript
// From oni-theme.ts
colors.primary.dark    // #0a0e1a - Background
colors.primary.accent  // #00e5ff - Cyan accent
colors.gateway.L8      // #ff9800 - Neural Gateway
colors.silicon.L1      // #2196f3 - Silicon layers
colors.biology.L9      // #4caf50 - Biology layers
```

## Development Tips

- Use `ONIDemoPreview` composition for faster iteration (30s preview)
- Hot reload works in Remotion Studio
- Spring animations from `remotion` for smooth physics
- All scenes are in their own files for easy editing

## Rendering

```bash
# Full quality 1080p
npx remotion render ONIDemoVideo out/ONI-Demo-1080p.mp4 --codec=h264

# Web optimized 720p
npx remotion render ONIDemoVideo out/ONI-Demo-720p.mp4 --scale=0.67

# Specific frame range (for testing)
npx remotion render ONIDemoVideo out/test.mp4 --frames=0-300
```

## License

Apache 2.0 - Same as ONI Framework

---

*Built with Remotion and Claude Code*
