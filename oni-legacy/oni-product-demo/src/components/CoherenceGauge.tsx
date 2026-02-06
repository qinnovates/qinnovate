import React from 'react';
import { useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';
import { colors, typography } from '../data/oni-theme';

interface CoherenceGaugeProps {
  value?: number; // 0-1
  showFormula?: boolean;
  animated?: boolean;
  showThreshold?: boolean;
  threshold?: number;
}

export const CoherenceGauge: React.FC<CoherenceGaugeProps> = ({
  value = 0.85,
  showFormula = true,
  animated = true,
  showThreshold = false,
  threshold = 0.65,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animate the value
  const animatedValue = animated
    ? interpolate(
        spring({
          frame,
          fps,
          config: { damping: 50, stiffness: 50 },
        }),
        [0, 1],
        [0, value]
      )
    : value;

  // Gauge dimensions
  const gaugeWidth = 400;
  const gaugeHeight = 30;

  // Color based on value
  const getColor = (v: number) => {
    if (v >= 0.8) return colors.security.safe;
    if (v >= 0.5) return colors.security.warning;
    return colors.security.danger;
  };

  const formulaOpacity = spring({
    frame: frame - 20,
    fps,
    config: { damping: 100 },
  });

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 30,
      }}
    >
      {/* Formula */}
      {showFormula && (
        <div
          style={{
            opacity: Math.max(0, formulaOpacity),
            fontFamily: typography.fontFamily.mono,
            fontSize: typography.fontSize.formula,
            color: colors.text.primary,
            padding: '20px 40px',
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            borderRadius: 12,
            border: `1px solid ${colors.primary.accent}44`,
          }}
        >
          C<sub>s</sub> = e<sup>−(σ²φ + σ²τ + σ²γ)</sup>
        </div>
      )}

      {/* Gauge container */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 20,
        }}
      >
        {/* Label */}
        <div
          style={{
            fontSize: typography.fontSize.body,
            color: colors.text.secondary,
            width: 120,
            textAlign: 'right',
          }}
        >
          Coherence
        </div>

        {/* Gauge background */}
        <div
          style={{
            width: gaugeWidth,
            height: gaugeHeight,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: gaugeHeight / 2,
            overflow: 'visible',
            position: 'relative',
          }}
        >
          {/* Gauge fill */}
          <div
            style={{
              width: `${animatedValue * 100}%`,
              height: '100%',
              backgroundColor: getColor(animatedValue),
              borderRadius: gaugeHeight / 2,
              boxShadow: `0 0 20px ${getColor(animatedValue)}88`,
              transition: 'background-color 0.3s ease',
            }}
          />

          {/* Threshold line */}
          {showThreshold && (
            <div
              style={{
                position: 'absolute',
                left: `${threshold * 100}%`,
                top: -8,
                bottom: -8,
                width: 3,
                backgroundColor: colors.security.warning,
                borderRadius: 2,
                boxShadow: `0 0 8px ${colors.security.warning}`,
              }}
            >
              {/* Threshold label */}
              <div
                style={{
                  position: 'absolute',
                  bottom: -24,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  fontSize: 11,
                  color: colors.security.warning,
                  whiteSpace: 'nowrap',
                  fontFamily: typography.fontFamily.mono,
                }}
              >
                {(threshold * 100).toFixed(0)}%
              </div>
            </div>
          )}
        </div>

        {/* Value */}
        <div
          style={{
            fontSize: typography.fontSize.heading,
            color: getColor(animatedValue),
            fontWeight: 700,
            width: 100,
            fontFamily: typography.fontFamily.mono,
          }}
        >
          {(animatedValue * 100).toFixed(0)}%
        </div>
      </div>

      {/* Component breakdown - matching formula: e^(−(σ²φ + σ²τ + σ²γ)) */}
      <div
        style={{
          display: 'flex',
          gap: 40,
          marginTop: 20,
          opacity: Math.max(0, formulaOpacity),
        }}
      >
        {[
          { label: 'Phase Variance', value: 0.08, symbol: 'σ²φ' },
          { label: 'Timing Variance', value: 0.12, symbol: 'σ²τ' },
          { label: 'Freq Variance', value: 0.05, symbol: 'σ²γ' },
        ].map((component, index) => (
          <div
            key={component.label}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <div
              style={{
                fontSize: typography.fontSize.small,
                color: colors.text.muted,
              }}
            >
              {component.label}
            </div>
            <div
              style={{
                fontSize: typography.fontSize.body,
                color: colors.primary.accent,
                fontFamily: typography.fontFamily.mono,
              }}
            >
              {component.symbol}: {(component.value * (1 - animatedValue)).toFixed(3)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
