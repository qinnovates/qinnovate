/**
 * TARA Stack Scene - 3D brain visualization
 * Features: React Three Fiber brain, particle effects, glassmorphism cards
 */

import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';
import { Brain2D } from '../components/Brain2D';
import { NeuralFlow } from '../components/NeuralFlow';
import { FloatingParticles } from '../components/Particles';
import { LettersPullUp, BlurInText } from '../components/TextAnimations';
import { AnomalyDetectionViz } from '../components/AnomalyDetectionViz';
import { colors, typography } from '../data/oni-theme';

// Feature cards for TARA stack - professional icons for academic audience
const features = [
  {
    title: 'Brain Topology',
    description: 'Real-time 3D visualization of neural activity patterns',
    iconType: 'topology' as const,
    color: colors.biology.L11,
  },
  {
    title: 'Attack Simulator',
    description: 'Test defenses across all 14 layers',
    iconType: 'attack' as const,
    color: colors.security.danger,
  },
  {
    title: 'NSAM Monitor',
    description: 'Neural Signal Assurance flags anomalies',
    iconType: 'monitor' as const,
    color: colors.primary.accent,
  },
  {
    title: 'Privacy-First',
    subtitle: 'with you in mind',
    description: 'Only Cₛ scores transmitted—raw data stays local',
    iconType: 'privacy' as const,
    color: colors.primary.accentPurple,
  },
];

