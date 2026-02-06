/**
 * Coherence Scene - The Coherence Score visualization
 * Features: Animated gauge, formula reveal, component cards
 */

import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';
import { CoherenceGauge } from '../components/CoherenceGauge';
import { FloatingParticles } from '../components/Particles';
import { NeuralFlow } from '../components/NeuralFlow';
import { LettersPullUp, BlurInText } from '../components/TextAnimations';
import { colors, typography } from '../data/oni-theme';

// Threshold value for defense activation
const COHERENCE_THRESHOLD = 0.65;

export const CoherenceScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase timing - Coherence intro, threshold demo, then Scale-Frequency
  const showCoherenceIntro = frame < 280;
  const showThresholdDemo = frame >= 280 && frame < 500;
  const showScaleFreq = frame >= 500;
  const showCoherence = frame < 500;

  // Animate coherence value over time - NOW INCLUDES A DROP BELOW THRESHOLD
  const coherenceValue = interpolate(
    frame,
    [0, 150, 280, 320, 360, 420, 500],
    [0.35, 0.82, 0.85, 0.45, 0.42, 0.78, 0.88], // Drops to 0.45 at frame 320
    { extrapolateRight: 'clamp' }
  );

  // Detect threshold breach
  const isBelowThreshold = coherenceValue < COHERENCE_THRESHOLD;
  const breachStarted = frame >= 300 && frame < 400;

  // Show interactive demo hint (during coherence phase, before threshold demo)
  const showDemo = frame > 200 && frame < 270;

  // Fade out coherence elements when transitioning to scale-frequency
  const coherenceFadeOut = interpolate(frame, [480, 520], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Background glow based on coherence
  const bgGlow = interpolate(
    coherenceValue,
    [0.3, 0.7, 0.9],
    [0.05, 0.1, 0.15]
  );

  // Scale-Frequency animation
  const sfProgress = interpolate(frame - 500, [0, 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Animated scale and frequency values for visualization
  const scaleValue = interpolate(frame - 520, [0, 200], [10, 1000], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const freqValue = interpolate(frame - 520, [0, 200], [100, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const kConstant = scaleValue * freqValue; // Should stay ~1000

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at center, ${coherenceValue > 0.7 ? colors.security.safe : colors.primary.accentPurple}${Math.round(bgGlow * 255).toString(16).padStart(2, '0')} 0%, ${colors.primary.main} 40%, ${colors.primary.dark} 100%)`,
      }}
    >
      {/* Particles that respond to coherence */}
      <FloatingParticles
        count={Math.round(30 + coherenceValue * 40)}
        color={coherenceValue > 0.7 ? colors.security.safe : colors.primary.accent}
        speed={0.1 + coherenceValue * 0.1}
        minSize={1}
        maxSize={3}
      />

      {/* Main content */}
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
        {/* ===== COHERENCE SECTION ===== */}
        {showCoherenceIntro && (
          <>
            {/* Title with letter animation */}
            <LettersPullUp
              text="The Coherence Score"
              delay={0}
              fontSize={56}
              fontWeight={700}
              gradient={true}
            />

            {/* Subtitle */}
            <BlurInText
              text="A unified metric for neural security"
              delay={20}
              fontSize={22}
              color={colors.text.muted}
              fontWeight={400}
            />
          </>
        )}

        {/* Threshold Demo Title */}
        {showThresholdDemo && (
          <div
            style={{
              position: 'absolute',
              bottom: 140,
              left: 0,
              right: 0,
              textAlign: 'center',
              opacity: interpolate(frame - 280, [0, 30], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }) * coherenceFadeOut,
            }}
          >
            <div
              style={{
                fontSize: 24,
                color: colors.text.secondary,
                fontWeight: 500,
              }}
            >
              When coherence drops below threshold...
            </div>
            <div
              style={{
                fontSize: 18,
                color: colors.text.muted,
                marginTop: 8,
              }}
            >
              automated defense mechanisms activate instantly
            </div>
          </div>
        )}

        {/* ===== SCALE-FREQUENCY SECTION ===== */}
        {showScaleFreq && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 30,
              opacity: sfProgress,
              transform: `translateY(${interpolate(sfProgress, [0, 1], [30, 0])}px)`,
            }}
          >
            {/* Title */}
            <div
              style={{
                fontSize: 48,
                fontWeight: 700,
                color: '#ffffff',
                fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
              }}
            >
              Scale-Frequency Invariant
            </div>

            {/* Formula */}
            <div
              style={{
                fontFamily: typography.fontFamily.mono,
                fontSize: 36,
                color: colors.primary.accent,
                padding: '20px 50px',
                backgroundColor: 'rgba(0, 0, 0, 0.4)',
                borderRadius: 12,
                border: `1px solid ${colors.primary.accent}44`,
              }}
            >
              f × S ≈ k
            </div>

            {/* Explanation */}
            <div
              style={{
                fontSize: 20,
                color: colors.text.secondary,
                maxWidth: 600,
                textAlign: 'center',
                lineHeight: 1.6,
              }}
            >
              Neural patterns maintain invariant relationships across scales
            </div>

            {/* Animated visualization */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 40,
                marginTop: 20,
                padding: '30px 50px',
                background: 'rgba(0,0,0,0.3)',
                borderRadius: 16,
                border: `1px solid ${colors.primary.accent}22`,
              }}
            >
              {/* Scale value */}
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 14, color: colors.text.muted, marginBottom: 8 }}>Scale (S)</div>
                <div
                  style={{
                    fontSize: 32,
                    fontFamily: typography.fontFamily.mono,
                    color: colors.biology.L11,
                    fontWeight: 600,
                  }}
                >
                  {scaleValue.toFixed(0)}
                </div>
                {/* Scale bar */}
                <div
                  style={{
                    width: 120,
                    height: 8,
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    borderRadius: 4,
                    marginTop: 10,
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${(scaleValue / 1000) * 100}%`,
                      height: '100%',
                      backgroundColor: colors.biology.L11,
                      borderRadius: 4,
                    }}
                  />
                </div>
              </div>

              {/* Multiplication symbol */}
              <div style={{ fontSize: 36, color: colors.text.muted }}>×</div>

              {/* Frequency value */}
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 14, color: colors.text.muted, marginBottom: 8 }}>Frequency (f)</div>
                <div
                  style={{
                    fontSize: 32,
                    fontFamily: typography.fontFamily.mono,
                    color: colors.gateway.L8,
                    fontWeight: 600,
                  }}
                >
                  {freqValue.toFixed(1)} Hz
                </div>
                {/* Frequency bar */}
                <div
                  style={{
                    width: 120,
                    height: 8,
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    borderRadius: 4,
                    marginTop: 10,
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${(freqValue / 100) * 100}%`,
                      height: '100%',
                      backgroundColor: colors.gateway.L8,
                      borderRadius: 4,
                    }}
                  />
                </div>
              </div>

              {/* Equals symbol */}
              <div style={{ fontSize: 36, color: colors.text.muted }}>≈</div>

              {/* k constant */}
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 14, color: colors.text.muted, marginBottom: 8 }}>Constant (k)</div>
                <div
                  style={{
                    fontSize: 32,
                    fontFamily: typography.fontFamily.mono,
                    color: colors.security.safe,
                    fontWeight: 600,
                  }}
                >
                  {kConstant.toFixed(0)}
                </div>
                {/* Stability indicator */}
                <div
                  style={{
                    fontSize: 12,
                    color: colors.security.safe,
                    marginTop: 10,
                  }}
                >
                  ✓ Invariant
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Coherence gauge - during coherence intro and threshold demo */}
        {showCoherence && (
          <div
            style={{
              marginTop: showThresholdDemo ? 180 : 20,
              opacity: interpolate(frame, [40, 80], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }) * coherenceFadeOut,
              transform: `scale(${interpolate(frame, [40, 80], [0.9, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              })}) ${showThresholdDemo ? 'scale(0.85)' : ''}`,
              // Add red glow when below threshold
              filter: isBelowThreshold
                ? `drop-shadow(0 0 30px ${colors.security.danger}66)`
                : 'none',
              transition: 'filter 0.3s ease',
            }}
          >
            <CoherenceGauge
              value={coherenceValue}
              showFormula={!showThresholdDemo}
              animated={true}
              showThreshold={showThresholdDemo}
              threshold={COHERENCE_THRESHOLD}
            />
          </div>
        )}

        {/* Component explanation cards - matching formula: e^(−(σ²φ + σ²τ + σ²γ)) */}
        {showCoherenceIntro && (
          <div
            style={{
              display: 'flex',
              gap: 24,
              marginTop: 30,
              opacity: coherenceFadeOut,
            }}
          >
            {[
              { label: 'σ²φ', name: 'Phase Variance', desc: 'Neural oscillation alignment', color: colors.biology.L11 },
              { label: 'σ²τ', name: 'Timing Variance', desc: 'Temporal jitter precision', color: colors.gateway.L8 },
              { label: 'σ²γ', name: 'Frequency Variance', desc: 'Band-specific stability', color: colors.silicon.L3 },
            ].map((item, index) => {
              const cardProgress = spring({
                frame: frame - 180 - index * 12,
                fps,
                config: { damping: 25, stiffness: 100 },
              });

              return (
                <div
                  key={item.label}
                  style={{
                    padding: '20px 28px',
                    background: `linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%)`,
                    backdropFilter: 'blur(15px)',
                    borderRadius: 14,
                    border: `1px solid ${item.color}22`,
                    textAlign: 'center',
                    minWidth: 200,
                    opacity: Math.max(0, cardProgress),
                    transform: `translateY(${interpolate(
                      Math.max(0, cardProgress),
                      [0, 1],
                      [30, 0]
                    )}px)`,
                  }}
                >
                  <div
                    style={{
                      fontSize: 24,
                      color: item.color,
                      fontFamily: typography.fontFamily.mono,
                      marginBottom: 6,
                      fontWeight: 700,
                    }}
                  >
                    {item.label}
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      color: colors.text.secondary,
                      marginBottom: 8,
                      fontWeight: 500,
                    }}
                  >
                    {item.name}
                  </div>
                  <div
                    style={{
                      fontSize: 13,
                      color: colors.text.muted,
                      lineHeight: 1.4,
                    }}
                  >
                    {item.desc}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Interactive demo callout */}
        {showDemo && (
          <div
            style={{
              marginTop: 30,
              padding: '16px 28px',
              background: `${colors.primary.accent}08`,
              backdropFilter: 'blur(10px)',
              borderRadius: 12,
              border: `1px solid ${colors.primary.accent}22`,
              display: 'flex',
              alignItems: 'center',
              gap: 14,
              opacity: interpolate(frame - 200, [0, 30], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }) * coherenceFadeOut,
              transform: `translateY(${interpolate(
                frame - 200,
                [0, 30],
                [20, 0],
                { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
              )}px)`,
            }}
          >
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: colors.security.safe,
                boxShadow: `0 0 10px ${colors.security.safe}`,
              }}
            />
            <span style={{ fontSize: 16, color: colors.text.secondary }}>
              Try it yourself in the
            </span>
            <span
              style={{
                fontSize: 16,
                color: colors.primary.accent,
                fontWeight: 600,
              }}
            >
              Interactive Playground →
            </span>
          </div>
        )}

        {/* ===== THRESHOLD DEFENSE VISUALIZATION ===== */}
        {showThresholdDemo && (
          <div
            style={{
              position: 'absolute',
              top: 80,
              left: 0,
              right: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              opacity: interpolate(frame - 280, [0, 30], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }) * coherenceFadeOut,
            }}
          >
            {/* Threshold Alert Header */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                padding: '14px 32px',
                background: isBelowThreshold
                  ? `${colors.security.danger}22`
                  : `${colors.security.safe}15`,
                borderRadius: 12,
                border: `2px solid ${isBelowThreshold ? colors.security.danger : colors.security.safe}`,
                transition: 'all 0.3s ease',
              }}
            >
              {/* Shield icon */}
              <div
                style={{
                  width: 40,
                  height: 40,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {isBelowThreshold ? (
                  // Alert shield - breach detected
                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M12 2L20 6V11C20 16 16 20 12 21C8 20 4 16 4 11V6L12 2Z"
                      stroke={colors.security.danger}
                      strokeWidth="2"
                      fill={`${colors.security.danger}33`}
                    />
                    <path
                      d="M12 8V12M12 16H12.01"
                      stroke={colors.security.danger}
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                ) : (
                  // Check shield - secure
                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M12 2L20 6V11C20 16 16 20 12 21C8 20 4 16 4 11V6L12 2Z"
                      stroke={colors.security.safe}
                      strokeWidth="2"
                      fill={`${colors.security.safe}33`}
                    />
                    <path
                      d="M9 12L11 14L15 10"
                      stroke={colors.security.safe}
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                )}
              </div>

              {/* Status text */}
              <div>
                <div
                  style={{
                    fontSize: 20,
                    fontWeight: 700,
                    color: isBelowThreshold ? colors.security.danger : colors.security.safe,
                    letterSpacing: '0.02em',
                  }}
                >
                  {isBelowThreshold ? '⚠️ THRESHOLD BREACH' : '✓ SYSTEM NOMINAL'}
                </div>
                <div
                  style={{
                    fontSize: 14,
                    color: colors.text.muted,
                    marginTop: 2,
                  }}
                >
                  Threshold: Cₛ ≥ {COHERENCE_THRESHOLD.toFixed(2)} | Current: {coherenceValue.toFixed(2)}
                </div>
              </div>

              {/* Animated pulse when breached */}
              {isBelowThreshold && (
                <div
                  style={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    background: colors.security.danger,
                    boxShadow: `0 0 ${20 + Math.sin(frame * 0.3) * 10}px ${colors.security.danger}`,
                    animation: 'pulse 0.5s infinite',
                  }}
                />
              )}
            </div>

            {/* Attack Type Indicator - shows during breach */}
            {breachStarted && (
              <div
                style={{
                  marginTop: 20,
                  display: 'flex',
                  gap: 16,
                  opacity: interpolate(frame - 310, [0, 20], [0, 1], {
                    extrapolateLeft: 'clamp',
                    extrapolateRight: 'clamp',
                  }),
                }}
              >
                {[
                  { type: 'MRI Interference', icon: '🧲', active: frame >= 310 && frame < 340 },
                  { type: 'EM Disruption', icon: '⚡', active: frame >= 340 && frame < 370 },
                  { type: 'Injection Attack', icon: '💉', active: frame >= 370 },
                ].map((attack, i) => (
                  <div
                    key={attack.type}
                    style={{
                      padding: '12px 20px',
                      background: attack.active
                        ? `${colors.security.danger}33`
                        : 'rgba(255,255,255,0.05)',
                      borderRadius: 10,
                      border: `1px solid ${attack.active ? colors.security.danger : 'rgba(255,255,255,0.1)'}`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                      transform: `scale(${attack.active ? 1.05 : 1})`,
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <span style={{ fontSize: 20 }}>{attack.icon}</span>
                    <span
                      style={{
                        fontSize: 14,
                        color: attack.active ? colors.security.danger : colors.text.muted,
                        fontWeight: attack.active ? 600 : 400,
                      }}
                    >
                      {attack.type}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Defense Activation Message */}
            {isBelowThreshold && (
              <div
                style={{
                  marginTop: 24,
                  padding: '16px 28px',
                  background: `linear-gradient(135deg, ${colors.security.danger}22 0%, ${colors.primary.accentPurple}22 100%)`,
                  borderRadius: 12,
                  border: `1px solid ${colors.security.danger}44`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 14,
                  opacity: interpolate(frame - 325, [0, 20], [0, 1], {
                    extrapolateLeft: 'clamp',
                    extrapolateRight: 'clamp',
                  }),
                }}
              >
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: colors.security.warning,
                    boxShadow: `0 0 10px ${colors.security.warning}`,
                  }}
                />
                <span style={{ fontSize: 16, color: colors.text.primary, fontWeight: 500 }}>
                  Automated defense mechanisms{' '}
                  <span style={{ color: colors.security.warning, fontWeight: 700 }}>ACTIVATED</span>
                </span>
              </div>
            )}

            {/* Recovery indicator */}
            {frame >= 400 && frame < 480 && (
              <div
                style={{
                  marginTop: 20,
                  padding: '14px 24px',
                  background: `${colors.security.safe}15`,
                  borderRadius: 10,
                  border: `1px solid ${colors.security.safe}44`,
                  opacity: interpolate(frame - 400, [0, 20], [0, 1], {
                    extrapolateLeft: 'clamp',
                    extrapolateRight: 'clamp',
                  }),
                }}
              >
                <span style={{ fontSize: 15, color: colors.security.safe, fontWeight: 500 }}>
                  ✓ Threat neutralized — Coherence restored to {coherenceValue.toFixed(2)}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Neural flow at bottom */}
        <div
          style={{
            position: 'absolute',
            bottom: 80,
            opacity: 0.4,
          }}
        >
          <NeuralFlow
            state={coherenceValue > 0.7 ? 'reactive' : 'resting'}
            width={500}
            height={40}
            intensity={coherenceValue * 0.6}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
