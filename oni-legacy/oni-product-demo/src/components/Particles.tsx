/**
 * Particle systems for ambient backgrounds
 * Floating particles, neural networks, starfields
 */

import React, { useMemo } from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { colors } from '../data/oni-theme';

// Floating particles background
export const FloatingParticles: React.FC<{
  count?: number;
  color?: string;
  speed?: number;
  minSize?: number;
  maxSize?: number;
}> = ({
  count = 50,
  color = colors.primary.accent,
  speed = 0.5,
  minSize = 2,
  maxSize = 6,
}) => {
  const frame = useCurrentFrame();

  const particles = useMemo(() => {
    return Array.from({ length: count }, (_, i) => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: minSize + Math.random() * (maxSize - minSize),
      speed: 0.5 + Math.random() * speed,
      opacity: 0.3 + Math.random() * 0.5,
      phase: Math.random() * Math.PI * 2,
    }));
  }, [count, minSize, maxSize, speed]);

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
      }}
    >
      {particles.map((particle, i) => {
        // Floating motion
        const floatY = Math.sin(frame * 0.02 * particle.speed + particle.phase) * 20;
        const floatX = Math.cos(frame * 0.015 * particle.speed + particle.phase) * 10;

        // Subtle pulse
        const pulse = 0.8 + Math.sin(frame * 0.05 + particle.phase) * 0.2;

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              width: particle.size * pulse,
              height: particle.size * pulse,
              borderRadius: '50%',
              backgroundColor: color,
              opacity: particle.opacity * pulse,
              transform: `translate(${floatX}px, ${floatY}px)`,
              boxShadow: `0 0 ${particle.size * 2}px ${color}`,
            }}
          />
        );
      })}
    </div>
  );
};

// Connected neural network background
export const NeuralNetworkBackground: React.FC<{
  nodeCount?: number;
  connectionDistance?: number;
}> = ({ nodeCount = 30, connectionDistance = 200 }) => {
  const frame = useCurrentFrame();

  const nodes = useMemo(() => {
    return Array.from({ length: nodeCount }, (_, i) => ({
      x: Math.random() * 1920,
      y: Math.random() * 1080,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      size: 3 + Math.random() * 3,
    }));
  }, [nodeCount]);

  // Animate node positions
  const animatedNodes = nodes.map((node, i) => ({
    ...node,
    x: node.x + Math.sin(frame * 0.01 + i) * 50,
    y: node.y + Math.cos(frame * 0.01 + i * 1.3) * 30,
  }));

  // Find connections between nearby nodes
  const connections: { x1: number; y1: number; x2: number; y2: number; distance: number }[] = [];
  animatedNodes.forEach((node, i) => {
    animatedNodes.forEach((other, j) => {
      if (i >= j) return;
      const dx = node.x - other.x;
      const dy = node.y - other.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      if (distance < connectionDistance) {
        connections.push({
          x1: node.x,
          y1: node.y,
          x2: other.x,
          y2: other.y,
          distance,
        });
      }
    });
  });

  return (
    <svg
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
      }}
    >
      <defs>
        <filter id="nodeGlow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {/* Connections */}
      {connections.map((conn, i) => {
        const opacity = interpolate(
          conn.distance,
          [0, connectionDistance],
          [0.4, 0]
        );
        return (
          <line
            key={`conn-${i}`}
            x1={conn.x1}
            y1={conn.y1}
            x2={conn.x2}
            y2={conn.y2}
            stroke={colors.primary.accent}
            strokeWidth={1}
            opacity={opacity}
          />
        );
      })}

      {/* Nodes */}
      {animatedNodes.map((node, i) => {
        const pulse = 0.8 + Math.sin(frame * 0.1 + i) * 0.2;
        return (
          <circle
            key={`node-${i}`}
            cx={node.x}
            cy={node.y}
            r={node.size * pulse}
            fill={colors.primary.accent}
            opacity={0.6}
            filter="url(#nodeGlow)"
          />
        );
      })}
    </svg>
  );
};

// Starfield / space background
export const Starfield: React.FC<{
  starCount?: number;
  speed?: number;
}> = ({ starCount = 200, speed = 1 }) => {
  const frame = useCurrentFrame();

  const stars = useMemo(() => {
    return Array.from({ length: starCount }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      z: Math.random(), // Depth for parallax
      size: 1 + Math.random() * 2,
      twinklePhase: Math.random() * Math.PI * 2,
    }));
  }, [starCount]);

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        overflow: 'hidden',
        background: 'transparent',
      }}
    >
      {stars.map((star, i) => {
        // Parallax movement based on depth
        const parallaxX = (frame * speed * star.z * 0.1) % 100;
        const xPos = (star.x + parallaxX) % 100;

        // Twinkle effect
        const twinkle = 0.5 + Math.sin(frame * 0.1 + star.twinklePhase) * 0.5;

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${xPos}%`,
              top: `${star.y}%`,
              width: star.size,
              height: star.size,
              borderRadius: '50%',
              backgroundColor: '#fff',
              opacity: twinkle * (0.3 + star.z * 0.7),
              boxShadow: `0 0 ${star.size * 2}px rgba(255,255,255,${twinkle * 0.5})`,
            }}
          />
        );
      })}
    </div>
  );
};

// Grid lines background (tech/cyberpunk feel)
export const GridBackground: React.FC<{
  cellSize?: number;
  color?: string;
  perspective?: boolean;
}> = ({ cellSize = 50, color = colors.primary.accent, perspective = true }) => {
  const frame = useCurrentFrame();

  // Scroll animation
  const scrollOffset = (frame * 0.5) % cellSize;

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        overflow: 'hidden',
        transform: perspective ? 'perspective(500px) rotateX(60deg)' : 'none',
        transformOrigin: 'center 120%',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: -cellSize,
          left: -cellSize,
          right: -cellSize,
          bottom: -cellSize,
          backgroundImage: `
            linear-gradient(${color}22 1px, transparent 1px),
            linear-gradient(90deg, ${color}22 1px, transparent 1px)
          `,
          backgroundSize: `${cellSize}px ${cellSize}px`,
          transform: `translateY(${scrollOffset}px)`,
        }}
      />
      {/* Glow line at horizon */}
      {perspective && (
        <div
          style={{
            position: 'absolute',
            bottom: '40%',
            left: 0,
            right: 0,
            height: 2,
            background: `linear-gradient(90deg, transparent, ${color}, transparent)`,
            boxShadow: `0 0 20px ${color}, 0 0 40px ${color}`,
          }}
        />
      )}
    </div>
  );
};
