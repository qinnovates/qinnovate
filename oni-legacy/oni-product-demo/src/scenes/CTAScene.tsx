/**
 * CTA Scene - Call to action with terminal animation
 * Features: Typing effect, glassmorphism buttons, smooth reveals
 */

import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';
import { FloatingParticles } from '../components/Particles';
import { NeuralFlow } from '../components/NeuralFlow';
import { LettersPullUp, BlurInText } from '../components/TextAnimations';
import { colors, typography } from '../data/oni-theme';

export const CTAScene: React.FC = () => {
  const frame = useCurrentFrame();

  // Terminal typing animation with package cycling
  const typingDelay = 120;
  const baseCommand = 'pip install oni-';
  const packages = ['framework', 'tara', 'academy'];

  // Timing for each package cycle (in frames after typingDelay)
  const typingSpeed = 2; // frames per character
  const baseTypingDuration = baseCommand.length * typingSpeed; // ~32 frames for base
  const pauseBetweenCycles = 45; // pause after completing each package
  const backspaceSpeed = 1.5; // faster backspace

  // Calculate which package and what state we're in
  const frameAfterBase = Math.max(0, frame - typingDelay - baseTypingDuration);

  // Each cycle: type package + pause + backspace package
  const getPackageCycleDuration = (pkg: string) => {
    return pkg.length * typingSpeed + pauseBetweenCycles + pkg.length * backspaceSpeed;
  };

  // Calculate current display text
  const getCurrentText = () => {
    if (frame < typingDelay) return '';

    const frameInTyping = frame - typingDelay;

    // Still typing base command
    if (frameInTyping < baseTypingDuration) {
      const charsTyped = Math.floor(frameInTyping / typingSpeed);
      return baseCommand.substring(0, charsTyped);
    }

    // After base command, cycle through packages
    let cycleFrame = frameAfterBase;
    let packageIndex = 0;

    while (packageIndex < packages.length) {
      const pkg = packages[packageIndex];
      const typeTime = pkg.length * typingSpeed;
      const totalCycleTime = getPackageCycleDuration(pkg);

      // Last package doesn't backspace
      if (packageIndex === packages.length - 1) {
        const charsTyped = Math.min(pkg.length, Math.floor(cycleFrame / typingSpeed));
        return baseCommand + pkg.substring(0, charsTyped);
      }

      if (cycleFrame < totalCycleTime) {
        // Within this package's cycle
        if (cycleFrame < typeTime) {
          // Typing phase
          const charsTyped = Math.floor(cycleFrame / typingSpeed);
          return baseCommand + pkg.substring(0, charsTyped);
        } else if (cycleFrame < typeTime + pauseBetweenCycles) {
          // Pause phase - full package shown
          return baseCommand + pkg;
        } else {
          // Backspace phase
          const backspaceFrame = cycleFrame - typeTime - pauseBetweenCycles;
          const charsDeleted = Math.floor(backspaceFrame / backspaceSpeed);
          const remaining = Math.max(0, pkg.length - charsDeleted);
          return baseCommand + pkg.substring(0, remaining);
        }
      }

      cycleFrame -= totalCycleTime;
      packageIndex++;
    }

    // Default to last package fully typed
    return baseCommand + packages[packages.length - 1];
  };

  const currentText = getCurrentText();

  // Background glow pulse
  const glowPulse = interpolate(
    Math.sin(frame * 0.04),
    [-1, 1],
    [0.15, 0.3]
  );

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at center, ${colors.primary.accentPurple}${Math.round(glowPulse * 255).toString(16).padStart(2, '0')} 0%, ${colors.primary.main} 40%, ${colors.primary.dark} 100%)`,
      }}
    >
      {/* Subtle particles */}
      <FloatingParticles
        count={60}
        color={colors.primary.accent}
        speed={0.2}
        minSize={1}
        maxSize={3}
      />

      {/* Content container */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          gap: 40,
        }}
      >
        {/* Main CTA with letter animation */}
        <LettersPullUp
          text="Ready to secure the neural frontier?"
          delay={0}
          fontSize={52}
          fontWeight={600}
          gradient={true}
        />

        {/* Subtitle */}
        <BlurInText
          text="Get started in seconds"
          delay={30}
          fontSize={22}
          color={colors.text.muted}
          fontWeight={400}
        />

        {/* Terminal window with glassmorphism */}
        <div
          style={{
            marginTop: 20,
            opacity: interpolate(frame - 80, [0, 30], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }),
            transform: `scale(${interpolate(
              frame - 80,
              [0, 30],
              [0.95, 1],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            )}) translateY(${interpolate(
              frame - 80,
              [0, 30],
              [20, 0],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            )}px)`,
          }}
        >
          {/* Terminal header */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(45,45,45,0.9) 0%, rgba(30,30,30,0.95) 100%)',
              backdropFilter: 'blur(20px)',
              padding: '14px 20px',
              borderTopLeftRadius: 14,
              borderTopRightRadius: 14,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ff5f56' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ffbd2e' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#27c93f' }} />
            <span style={{ marginLeft: 16, color: colors.text.muted, fontSize: 13 }}>
              Terminal
            </span>
          </div>

          {/* Terminal body */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(20,20,25,0.95) 0%, rgba(15,15,20,0.98) 100%)',
              backdropFilter: 'blur(20px)',
              padding: '28px 36px',
              borderBottomLeftRadius: 14,
              borderBottomRightRadius: 14,
              fontFamily: typography.fontFamily.mono,
              fontSize: 22,
              minWidth: 580,
              border: '1px solid rgba(255,255,255,0.05)',
              borderTop: 'none',
            }}
          >
            <span style={{ color: colors.security.safe }}>$ </span>
            <span style={{ color: colors.text.primary }}>{currentText}</span>
            <span
              style={{
                color: colors.text.primary,
                opacity: Math.sin(frame * 0.15) > 0 ? 1 : 0,
                marginLeft: 2,
              }}
            >
              |
            </span>
          </div>
        </div>

        {/* Single primary CTA button */}
        <div
          style={{
            marginTop: 30,
            opacity: interpolate(frame - 280, [0, 30], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }),
            transform: `translateY(${interpolate(
              frame - 280,
              [0, 30],
              [20, 0],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            )}px)`,
          }}
        >
          <div
            style={{
              padding: '22px 48px',
              background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(220,220,225,0.9) 100%)',
              borderRadius: 14,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 14,
              boxShadow: '0 0 40px rgba(255,255,255,0.15)',
              border: '1px solid rgba(255,255,255,0.2)',
            }}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M12 2C6.48 2 2 6.48 2 12C2 16.42 4.87 20.17 8.84 21.5C9.34 21.58 9.5 21.27 9.5 21C9.5 20.77 9.5 20.14 9.5 19.31C6.73 19.91 6.14 17.97 6.14 17.97C5.68 16.81 5.03 16.5 5.03 16.5C4.12 15.88 5.1 15.9 5.1 15.9C6.1 15.97 6.63 16.93 6.63 16.93C7.5 18.45 8.97 18 9.54 17.76C9.63 17.11 9.89 16.67 10.17 16.42C7.95 16.17 5.62 15.31 5.62 11.5C5.62 10.39 6 9.5 6.65 8.79C6.55 8.54 6.2 7.5 6.75 6.15C6.75 6.15 7.59 5.88 9.5 7.17C10.29 6.95 11.15 6.84 12 6.84C12.85 6.84 13.71 6.95 14.5 7.17C16.41 5.88 17.25 6.15 17.25 6.15C17.8 7.5 17.45 8.54 17.35 8.79C18 9.5 18.38 10.39 18.38 11.5C18.38 15.32 16.04 16.16 13.81 16.41C14.17 16.72 14.5 17.33 14.5 18.26C14.5 19.6 14.5 20.68 14.5 21C14.5 21.27 14.66 21.59 15.17 21.5C19.14 20.16 22 16.42 22 12C22 6.48 17.52 2 12 2Z" fill="#1a1a2e" />
            </svg>
            <span
              style={{
                fontSize: 18,
                color: '#1a1a2e',
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}
            >
              View Documentation on GitHub
            </span>
          </div>
        </div>

        {/* Secondary text links */}
        <div
          style={{
            marginTop: 24,
            fontSize: 15,
            color: colors.text.muted,
            opacity: interpolate(frame - 320, [0, 30], [0, 0.8], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }),
          }}
        >
          Or explore the{' '}
          <span style={{ color: colors.primary.accent }}>research paper</span>
          {' '}and{' '}
          <span style={{ color: colors.primary.accent }}>interactive playground</span>
        </div>

        {/* GitHub URL with subtle animation */}
        <div
          style={{
            marginTop: 20,
            fontSize: 16,
            color: colors.text.muted,
            fontFamily: typography.fontFamily.mono,
            opacity: interpolate(frame - 360, [0, 30], [0, 0.7], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }),
            letterSpacing: '0.02em',
          }}
        >
          qinnovate.com
        </div>

        {/* Neural flow at bottom */}
        <div
          style={{
            position: 'absolute',
            bottom: 80,
            opacity: 0.4,
          }}
        >
          <NeuralFlow
            state={frame > 200 ? 'reactive' : 'resting'}
            width={600}
            height={40}
            intensity={0.4}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
