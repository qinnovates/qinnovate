/**
 * Premium Text Animations - Apple keynote style
 * Blur-in, staggered fade, character animations, pull-up effects
 */

import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { colors } from '../data/oni-theme';

// Blur-in text reveal (like Apple's product reveals)
export const BlurInText: React.FC<{
  text: string;
  delay?: number;
  fontSize?: number;
  color?: string;
  fontWeight?: number;
  gradient?: boolean;
}> = ({
  text,
  delay = 0,
  fontSize = 48,
  color = colors.text.primary,
  fontWeight = 600,
  gradient = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 30, stiffness: 80 },
  });

  const blur = interpolate(Math.max(0, progress), [0, 1], [20, 0]);
  const opacity = interpolate(Math.max(0, progress), [0, 0.5, 1], [0, 0.8, 1]);
  const scale = interpolate(Math.max(0, progress), [0, 1], [0.9, 1]);

  const textStyle: React.CSSProperties = {
    fontSize,
    fontWeight,
    filter: `blur(${blur}px)`,
    opacity,
    transform: `scale(${scale})`,
    ...(gradient
      ? {
          background: `linear-gradient(90deg, ${colors.text.primary} 0%, rgba(255,255,255,0.85) 50%, ${colors.text.primary} 100%)`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }
      : { color }),
  };

  return <div style={textStyle}>{text}</div>;
};

