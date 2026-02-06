import React from 'react';
import { useCurrentFrame, spring, useVideoConfig, Img, staticFile } from 'remotion';
import { colors, typography } from '../data/oni-theme';

interface TitleCardProps {
  showSubtitle?: boolean;
  subtitle?: string;
}

export const TitleCard: React.FC<TitleCardProps> = ({
  showSubtitle = true,
  subtitle = "The OSI of Mind",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo scale animation
  const logoScale = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Logo glow animation
  const glowOpacity = spring({
    frame: frame - 10,
    fps,
    config: { damping: 100 },
  });

  // Subtitle fade in
  const subtitleOpacity = spring({
    frame: frame - 20,
    fps,
    config: { damping: 100 },
  });

  const subtitleY = spring({
    frame: frame - 20,
    fps,
    config: { damping: 20, stiffness: 100 },
  });

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        width: '100%',
      }}
    >
      {/* Neural glow effect behind logo */}
      <div
        style={{
          position: 'absolute',
          width: 600,
          height: 600,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${colors.primary.accent}22 0%, transparent 70%)`,
          opacity: Math.max(0, glowOpacity),
          filter: 'blur(60px)',
        }}
      />

      {/* ONI Banner Logo */}
      <div
        style={{
          transform: `scale(${Math.max(0, logoScale)})`,
          marginBottom: 40,
        }}
      >
        <Img
          src={staticFile("assets/ONI_Banner_Logo.png")}
          style={{
            width: 800,
            objectFit: 'contain',
          }}
        />
      </div>

      {/* Subtitle */}
      {showSubtitle && (
        <div
          style={{
            opacity: Math.max(0, subtitleOpacity),
            transform: `translateY(${(1 - Math.max(0, subtitleY)) * 30}px)`,
            fontSize: typography.fontSize.subtitle,
            color: colors.primary.accent,
            fontWeight: 300,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
          }}
        >
          {subtitle}
        </div>
      )}
    </div>
  );
};
