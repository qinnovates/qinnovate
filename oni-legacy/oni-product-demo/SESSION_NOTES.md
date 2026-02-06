# ONI Demo Video - Session Notes
**Date:** 2026-01-26
**Session Summary:** Major video scene updates and script revisions

---

## COMPLETED WORK

### 1. TitleScene.tsx
- Added orbiting electron animation around ONI letters
- Electron orbits horizontally, dips into the "O" center
- Blue electron with glowing trail effect
- Changed ONI text to solid white (removed gradient)
- Updated tagline: "OPEN **NEURO**SECURITY INTEROPERABILITY" (NEURO is bold)
- Removed "No brains left behind" tagline

### 2. ProblemScene.tsx
- Made "ONI Framework" full-screen reveal
- ONI and Framework same size (140px)
- Added left-to-right animated gradient on ONI (darker blue → white)
- Gradient flows/animates to become bluer over time
- Staggered reveal: "Introducing" → "ONI Framework" → typing effect for bottom text
- Bottom text: "A unified neurosecurity stack for the next era of computing"

### 3. LayersScene.tsx (Complete Rewrite)
- Intro text: "14 layers spanning silicon to synapse"
- Phase 1 (frames 0-150): Intro animation
- Phase 2 (frames 150-450): Pan through L1-L7 with OSI model labels
  - Header: "SILICON LAYERS (L1-L7) — CLASSICAL OSI MODEL"
  - Each layer shows OSI mapping (Physical, Data Link, Network, etc.)
- Phase 3 (frames 450-750): L8 Neural Gateway zoom with dramatic glow
  - Header: "★ NEURAL GATEWAY — THE BRIDGE ★"
  - Scale up to 1.8x with pulsing glow effect
- Phase 4 (frames 750-1050): Pan through L9-L14 biology layers
  - Header: "BIOLOGY LAYERS (L9-L14) — NEURAL PROCESSING"
- Phase 5 (frames 1050-1200): Full stack view

### 4. CoherenceScene.tsx
- Fixed coherence formula to: **Cₛ = e^(−(σ²φ + σ²τ + σ²γ))**
- Updated component cards to show: σ²φ, σ²τ, σ²γ (variance notation)
- Added phase transitions:
  - Coherence section: frames 0-500
  - Scale-Frequency section: frames 500+
- Added `coherenceFadeOut` for smooth transitions between phases
- Added Scale-Frequency Invariant visualization:
  - Title: "Scale-Frequency Invariant"
  - Formula: f × S ≈ k
  - Animated bars showing Scale (10→1000), Frequency (100→1 Hz)
  - k constant stays ~1000 (invariant indicator)
- Fixed interactive demo callout animation timing

### 5. CoherenceGauge.tsx
- Formula correct: `C<sub>s</sub> = e<sup>−(σ²φ + σ²τ + σ²γ)</sup>`
- Updated component breakdown to show variance symbols (σ²φ, σ²τ, σ²γ)
- Values now show inverse relationship with coherence

### 6. script.ts (Narration Script)
- Updated coherence section with threshold/defense mechanism language
- Added Scale-Frequency narration
- Removed "All open source. All verifiable." from TARA section
- Extended "...and you" line timing for emphasis (frames 5460-5700)
- Adjusted all frame timings for ~3:53 runtime

---

## TODO - PENDING WORK

### Completed (2026-01-28)

1. **Coherence Threshold Defense Visualization** ✅
   - [x] Set threshold value to 0.65
   - [x] Add visual when coherence drops below threshold (shield icon changes)
   - [x] Show shield/alert animation for defense mechanism activation
   - [x] Include examples: MRI interference, electromagnetic disruption, injection attacks
   - [x] Added threshold line to CoherenceGauge component
   - [x] Coherence animation now drops to 0.45 at frame 320, triggers breach

2. **"...and you" Animation Enhancement** ✅ (Already Done)
   - [x] Implemented slow pan-in effect (scale 0.85→1 + translateY)
   - [x] Made text white with glow for emphasis
   - [x] Extended hold time for dramatic effect

