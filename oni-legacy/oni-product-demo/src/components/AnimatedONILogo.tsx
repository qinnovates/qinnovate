/**
 * AnimatedONILogo - Cinematic full-screen logo animation
 * Features: Aurora effects, elegant typography, smooth reveals
 */

import React, { useMemo } from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { colors } from '../data/oni-theme';

interface AnimatedONILogoProps {
  width?: number;
  height?: number;
  showTagline?: boolean;
}

// Seeded random for consistent animations
const seededRandom = (seed: number) => {
  const x = Math.sin(seed * 9999) * 10000;
  return x - Math.floor(x);
};

export const AnimatedONILogo: React.FC<AnimatedONILogoProps> = ({
  width = 1920,
  height = 1080,
  showTagline = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const centerX = width / 2;
  const centerY = height / 2;

  // Main entrance animation - cinematic slow reveal
  const mainProgress = spring({
    frame,
    fps,
    config: { damping: 80, stiffness: 30, mass: 2 },
  });

  // Letter animations with stagger
  const letterConfigs = ['O', 'N', 'I'].map((letter, i) => ({
    letter,
    progress: spring({
      frame: frame - 15 - i * 12,
      fps,
      config: { damping: 20, stiffness: 60, mass: 1.5 },
    }),
  }));

  // Tagline animation
  const taglineProgress = spring({
    frame: frame - 60,
    fps,
    config: { damping: 30, stiffness: 50 },
  });

  // Aurora wave animation
  const auroraPhase = frame * 0.015;

  // Glow pulse
  const glowPulse = interpolate(
    Math.sin(frame * 0.03),
    [-1, 1],
    [0.6, 1]
  );

  // Generate aurora paths
  const auroraPaths = useMemo(() => {
    return Array.from({ length: 5 }, (_, i) => ({
      offset: i * 0.2,
      amplitude: 80 + i * 30,
      wavelength: 400 + i * 100,
      color: i % 2 === 0 ? colors.primary.accent : colors.primary.accentPurple,
      opacity: 0.15 - i * 0.02,
    }));
  }, []);

  // Particle field
  const particles = useMemo(() => {
    return Array.from({ length: 80 }, (_, i) => ({
      x: seededRandom(i * 1.1) * width,
      y: seededRandom(i * 2.2) * height,
      size: 1 + seededRandom(i * 3.3) * 3,
      speed: 0.2 + seededRandom(i * 4.4) * 0.5,
      delay: seededRandom(i * 5.5) * 100,
    }));
  }, [width, height]);

  return (
    <div
      style={{
        width,
        height,
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Background gradient layers */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `
            radial-gradient(ellipse 120% 80% at 50% 120%, ${colors.primary.accentPurple}25 0%, transparent 50%),
            radial-gradient(ellipse 100% 60% at 50% -20%, ${colors.primary.accent}15 0%, transparent 40%),
            radial-gradient(ellipse at center, ${colors.primary.main} 0%, ${colors.primary.dark} 100%)
          `,
        }}
      />

      {/* Aurora SVG layer */}
      <svg
        width={width}
        height={height}
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        <defs>
          {/* Blur filter for aurora */}
          <filter id="auroraBlur" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="40" />
          </filter>

          {/* Glow filter for particles */}
          <filter id="particleGlow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>

          {/* Gradient for light rays */}
          <linearGradient id="rayGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={colors.primary.accent} stopOpacity="0.3" />
            <stop offset="50%" stopColor={colors.primary.accentPurple} stopOpacity="0.1" />
            <stop offset="100%" stopColor="transparent" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Aurora waves */}
        {auroraPaths.map((aurora, i) => {
          const pathD = Array.from({ length: 20 }, (_, j) => {
            const x = (j / 19) * width;
            const baseY = height * 0.3;
            const wave = Math.sin((x / aurora.wavelength) + auroraPhase + aurora.offset * Math.PI * 2) * aurora.amplitude;
            const wave2 = Math.sin((x / (aurora.wavelength * 0.7)) + auroraPhase * 1.3) * (aurora.amplitude * 0.5);
            const y = baseY + wave + wave2;
            return j === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
          }).join(' ');

          return (
            <path
              key={i}
              d={pathD + ` L ${width} ${height} L 0 ${height} Z`}
              fill={aurora.color}
              opacity={aurora.opacity * Math.max(0, mainProgress)}
              filter="url(#auroraBlur)"
            />
          );
        })}

        {/* Vertical light rays */}
        {[0.3, 0.5, 0.7].map((pos, i) => {
          const rayOpacity = interpolate(
            Math.sin(frame * 0.02 + i * 2),
            [-1, 1],
            [0.02, 0.08]
          ) * Math.max(0, mainProgress);

          return (
            <rect
              key={i}
              x={width * pos - 100}
              y={0}
              width={200}
              height={height}
              fill="url(#rayGradient)"
              opacity={rayOpacity}
            />
          );
        })}

        {/* Floating particles */}
        {particles.map((particle, i) => {
          const particleY = (particle.y - (frame * particle.speed) % height + height) % height;
          const fadeIn = interpolate(
            frame - particle.delay,
            [0, 30],
            [0, 1],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );
          const twinkle = 0.3 + Math.sin(frame * 0.1 + i) * 0.7;

          return (
            <circle
              key={i}
              cx={particle.x}
              cy={particleY}
              r={particle.size}
              fill={i % 3 === 0 ? colors.primary.accent : colors.primary.accentPurple}
              opacity={fadeIn * twinkle * 0.6 * Math.max(0, mainProgress)}
              filter="url(#particleGlow)"
            />
          );
        })}

        {/* Central glow */}
        <ellipse
          cx={centerX}
          cy={centerY}
          rx={400 * glowPulse}
          ry={250 * glowPulse}
          fill={colors.primary.accentPurple}
          opacity={0.08 * Math.max(0, mainProgress)}
          filter="url(#auroraBlur)"
        />
        <ellipse
          cx={centerX}
          cy={centerY}
          rx={300 * glowPulse}
          ry={180 * glowPulse}
          fill={colors.primary.accent}
          opacity={0.1 * Math.max(0, mainProgress)}
          filter="url(#auroraBlur)"
        />
      </svg>

      {/* Concentric rings */}
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {[1, 2, 3].map((ring) => {
          const ringProgress = spring({
            frame: frame - 30 - ring * 20,
            fps,
            config: { damping: 40, stiffness: 40 },
          });
          const size = 300 + ring * 150;
          const rotation = frame * (0.05 / ring) * (ring % 2 === 0 ? 1 : -1);

          return (
            <div
              key={ring}
              style={{
                position: 'absolute',
                width: size,
                height: size,
                borderRadius: '50%',
                border: `1px solid ${ring % 2 === 0 ? colors.primary.accent : colors.primary.accentPurple}`,
                opacity: Math.max(0, ringProgress) * 0.2,
                transform: `rotate(${rotation}deg) scale(${interpolate(Math.max(0, ringProgress), [0, 1], [0.8, 1])})`,
              }}
            />
          );
        })}
      </div>

      {/* Main ONI text */}
      <div
        style={{
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 30,
          zIndex: 10,
        }}
      >
        {/* ONI Letters */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 20,
          }}
        >
          {letterConfigs.map(({ letter, progress }, i) => {
            const y = interpolate(Math.max(0, progress), [0, 1], [80, 0]);
            const opacity = Math.max(0, progress);
            const scale = interpolate(Math.max(0, progress), [0, 1], [0.8, 1]);
            const blur = interpolate(Math.max(0, progress), [0, 1], [20, 0]);

            return (
              <div
                key={letter}
                style={{
                  fontSize: 200,
                  fontWeight: 800,
                  fontFamily: "'Inter', 'Helvetica Neue', sans-serif",
                  letterSpacing: '-0.02em',
                  background: `linear-gradient(180deg,
                    #ffffff 0%,
                    rgba(255,255,255,0.95) 30%,
                    ${colors.primary.accent}90 70%,
                    ${colors.primary.accentPurple}80 100%
                  )`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  transform: `translateY(${y}px) scale(${scale})`,
                  opacity,
                  filter: `blur(${blur}px) drop-shadow(0 0 ${60 * glowPulse}px ${colors.primary.accent}66)`,
                  textShadow: `0 0 80px ${colors.primary.accent}44`,
                }}
              >
                {letter}
              </div>
            );
          })}
        </div>

        {/* Tagline */}
        {showTagline && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 16,
              opacity: Math.max(0, taglineProgress),
              transform: `translateY(${interpolate(Math.max(0, taglineProgress), [0, 1], [30, 0])}px)`,
            }}
          >
            <div
              style={{
                fontSize: 28,
                fontWeight: 300,
                letterSpacing: '0.4em',
                color: colors.primary.accent,
                textTransform: 'uppercase',
              }}
            >
              Open Neurocomputing Interface
            </div>
            <div
              style={{
                fontSize: 18,
                fontWeight: 400,
                letterSpacing: '0.15em',
                color: colors.text.muted,
              }}
            >
              The OSI of Mind
            </div>
          </div>
        )}
      </div>

      {/* Bottom fade gradient */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 200,
          background: `linear-gradient(transparent, ${colors.primary.dark}cc)`,
          pointerEvents: 'none',
        }}
      />

      {/* Top fade gradient */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 150,
          background: `linear-gradient(${colors.primary.dark}88, transparent)`,
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};

