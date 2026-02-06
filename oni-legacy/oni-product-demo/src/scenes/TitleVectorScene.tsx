/**
 * Title Scene - Vector Waves
 * Clean, minimal, calm
 * Abstract vector waves flowing smoothly
 */

import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';
import { WaveGrid } from '../components/reactbits';

export const TitleVectorScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animation phases
  const showONI = frame >= 45;
  const showTagline = frame >= 110;
  const showSubtitle = frame >= 170;

  // Smooth spring for logo
  const oniProgress = spring({
    frame: frame - 45,
    fps,
    config: { damping: 30, stiffness: 35, mass: 1.8 },
  });

  // Subtle glow pulse - very slow
  const glowPulse = interpolate(
    Math.sin(frame * 0.02),
    [-1, 1],
    [0.4, 0.7]
  );

  // Letter-by-letter animation for ONI
  const letterAnimations = ['O', 'N', 'I'].map((letter, i) => {
    const letterDelay = 45 + i * 10;
    const letterProgress = spring({
      frame: frame - letterDelay,
      fps,
      config: { damping: 25, stiffness: 80 },
    });
    const opacity = Math.max(0, letterProgress);
    const blur = interpolate(Math.max(0, letterProgress), [0, 1], [8, 0]);
    const y = interpolate(Math.max(0, letterProgress), [0, 1], [15, 0]);
    return { letter, opacity, blur, y };
  });

  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(180deg, #020406 0%, #040810 50%, #030608 100%)',
      }}
    >
      {/* Single clean wave layer */}
      <WaveGrid
        lineCount={10}
        color="#006699"
        secondaryColor="#004466"
        amplitude={30}
        speed={0.15}
        strokeWidth={1.2}
        showNodes={false}
        glow={true}
        glowIntensity={8}
      />

      {/* Soft vignette for focus */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(ellipse 70% 55% at 50% 50%,
            transparent 0%,
            rgba(2, 4, 6, 0.5) 60%,
            rgba(2, 4, 6, 0.9) 100%
          )`,
          pointerEvents: 'none',
        }}
      />

      {/* Content */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 20,
        }}
      >
        {/* ONI Logo */}
        {showONI && (
          <div
            style={{
              opacity: Math.max(0, oniProgress),
              transform: `scale(${0.95 + Math.max(0, oniProgress) * 0.05})`,
              filter: `drop-shadow(0 0 ${50 * glowPulse}px rgba(0, 100, 150, 0.4))`,
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {letterAnimations.map(({ letter, opacity, blur, y }, i) => (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  fontSize: 200,
                  fontWeight: 600,
                  fontFamily: "'Inter', 'Helvetica Neue', sans-serif",
                  letterSpacing: '0.06em',
                  background: `linear-gradient(180deg,
                    #ffffff 0%,
                    #d0e8f4 25%,
                    #80b8d0 60%,
                    #4090b0 100%
                  )`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  opacity,
                  filter: `blur(${blur}px)`,
                  transform: `translateY(${y}px)`,
                }}
              >
                {letter}
              </span>
            ))}
          </div>
        )}

        {/* The OSI of Mind */}
        {showTagline && (
          <div
            style={{
              opacity: interpolate(frame - 110, [0, 40], [0, 1], { extrapolateRight: 'clamp' }),
              transform: `translateY(${interpolate(frame - 110, [0, 40], [10, 0], { extrapolateRight: 'clamp' })}px)`,
            }}
          >
            <span
              style={{
                fontSize: 26,
                fontWeight: 300,
                letterSpacing: '0.3em',
                textTransform: 'uppercase',
                color: 'rgba(100, 170, 200, 0.9)',
              }}
            >
              The OSI of Mind
            </span>
          </div>
        )}

        {/* Introducing line */}
        {showSubtitle && (
          <div
            style={{
              opacity: interpolate(frame - 170, [0, 45], [0, 1], { extrapolateRight: 'clamp' }),
              transform: `translateY(${interpolate(frame - 170, [0, 45], [8, 0], { extrapolateRight: 'clamp' })}px)`,
              marginTop: 16,
            }}
          >
            <span
              style={{
                fontSize: 17,
                fontWeight: 300,
                letterSpacing: '0.12em',
                color: 'rgba(140, 190, 210, 0.75)',
              }}
            >
              introducing a unified neurosecurity stack
            </span>
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

export default TitleVectorScene;