3. **Remove TARA "100% open source" Text** ✅ (Already Done)
   - [x] Text was already removed from TARAScene.tsx
   - [x] Script already updated

4. **Header Text Update** ✅
   - [x] Changed Watermark: "ONI Framework™" → "ONI Neural Security Suite™"
   - [x] Matches GitHub Pages branding

5. **Scale-Frequency Detailed Visualization** ✅ (Already Done)
   - [x] Created dedicated visualization in CoherenceScene (frames 500+)
   - [x] Shows how f × S ≈ k works with animated bars
   - [x] Scale increases 10→1000, Frequency decreases 100→1 Hz, k stays ~1000

### Remaining Tasks

1. **Generate Voiceover**
   - [ ] Use ElevenLabs with voice "Adam" or "Rachel"
   - [ ] Request word-level timestamps for sync
   - [ ] Save to public/audio/voiceover.mp3

2. **Final Render**
   - [ ] Test all scenes in Remotion Studio
   - [ ] Render final MP4 at 1080p
   - [ ] Integrate with GitHub Pages

3. **Fix TypeScript Errors** (Non-blocking)
   - [ ] AnomalyDetectionViz.tsx: `typography.fontFamily.base` should be `typography.fontFamily.body`
   - [ ] Brain3D module missing
   - [ ] Unused variable warnings

---

## Session 2026-01-28 Updates

### Files Modified
- `src/scenes/CoherenceScene.tsx` - Added threshold defense visualization
- `src/components/CoherenceGauge.tsx` - Added threshold line support
- `src/components/Watermark.tsx` - Updated branding to "ONI Neural Security Suite™"
- `SESSION_NOTES.md` - Updated progress

### Threshold Defense Animation Details
- **Threshold**: Cₛ ≥ 0.65
- **Timeline**:
  - Frames 0-280: Normal coherence intro
  - Frame 280: Threshold demo begins
  - Frame 320: Coherence drops to 0.45 (breach!)
  - Frames 310-370: Attack type indicators cycle (MRI → EM → Injection)
  - Frame 325+: "Defense mechanisms ACTIVATED" message
  - Frame 400+: Recovery message shown
  - Frame 500: Transition to Scale-Frequency section

---

### Historical Reference - Files to Check for Threshold Values
- `/oni/neurosecurity/legacy-core/oni-framework/COHERENCE.md`
- `/oni/neurosecurity/legacy-core/oni-framework/ONI_LAYERS.md`
- `/oni/autodidactive/oni-academy/` (course materials)
- `/oni/docs/` (GitHub Pages source)
- `/oni/README.md`

---

## KEY FORMULAS (Verified Correct)

### Coherence Score
```
Cₛ = e^(−(σ²φ + σ²τ + σ²γ))

Where:
- σ²φ = Phase Variance (neural oscillation alignment)
- σ²τ = Timing Variance (temporal jitter precision)
- σ²γ = Frequency Variance (band-specific stability)
```

### Scale-Frequency Invariant
```
f × S ≈ k

Where:
- f = Frequency (Hz)
- S = Scale
- k = Invariant constant

As scale increases, frequency decreases proportionally.
The product remains constant - a fingerprint of healthy neural activity.
```

---

## GIT COMMANDS TO SAVE

Run these commands to commit all changes:

