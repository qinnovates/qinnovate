/**
 * Credits Scene - Powerful closing with manifesto
 * Features: Dramatic text reveals, cinematic pacing, circular wave finale
 */

import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';
import { FloatingParticles } from '../components/Particles';
import { colors } from '../data/oni-theme';

// Complex geometric wave animation for the finale - depth-based z-axis movement
// voiceIntensity: 0-1 value that creates depth pulsing effect when voice is active
const GeometricWaveEffect: React.FC<{ intensity: number; voiceIntensity?: number }> = ({
  intensity,
  voiceIntensity = 0
}) => {
  const frame = useCurrentFrame();

  // Voice intensity affects scale (z-axis depth) - waves pulse forward/back
  const voiceScale = 1 + voiceIntensity * 0.15; // Subtle 15% scale boost
  const voiceOpacity = 1 + voiceIntensity * 0.3; // Brighter when voice active

  // Generate flowing wave paths - gentler movement
  const generateWavePath = (
    yOffset: number,
    amplitude: number,
    frequency: number,
    phase: number,
    points: number = 100
  ) => {
    const pathPoints: string[] = [];
    // Reduced amplitude for subtler movement
    const gentleAmplitude = amplitude * 0.6;
    for (let i = 0; i <= points; i++) {
      const x = (i / points) * 1920;
      const wave1 = Math.sin((x * frequency) / 100 + phase) * gentleAmplitude;
      const wave2 = Math.sin((x * frequency * 1.5) / 100 + phase * 0.7) * (gentleAmplitude * 0.4);
      const y = yOffset + wave1 + wave2;
      pathPoints.push(`${i === 0 ? 'M' : 'L'} ${x} ${y}`);
    }
    return pathPoints.join(' ');
  };

  // Wave configurations - depth layers (different scales create z-axis illusion)
  const waves = [
    { y: 540, amp: 50, freq: 1.5, speed: 0.015, color: '#3b82f6', width: 2, depth: 0.9 },
    { y: 540, amp: 70, freq: 1.2, speed: 0.012, color: '#8b5cf6', width: 2.5, depth: 0.95 },
    { y: 540, amp: 40, freq: 1.8, speed: 0.018, color: '#06b6d4', width: 1.5, depth: 0.85 },
    { y: 540, amp: 80, freq: 1, speed: 0.01, color: '#a855f7', width: 3, depth: 1.0 },
    { y: 540, amp: 30, freq: 2, speed: 0.02, color: '#3b82f6', width: 1, depth: 0.8 },
  ];

  // Geometric shapes that orbit and rotate
  const numShapes = 12;
  const shapes = Array.from({ length: numShapes }, (_, i) => {
    const angle = (i / numShapes) * Math.PI * 2 + frame * 0.01;
    const radius = 300 + Math.sin(frame * 0.02 + i) * 50;
    const x = 960 + Math.cos(angle) * radius;
    const y = 540 + Math.sin(angle) * radius * 0.6;
    const rotation = frame * (0.5 + i * 0.1);
    const size = 20 + Math.sin(frame * 0.03 + i * 0.5) * 10;
    return { x, y, rotation, size, index: i };
  });

  return (
    <svg
      style={{
        position: 'absolute',
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
      }}
      viewBox="0 0 1920 1080"
    >
      <defs>
        <filter id="geoBlur">
          <feGaussianBlur stdDeviation="1.5" />
        </filter>
        <filter id="geoGlow">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <linearGradient id="waveGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
          <stop offset="20%" stopColor="#3b82f6" stopOpacity="0.8" />
          <stop offset="80%" stopColor="#8b5cf6" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="waveGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#06b6d4" stopOpacity="0" />
          <stop offset="30%" stopColor="#06b6d4" stopOpacity="0.6" />
          <stop offset="70%" stopColor="#a855f7" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#a855f7" stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* Flowing wave lines - z-axis depth effect */}
      {waves.map((wave, i) => {
        // Calculate depth-based scale (voice makes waves pulse forward)
        const depthScale = (wave.depth || 1) * voiceScale;
        const waveOpacity = 0.4 * intensity * Math.min(voiceOpacity, 1.2);

        return (
          <g
            key={`wave-${i}`}
            style={{
              transformOrigin: '960px 540px',
              transform: `scale(${depthScale})`,
            }}
          >
            <path
              d={generateWavePath(wave.y, wave.amp, wave.freq, frame * wave.speed + i * 0.3)}
              fill="none"
              stroke={wave.color}
              strokeWidth={wave.width * depthScale}
              opacity={waveOpacity}
              filter="url(#geoGlow)"
            />
          </g>
        );
      })}

      {/* Orbiting geometric shapes */}
      {shapes.map((shape) => (
        <g
          key={`shape-${shape.index}`}
          transform={`translate(${shape.x}, ${shape.y}) rotate(${shape.rotation})`}
        >
          {/* Alternating between different geometric shapes */}
          {shape.index % 3 === 0 ? (
            // Triangle
            <polygon
              points={`0,${-shape.size} ${shape.size * 0.866},${shape.size * 0.5} ${-shape.size * 0.866},${shape.size * 0.5}`}
              fill="none"
              stroke={shape.index % 2 === 0 ? '#3b82f6' : '#8b5cf6'}
              strokeWidth={1.5}
              opacity={0.5 * intensity}
            />
          ) : shape.index % 3 === 1 ? (
            // Square/Diamond
            <rect
              x={-shape.size / 2}
              y={-shape.size / 2}
              width={shape.size}
              height={shape.size}
              fill="none"
              stroke={shape.index % 2 === 0 ? '#06b6d4' : '#a855f7'}
              strokeWidth={1.5}
              opacity={0.4 * intensity}
            />
          ) : (
            // Hexagon
            <polygon
              points={Array.from({ length: 6 }, (_, j) => {
                const a = (j / 6) * Math.PI * 2 - Math.PI / 2;
                return `${Math.cos(a) * shape.size},${Math.sin(a) * shape.size}`;
              }).join(' ')}
              fill="none"
              stroke={shape.index % 2 === 0 ? '#3b82f6' : '#06b6d4'}
              strokeWidth={1.5}
              opacity={0.45 * intensity}
            />
          )}
        </g>
      ))}

      {/* Central connecting lines that pulse */}
      {Array.from({ length: 6 }, (_, i) => {
        const angle1 = (i / 6) * Math.PI * 2 + frame * 0.008;
        const angle2 = ((i + 3) / 6) * Math.PI * 2 + frame * 0.008;
        const r1 = 200 + Math.sin(frame * 0.025 + i) * 30;
        const r2 = 200 + Math.sin(frame * 0.025 + i + Math.PI) * 30;
        return (
          <line
            key={`line-${i}`}
            x1={960 + Math.cos(angle1) * r1}
            y1={540 + Math.sin(angle1) * r1 * 0.6}
            x2={960 + Math.cos(angle2) * r2}
            y2={540 + Math.sin(angle2) * r2 * 0.6}
            stroke={i % 2 === 0 ? '#3b82f6' : '#8b5cf6'}
            strokeWidth={1}
            opacity={0.25 * intensity}
            filter="url(#geoBlur)"
          />
        );
      })}
    </svg>
  );
};

