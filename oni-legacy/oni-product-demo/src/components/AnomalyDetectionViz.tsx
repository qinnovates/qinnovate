/**
 * Anomaly Detection Visualization
 * Shows how TARA calculates anomalies like enterprise SIEM/DLP/NTA systems
 * Real-time streaming graph with rolling window effect
 */

import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import { colors, typography } from '../data/oni-theme';

interface AnomalyDetectionVizProps {
  width?: number;
  height?: number;
  showLabels?: boolean;
  showDistribution?: boolean;
  anomalyFrame?: number;
}

export const AnomalyDetectionViz: React.FC<AnomalyDetectionVizProps> = ({
  width = 800,
  height = 400,
  showLabels = true,
  showDistribution = true,
  anomalyFrame = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Chart dimensions
  const padding = { top: 60, right: 140, bottom: 60, left: 80 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Streaming parameters
  const visiblePoints = 60; // Number of points visible at once
  const scrollSpeed = 0.8; // Points per frame
  const baseline = 0.5;
  const normalStdDev = 0.08;
  const upperThreshold = baseline + normalStdDev * 2.5;
  const lowerThreshold = baseline - normalStdDev * 2.5;

  // Calculate the current "window" of data based on frame
  const streamOffset = frame * scrollSpeed;

  // Generate streaming data point at index i
  const getDataPoint = (i: number) => {
    // Normal oscillation using deterministic "randomness"
    let y = baseline +
      Math.sin(i * 0.5) * 0.04 +
      Math.cos(i * 0.3 + 1) * 0.03 +
      Math.sin(i * 1.2 + 2) * 0.025 +
      Math.cos(i * 0.7) * 0.02;

    // Inject anomalies at specific intervals
    let isAnomaly = false;
    const anomalyPattern = i % 80; // Repeat pattern every 80 points

    if (anomalyPattern === 45) {
      y = baseline + normalStdDev * 3.5; // Upper spike
      isAnomaly = true;
    } else if (anomalyPattern === 62) {
      y = baseline - normalStdDev * 3.2; // Lower dip
      isAnomaly = true;
    }

    return { y, isAnomaly };
  };

  // Generate visible data points for current frame
  const generateStreamingData = () => {
    const data: { x: number; y: number; isAnomaly: boolean; globalIndex: number }[] = [];
    const startIndex = Math.floor(streamOffset);

    for (let i = 0; i < visiblePoints; i++) {
      const globalIndex = startIndex + i;
      const { y, isAnomaly } = getDataPoint(globalIndex);

      // X position slides based on fractional offset for smooth scrolling
      const fractionalOffset = streamOffset - startIndex;
      const x = (i - fractionalOffset) / visiblePoints;

      if (x >= 0 && x <= 1) {
        data.push({ x, y, isAnomaly, globalIndex });
      }
    }
    return data;
  };

  const data = generateStreamingData();

  // Fade in animation
  const fadeIn = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const thresholdProgress = interpolate(frame, [10, 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const anomalyPulse = Math.sin(frame * 0.2) * 0.5 + 0.5;

  // Convert data to SVG path
  const dataToPath = (points: typeof data) => {
    if (points.length < 2) return '';
    return points.map((point, i) => {
      const x = padding.left + point.x * chartWidth;
      const y = padding.top + (1 - point.y) * chartHeight;
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');
  };

  // Distribution curve (bell curve on the right)
  const distributionWidth = 60;
  const generateDistributionPath = () => {
    const points: string[] = [];
    for (let i = 0; i <= 50; i++) {
      const t = i / 50;
      const y = padding.top + t * chartHeight;
      const normalizedY = (t - 0.5) / 0.15;
      const gaussian = Math.exp(-normalizedY * normalizedY / 2);
      const x = width - padding.right + 20 + gaussian * distributionWidth;
      points.push(`${i === 0 ? 'M' : 'L'} ${x} ${y}`);
    }
    return points.join(' ');
  };

  // Check if any visible anomaly for alert display
  const visibleAnomalies = data.filter(p => p.isAnomaly);
  const hasVisibleAnomaly = visibleAnomalies.length > 0;

  const alertProgress = spring({
    frame: hasVisibleAnomaly ? frame : 0,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Scanline effect
  const scanlineX = padding.left + ((frame * 2) % chartWidth);

  return (
    <div style={{ position: 'relative', width, height, opacity: fadeIn }}>
      <svg width={width} height={height} style={{ overflow: 'visible' }}>
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke={colors.text.muted} strokeWidth="0.3" strokeOpacity="0.2" />
          </pattern>
          <linearGradient id="dangerGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={colors.security.danger} stopOpacity="0.15" />
            <stop offset="50%" stopColor={colors.security.danger} stopOpacity="0" />
          </linearGradient>
          <linearGradient id="dangerGradientBottom" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stopColor={colors.security.danger} stopOpacity="0.15" />
            <stop offset="50%" stopColor={colors.security.danger} stopOpacity="0" />
          </linearGradient>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={colors.security.safe} stopOpacity="0.3" />
            <stop offset="20%" stopColor={colors.security.safe} stopOpacity="1" />
            <stop offset="100%" stopColor={colors.security.safe} stopOpacity="1" />
          </linearGradient>
          <filter id="anomalyGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <clipPath id="chartClip">
            <rect x={padding.left} y={padding.top} width={chartWidth} height={chartHeight} />
          </clipPath>
        </defs>

        {/* Grid background */}
        <rect
          x={padding.left}
          y={padding.top}
          width={chartWidth}
          height={chartHeight}
          fill="url(#grid)"
          opacity={0.5}
        />

        {/* Anomaly zones */}
        <rect
          x={padding.left}
          y={padding.top}
          width={chartWidth}
          height={(1 - upperThreshold) * chartHeight}
          fill="url(#dangerGradient)"
          opacity={thresholdProgress}
        />
        <rect
          x={padding.left}
          y={padding.top + (1 - lowerThreshold) * chartHeight}
          width={chartWidth}
          height={lowerThreshold * chartHeight}
          fill="url(#dangerGradientBottom)"
          opacity={thresholdProgress}
        />

        {/* Threshold lines */}
        <line
          x1={padding.left}
          y1={padding.top + (1 - upperThreshold) * chartHeight}
          x2={padding.left + chartWidth}
          y2={padding.top + (1 - upperThreshold) * chartHeight}
          stroke={colors.security.warning}
          strokeWidth="2"
          strokeDasharray="8 4"
          opacity={thresholdProgress}
        />
        <line
          x1={padding.left}
          y1={padding.top + (1 - lowerThreshold) * chartHeight}
          x2={padding.left + chartWidth}
          y2={padding.top + (1 - lowerThreshold) * chartHeight}
          stroke={colors.security.warning}
          strokeWidth="2"
          strokeDasharray="8 4"
          opacity={thresholdProgress}
        />

        {/* Baseline */}
        <line
          x1={padding.left}
          y1={padding.top + (1 - baseline) * chartHeight}
          x2={padding.left + chartWidth}
          y2={padding.top + (1 - baseline) * chartHeight}
          stroke={colors.primary.accent}
          strokeWidth="1.5"
          strokeDasharray="4 4"
          opacity={0.6}
        />

        {/* Clipped streaming data */}
        <g clipPath="url(#chartClip)">
          {/* Data line with gradient fade on left edge */}
          <path
            d={dataToPath(data)}
            fill="none"
            stroke="url(#lineGradient)"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points */}
          {data.map((point, i) => {
            const x = padding.left + point.x * chartWidth;
            const y = padding.top + (1 - point.y) * chartHeight;

            if (point.isAnomaly) {
              return (
                <g key={point.globalIndex} filter="url(#anomalyGlow)">
                  <circle
                    cx={x}
                    cy={y}
                    r={10 + anomalyPulse * 6}
                    fill={colors.security.danger}
                    opacity={0.2 + anomalyPulse * 0.3}
                  />
                  <circle
                    cx={x}
                    cy={y}
                    r={6}
                    fill={colors.security.danger}
                    stroke="#fff"
                    strokeWidth="2"
                  />
                </g>
              );
            }
            // Only show some normal points for performance
            if (i % 3 === 0) {
              return (
                <circle
                  key={point.globalIndex}
                  cx={x}
                  cy={y}
                  r={2.5}
                  fill={colors.security.safe}
                  opacity={0.6}
                />
              );
            }
            return null;
          })}

          {/* Scanline effect */}
          <line
            x1={scanlineX}
            y1={padding.top}
            x2={scanlineX}
            y2={padding.top + chartHeight}
            stroke={colors.primary.accent}
            strokeWidth="1"
            opacity={0.3}
          />
        </g>

        {/* Distribution curve */}
        {showDistribution && (
          <g opacity={thresholdProgress}>
            <path
              d={generateDistributionPath()}
              fill="none"
              stroke={colors.primary.accent}
              strokeWidth="2"
              opacity={0.8}
            />
            <path
              d={`${generateDistributionPath()} L ${width - padding.right + 20} ${padding.top + chartHeight} L ${width - padding.right + 20} ${padding.top} Z`}
              fill={colors.primary.accent}
              opacity={0.1}
            />
          </g>
        )}

        {/* Labels */}
        {showLabels && (
          <>
            <text
              x={padding.left - 15}
              y={padding.top + (1 - upperThreshold) * chartHeight}
              fill={colors.security.warning}
              fontSize="12"
              textAnchor="end"
              dominantBaseline="middle"
              fontFamily={typography.fontFamily.mono}
              opacity={thresholdProgress}
            >
              +2.5σ
            </text>
            <text
              x={padding.left - 15}
              y={padding.top + (1 - baseline) * chartHeight}
              fill={colors.primary.accent}
              fontSize="12"
              textAnchor="end"
              dominantBaseline="middle"
              fontFamily={typography.fontFamily.mono}
            >
              μ
            </text>
            <text
              x={padding.left - 15}
              y={padding.top + (1 - lowerThreshold) * chartHeight}
              fill={colors.security.warning}
              fontSize="12"
              textAnchor="end"
              dominantBaseline="middle"
              fontFamily={typography.fontFamily.mono}
              opacity={thresholdProgress}
            >
              -2.5σ
            </text>

            <text
              x={padding.left + chartWidth / 2}
              y={height - 15}
              fill={colors.text.muted}
              fontSize="14"
              textAnchor="middle"
              fontFamily={typography.fontFamily.base}
            >
              Real-Time Neural Signal Stream
            </text>

            <text
              x={20}
              y={padding.top + chartHeight / 2}
              fill={colors.text.muted}
              fontSize="14"
              textAnchor="middle"
              fontFamily={typography.fontFamily.base}
              transform={`rotate(-90 20 ${padding.top + chartHeight / 2})`}
            >
              Signal Amplitude
            </text>

            <text
              x={padding.left + chartWidth / 2}
              y={25}
              fill={colors.text.primary}
              fontSize="18"
              fontWeight="600"
              textAnchor="middle"
              fontFamily={typography.fontFamily.base}
            >
              Real-Time Threat Detection
            </text>

            {showDistribution && (
              <text
                x={width - padding.right + 50}
                y={padding.top - 10}
                fill={colors.primary.accent}
                fontSize="12"
                textAnchor="middle"
                fontFamily={typography.fontFamily.mono}
                opacity={thresholdProgress}
              >
                N(μ, σ²)
              </text>
            )}
          </>
        )}

        {/* Legend */}
        <g transform={`translate(${padding.left}, ${height - 45})`}>
          <circle cx={0} cy={0} r={4} fill={colors.security.safe} />
          <text x={10} y={4} fill={colors.text.muted} fontSize="11" fontFamily={typography.fontFamily.base}>
            Normal
          </text>

          <circle cx={80} cy={0} r={4} fill={colors.security.danger} />
          <text x={90} y={4} fill={colors.text.muted} fontSize="11" fontFamily={typography.fontFamily.base}>
            Anomaly
          </text>

          <line x1={160} y1={0} x2={175} y2={0} stroke={colors.security.warning} strokeWidth="2" strokeDasharray="4 2" />
          <text x={180} y={4} fill={colors.text.muted} fontSize="11" fontFamily={typography.fontFamily.base}>
            Threshold
          </text>

          <line x1={260} y1={0} x2={275} y2={0} stroke={colors.primary.accent} strokeWidth="1.5" strokeDasharray="3 3" />
          <text x={280} y={4} fill={colors.text.muted} fontSize="11" fontFamily={typography.fontFamily.base}>
            Baseline
          </text>

          {/* Live indicator */}
          <circle cx={360} cy={0} r={5} fill={colors.security.danger} opacity={0.5 + anomalyPulse * 0.5} />
          <text x={372} y={4} fill={colors.security.danger} fontSize="11" fontWeight="600" fontFamily={typography.fontFamily.base}>
            LIVE
          </text>
        </g>
      </svg>

      {/* Alert overlay when anomaly is visible */}
      {hasVisibleAnomaly && (
        <div
          style={{
            position: 'absolute',
            top: padding.top + 15,
            right: padding.right + 80,
            background: 'rgba(0, 0, 0, 0.9)',
            border: `2px solid ${colors.security.danger}`,
            borderRadius: 12,
            padding: '14px 18px',
            opacity: alertProgress,
            transform: `scale(${interpolate(alertProgress, [0, 1], [0.9, 1])})`,
            boxShadow: `0 0 20px ${colors.security.danger}44`,
          }}
        >
          <div style={{
            color: colors.security.danger,
            fontSize: 14,
            fontWeight: 700,
            marginBottom: 6,
            fontFamily: typography.fontFamily.base,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}>
            <span style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: colors.security.danger,
              boxShadow: `0 0 8px ${colors.security.danger}`,
              animation: 'pulse 0.5s infinite',
            }} />
            ANOMALY DETECTED
          </div>
          <div style={{
            color: colors.text.muted,
            fontSize: 12,
            fontFamily: typography.fontFamily.mono,
            lineHeight: 1.6,
          }}>
            z-score: <span style={{ color: colors.security.danger }}>3.5σ</span>
            <br />
            p-value: <span style={{ color: colors.security.danger }}>&lt;0.001</span>
            <br />
            Action: <span style={{ color: colors.security.warning }}>TRIGGERED</span>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Simplified streaming version for inline use
 */
export const MiniAnomalyChart: React.FC<{ width?: number; height?: number }> = ({
  width = 200,
  height = 80,
}) => {
  const frame = useCurrentFrame();

  const visiblePoints = 40;
  const scrollSpeed = 0.6;
  const offset = frame * scrollSpeed;

  const points: string[] = [];
  const startIndex = Math.floor(offset);

  for (let i = 0; i < visiblePoints; i++) {
    const globalIndex = startIndex + i;
    const fractionalOffset = offset - startIndex;
    const x = ((i - fractionalOffset) / visiblePoints) * width;

    if (x < 0 || x > width) continue;

    let y = height / 2 + Math.sin(globalIndex * 0.4) * 12 + Math.cos(globalIndex * 0.7) * 8;

    // Anomaly spike every 50 points
    if (globalIndex % 50 === 30) {
      y = height * 0.1;
    }

    points.push(`${points.length === 0 ? 'M' : 'L'} ${x} ${y}`);
  }

  return (
    <svg width={width} height={height}>
      <line x1={0} y1={height * 0.2} x2={width} y2={height * 0.2}
        stroke={colors.security.warning} strokeWidth="1" strokeDasharray="4 2" opacity={0.5} />
      <line x1={0} y1={height * 0.8} x2={width} y2={height * 0.8}
        stroke={colors.security.warning} strokeWidth="1" strokeDasharray="4 2" opacity={0.5} />
      <path d={points.join(' ')} fill="none" stroke={colors.security.safe} strokeWidth="2" />
    </svg>
  );
};