// Professional abstract icons (SVG-based)
const FeatureIcon: React.FC<{ type: 'topology' | 'attack' | 'monitor' | 'privacy'; color: string }> = ({ type, color }) => {
  if (type === 'topology') {
    return (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="3" stroke={color} strokeWidth="1.5" />
        <circle cx="12" cy="4" r="2" fill={color} />
        <circle cx="20" cy="12" r="2" fill={color} />
        <circle cx="12" cy="20" r="2" fill={color} />
        <circle cx="4" cy="12" r="2" fill={color} />
        <line x1="12" y1="6" x2="12" y2="9" stroke={color} strokeWidth="1" />
        <line x1="18" y1="12" x2="15" y2="12" stroke={color} strokeWidth="1" />
        <line x1="12" y1="18" x2="12" y2="15" stroke={color} strokeWidth="1" />
        <line x1="6" y1="12" x2="9" y2="12" stroke={color} strokeWidth="1" />
      </svg>
    );
  }
  if (type === 'attack') {
    return (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M12 2L15 8H21L16 12L18 20L12 16L6 20L8 12L3 8H9L12 2Z" stroke={color} strokeWidth="1.5" fill="none" />
        <circle cx="12" cy="11" r="2" fill={color} />
      </svg>
    );
  }
  if (type === 'privacy') {
    // Lock inside shield - privacy-first icon
    return (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M12 2L20 6V11C20 16 16 20 12 21C8 20 4 16 4 11V6L12 2Z" stroke={color} strokeWidth="1.5" fill="none" />
        <rect x="9" y="10" width="6" height="5" rx="1" stroke={color} strokeWidth="1.5" fill="none" />
        <path d="M10 10V8C10 6.9 10.9 6 12 6C13.1 6 14 6.9 14 8V10" stroke={color} strokeWidth="1.5" fill="none" />
        <circle cx="12" cy="12.5" r="1" fill={color} />
      </svg>
    );
  }
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
      <path d="M12 3L20 7V11C20 16 16 20 12 21C8 20 4 16 4 11V7L12 3Z" stroke={color} strokeWidth="1.5" fill="none" />
      <path d="M9 12L11 14L15 10" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export const TARAScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase control - TARA intro first, then anomaly detection
  const showTARAIntro = frame < 500;
  const showAnomalyDetection = frame >= 500;
  const showBrain = frame > 80 && showTARAIntro;
  const showFeatures = frame > 250 && showTARAIntro;

  // Title animation
  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 80 },
  });

  // Brain fade in
  const brainProgress = spring({
    frame: frame - 80,
    fps,
    config: { damping: 30, stiffness: 60 },
  });

  // Subtle glow pulse
  const glowPulse = interpolate(
    Math.sin(frame * 0.05),
    [-1, 1],
    [0.3, 0.6]
  );

  return (
    <AbsoluteFill
      style={{
        background: colors.gradients.innovation,
      }}
    >
      {/* Subtle particles */}
      <FloatingParticles
        count={50}
        color={colors.primary.accent}
        speed={0.15}
        minSize={1}
        maxSize={4}
      />

      {/* Content layout - TARA Intro Phase */}
      {showTARAIntro && (
      <div
        style={{
          display: 'flex',
          height: '100%',
          padding: 80,
          gap: 60,
          opacity: interpolate(frame, [480, 500], [1, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
        }}
      >
        {/* Left side - 3D Brain */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: Math.max(0, brainProgress),
            transform: `scale(${interpolate(
              Math.max(0, brainProgress),
              [0, 1],
              [0.9, 1]
            )})`,
          }}
        >
          {showBrain && (
            <div
              style={{
                filter: `drop-shadow(0 0 ${40 * glowPulse}px ${colors.primary.accent}44)`,
              }}
            >
              <Brain2D width={550} height={550} />
            </div>
          )}

          {/* Neural flow under brain */}
          <div style={{ marginTop: -40 }}>
            <NeuralFlow
              state={frame > 180 ? 'reactive' : 'resting'}
              width={350}
              height={45}
              intensity={0.5}
            />
          </div>
        </div>

        {/* Right side - Info */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            gap: 40,
          }}
        >
          {/* TARA Title with letters pull-up */}
          <div
            style={{
              opacity: Math.max(0, titleProgress),
            }}
          >
            <LettersPullUp
              text="TARA"
              delay={0}
              fontSize={72}
              fontWeight={700}
              gradient={true}
            />

            <div style={{ marginTop: 12 }}>
              <BlurInText
                text="Telemetry Analysis & Response Automation"
                delay={20}
                fontSize={18}
                color={colors.text.muted}
                fontWeight={400}
              />
            </div>
          </div>

          {/* Feature cards with staggered animation */}
          {showFeatures && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 16,
              }}
            >
              {features.map((feature, index) => {
                const cardProgress = spring({
                  frame: frame - 250 - index * 15,
                  fps,
                  config: { damping: 25, stiffness: 100 },
                });

                const cardX = interpolate(
                  Math.max(0, cardProgress),
                  [0, 1],
                  [80, 0]
                );

                return (
                  <div
                    key={feature.title}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 20,
                      padding: 20,
                      background: `linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%)`,
                      backdropFilter: 'blur(20px)',
                      borderRadius: 16,
                      border: `1px solid ${feature.color}22`,
                      opacity: Math.max(0, cardProgress),
                      transform: `translateX(${cardX}px)`,
                    }}
                  >
                    {/* Professional icon with subtle glow */}
                    <div
                      style={{
                        width: 52,
                        height: 52,
                        borderRadius: 14,
                        background: `${feature.color}15`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: `0 0 20px ${feature.color}33`,
                      }}
                    >
                      <FeatureIcon type={feature.iconType} color={feature.color} />
                    </div>

                    {/* Text */}
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          fontSize: 18,
                          fontWeight: 600,
                          color: colors.text.primary,
                          marginBottom: 4,
                          letterSpacing: '-0.01em',
                        }}
                      >
                        {feature.title}
                        {(feature as any).subtitle && (
                          <span style={{ fontStyle: 'italic', fontWeight: 400, marginLeft: 8, color: colors.text.muted }}>
                            {(feature as any).subtitle}
                          </span>
                        )}
                      </div>
                      <div
                        style={{
                          fontSize: 14,
                          color: colors.text.muted,
                          lineHeight: 1.4,
                        }}
                      >
                        {feature.description}
                      </div>
                    </div>

                    {/* Status indicator */}
                    <div
                      style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: feature.color,
                        boxShadow: `0 0 10px ${feature.color}`,
                      }}
                    />
                  </div>
                );
              })}
            </div>
          )}

        </div>
      </div>
      )}

      {/* ===== ANOMALY DETECTION PHASE ===== */}
      {showAnomalyDetection && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 40,
            opacity: interpolate(frame - 500, [0, 40], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }),
          }}
        >
          {/* Title */}
          <div
            style={{
              fontSize: 48,
              fontWeight: 700,
              color: '#ffffff',
              fontFamily: "-apple-system, 'SF Pro Display', sans-serif",
              marginBottom: 12,
              transform: `translateY(${interpolate(frame - 500, [0, 40], [20, 0], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              })}px)`,
            }}
          >
            How TARA Detects Threats
          </div>

          {/* Subtitle */}
          <div
            style={{
              fontSize: 18,
              color: colors.text.secondary,
              maxWidth: 750,
              textAlign: 'center',
              lineHeight: 1.5,
              marginBottom: 30,
              opacity: interpolate(frame - 520, [0, 30], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }),
            }}
          >
            Like enterprise SIEM systems, TARA uses statistical baselines and z-score thresholds
            to identify anomalous neural signals in real-time
          </div>

          {/* Anomaly Detection Visualization */}
          <AnomalyDetectionViz
            width={950}
            height={400}
            showLabels={true}
            showDistribution={true}
            anomalyFrame={frame - 500}
          />

          {/* Method cards */}
          <div
            style={{
              display: 'flex',
              gap: 24,
              marginTop: 30,
              opacity: interpolate(frame - 580, [0, 30], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }),
            }}
          >
            {[
              { label: 'Statistical Baseline', desc: 'Moving average μ from historical data', icon: 'μ' },
              { label: 'Threshold Detection', desc: 'Z-score alerts at ±2.5σ deviation', icon: 'σ' },
              { label: 'Real-time Response', desc: 'Automated defense on anomaly detection', icon: '⚡' },
            ].map((item, i) => (
              <div
                key={i}
                style={{
                  padding: '18px 28px',
                  background: 'rgba(0,0,0,0.5)',
                  borderRadius: 14,
                  border: `1px solid ${colors.primary.accent}33`,
                  textAlign: 'center',
                  minWidth: 220,
                  backdropFilter: 'blur(10px)',
                }}
              >
                <div style={{
                  fontSize: 32,
                  color: colors.primary.accent,
                  fontFamily: typography.fontFamily.mono,
                  marginBottom: 10,
                }}>
                  {item.icon}
                </div>
                <div style={{
                  fontSize: 15,
                  fontWeight: 600,
                  color: colors.text.primary,
                  marginBottom: 6,
                }}>
                  {item.label}
                </div>
                <div style={{
                  fontSize: 13,
                  color: colors.text.muted,
                  lineHeight: 1.4,
                }}>
                  {item.desc}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decorative corner elements */}
      {showTARAIntro && (
        <div
          style={{
            position: 'absolute',
            top: 40,
            right: 40,
            width: 60,
            height: 60,
            borderTop: `1px solid ${colors.primary.accent}33`,
            borderRight: `1px solid ${colors.primary.accent}33`,
            opacity: interpolate(frame, [0, 60], [0, 0.5], {
              extrapolateRight: 'clamp',
            }),
          }}
        />
      )}
    </AbsoluteFill>
  );
};