// Character-by-character reveal with wave effect
export const CharacterReveal: React.FC<{
  text: string;
  delay?: number;
  fontSize?: number;
  color?: string;
  fontWeight?: number;
  staggerDelay?: number;
}> = ({
  text,
  delay = 0,
  fontSize = 48,
  color = colors.text.primary,
  fontWeight = 600,
  staggerDelay = 2,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const characters = text.split('');

  return (
    <div style={{ display: 'flex', fontSize, fontWeight }}>
      {characters.map((char, i) => {
        const charProgress = spring({
          frame: frame - delay - i * staggerDelay,
          fps,
          config: { damping: 20, stiffness: 150 },
        });

        const y = interpolate(Math.max(0, charProgress), [0, 1], [30, 0]);
        const opacity = Math.max(0, charProgress);

        return (
          <span
            key={i}
            style={{
              color,
              transform: `translateY(${y}px)`,
              opacity,
              display: 'inline-block',
              whiteSpace: char === ' ' ? 'pre' : 'normal',
            }}
          >
            {char}
          </span>
        );
      })}
    </div>
  );
};

// Word-by-word staggered fade (like ElevenLabs)
export const WordsStaggerFade: React.FC<{
  text: string;
  delay?: number;
  fontSize?: number;
  color?: string;
  fontWeight?: number;
  staggerDelay?: number;
  lineHeight?: number;
}> = ({
  text,
  delay = 0,
  fontSize = 32,
  color = colors.text.secondary,
  fontWeight = 400,
  staggerDelay = 4,
  lineHeight = 1.6,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const words = text.split(' ');

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        fontSize,
        fontWeight,
        lineHeight,
        gap: '0.3em',
      }}
    >
      {words.map((word, i) => {
        const wordProgress = spring({
          frame: frame - delay - i * staggerDelay,
          fps,
          config: { damping: 25, stiffness: 100 },
        });

        const y = interpolate(Math.max(0, wordProgress), [0, 1], [20, 0]);
        const opacity = interpolate(
          Math.max(0, wordProgress),
          [0, 0.5, 1],
          [0, 0.7, 1]
        );

        return (
          <span
            key={i}
            style={{
              color,
              transform: `translateY(${y}px)`,
              opacity,
              display: 'inline-block',
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

// Pull-up letters effect (premium feel)
export const LettersPullUp: React.FC<{
  text: string;
  delay?: number;
  fontSize?: number;
  fontWeight?: number;
  gradient?: boolean;
}> = ({
  text,
  delay = 0,
  fontSize = 72,
  fontWeight = 700,
  gradient = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const letters = text.split('');

  return (
    <div
      style={{
        display: 'flex',
        fontSize,
        fontWeight,
        overflow: 'hidden',
      }}
    >
      {letters.map((letter, i) => {
        const letterProgress = spring({
          frame: frame - delay - i * 1.5,
          fps,
          config: { damping: 15, stiffness: 200 },
        });

        const y = interpolate(Math.max(0, letterProgress), [0, 1], [fontSize, 0]);
        const opacity = Math.max(0, letterProgress);

        const letterStyle: React.CSSProperties = {
          transform: `translateY(${y}px)`,
          opacity,
          display: 'inline-block',
          whiteSpace: letter === ' ' ? 'pre' : 'normal',
          ...(gradient
            ? {
                background: `linear-gradient(180deg, ${colors.text.primary} 0%, rgba(200,210,230,0.9) 100%)`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }
            : { color: colors.text.primary }),
        };

        return (
          <span key={i} style={letterStyle}>
            {letter}
          </span>
        );
      })}
    </div>
  );
};

// Gradual spacing reveal (elegant expansion)
export const GradualSpacing: React.FC<{
  text: string;
  delay?: number;
  fontSize?: number;
  color?: string;
  fontWeight?: number;
}> = ({
  text,
  delay = 0,
  fontSize = 24,
  color = colors.text.secondary,
  fontWeight = 500,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 40, stiffness: 60 },
  });

  const letterSpacing = interpolate(
    Math.max(0, progress),
    [0, 1],
    [0.5, 0.1]
  );
  const opacity = interpolate(
    Math.max(0, progress),
    [0, 0.3, 1],
    [0, 0.5, 1]
  );

  return (
    <div
      style={{
        fontSize,
        fontWeight,
        color,
        letterSpacing: `${letterSpacing}em`,
        opacity,
        textTransform: 'uppercase',
      }}
    >
      {text}
    </div>
  );
};

// Typing effect with cursor
export const TypingText: React.FC<{
  text: string;
  delay?: number;
  fontSize?: number;
  color?: string;
  typingSpeed?: number;
  showCursor?: boolean;
}> = ({
  text,
  delay = 0,
  fontSize = 24,
  color = colors.text.primary,
  typingSpeed = 2,
  showCursor = true,
}) => {
  const frame = useCurrentFrame();

  const effectiveFrame = Math.max(0, frame - delay);
  const charCount = Math.min(
    Math.floor(effectiveFrame / typingSpeed),
    text.length
  );
  const displayText = text.slice(0, charCount);
  const cursorBlink = Math.floor(frame / 15) % 2 === 0;

  return (
    <div
      style={{
        fontSize,
        color,
        fontFamily: 'monospace',
        display: 'flex',
      }}
    >
      <span>{displayText}</span>
      {showCursor && charCount < text.length && (
        <span
          style={{
            opacity: cursorBlink ? 1 : 0,
            marginLeft: 2,
          }}
        >
          |
        </span>
      )}
    </div>
  );
};

// Glowing text with pulse
export const GlowingText: React.FC<{
  text: string;
  delay?: number;
  fontSize?: number;
  color?: string;
  glowColor?: string;
  fontWeight?: number;
}> = ({
  text,
  delay = 0,
  fontSize = 48,
  color = colors.text.primary,
  glowColor = colors.primary.accent,
  fontWeight = 600,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entryProgress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 30, stiffness: 80 },
  });

  // Subtle pulsing glow after entry
  const pulsePhase = Math.sin((frame - delay) * 0.08);
  const glowIntensity = interpolate(pulsePhase, [-1, 1], [15, 25]);

  const opacity = Math.max(0, entryProgress);
  const scale = interpolate(Math.max(0, entryProgress), [0, 1], [0.95, 1]);

  return (
    <div
      style={{
        fontSize,
        fontWeight,
        color,
        opacity,
        transform: `scale(${scale})`,
        textShadow: `0 0 ${glowIntensity}px ${glowColor}, 0 0 ${glowIntensity * 2}px ${glowColor}40`,
      }}
    >
      {text}
    </div>
  );
};

// Rotating words (cycle through options)
export const RotatingWords: React.FC<{
  words: string[];
  delay?: number;
  fontSize?: number;
  color?: string;
  fontWeight?: number;
  cycleDuration?: number;
}> = ({
  words,
  delay = 0,
  fontSize = 48,
  color = colors.primary.accent,
  fontWeight = 600,
  cycleDuration = 60,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const effectiveFrame = Math.max(0, frame - delay);
  const currentIndex = Math.floor(effectiveFrame / cycleDuration) % words.length;
  const localFrame = effectiveFrame % cycleDuration;

  const entryProgress = spring({
    frame: localFrame,
    fps,
    config: { damping: 20, stiffness: 120 },
  });

  const exitProgress =
    localFrame > cycleDuration - 15
      ? spring({
          frame: localFrame - (cycleDuration - 15),
          fps,
          config: { damping: 20, stiffness: 120 },
        })
      : 0;

  const y = interpolate(Math.max(0, entryProgress), [0, 1], [30, 0]);
  const exitY = interpolate(Math.max(0, exitProgress), [0, 1], [0, -30]);
  const opacity = interpolate(
    Math.max(0, entryProgress) - Math.max(0, exitProgress),
    [0, 1],
    [0, 1]
  );

  return (
    <div
      style={{
        fontSize,
        fontWeight,
        color,
        transform: `translateY(${y + exitY}px)`,
        opacity: Math.max(0, opacity),
      }}
    >
      {words[currentIndex]}
    </div>
  );
};

// Number counter animation
export const CountUp: React.FC<{
  target: number;
  delay?: number;
  fontSize?: number;
  color?: string;
  fontWeight?: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
}> = ({
  target,
  delay = 0,
  fontSize = 64,
  color = colors.primary.accent,
  fontWeight = 700,
  prefix = '',
  suffix = '',
  duration = 60,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 50, stiffness: 60 },
  });

  const currentValue = Math.round(
    interpolate(Math.max(0, progress), [0, 1], [0, target])
  );

  return (
    <div
      style={{
        fontSize,
        fontWeight,
        color,
        fontVariantNumeric: 'tabular-nums',
      }}
    >
      {prefix}
      {currentValue.toLocaleString()}
      {suffix}
    </div>
  );
};

// Subtitle with fade and slide
export const Subtitle: React.FC<{
  text: string;
  delay?: number;
  fontSize?: number;
  maxWidth?: number;
}> = ({ text, delay = 0, fontSize = 24, maxWidth = 800 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 30, stiffness: 80 },
  });

  const y = interpolate(Math.max(0, progress), [0, 1], [30, 0]);
  const opacity = interpolate(Math.max(0, progress), [0, 0.5, 1], [0, 0.6, 1]);

  return (
    <div
      style={{
        fontSize,
        fontWeight: 400,
        color: colors.text.muted,
        lineHeight: 1.6,
        maxWidth,
        textAlign: 'center',
        transform: `translateY(${y}px)`,
        opacity,
      }}
    >
      {text}
    </div>
  );
};
