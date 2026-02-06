/**
 * Cold Open Scene - Dramatic BCI headlines montage
 * Features: Smooth transitions, blur effects, clean typography
 */

import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import { Starfield } from '../components/Particles';
import { NeuralFlow } from '../components/NeuralFlow';
import { WaveGrid } from '../components/reactbits';
import { colors, typography } from '../data/oni-theme';

// Headlines for the cold open montage - alternating hope and tension
const headlines = [
  { text: 'Neuralink receives FDA approval', source: '2024', accent: colors.primary.accent },
  { text: 'Synchron achieves thought-to-text', source: '2024', accent: colors.silicon.L3 },
  { text: 'But security standards remain undefined', source: 'Research Gap', accent: colors.security.warning },
  { text: 'Who is protecting your neural data?', source: 'The Question', accent: colors.security.danger },
];

export const ColdOpenScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Calculate which headline to show (slower pacing)
  const headlineIndex = Math.min(
    Math.floor(frame / 60),
    headlines.length - 1
  );

  // Subtle camera drift for depth
  const cameraX = Math.sin(frame * 0.01) * 5;
  const cameraY = Math.cos(frame * 0.008) * 3;

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at center, ${colors.primary.main} 0%, ${colors.primary.dark} 70%)`,
        transform: `translate(${cameraX}px, ${cameraY}px)`,
      }}
    >
      {/* Starfield background - subtle depth */}
      <Starfield starCount={200} speed={0.3} />

      {/* Wave grid - fades in 5 seconds before transition for smooth continuity */}
      {frame > 90 && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            opacity: interpolate(frame, [90, 180], [0, 0.15], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }),
          }}
        >
          <WaveGrid
            lineCount={6}
            color="#006688"
            secondaryColor="#004455"
            amplitude={20}
            speed={0.06}
            strokeWidth={0.8}
            showNodes={false}
            glow={true}
            glowIntensity={5}
          />
        </div>
      )}

      {/* Gradient overlay for depth */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(ellipse at center, transparent 20%, rgba(0,0,0,0.6) 100%)',
          pointerEvents: 'none',
        }}
      />

      {/* Main content */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
        }}
      >
        {/* Headlines with smooth transitions */}
        {headlines.map((headline, index) => {
          const isActive = index === headlineIndex;
          const startFrame = index * 60;
          const localFrame = frame - startFrame;

          // Smooth entry animation
          const entryProgress = spring({
            frame: localFrame,
            fps,
            config: { damping: 25, stiffness: 80 },
          });

          // Smooth exit animation
          const exitStart = 45;
          const exitProgress = localFrame > exitStart
            ? spring({
                frame: localFrame - exitStart,
                fps,
                config: { damping: 30, stiffness: 100 },
              })
            : 0;

          // Combined opacity
          const opacity = interpolate(
            Math.max(0, entryProgress) - Math.max(0, exitProgress),
            [0, 1],
            [0, 1]
          );

          // Subtle scale and blur
          const scale = interpolate(
            Math.max(0, entryProgress),
            [0, 1],
            [0.95, 1]
          );

          const blur = interpolate(
            Math.max(0, entryProgress),
            [0, 1],
            [10, 0]
          );

          const y = interpolate(
            Math.max(0, entryProgress),
            [0, 1],
            [40, 0]
          ) + interpolate(
            Math.max(0, exitProgress),
            [0, 1],
            [0, -30]
          );

          if (!isActive && localFrame < 0) return null;
          if (localFrame > 75) return null;

          return (
            <div
              key={index}
              style={{
                position: 'absolute',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 24,
                opacity: Math.max(0, opacity),
                transform: `scale(${scale}) translateY(${y}px)`,
                filter: `blur(${blur}px)`,
              }}
            >
              {/* Source tag with accent color */}
              <div
                style={{
                  fontSize: typography.fontSize.small,
                  color: headline.accent,
                  fontWeight: 500,
                  letterSpacing: '0.3em',
                  textTransform: 'uppercase',
                  opacity: 0.9,
                }}
              >
                {headline.source}
              </div>

              {/* Main headline */}
              <div
                style={{
                  fontSize: 52,
                  fontWeight: 600,
                  color: colors.text.primary,
                  textAlign: 'center',
                  maxWidth: 900,
                  lineHeight: 1.3,
                  letterSpacing: '-0.02em',
                }}
              >
                "{headline.text}"
              </div>

              {/* Accent line */}
              <div
                style={{
                  width: interpolate(Math.max(0, entryProgress), [0, 1], [0, 120]),
                  height: 2,
                  background: `linear-gradient(90deg, transparent, ${headline.accent}, transparent)`,
                  marginTop: 8,
                }}
              />
            </div>
          );
        })}

        {/* Neural flow at bottom - reacts to tension */}
        <div
          style={{
            position: 'absolute',
            bottom: 120,
            opacity: 0.5,
          }}
        >
          <NeuralFlow
            state={frame > 120 ? 'reactive' : 'resting'}
            width={700}
            height={50}
            intensity={0.4}
          />
        </div>
      </div>

      {/* Subtle vignette */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          boxShadow: 'inset 0 0 200px rgba(0,0,0,0.4)',
          pointerEvents: 'none',
        }}
      />

      {/* Progress indicator dots */}
      <div
        style={{
          position: 'absolute',
          bottom: 50,
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: 12,
        }}
      >
        {headlines.map((_, i) => {
          const isActive = i === headlineIndex;
          const dotProgress = spring({
            frame: frame - i * 60,
            fps,
            config: { damping: 20, stiffness: 100 },
          });

          return (
            <div
              key={i}
              style={{
                width: isActive ? 24 : 8,
                height: 8,
                borderRadius: 4,
                background: isActive
                  ? colors.primary.accent
                  : `${colors.text.muted}44`,
                opacity: Math.max(0.3, dotProgress),
                transition: 'width 0.3s ease',
              }}
            />
          );
        })}
      </div>

      {/* Top gradient */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 100,
          background: `linear-gradient(${colors.primary.dark}, transparent)`,
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};