export const CreditsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase timing for the manifesto - SYNCED TO VOICEOVER
  // vo-credits: "Your mind. Your privacy. Our future." (~3.5s)
  //             "ONI. The bridge between worlds." (~3.5s)
  //             "Only life's most important connections deserves the most thought." (~4s)
  const showMind = frame >= 0;        // "Your Mind" at start
  const showPrivacy = frame >= 45;    // "Your Privacy" ~1.5s later
  const showFuture = frame >= 90;     // "Our Future" ~3s
  const showBecause = frame >= 210;   // "Because only..." after ~7s (2s after previous ends)
  const showWelcome = frame >= 400;   // "OSI of Mind" finale ~13s in

  // ═══ FINALE SEQUENCE - 25 seconds before end ═══
  // Credits scene is 1410 frames (47s), so finale starts at frame 660
  const finaleStart = 660;

  // Text fades out first
  const textFadeOut = frame >= finaleStart
    ? interpolate(frame - finaleStart, [0, 60], [1, 0], { extrapolateRight: 'clamp' })
    : 1;

  // Lines/waves fade out after text (starts 2s after text starts fading)
  const linesFadeOut = frame >= finaleStart + 60
    ? interpolate(frame - finaleStart - 60, [0, 90], [1, 0], { extrapolateRight: 'clamp' })
    : 1;

  // Renaissance text appears after lines fade, then disappears
  const showRenaissance = frame >= finaleStart + 180 && frame < finaleStart + 480;
  const renaissanceOpacity = showRenaissance
    ? frame < finaleStart + 400
      ? interpolate(frame - finaleStart - 180, [0, 45], [0, 1], { extrapolateRight: 'clamp' })
      : interpolate(frame - finaleStart - 400, [0, 80], [1, 0], { extrapolateRight: 'clamp' })
    : 0;

  // Glow pulse
  const glowPulse = interpolate(
    Math.sin(frame * 0.04),
    [-1, 1],
    [0.5, 1]
  );

  // Manifesto phrases - synced to voiceover timing
  const manifestoPhrases = [
    { text: 'Your Mind.', delay: 0, show: showMind },
    { text: 'Your Privacy.', delay: 45, show: showPrivacy },
    { text: 'Our Future.', delay: 90, show: showFuture },
  ];

  return (
    <AbsoluteFill
      style={{
        background: colors.gradients.background,
      }}
    >
      {/* Ambient particles */}
      <FloatingParticles
        count={40}
        color={colors.primary.accentPurple}
        speed={0.08}
        minSize={1}
        maxSize={3}
      />

      {/* Background glow */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: 800,
          height: 600,
          transform: 'translate(-50%, -50%)',
          background: `radial-gradient(ellipse, ${colors.primary.accentPurple}15 0%, transparent 60%)`,
          filter: 'blur(60px)',
          opacity: glowPulse,
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
          gap: 0,
        }}
      >
        {/* Manifesto: Our mind. Our future. Our rules. */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 20,
            marginBottom: 60,
          }}
        >
          {manifestoPhrases.map((phrase, i) => {
            const phraseProgress = spring({
              frame: frame - phrase.delay,
              fps,
              config: { damping: 25, stiffness: 60 },
            });

            const y = interpolate(Math.max(0, phraseProgress), [0, 1], [50, 0]);
            const opacity = Math.max(0, phraseProgress);
            const blur = interpolate(Math.max(0, phraseProgress), [0, 1], [15, 0]);

            // Fade out when next section appears (5 seconds sooner)
            const fadeOut = showBecause
              ? interpolate(frame - 60, [0, 60], [1, 0], { extrapolateRight: 'clamp' })
              : 1;

            if (!phrase.show) return null;

            return (
              <div
                key={phrase.text}
                style={{
                  fontSize: 72,
                  fontWeight: 700,
                  letterSpacing: '-0.02em',
                  color: '#ffffff',
                  transform: `translateY(${y}px)`,
                  opacity: opacity * fadeOut,
                  filter: `blur(${blur}px)`,
                  textAlign: 'center',
                  textShadow: '0 0 40px rgba(255,255,255,0.3)',
                }}
              >
                {phrase.text}
              </div>
            );
          })}
        </div>

        {/* "Because only life's most important connections..." */}
        {showBecause && !showWelcome && (
          <div
            style={{
              position: 'absolute',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 20,
            }}
          >
            {(() => {
              const becauseProgress = spring({
                frame: frame - 210,
                fps,
                config: { damping: 30, stiffness: 50 },
              });

              const fadeOut = showWelcome
                ? interpolate(frame - 400, [0, 40], [1, 0], { extrapolateRight: 'clamp' })
                : 1;

              return (
                <div
                  style={{
                    fontSize: 36,
                    fontWeight: 400,
                    color: colors.text.secondary,
                    textAlign: 'center',
                    maxWidth: 900,
                    lineHeight: 1.5,
                    opacity: Math.max(0, becauseProgress) * fadeOut,
                    transform: `translateY(${interpolate(Math.max(0, becauseProgress), [0, 1], [30, 0])}px)`,
                  }}
                >
                  Because only life's most important connections
                  <br />
                  <span style={{ color: colors.text.primary, fontWeight: 700 }}>
                    deserve the most thought.
                  </span>
                </div>
              );
            })()}
          </div>
        )}

        {/* "Welcome to the OSI of Mind" - Door opening with light flooding in */}
        {showWelcome && (
          <>
            {/* Door opening effect - vertical split that opens */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                overflow: 'hidden',
              }}
            >
              {/* Left door panel */}
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '50%',
                  height: '100%',
                  background: '#0a0a12',
                  transform: `translateX(${interpolate(frame - 400, [0, 60], [0, -100], {
                    extrapolateLeft: 'clamp',
                    extrapolateRight: 'clamp',
                  })}%)`,
                  boxShadow: '10px 0 60px rgba(0,0,0,0.8)',
                }}
              />
              {/* Right door panel */}
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  width: '50%',
                  height: '100%',
                  background: '#0a0a12',
                  transform: `translateX(${interpolate(frame - 400, [0, 60], [0, 100], {
                    extrapolateLeft: 'clamp',
                    extrapolateRight: 'clamp',
                  })}%)`,
                  boxShadow: '-10px 0 60px rgba(0,0,0,0.8)',
                }}
              />
            </div>

            {/* Brilliant light flooding through the opening */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                background: `radial-gradient(ellipse 120% 100% at 50% 50%,
                  rgba(255,255,255,1) 0%,
                  rgba(255,255,255,0.95) 20%,
                  rgba(240,248,255,0.9) 40%,
                  rgba(220,240,255,0.7) 60%,
                  rgba(200,230,255,0.4) 80%,
                  transparent 100%
                )`,
                opacity: interpolate(frame - 400, [0, 30, 60, 120], [0, 0.3, 1, 1], {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                }),
              }}
            />

            {/* Light rays streaming through */}
            {Array.from({ length: 12 }, (_, i) => {
              const angle = (i / 12) * 360;
              const rayDelay = i * 3;
              const rayLength = interpolate(frame - 400 - rayDelay, [0, 80], [0, 1500], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              });
              const rayOpacity = interpolate(frame - 400 - rayDelay, [0, 40, 120, 180], [0, 0.4, 0.2, 0], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              });

              return (
                <div
                  key={`ray-${i}`}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: 3,
                    height: rayLength,
                    background: `linear-gradient(to bottom, rgba(255,255,255,0.8) 0%, transparent 100%)`,
                    transformOrigin: 'top center',
                    transform: `translate(-50%, 0) rotate(${angle}deg)`,
                    opacity: rayOpacity,
                    filter: 'blur(2px)',
                  }}
                />
              );
            })}

            {/* Particle burst on door open */}
            {Array.from({ length: 30 }, (_, i) => {
              const angle = (i / 30) * Math.PI * 2;
              const speed = 5 + (i % 3) * 3;
              const distance = interpolate(frame - 420, [0, 100], [0, 400 + (i % 5) * 100], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              });
              const particleOpacity = interpolate(frame - 420, [0, 20, 80, 120], [0, 1, 0.5, 0], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              });
              const x = 960 + Math.cos(angle) * distance;
              const y = 540 + Math.sin(angle) * distance * 0.6;

              return (
                <div
                  key={`particle-${i}`}
                  style={{
                    position: 'absolute',
                    left: x,
                    top: y,
                    width: 4 + (i % 3) * 2,
                    height: 4 + (i % 3) * 2,
                    borderRadius: '50%',
                    background: i % 2 === 0 ? '#ffffff' : '#e0f0ff',
                    opacity: particleOpacity,
                    boxShadow: `0 0 ${10 + (i % 4) * 5}px rgba(255,255,255,0.8)`,
                  }}
                />
              );
            })}

            {/* Complex geometric wave background animation */}
            {/* Waves react to voice - pulses with speech */}
            <GeometricWaveEffect
              intensity={interpolate(frame - 460, [0, 60], [0, 0.8], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              })}
              voiceIntensity={(() => {
                // Voice 1: "Welcome to the OSI of Mind..." at frame 460-670
                const voice1Active = frame >= 460 && frame <= 670;
                // Voice 2: "So... what are you waiting for?" at frame 1050-1110
                const voice2Active = frame >= 1050 && frame <= 1110;

                if (voice1Active) {
                  // Pulsing intensity that mimics speech rhythm
                  const t = (frame - 460) / 210; // 0-1 over voice duration
                  const pulse = Math.sin(frame * 0.3) * 0.3 + 0.7; // Oscillate 0.4-1.0
                  const envelope = Math.sin(t * Math.PI); // Fade in/out
                  return pulse * envelope;
                }
                if (voice2Active) {
                  const t = (frame - 1050) / 60;
                  const pulse = Math.sin(frame * 0.35) * 0.3 + 0.7;
                  const envelope = Math.sin(t * Math.PI);
                  return pulse * envelope * 1.2; // Slightly more intense for CTA
                }
                return 0;
              })()}
            />

            <div
              style={{
                position: 'absolute',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 30,
                zIndex: 10,
              }}
            >
              {(() => {
                const textStart = 460; // Text appears after door opens
                const welcomeProgress = spring({
                  frame: frame - textStart,
                  fps,
                  config: { damping: 18, stiffness: 35 },
                });

                const oniProgress = spring({
                  frame: frame - textStart - 30,
                  fps,
                  config: { damping: 20, stiffness: 40 },
                });

                const taglineProgress = spring({
                  frame: frame - textStart - 60,
                  fps,
                  config: { damping: 22, stiffness: 45 },
                });

                // Subtle floating animation
                const floatY = Math.sin(frame * 0.03) * 5;

                return (
                  <>
                  {/* "Welcome to" - fades in first */}
                  <div
                    style={{
                      fontSize: 28,
                      fontWeight: 300,
                      letterSpacing: '0.4em',
                      color: '#475569',
                      textTransform: 'uppercase',
                      opacity: Math.max(0, welcomeProgress),
                      transform: `translateY(${interpolate(Math.max(0, welcomeProgress), [0, 1], [40, 0]) + floatY}px)`,
                      filter: `blur(${interpolate(Math.max(0, welcomeProgress), [0, 1], [10, 0])}px)`,
                    }}
                  >
                    Welcome to
                  </div>

                  {/* "The OSI of Mind" - main title with dramatic entrance */}
                  <div
                    style={{
                      fontSize: 96,
                      fontWeight: 800,
                      letterSpacing: '-0.02em',
                      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 50%, #1e3a5f 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      opacity: Math.max(0, oniProgress),
                      transform: `scale(${interpolate(Math.max(0, oniProgress), [0, 1], [0.8, 1])}) translateY(${floatY}px)`,
                      filter: `blur(${interpolate(Math.max(0, oniProgress), [0, 1], [15, 0])}px)`,
                      textAlign: 'center',
                      textShadow: '0 4px 30px rgba(0,0,0,0.1)',
                    }}
                  >
                    The OSI of Mind
                  </div>

                  {/* ONI tagline */}
                  <div
                    style={{
                      fontSize: 20,
                      fontWeight: 400,
                      letterSpacing: '0.15em',
                      color: '#64748b',
                      opacity: Math.max(0, taglineProgress),
                      transform: `translateY(${interpolate(Math.max(0, taglineProgress), [0, 1], [30, 0]) + floatY}px)`,
                      textAlign: 'center',
                      maxWidth: 700,
                      lineHeight: 1.6,
                    }}
                  >
                    Open{' '}
                    <span
                      style={{
                        background: 'linear-gradient(90deg, #2563eb 0%, #3b82f6 40%, #06b6d4 70%, #8b5cf6 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        fontWeight: 600,
                      }}
                    >
                      Neuro
                    </span>
                    security Interoperability
                  </div>

                  {/* Credits footer */}
                  <div
                    style={{
                      position: 'absolute',
                      bottom: -180,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 8,
                      opacity: interpolate(frame - textStart - 90, [0, 40], [0, 0.8], {
                        extrapolateLeft: 'clamp',
                        extrapolateRight: 'clamp',
                      }),
                    }}
                  >
                    <div style={{ fontSize: 18, color: '#1e293b', fontWeight: 600, letterSpacing: '0.02em' }}>
                      Kevin L. Qi
                    </div>
                    <div style={{ fontSize: 14, color: '#64748b', letterSpacing: '0.05em' }}>
                      Qinnovate LLC
                    </div>
                  </div>
                  </>
                );
              })()}
            </div>
          </>
        )}
      </div>

      {/* Corner accents - fade with lines */}
      {[
        { top: 40, left: 40 },
        { top: 40, right: 40 },
        { bottom: 40, left: 40 },
        { bottom: 40, right: 40 },
      ].map((pos, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            ...pos,
            width: 60,
            height: 60,
            borderTop: pos.top !== undefined ? `1px solid ${colors.primary.accent}22` : 'none',
            borderBottom: pos.bottom !== undefined ? `1px solid ${colors.primary.accent}22` : 'none',
            borderLeft: pos.left !== undefined ? `1px solid ${colors.primary.accent}22` : 'none',
            borderRight: pos.right !== undefined ? `1px solid ${colors.primary.accent}22` : 'none',
            opacity: interpolate(frame, [0, 60], [0, 0.5], { extrapolateRight: 'clamp' }) * linesFadeOut,
          }}
        />
      ))}

      {/* ═══ RENAISSANCE TEXT ═══ */}
      {/* "The Human-AI Renaissance In The Age of BCIs is Here" - small and thin */}
      {showRenaissance && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: renaissanceOpacity,
          }}
        >
          <div
            style={{
              fontSize: 24,
              fontWeight: 300,
              letterSpacing: '0.08em',
              color: 'rgba(255, 255, 255, 0.8)',
              textAlign: 'center',
              textTransform: 'uppercase',
            }}
          >
            The Human-AI Renaissance In The Age of BCIs is Here
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