```bash
cd /Users/mac/Documents/PROJECTS/qinnovates/mindloft/main/MAIN/legacy-core/oni-product-demo

git add src/scenes/TitleScene.tsx
git add src/scenes/ProblemScene.tsx
git add src/scenes/LayersScene.tsx
git add src/scenes/CoherenceScene.tsx
git add src/components/CoherenceGauge.tsx
git add src/data/script.ts
git add SESSION_NOTES.md

git commit -m "ONI Demo Video: Major scene updates and script revisions

Scenes Updated:
- TitleScene: Orbiting electron, solid white ONI, bold NEURO tagline
- ProblemScene: Full-screen ONI Framework reveal with animated gradient
- LayersScene: Complete rewrite with L1-L14 animation, L8 Gateway emphasis
- CoherenceScene: Fixed formula, added Scale-Frequency visualization

Formula Corrections:
- Coherence: Cₛ = e^(−(σ²φ + σ²τ + σ²γ))
- Scale-Frequency: f × S ≈ k

Script Updates:
- Added threshold/defense mechanism narration
- Removed '100% open source' from TARA section
- Extended '...and you' for emphasis
- Adjusted timing to ~3:53 runtime

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

git push origin main
```

---

## NEXT SESSION CHECKLIST

1. [ ] Find coherence threshold value in docs
2. [ ] Implement threshold defense visualization
3. [ ] Update header to "ONI Neural Security Suite"
4. [ ] Create "...and you" pan-in animation
5. [ ] Remove TARA open source text from scene
6. [ ] Create detailed Scale-Frequency visualization
7. [ ] Test all scenes in Remotion Studio
8. [ ] Generate voiceover with ElevenLabs
9. [ ] Final render and GitHub Pages integration

---

*Notes created by Claude Opus 4.5 - Session 2026-01-26*

---

## Session 2026-01-29: VIDEO COMPLETE (v1.0)

**Status:** COMPLETE
**Final Duration:** 3:56 (7080 frames @ 30fps)

### Major Accomplishments

1. **All Voiceovers Generated**
   - Jay Wayne (Male, American) - All main narration
   - Lily (Female, British) - Finale welcome + CTA

2. **Complete Sound Design**
   - Intro: ambient + pulse → ding tones → boot chime
   - Credits: door opening effects + wind
   - Finale: orchestrated closing (4th → 5th → Major bookend)
   - Ambient + pulse reprise at end

3. **Credits Scene Finale**
   - Door opening effect with light rays
   - Voice-reactive waves (z-axis depth pulsing)
   - Renaissance text: "The Human-AI Renaissance In The Age of BCIs is Here"
   - Final CTA: "So... what are you waiting for?"

4. **Documentation Complete**
   - `CLAUDE.md` - Video production instructions for future sessions
   - `SESSION_NOTES.md` - Updated with full session history
   - `ONI_VIDEO_SOUND_DESIGN.md` - Complete audio documentation

### Audio Files Created (2026-01-29)

**Voiceovers:**
| File | Voice | Duration | Content |
|------|-------|----------|---------|
| `vo-problem.mp3` | Jay Wayne | ~25s | Problem statement |
| `vo-layers.mp3` | Jay Wayne | ~40s | 14-layer explanation |
| `vo-coherence.mp3` | Jay Wayne | ~30s | Coherence metric |
| `vo-tara.mp3` | Jay Wayne | ~35s | TARA platform |
| `vo-academic.mp3` | Jay Wayne | ~19s | Academic foundation |
| `vo-cta.mp3` | Jay Wayne | ~25s | Call to action |
| `vo-credits.mp3` | Jay Wayne | ~11s | Credits manifesto |
| `vo-finale-lily.mp3` | Lily (Bold) | ~7.94s | "Welcome to the OSI of Mind..." |
| `vo-finale-cta.mp3` | Lily (Encouraging) | ~1.81s | "So... what are you waiting for?" |

**Sound Effects:**
| File | Purpose |
|------|---------|
| `ambient-tech.mp3` | Atmospheric foundation |
| `original-pulse.mp3` | Deep 80Hz curiosity trigger |
| `curiosity-pulse.mp3` | 60 BPM sustained anticipation |
| `ding-tone.mp3` | Perfect 4th interval |
| `ding-tone-2.mp3` | Perfect 5th interval |
| `boot-chime.mp3` | Major resolution |
| `wind-door-morning.mp3` | Hopeful closing ambience |
| `finale-ascend.mp3` | Ascending chord (door opening) |
| `finale-shimmer.mp3` | Shimmering bells |

