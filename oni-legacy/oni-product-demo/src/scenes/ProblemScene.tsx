/**
 * Problem Scene - Apple-quality production
 * Clean, minimal, impactful messaging
 */

import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { WaveGrid } from '../components/reactbits';

export const ProblemScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Apple-style ease
  const appleEase = (t: number) => {
    return t < 0.5
      ? 4 * t * t * t
      : 1 - Math.pow(-2 * t + 2, 3) / 2;
  };

  // Phase timing
  const phase1End = 90;    // "BCIs are here"
  const phase2Start = 100;
  const phase2End = 200;   // "Neurosecurity is..."
  const phase3Start = 220;
  const phase3End = 400;   // Problem words
  const phase4Start = 420;
  const phase4End = 520;   // "Until now"
  const phase5Start = 540; // "ONI Framework"
  const phase5End = 780;   // End of ONI Framework intro
  const phase6Start = 800; // Selling points

  // Wave opacity - subtle background
  const waveOpacity = interpolate(frame, [0, 40], [0, 0.3], {
    extrapolateRight: 'clamp',
  });

  // Phase 1: "BCIs are here"
  const bciRaw = interpolate(frame, [20, 70], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const bciProgress = appleEase(bciRaw);
  const bciOut = interpolate(frame, [phase1End, phase1End + 30], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Phase 2: "Neurosecurity today is..."
  const neuroRaw = interpolate(frame, [phase2Start, phase2Start + 50], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const neuroProgress = appleEase(neuroRaw);
  const neuroOut = interpolate(frame, [phase2End, phase2End + 20], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Phase 3: Problem words - staggered
  const problemWords = [
    { word: 'Fragmented.', delay: 0 },
    { word: 'Complex.', delay: 35 },
    { word: 'Inaccessible.', delay: 70 },
  ];
  const problemOut = interpolate(frame, [phase3End, phase3End + 20], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Phase 4: "Until now"
  const untilRaw = interpolate(frame, [phase4Start, phase4Start + 50], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const untilProgress = appleEase(untilRaw);
  const untilOut = interpolate(frame, [phase4End, phase4End + 20], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Phase 5: "ONI changes that"
  const oniRaw = interpolate(frame, [phase5Start, phase5Start + 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const oniProgress = appleEase(oniRaw);
  const phase5Out = interpolate(frame, [phase5End, phase5End + 30], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Staggered timing for Phase 5 elements
  const introTextProgress = appleEase(interpolate(frame - phase5Start, [0, 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }));

  const oniFrameworkProgress = appleEase(interpolate(frame - phase5Start, [35, 75], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }));

  // Phase 6: Selling points - emphasize "first" positioning
  const sellingPoints = [
    { text: 'Security-First', sub: 'The first BCI framework with protection at its foundation' },
    { text: 'Privacy-Native', sub: 'Your thoughts stay yours—by design, not by promise' },
    { text: 'The Standard', sub: 'The OSI model the neural era has been waiting for' },
  ];

  // Typing effect for bottom text
  const bottomTextStart = phase5Start + 70;
  const bottomText = "A unified neurosecurity stack for the next era of computing";
  const charsToShow = Math.floor(interpolate(frame - bottomTextStart, [0, 90], [0, bottomText.length], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }));
  const typedText = bottomText.slice(0, charsToShow);
  const showCursor = frame >= bottomTextStart && charsToShow < bottomText.length;

  // Animated gradient flow - slowly shifts bluer over time
  const gradientShift = interpolate(frame - phase5Start, [60, 260], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: '#000000',
      }}
    >
      {/* Subtle wave background */}
      <div style={{ opacity: waveOpacity * 0.5 }}>
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

      {/* Subtle center glow */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(ellipse 60% 50% at 50% 50%,
            rgba(0, 40, 60, 0.2) 0%,
            transparent 60%
          )`,
        }}
      />

      {/* Phase 1: BCIs are here */}
      {frame < phase2Start && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 16,
            opacity: bciProgress * bciOut,
            transform: `translateY(${interpolate(bciProgress, [0, 1], [30, 0])}px)`,
          }}
        >
          <div
            style={{
              fontSize: 56,
              fontWeight: 600,
              fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
              color: '#ffffff',
              letterSpacing: '-0.02em',
            }}
          >
            Brain-computer interfaces are here.
          </div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 400,
              fontFamily: "-apple-system, 'SF Pro Text', sans-serif",
              color: 'rgba(140, 180, 200, 0.7)',
              letterSpacing: '0.02em',
              opacity: interpolate(bciProgress, [0.5, 1], [0, 1]),
            }}
          >
            FDA approved. In clinical trials. Shipping to consumers.
          </div>
        </div>
      )}

      {/* Phase 2: Neurosecurity today is... */}
      {frame >= phase2Start && frame < phase3Start && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: neuroProgress * neuroOut,
            transform: `translateY(${interpolate(neuroProgress, [0, 1], [25, 0])}px)`,
          }}
        >
          <div
            style={{
              fontSize: 48,
              fontWeight: 500,
              fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
              color: 'rgba(180, 200, 220, 0.9)',
              letterSpacing: '-0.01em',
            }}
          >
            Neurosecurity today is...
          </div>
        </div>
      )}

      {/* Phase 3: Problem words */}
      {frame >= phase3Start && frame < phase4Start && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 24,
            opacity: problemOut,
          }}
        >
          {problemWords.map(({ word, delay }, i) => {
            const wordRaw = interpolate(frame - phase3Start - delay, [0, 40], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
            const wordProgress = appleEase(wordRaw);

            return (
              <div
                key={i}
                style={{
                  fontSize: 72,
                  fontWeight: 600,
                  fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
                  color: i === 2 ? '#ff6b6b' : '#ffffff',
                  letterSpacing: '-0.02em',
                  opacity: wordProgress,
                  transform: `translateY(${interpolate(wordProgress, [0, 1], [20, 0])}px)`,
                }}
              >
                {word}
              </div>
            );
          })}
        </div>
      )}

      {/* Phase 4: Until now */}
      {frame >= phase4Start && frame < phase5Start && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: untilProgress * untilOut,
            transform: `scale(${interpolate(untilProgress, [0, 1], [0.95, 1])})`,
          }}
        >
          <div
            style={{
              fontSize: 80,
              fontWeight: 700,
              fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
              color: '#ffffff',
              letterSpacing: '-0.02em',
            }}
          >
            Until now.
          </div>
        </div>
      )}

      {/* Phase 5: ONI Framework - Full screen with staggered reveal */}
      {frame >= phase5Start && frame < phase6Start && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: phase5Out,
          }}
        >
          {/* 1. "Introducing" appears first */}
          <div
            style={{
              fontSize: 24,
              fontWeight: 400,
              fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
              color: 'rgba(100, 180, 220, 0.9)',
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              opacity: introTextProgress,
              transform: `translateY(${interpolate(introTextProgress, [0, 1], [20, 0])}px)`,
              marginBottom: 30,
            }}
          >
            Introducing
          </div>
          {/* 2. "ONI Framework" appears second */}
          <div
            style={{
              display: 'flex',
              alignItems: 'baseline',
              justifyContent: 'center',
              width: '100%',
              opacity: oniFrameworkProgress,
              transform: `scale(${interpolate(oniFrameworkProgress, [0, 1], [0.9, 1])})`,
            }}
          >
            <span
              style={{
                fontSize: 140,
                fontWeight: 700,
                fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
                letterSpacing: '-0.02em',
                display: 'inline-block',
                background: 'linear-gradient(90deg, #2a7ab8 0%, #4aa8d8 40%, #a0dff0 70%, #ffffff 100%)',
                backgroundSize: '200% 100%',
                backgroundPosition: `${gradientShift * 50}% 0%`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                filter: `drop-shadow(0 0 ${30 + gradientShift * 20}px rgba(0, 120, 200, ${0.3 + gradientShift * 0.3}))`,
              }}
            >
              ONI
            </span>
            <span
              style={{
                fontSize: 140,
                fontWeight: 300,
                fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
                letterSpacing: '-0.02em',
                color: '#ffffff',
                marginLeft: 30,
              }}
            >
              Framework
            </span>
          </div>
          {/* 3. Bottom text with typing effect */}
          <div
            style={{
              fontSize: 24,
              fontWeight: 300,
              fontFamily: "-apple-system, 'SF Pro Text', sans-serif",
              color: 'rgba(140, 190, 210, 0.85)',
              letterSpacing: '0.1em',
              opacity: frame >= bottomTextStart ? 1 : 0,
              marginTop: 40,
              minHeight: 30,
            }}
          >
            {typedText}
            {showCursor && (
              <span
                style={{
                  borderRight: '2px solid rgba(140, 190, 210, 0.85)',
                  marginLeft: 2,
                  opacity: Math.floor(frame / 8) % 2 === 0 ? 1 : 0,
                }}
              />
            )}
          </div>
        </div>
      )}

      {/* Phase 6: Selling Points */}
      {frame >= phase6Start && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 50,
          }}
        >
          {sellingPoints.map((point, i) => {
            const pointDelay = i * 50;
            const pointRaw = interpolate(frame - phase6Start - pointDelay, [0, 40], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
            const pointProgress = appleEase(pointRaw);

            return (
              <div
                key={i}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 12,
                  opacity: pointProgress,
                  transform: `translateY(${interpolate(pointProgress, [0, 1], [30, 0])}px)`,
                }}
              >
                <div
                  style={{
                    fontSize: 56,
                    fontWeight: 600,
                    fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
                    background: i === 0
                      ? 'linear-gradient(90deg, #2a7ab8, #4aa8d8, #a0dff0)'
                      : i === 1
                      ? 'linear-gradient(90deg, #22c55e, #4ade80, #86efac)'
                      : 'linear-gradient(90deg, #f59e0b, #fbbf24, #fde68a)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    letterSpacing: '-0.02em',
                  }}
                >
                  {point.text}
                </div>
                <div
                  style={{
                    fontSize: 20,
                    fontWeight: 400,
                    fontFamily: "-apple-system, 'SF Pro Text', sans-serif",
                    color: 'rgba(180, 200, 220, 0.8)',
                    letterSpacing: '0.02em',
                  }}
                >
                  {point.sub}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </AbsoluteFill>
  );
};
