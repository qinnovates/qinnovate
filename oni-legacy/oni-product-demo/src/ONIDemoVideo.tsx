import { AbsoluteFill, Audio, Sequence, staticFile, interpolate } from "remotion";
import { colors, sceneTimestamps } from "./data/oni-theme";

// Scene components
import { ColdOpenScene } from "./scenes/ColdOpenScene";
import { TitleScene } from "./scenes/TitleScene";
import { ProblemScene } from "./scenes/ProblemScene";
import { LayersScene } from "./scenes/ONILayersAnimation";
import { CoherenceScene } from "./scenes/CoherenceScene";
import { TARAScene } from "./scenes/TARAScene";
import { AcademicScene } from "./scenes/AcademicScene";
import { CTAScene } from "./scenes/CTAScene";
import { CreditsScene } from "./scenes/CreditsScene";

// Persistent components
import { Watermark } from "./components/Watermark";

export const ONIDemoVideo: React.FC = () => {
  const { coldOpen, title, problem, layers, coherence, tara, academic, cta, credits } = sceneTimestamps;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.primary.dark,
        fontFamily: "'Inter', sans-serif",
      }}
    >
      {/* Ambient tech atmosphere - starts immediately, dips 25% at 9s, fades out before narration */}
      <Sequence from={0} durationInFrames={problem.start + 20}>
        <Audio
          src={staticFile("audio/ambient-tech.mp3")}
          volume={(f) => interpolate(
            f,
            [0, 260, 290, problem.start - 70, problem.start + 20],
            [0.35, 0.35, 0.26, 0.26, 0],
            { extrapolateRight: "clamp" }
          )}
        />
      </Sequence>

      {/* Original pulse - deeper, starts first, fades out as smooth pulse takes over */}
      <Sequence from={0} durationInFrames={210}>
        <Audio
          src={staticFile("audio/original-pulse.mp3")}
          volume={(f) => interpolate(
            f,
            [0, 30, 150, 210],
            [0, 0.7, 0.7, 0],
            { extrapolateRight: "clamp" }
          )}
        />
      </Sequence>

      {/* Smooth pulse - crossfades in, dips at 9s with ambient, continues to boot chime */}
      <Sequence from={150} durationInFrames={422 - 150}>
        <Audio
          src={staticFile("audio/curiosity-pulse.mp3")}
          volume={(f) => {
            const duration = 422 - 150;
            // f is relative to sequence start (frame 150)
            // 9s = frame 270, so relative frame = 270 - 150 = 120
            // Dip from 0.8 to 0.6 at 9s, matching ambient dip
            return interpolate(
              f,
              [0, 60, 110, 140, duration - 20, duration],
              [0, 0.8, 0.8, 0.6, 0.6, 0],
              { extrapolateRight: "clamp" }
            );
          }}
        />
      </Sequence>

      {/* Ding tone at 9.11s - perfect 4th interval, sets up the chime */}
      <Sequence from={273}>
        <Audio src={staticFile("audio/ding-tone.mp3")} volume={0.5} />
      </Sequence>

      {/* Second ding tone at ~11s - perfect 5th interval, bridges to boot chime */}
      <Sequence from={330}>
        <Audio src={staticFile("audio/ding-tone-2.mp3")} volume={0.45} />
      </Sequence>

      {/* Boot chime - starts at 14.07s (frame 422), fades in gradually */}
      <Sequence from={422}>
        <Audio
          src={staticFile("audio/boot-chime.mp3")}
          volume={(f) => interpolate(
            f,
            [0, 45],
            [0, 0.6],
            { extrapolateRight: "clamp" }
          )}
        />
      </Sequence>

      {/* Scene 0: Cold Open (0:00-0:08) - NO VOICEOVER, visuals only */}
      <Sequence from={coldOpen.start} durationInFrames={coldOpen.end - coldOpen.start}>
        <ColdOpenScene />
      </Sequence>

      {/* Scene 1: Title (0:08-0:15) - NO VOICEOVER, visuals only */}
      <Sequence from={title.start} durationInFrames={title.end - title.start}>
        <TitleScene />
      </Sequence>

      {/* Scene 2: Problem Statement (0:15-0:40) */}
      <Sequence from={problem.start} durationInFrames={problem.end - problem.start}>
        <ProblemScene />
      </Sequence>

      {/* Problem scene voiceover - single continuous track */}
      {/* Starts at frame 20 when "BCI are here" text first appears */}
      <Sequence from={problem.start + 20}>
        <Audio src={staticFile("audio/vo-problem.mp3")} />
      </Sequence>

      {/* Scene 3: 14-Layer Model (0:40-1:20) */}
      <Sequence from={layers.start} durationInFrames={layers.end - layers.start}>
        <LayersScene />
      </Sequence>
      {/* Layers voiceover with fade-out to prevent bleed into coherence */}
      <Sequence from={layers.start} durationInFrames={layers.end - layers.start}>
        <Audio
          src={staticFile("audio/vo-layers.mp3")}
          volume={(f) => {
            const duration = layers.end - layers.start;
            return interpolate(f, [duration - 30, duration], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
          }}
        />
      </Sequence>

      {/* Scene 4: Coherence Metric (1:20-1:50) */}
      <Sequence from={coherence.start} durationInFrames={coherence.end - coherence.start}>
        <CoherenceScene />
      </Sequence>
      {/* Voiceover starts 1s after scene to create breathing room */}
      <Sequence from={coherence.start + 30} durationInFrames={coherence.end - coherence.start - 30}>
        <Audio src={staticFile("audio/vo-coherence.mp3")} />
      </Sequence>

      {/* Scene 5: TARA Stack (1:50-2:25) */}
      <Sequence from={tara.start} durationInFrames={tara.end - tara.start}>
        <TARAScene />
      </Sequence>
      <Sequence from={tara.start} durationInFrames={tara.end - tara.start}>
        <Audio src={staticFile("audio/vo-tara.mp3")} />
      </Sequence>

      {/* Scene 6: Academic Foundation (2:25-2:50) */}
      <Sequence from={academic.start} durationInFrames={academic.end - academic.start}>
        <AcademicScene />
      </Sequence>
      <Sequence from={academic.start} durationInFrames={academic.end - academic.start}>
        <Audio src={staticFile("audio/vo-academic.mp3")} />
      </Sequence>

      {/* Scene 7: Call to Action (2:50-3:15) */}
      <Sequence from={cta.start} durationInFrames={cta.end - cta.start}>
        <CTAScene />
      </Sequence>
      <Sequence from={cta.start} durationInFrames={cta.end - cta.start}>
        <Audio src={staticFile("audio/vo-cta.mp3")} />
      </Sequence>

      {/* Scene 8: Credits (3:09-3:34) */}
      <Sequence from={credits.start} durationInFrames={credits.end - credits.start}>
        <CreditsScene />
      </Sequence>
      <Sequence from={credits.start} durationInFrames={credits.end - credits.start}>
        <Audio src={staticFile("audio/vo-credits.mp3")} />
        {/* Wind through open door - bright morning, new beginnings */}
        <Audio src={staticFile("audio/wind-door-morning.mp3")} volume={0.5} />
      </Sequence>

      {/* Finale Sound Effects - Door opening moment (frame 400 relative to credits) */}
      {/* Ascending chord - starts when door begins to open */}
      <Sequence from={credits.start + 395}>
        <Audio
          src={staticFile("audio/finale-ascend.mp3")}
          volume={(f) => interpolate(f, [0, 15, 60, 90], [0, 0.4, 0.4, 0], {
            extrapolateRight: "clamp",
          })}
        />
      </Sequence>

      {/* Shimmering bells - layers in as door opens wider */}
      <Sequence from={credits.start + 420}>
        <Audio
          src={staticFile("audio/finale-shimmer.mp3")}
          volume={(f) => interpolate(f, [0, 20, 80, 120], [0, 0.35, 0.25, 0], {
            extrapolateRight: "clamp",
          })}
        />
      </Sequence>

      {/* Female British voiceover - "Welcome to the OSI of Mind... This is ONI..." */}
      {/* Starts when "Welcome to" text appears (frame 460) */}
      <Sequence from={credits.start + 460}>
        <Audio
          src={staticFile("audio/vo-finale-lily.mp3")}
          volume={0.85}
        />
      </Sequence>

      {/* ═══ Orchestrated Closing Sequence ═══ */}
      {/* Mirrors the intro's 4th → 5th → Major progression */}
      {/* Voiceover ends at ~frame 665, then the closing begins */}

      {/* Ding tone 1 - Perfect 4th, signals closing */}
      <Sequence from={credits.start + 670}>
        <Audio src={staticFile("audio/ding-tone.mp3")} volume={0.55} />
      </Sequence>

      {/* Ding tone 2 - Perfect 5th, builds to resolution */}
      <Sequence from={credits.start + 700}>
        <Audio src={staticFile("audio/ding-tone-2.mp3")} volume={0.5} />
      </Sequence>

      {/* Boot chime - Major resolution, final closure */}
      <Sequence from={credits.start + 725}>
        <Audio
          src={staticFile("audio/boot-chime.mp3")}
          volume={(f) => interpolate(f, [0, 30, 60, 90], [0, 0.6, 0.5, 0], {
            extrapolateRight: "clamp",
          })}
        />
      </Sequence>

      {/* ═══ Ambient + Pulse Reprise - Bookends the video ═══ */}
      {/* Same ambient + pulse from intro returns, creating satisfying closure */}

      {/* Ambient tech atmosphere - fades in after chime */}
      <Sequence from={credits.start + 760} durationInFrames={credits.end - credits.start - 760}>
        <Audio
          src={staticFile("audio/ambient-tech.mp3")}
          volume={(f) => {
            const duration = credits.end - credits.start - 760;
            return interpolate(
              f,
              [0, 60, duration - 90, duration],
              [0, 0.30, 0.30, 0],
              { extrapolateRight: "clamp" }
            );
          }}
        />
      </Sequence>

      {/* Curiosity pulse - the 60 BPM heartbeat returns */}
      <Sequence from={credits.start + 780} durationInFrames={credits.end - credits.start - 780}>
        <Audio
          src={staticFile("audio/curiosity-pulse.mp3")}
          volume={(f) => {
            const duration = credits.end - credits.start - 780;
            return interpolate(
              f,
              [0, 45, duration - 90, duration],
              [0, 0.5, 0.5, 0],
              { extrapolateRight: "clamp" }
            );
          }}
        />
      </Sequence>

      {/* ═══ Final CTA at 3:39 ═══ */}
      {/* "So... what are you waiting for?" - then 10s ambient, then cut */}
      <Sequence from={credits.start + 1050}>
        <Audio src={staticFile("audio/vo-finale-cta.mp3")} volume={0.9} />
      </Sequence>

      {/* Persistent watermark - © 2026 Kevin Qi • ONI Neural Security Stack™ */}
      <Watermark position="bottom-right" opacity={0.6} fadeInDelay={60} />
    </AbsoluteFill>
  );
};
