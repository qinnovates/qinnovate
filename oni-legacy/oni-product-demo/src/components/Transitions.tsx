/**
 * Professional scene transitions
 * Apple-quality wipes, fades, and reveals
 */

import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { colors } from '../data/oni-theme';

// Smooth fade transition
export const FadeTransition: React.FC<{
  type: 'in' | 'out';
  duration?: number;
  delay?: number;
  children: React.ReactNode;
}> = ({ type, duration = 20, delay = 0, children }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(
    frame,
    type === 'in'
      ? [delay, delay + duration]
      : [delay, delay + duration],
    type === 'in' ? [0, 1] : [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  return <div style={{ opacity }}>{children}</div>;
};

// Wipe transition with gradient edge
export const WipeTransition: React.FC<{
  direction?: 'left' | 'right' | 'up' | 'down';
  progress: number; // 0-1
  color?: string;
}> = ({ direction = 'right', progress, color = colors.primary.dark }) => {
  const getTransform = () => {
    const offset = interpolate(progress, [0, 1], [0, 100]);
    switch (direction) {
      case 'left': return `translateX(${100 - offset}%)`;
      case 'right': return `translateX(${-100 + offset}%)`;
      case 'up': return `translateY(${100 - offset}%)`;
      case 'down': return `translateY(${-100 + offset}%)`;
    }
  };

  const getGradient = () => {
    const gradientDir = direction === 'left' || direction === 'right' ? 'to right' : 'to bottom';
    return `linear-gradient(${gradientDir}, ${color} 0%, ${color} 85%, transparent 100%)`;
  };

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: getGradient(),
        transform: getTransform(),
        pointerEvents: 'none',
      }}
    />
  );
};

// Circular reveal (like Apple keynote)
export const CircleReveal: React.FC<{
  progress: number; // 0-1
  centerX?: number;
  centerY?: number;
  color?: string;
}> = ({ progress, centerX = 50, centerY = 50, color = colors.primary.dark }) => {
  // Max radius to cover entire screen (diagonal)
  const maxRadius = 150;
  const radius = interpolate(progress, [0, 1], [0, maxRadius]);

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: color,
        clipPath: `circle(${radius}% at ${centerX}% ${centerY}%)`,
        pointerEvents: 'none',
      }}
    />
  );
};

// Glitch transition effect
export const GlitchTransition: React.FC<{
  intensity?: number;
  children: React.ReactNode;
}> = ({ intensity = 1, children }) => {
  const frame = useCurrentFrame();

  // Random offset that changes every few frames
  const glitchFrame = Math.floor(frame / 3);
  const offsetX = (Math.sin(glitchFrame * 7.3) * 10 + Math.sin(glitchFrame * 13.7) * 5) * intensity;
  const offsetY = (Math.cos(glitchFrame * 5.1) * 5) * intensity;

  // RGB split effect
  const rgbOffset = intensity * 3;

  return (
    <div style={{ position: 'relative' }}>
      {/* Red channel */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          transform: `translate(${-rgbOffset}px, 0)`,
          filter: 'url(#redChannel)',
          mixBlendMode: 'screen',
          opacity: 0.5,
        }}
      >
        {children}
      </div>
      {/* Blue channel */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          transform: `translate(${rgbOffset}px, 0)`,
          filter: 'url(#blueChannel)',
          mixBlendMode: 'screen',
          opacity: 0.5,
        }}
      >
        {children}
      </div>
      {/* Main content with offset */}
      <div
        style={{
          transform: `translate(${offsetX}px, ${offsetY}px)`,
        }}
      >
        {children}
      </div>
    </div>
  );
};

// Smooth zoom transition
export const ZoomTransition: React.FC<{
  type: 'in' | 'out';
  duration?: number;
  delay?: number;
  children: React.ReactNode;
}> = ({ type, duration = 30, delay = 0, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 100, stiffness: 80 },
  });

  const scale = type === 'in'
    ? interpolate(progress, [0, 1], [0.8, 1])
    : interpolate(progress, [0, 1], [1, 1.2]);

  const opacity = type === 'in'
    ? interpolate(progress, [0, 1], [0, 1])
    : interpolate(progress, [0, 1], [1, 0]);

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        opacity: Math.max(0, opacity),
      }}
    >
      {children}
    </div>
  );
};

// Slide with spring physics
export const SlideIn: React.FC<{
  direction?: 'left' | 'right' | 'up' | 'down';
  delay?: number;
  distance?: number;
  children: React.ReactNode;
}> = ({ direction = 'up', delay = 0, distance = 100, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 20, stiffness: 100 },
  });

  const getTransform = () => {
    const offset = interpolate(progress, [0, 1], [distance, 0]);
    switch (direction) {
      case 'left': return `translateX(${offset}px)`;
      case 'right': return `translateX(${-offset}px)`;
      case 'up': return `translateY(${offset}px)`;
      case 'down': return `translateY(${-offset}px)`;
    }
  };

  return (
    <div
      style={{
        transform: getTransform(),
        opacity: Math.max(0, progress),
      }}
    >
      {children}
    </div>
  );
};

// Staggered children animation
export const StaggeredReveal: React.FC<{
  staggerDelay?: number;
  children: React.ReactNode[];
}> = ({ staggerDelay = 5, children }) => {
  return (
    <>
      {React.Children.map(children, (child, index) => (
        <SlideIn key={index} delay={index * staggerDelay}>
          {child}
        </SlideIn>
      ))}
    </>
  );
};
