/**
 * Academic Scene - Research foundation and citations
 * Features: Citation cards, institution highlights, research badges
 */

import React from 'react';
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';
import { FloatingParticles } from '../components/Particles';
import { LettersPullUp, BlurInText } from '../components/TextAnimations';
import { colors, typography } from '../data/oni-theme';

// Academic citations and institutions
const citations = [
  {
    author: 'Kohno et al.',
    institution: 'University of Washington',
    paper: 'BCI Threat Modeling Framework',
    year: '2009',
    color: colors.silicon.L3,
  },
  {
    author: 'Martinovic et al.',
    institution: 'Columbia University',
    paper: 'Side-Channel BCI Attacks',
    year: '2012',
    color: colors.biology.L11,
  },
  {
    author: 'Bonaci et al.',
    institution: 'Yale University',
    paper: 'App Stores for the Brain',
    year: '2015',
    color: colors.gateway.L8,
  },
  {
    author: 'Müller-Putz et al.',
    institution: 'Graz BCI Lab',
    paper: 'BCI Standardization Guidelines',
    year: '2021',
    color: colors.security.safe,
  },
];

export const AcademicScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        background: colors.gradients.backgroundSubtle,
      }}
    >
      {/* Subtle particles */}
      <FloatingParticles
        count={35}
        color={colors.primary.accent}
        speed={0.12}
        minSize={1}
        maxSize={2}
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
          padding: '60px 100px',
        }}
      >
        {/* Title section */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 20,
          }}
        >
          <LettersPullUp
            text="Built on Academic Foundation"
            delay={0}
            fontSize={52}
            fontWeight={700}
            gradient={true}
          />

          <BlurInText
            text="Every claim is cited. Every formula is documented."
            delay={25}
            fontSize={20}
            color={colors.text.muted}
            fontWeight={400}
          />
        </div>

        {/* Citation grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: 24,
            maxWidth: 1100,
            marginTop: 20,
          }}
        >
          {citations.map((citation, index) => {
            const cardProgress = spring({
              frame: frame - 50 - index * 15,
              fps,
              config: { damping: 25, stiffness: 100 },
            });

            const slideX = interpolate(
              Math.max(0, cardProgress),
              [0, 1],
              [index % 2 === 0 ? -40 : 40, 0]
            );

            return (
              <div
                key={citation.author}
                style={{
                  padding: 26,
                  background: `linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%)`,
                  backdropFilter: 'blur(15px)',
                  borderRadius: 16,
                  border: `1px solid ${citation.color}22`,
                  opacity: Math.max(0, cardProgress),
                  transform: `translateX(${slideX}px)`,
                }}
              >
                {/* Header row */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 14,
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                    }}
                  >
                    <div
                      style={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        background: citation.color,
                        boxShadow: `0 0 8px ${citation.color}`,
                      }}
                    />
                    <div
                      style={{
                        fontSize: 18,
                        color: citation.color,
                        fontWeight: 600,
                        letterSpacing: '-0.01em',
                      }}
                    >
                      {citation.author}
                    </div>
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      color: colors.text.muted,
                      fontFamily: typography.fontFamily.mono,
                    }}
                  >
                    {citation.year}
                  </div>
                </div>

                {/* Institution */}
                <div
                  style={{
                    fontSize: 15,
                    color: colors.text.secondary,
                    marginBottom: 10,
                  }}
                >
                  {citation.institution}
                </div>

                {/* Paper title */}
                <div
                  style={{
                    fontSize: 14,
                    color: colors.text.muted,
                    fontStyle: 'italic',
                    lineHeight: 1.4,
                  }}
                >
                  "{citation.paper}"
                </div>
              </div>
            );
          })}
        </div>

        {/* Research badges */}
        <div
          style={{
            display: 'flex',
            gap: 40,
            marginTop: 30,
          }}
        >
          {['Peer Reviewed', 'IEEE Cited', 'Open Research'].map((badge, index) => {
            const badgeProgress = spring({
              frame: frame - 180 - index * 12,
              fps,
              config: { damping: 25, stiffness: 100 },
            });

            return (
              <div
                key={badge}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '12px 22px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: 10,
                  border: '1px solid rgba(255,255,255,0.06)',
                  fontSize: 15,
                  color: colors.text.secondary,
                  fontWeight: 500,
                  opacity: Math.max(0, badgeProgress),
                  transform: `translateY(${interpolate(
                    Math.max(0, badgeProgress),
                    [0, 1],
                    [20, 0]
                  )}px)`,
                }}
              >
                <span style={{ color: colors.security.safe }}>✓</span>
                {badge}
              </div>
            );
          })}
        </div>

        {/* Who ONI Is For - matches GitHub Pages */}
        <div
          style={{
            marginTop: 40,
            opacity: interpolate(frame - 230, [0, 30], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }),
          }}
        >
          <div
            style={{
              fontSize: 12,
              color: colors.text.muted,
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              marginBottom: 16,
              textAlign: 'center',
            }}
          >
            Who ONI Is For
          </div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              gap: 40,
              flexWrap: 'wrap',
            }}
          >
            {[
              { role: 'Researchers', icon: '🔬' },
              { role: 'Developers', icon: '💻' },
              { role: 'Regulators', icon: '⚖️' },
              { role: 'Security Teams', icon: '🛡️' },
            ].map((item, i) => {
              const itemProgress = spring({
                frame: frame - 240 - i * 8,
                fps,
                config: { damping: 20, stiffness: 100 },
              });

              return (
                <div
                  key={item.role}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    fontSize: 15,
                    color: colors.text.secondary,
                    fontWeight: 500,
                    letterSpacing: '0.02em',
                    opacity: Math.max(0, itemProgress),
                    transform: `translateY(${interpolate(
                      Math.max(0, itemProgress),
                      [0, 1],
                      [15, 0]
                    )}px)`,
                  }}
                >
                  <span style={{ fontSize: 18 }}>{item.icon}</span>
                  {item.role}
                </div>
              );
            })}
          </div>

          {/* And You - emphasized with white text and dramatic animation */}
          <div
            style={{
              marginTop: 24,
              textAlign: 'center',
              opacity: interpolate(frame - 290, [0, 40], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }),
              transform: `scale(${interpolate(frame - 290, [0, 40], [0.85, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              })}) translateY(${interpolate(frame - 290, [0, 40], [20, 0], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              })}px)`,
            }}
          >
            <span
              style={{
                fontSize: 28,
                fontWeight: 700,
                color: '#ffffff',
                letterSpacing: '0.08em',
                textShadow: `0 0 30px ${colors.primary.accent}66, 0 0 60px ${colors.primary.accent}33`,
              }}
            >
              ...and you.
            </span>
          </div>
        </div>
      </div>

      {/* Side accent lines */}
      <div
        style={{
          position: 'absolute',
          left: 60,
          top: '25%',
          bottom: '25%',
          width: 2,
          background: `linear-gradient(transparent, ${colors.primary.accent}33, transparent)`,
          opacity: 0.5,
        }}
      />
      <div
        style={{
          position: 'absolute',
          right: 60,
          top: '25%',
          bottom: '25%',
          width: 2,
          background: `linear-gradient(transparent, ${colors.primary.accent}33, transparent)`,
          opacity: 0.5,
        }}
      />
    </AbsoluteFill>
  );
};
