import React from 'react';
import { useCurrentFrame, spring, useVideoConfig, interpolate } from 'remotion';
import { colors, typography } from '../data/oni-theme';

// Layer definitions - MUST MATCH brand.json (MAIN/resources/brand/brand.json)
// Source of truth: brand.json > layers section
// L1-L7: Silicon (OSI), L8: Neural Gateway (Bridge), L9-L14: Biology (Cognitive)
// Updated 2026-01-26: Aligned with ONI_LAYERS.md v3.0 (Biological Foundation research)
const layers = [
  { id: 'L14', name: 'Identity Layer', zoneLabel: 'Self', zone: 'biology', color: colors.biology.L14 },
  { id: 'L13', name: 'Semantic Layer', zoneLabel: 'Intent', zone: 'biology', color: colors.biology.L13 },
  { id: 'L12', name: 'Cognitive Session', zoneLabel: 'Context', zone: 'biology', color: colors.biology.L12 },
  { id: 'L11', name: 'Cognitive Transport', zoneLabel: 'Delivery', zone: 'biology', color: colors.biology.L11 },
  { id: 'L10', name: 'Neural Protocol', zoneLabel: 'Encoding', zone: 'biology', color: colors.biology.L10 },
  { id: 'L9', name: 'Signal Processing', zoneLabel: 'Filtering', zone: 'biology', color: colors.biology.L9 },
  { id: 'L8', name: 'Neural Gateway', zoneLabel: 'Firewall', zone: 'gateway', color: colors.gateway.L8 },
  { id: 'L7', name: 'Application Interface', zoneLabel: 'Application', zone: 'silicon', color: colors.silicon.L7 },
  { id: 'L6', name: 'Presentation', zoneLabel: 'Presentation', zone: 'silicon', color: colors.silicon.L6 },
  { id: 'L5', name: 'Session', zoneLabel: 'Session', zone: 'silicon', color: colors.silicon.L5 },
  { id: 'L4', name: 'Transport', zoneLabel: 'Transport', zone: 'silicon', color: colors.silicon.L4 },
  { id: 'L3', name: 'Protocol', zoneLabel: 'Network', zone: 'silicon', color: colors.silicon.L3 },
  { id: 'L2', name: 'Signal Processing', zoneLabel: 'Data Link', zone: 'silicon', color: colors.silicon.L2 },
  { id: 'L1', name: 'Physical Carrier', zoneLabel: 'Physical', zone: 'silicon', color: colors.silicon.L1 },
];

interface LayerStackProps {
  highlightLayer?: number; // 1-14 to highlight specific layer
  animationStyle?: 'cascade' | 'reveal' | 'highlight';
}

export const LayerStack: React.FC<LayerStackProps> = ({
  highlightLayer,
  animationStyle = 'cascade',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const layerHeight = 50;
  const layerWidth = 600;
  const gap = 4;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap,
      }}
    >
      {/* Biology label */}
      <div
        style={{
          color: colors.text.secondary,
          fontSize: typography.fontSize.small,
          marginBottom: 8,
          opacity: spring({ frame: frame - 10, fps, config: { damping: 100 } }),
        }}
      >
        BIOLOGY (L9-L14)
      </div>

      {layers.map((layer, index) => {
        // Staggered animation for cascade effect
        const delay = animationStyle === 'cascade' ? index * 3 : 0;

        const layerOpacity = spring({
          frame: frame - delay,
          fps,
          config: { damping: 100 },
        });

        const slideIn = interpolate(
          spring({
            frame: frame - delay,
            fps,
            config: { damping: 20, stiffness: 100 },
          }),
          [0, 1],
          [-100, 0]
        );

        // Highlight effect
        const isHighlighted = highlightLayer === 15 - index;
        const highlightScale = isHighlighted ? 1.05 : 1;

        // Gateway glow effect
        const isGateway = layer.zone === 'gateway';
        const gatewayGlow = isGateway
          ? `0 0 20px ${colors.gateway.L8}88, 0 0 40px ${colors.gateway.L8}44`
          : 'none';

        return (
          <React.Fragment key={layer.id}>
            {/* Zone separator before gateway */}
            {layer.id === 'L8' && (
              <div
                style={{
                  color: colors.text.secondary,
                  fontSize: typography.fontSize.small,
                  margin: '12px 0 8px',
                  opacity: Math.max(0, layerOpacity),
                }}
              >
                NEURAL GATEWAY (L8)
              </div>
            )}

            {/* Zone separator before silicon */}
            {layer.id === 'L7' && (
              <div
                style={{
                  color: colors.text.secondary,
                  fontSize: typography.fontSize.small,
                  margin: '12px 0 8px',
                  opacity: Math.max(0, layerOpacity),
                }}
              >
                SILICON (L1-L7)
              </div>
            )}

            <div
              style={{
                width: layerWidth,
                height: layerHeight,
                backgroundColor: layer.color,
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0 20px',
                opacity: Math.max(0, layerOpacity),
                transform: `translateX(${slideIn}px) scale(${highlightScale})`,
                boxShadow: isHighlighted
                  ? `0 0 30px ${layer.color}88`
                  : gatewayGlow,
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              }}
            >
              <span
                style={{
                  color: colors.text.primary,
                  fontSize: typography.fontSize.body,
                  fontWeight: 700,
                }}
              >
                {layer.id}
              </span>
              <span
                style={{
                  color: colors.text.primary,
                  fontSize: typography.fontSize.small,
                  fontWeight: 500,
                }}
              >
                {layer.name}
              </span>
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};