**Deprecated (not used in final):**
- `reactor-hum.mp3` - Too dark sounding
- `energy-pulse.mp3` - User preferred original sounds

### Voice Configuration Reference

**Jay Wayne (Primary):**
```json
{
  "voice_id": "8Ln42OXYupYsag45MAUy",
  "stability": 0.5,
  "similarity_boost": 0.75,
  "style": 0.5,
  "use_speaker_boost": true
}
```

**Lily (Bold - Finale Welcome):**
```json
{
  "voice_id": "pFZP5JQG7iQjIQuC4Bku",
  "stability": 0.35,
  "similarity_boost": 0.85,
  "style": 0.6,
  "use_speaker_boost": true
}
```

**Lily (Encouraging - Finale CTA):**
```json
{
  "voice_id": "pFZP5JQG7iQjIQuC4Bku",
  "stability": 0.45,
  "similarity_boost": 0.75,
  "style": 0.5,
  "use_speaker_boost": true
}
```

### Finale Sequence Timeline (Credits Scene)

| Frame | Time | Event |
|-------|------|-------|
| 0 | 3:09 | Credits scene starts |
| 400 | 3:22 | Door begins opening |
| 460 | 3:24 | Lily: "Welcome to the OSI of Mind..." |
| 660 | 3:31 | Text fades out |
| 670 | 3:31 | Ding tone 1 (Perfect 4th) |
| 700 | 3:32 | Ding tone 2 (Perfect 5th) |
| 720 | 3:33 | Lines/waves fade out |
| 725 | 3:33 | Boot chime (Major resolution) |
| 760 | 3:34 | Ambient + pulse reprise |
| 840 | 3:37 | Renaissance text appears |
| 1050 | 3:44 | Lily: "So... what are you waiting for?" |
| 1140 | 3:47 | Renaissance text fades |
| 1410 | 3:56 | Video ends |

### Iterations & Decisions

1. **Voice Settings:**
   - Standard → Bold → More Bold → Encouraging (for CTA)
   - Bold settings create dramatic, commanding delivery
   - Encouraging settings create warm, inviting delivery

2. **Finale Evolution:**
   - v1: Black hole collapse effect - REJECTED
   - v2: Spiral graphics into center - REJECTED
   - v3: Simple fade with Renaissance text - APPROVED

3. **Sound Design:**
   - Reactor hum rejected ("too dark")
   - Energy pulse rejected (preferred original)
   - Final: Reused intro sounds for bookend effect

### Files Modified

- `src/ONIDemoVideo.tsx` - Complete audio integration
- `src/scenes/CreditsScene.tsx` - Finale with voice-reactive waves
- `src/data/oni-theme.ts` - Extended to 3:56 (7080 frames)
- `src/data/script.ts` - Full script with frame timing
- `MAIN/legacy-core/resources/sound-engineering/ONI_VIDEO_SOUND_DESIGN.md` - Complete docs
- `MAIN/legacy-core/oni-product-demo/CLAUDE.md` - Video production instructions (NEW)
- `MAIN/legacy-core/oni-product-demo/SESSION_NOTES.md` - This file

### Video Production Pipeline (for future reference)

See `MAIN/legacy-core/oni-product-demo/CLAUDE.md` for complete instructions including:
- Frame-based timing system
- Voiceover sync strategy
- Audio layering rules
- Visual-audio phase matching
- Voice-reactive element implementation

---

## CHECKLIST COMPLETE

- [x] All scenes implemented
- [x] All voiceovers generated
- [x] Sound design complete
- [x] Video-audio sync verified
- [x] Finale sequence polished
- [x] Documentation complete
- [x] Claude instructions created
- [x] Session notes updated

---

## Credits

**Created by:** Kevin L. Qi / Qinnovate LLC
**AI Assistance:** Claude Opus 4.5 (Anthropic)
**Voice Generation:** ElevenLabs
**Video Framework:** Remotion

---

*Session completed: 2026-01-29*
*Video v1.0 COMPLETE*