// Standalone circular wave component for backgrounds
export const CircularWaves: React.FC<{
  width?: number;
  height?: number;
  numWaves?: number;
  baseRadius?: number;
  color?: string;
}> = ({
  width = 1920,
  height = 1080,
  numWaves = 5,
  baseRadius = 100,
  color = colors.primary.accent,
}) => {
  const frame = useCurrentFrame();
  const centerX = width / 2;
  const centerY = height / 2;

  // Apple-style ease out
  const appleEaseOut = (t: number) => 1 - Math.pow(1 - t, 4);

  return (
    <svg width={width} height={height} style={{ position: 'absolute' }}>
      <defs>
        <filter id="circularWaveBlur">
          <feGaussianBlur stdDeviation="3" />
        </filter>
      </defs>

      {Array.from({ length: numWaves }, (_, i) => {
        const delay = i * 20;
        const waveFrame = Math.max(0, frame - delay);
        const cycleDuration = 120;
        const progress = (waveFrame % cycleDuration) / cycleDuration;
        const easedProgress = appleEaseOut(progress);

        const maxRadius = Math.max(width, height) * 0.8;
        const radius = interpolate(easedProgress, [0, 1], [baseRadius, maxRadius]);
        const opacity = interpolate(easedProgress, [0, 0.1, 0.6, 1], [0, 0.4, 0.2, 0]);

        return (
          <circle
            key={i}
            cx={centerX}
            cy={centerY}
            r={radius}
            fill="none"
            stroke={i % 2 === 0 ? color : colors.primary.accentPurple}
            strokeWidth={2}
            opacity={opacity}
            filter="url(#circularWaveBlur)"
          />
        );
      })}
    </svg>
  );
};

export default AnimatedONILogo;
