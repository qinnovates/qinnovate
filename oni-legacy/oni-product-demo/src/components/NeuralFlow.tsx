/**
 * NeuralFlow - Animated neural signal visualization
 * Inspired by ElevenLabs' "Sound Flow" concept
 * Three states: static, resting (ambient), reactive
 */

import React, { useMemo } from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { colors } from '../data/oni-theme';

interface NeuralFlowProps {
  state?: 'static' | 'resting' | 'reactive';
  width?: number;
  height?: number;
  color?: string;
  intensity?: number;
}

export const NeuralFlow: React.FC<NeuralFlowProps> = ({
  state = 'resting',
  width = 400,
  height = 100,
  color = colors.primary.accent,
  intensity = 1,
}) => {
  const frame = useCurrentFrame();

  // Generate wave points
  const points = useMemo(() => {
    const numPoints = 50;
    return Array.from({ length: numPoints }, (_, i) => i / (numPoints - 1));
  }, []);

  // Calculate wave path based on state
  const getWavePath = () => {
    const amplitude = state === 'static' ? 0 : state === 'resting' ? 15 : 30;
    const frequency = state === 'reactive' ? 4 : 2;
    const speed = state === 'reactive' ? 0.15 : 0.05;
    const time = frame * speed;

    const pathPoints = points.map((t, i) => {
      const x = t * width;

      // Multiple sine waves for organic feel
      const wave1 = Math.sin(t * Math.PI * frequency + time) * amplitude * intensity;
      const wave2 = Math.sin(t * Math.PI * frequency * 1.5 + time * 1.3) * amplitude * 0.5 * intensity;
      const wave3 = Math.sin(t * Math.PI * frequency * 2.5 + time * 0.7) * amplitude * 0.25 * intensity;

      // Add some noise for neural feel
      const noise = state === 'reactive'
        ? Math.sin(i * 0.5 + frame * 0.3) * 5 * intensity
        : 0;

      const y = height / 2 + wave1 + wave2 + wave3 + noise;

      return { x, y };
    });

    // Create smooth bezier path
    let path = `M ${pathPoints[0].x} ${pathPoints[0].y}`;
    for (let i = 1; i < pathPoints.length - 2; i++) {
      const xc = (pathPoints[i].x + pathPoints[i + 1].x) / 2;
      const yc = (pathPoints[i].y + pathPoints[i + 1].y) / 2;
      path += ` Q ${pathPoints[i].x} ${pathPoints[i].y} ${xc} ${yc}`;
    }
    path += ` T ${pathPoints[pathPoints.length - 1].x} ${pathPoints[pathPoints.length - 1].y}`;

    return path;
  };

  // Pulse opacity for reactive state
  const glowOpacity = state === 'reactive'
    ? interpolate(Math.sin(frame * 0.2), [-1, 1], [0.3, 0.8])
    : 0.5;

  return (
    <svg
      width={width}
      height={height}
      style={{ overflow: 'visible' }}
    >
      <defs>
        {/* Gradient for the flow */}
        <linearGradient id="neuralFlowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={color} stopOpacity={0.2} />
          <stop offset="50%" stopColor={color} stopOpacity={1} />
          <stop offset="100%" stopColor={color} stopOpacity={0.2} />
        </linearGradient>

        {/* Glow filter */}
        <filter id="neuralGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>

        {/* Stronger glow for reactive state */}
        <filter id="neuralGlowStrong" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="8" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {/* Background glow */}
      <path
        d={getWavePath()}
        fill="none"
        stroke={color}
        strokeWidth={state === 'reactive' ? 12 : 8}
        strokeLinecap="round"
        opacity={glowOpacity * 0.3}
        filter="url(#neuralGlowStrong)"
      />

      {/* Main wave */}
      <path
        d={getWavePath()}
        fill="none"
        stroke="url(#neuralFlowGradient)"
        strokeWidth={state === 'reactive' ? 4 : 3}
        strokeLinecap="round"
        filter="url(#neuralGlow)"
      />

      {/* Traveling pulse particles */}
      {state !== 'static' && Array.from({ length: 5 }).map((_, i) => {
        const progress = ((frame * 0.02 + i * 0.2) % 1);
        const x = progress * width;
        const pathY = height / 2 + Math.sin(progress * Math.PI * 2 + frame * 0.05) * 15 * intensity;

        return (
          <circle
            key={i}
            cx={x}
            cy={pathY}
            r={state === 'reactive' ? 4 : 3}
            fill={color}
            opacity={interpolate(progress, [0, 0.1, 0.9, 1], [0, 1, 1, 0])}
            filter="url(#neuralGlow)"
          />
        );
      })}
    </svg>
  );
};

// Multiple flowing lines version for backgrounds
export const NeuralFlowBackground: React.FC<{
  numLines?: number;
  opacity?: number;
}> = ({ numLines = 5, opacity = 0.3 }) => {
  const frame = useCurrentFrame();

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        overflow: 'hidden',
        opacity,
      }}
    >
      {Array.from({ length: numLines }).map((_, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            top: `${20 + i * 15}%`,
            left: -100,
            right: -100,
            transform: `translateX(${Math.sin(frame * 0.01 + i) * 50}px)`,
          }}
        >
          <NeuralFlow
            state="resting"
            width={2200}
            height={60}
            intensity={0.5 + i * 0.1}
            color={i % 2 === 0 ? colors.primary.accent : colors.primary.light}
          />
        </div>
      ))}
    </div>
  );
};
