import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import { colors, typography } from '../data/oni-theme';

interface TextRevealProps {
  text: string;
  delay?: number;
  style?: React.CSSProperties;
  fontSize?: number;
  color?: string;
}

export const TextReveal: React.FC<TextRevealProps> = ({
  text,
  delay = 0,
  style = {},
  fontSize = typography.fontSize.body,
  color = colors.text.primary,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = spring({
    frame: frame - delay,
    fps,
    config: { damping: 100, stiffness: 200 },
  });

  const translateY = interpolate(
    spring({
      frame: frame - delay,
      fps,
      config: { damping: 100, stiffness: 200 },
    }),
    [0, 1],
    [20, 0]
  );

  return (
    <div
      style={{
        opacity: Math.max(0, opacity),
        transform: `translateY(${translateY}px)`,
        fontSize,
        color,
        fontWeight: 500,
        lineHeight: 1.4,
        ...style,
      }}
    >
      {text}
    </div>
  );
};

// Word-by-word reveal animation
interface WordRevealProps {
  text: string;
  startDelay?: number;
  wordDelay?: number;
  style?: React.CSSProperties;
  fontSize?: number;
  color?: string;
}

export const WordReveal: React.FC<WordRevealProps> = ({
  text,
  startDelay = 0,
  wordDelay = 3,
  style = {},
  fontSize = typography.fontSize.body,
  color = colors.text.primary,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(' ');

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.3em',
        fontSize,
        color,
        fontWeight: 500,
        lineHeight: 1.4,
        ...style,
      }}
    >
      {words.map((word, index) => {
        const wordStart = startDelay + index * wordDelay;
        const opacity = spring({
          frame: frame - wordStart,
          fps,
          config: { damping: 100, stiffness: 200 },
        });

        return (
          <span
            key={index}
            style={{
              opacity: Math.max(0, opacity),
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
