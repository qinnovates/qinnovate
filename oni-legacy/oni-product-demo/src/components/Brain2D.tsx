/**
 * Brain2D - 2D neural network visualization
 * SVG-based, no WebGL required
 */

import React, { useMemo } from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { colors } from '../data/oni-theme';

interface Brain2DProps {
  width?: number;
  height?: number;
}

// Seeded random for consistent renders
const seededRandom = (seed: number) => {
  const x = Math.sin(seed * 9999) * 10000;
  return x - Math.floor(x);
};

export const Brain2D: React.FC<Brain2DProps> = ({ width = 600, height = 600 }) => {
  const frame = useCurrentFrame();
  const centerX = width / 2;
  const centerY = height / 2;

  // Generate nodes in a brain-like elliptical shape
  const nodes = useMemo(() => {
    const nodeList: { x: number; y: number; layer: number; size: number }[] = [];
    const nodeCount = 40;

    for (let i = 0; i < nodeCount; i++) {
      const angle = seededRandom(i * 1.1) * Math.PI * 2;
      const radiusX = 180 + seededRandom(i * 2.2) * 80;
      const radiusY = 140 + seededRandom(i * 3.3) * 60;

      // Create brain-like shape (wider at top)
      const yOffset = Math.cos(angle) * 0.3;
      const adjustedRadiusX = radiusX * (1 + yOffset * 0.2);

      const x = centerX + Math.cos(angle) * adjustedRadiusX;
      const y = centerY + Math.sin(angle) * radiusY * 0.9;

      // Assign layer based on position (for coloring)
      const distFromCenter = Math.sqrt(
        Math.pow((x - centerX) / radiusX, 2) +
        Math.pow((y - centerY) / radiusY, 2)
      );
      const layer = Math.floor(distFromCenter * 14) + 1;

      nodeList.push({
        x,
        y,
        layer: Math.min(14, Math.max(1, layer)),
        size: 4 + seededRandom(i * 4.4) * 4,
      });
    }

    // Add central nodes
    for (let i = 0; i < 15; i++) {
      const angle = seededRandom(i * 5.5 + 100) * Math.PI * 2;
      const radius = 40 + seededRandom(i * 6.6 + 100) * 80;
      nodeList.push({
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius * 0.8,
        layer: 8, // Gateway layer
        size: 5 + seededRandom(i * 7.7 + 100) * 3,
      });
    }

    return nodeList;
  }, [centerX, centerY]);

  // Generate connections between nearby nodes
  const connections = useMemo(() => {
    const connList: { x1: number; y1: number; x2: number; y2: number; layer: number }[] = [];
    const maxDist = 120;

    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDist && seededRandom(i * 100 + j) > 0.6) {
          connList.push({
            x1: nodes[i].x,
            y1: nodes[i].y,
            x2: nodes[j].x,
            y2: nodes[j].y,
            layer: Math.round((nodes[i].layer + nodes[j].layer) / 2),
          });
        }
      }
    }

    return connList;
  }, [nodes]);

  // Get color based on layer
  const getLayerColor = (layer: number) => {
    if (layer <= 7) return colors.silicon.L3;
    if (layer === 8) return colors.gateway.L8;
    return colors.biology.L11;
  };

  // Rotation animation
  const rotation = frame * 0.3;

  // Pulse animation for nodes
  const pulsePhase = frame * 0.1;

  return (
    <svg width={width} height={height} style={{ overflow: 'visible' }}>
      <defs>
        {/* Glow filter */}
        <filter id="brain2dGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>

        {/* Radial gradient for brain shape */}
        <radialGradient id="brainGradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={colors.gateway.L8} stopOpacity="0.15" />
          <stop offset="70%" stopColor={colors.primary.accent} stopOpacity="0.05" />
          <stop offset="100%" stopColor="transparent" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Background glow */}
      <ellipse
        cx={centerX}
        cy={centerY}
        rx={220}
        ry={180}
        fill="url(#brainGradient)"
      />

      {/* Connections */}
      <g style={{ transform: `rotate(${rotation}deg)`, transformOrigin: `${centerX}px ${centerY}px` }}>
        {connections.map((conn, i) => {
          const animOffset = Math.sin(pulsePhase + i * 0.2) * 0.3 + 0.5;
          const color = getLayerColor(conn.layer);

          return (
            <line
              key={`conn-${i}`}
              x1={conn.x1}
              y1={conn.y1}
              x2={conn.x2}
              y2={conn.y2}
              stroke={color}
              strokeWidth={1}
              opacity={0.2 + animOffset * 0.2}
            />
          );
        })}
      </g>

      {/* Nodes */}
      <g style={{ transform: `rotate(${rotation}deg)`, transformOrigin: `${centerX}px ${centerY}px` }}>
        {nodes.map((node, i) => {
          const pulse = 1 + Math.sin(pulsePhase + i * 0.3) * 0.2;
          const color = getLayerColor(node.layer);

          return (
            <circle
              key={`node-${i}`}
              cx={node.x}
              cy={node.y}
              r={node.size * pulse}
              fill={color}
              opacity={0.6 + Math.sin(pulsePhase + i * 0.5) * 0.3}
              filter="url(#brain2dGlow)"
            />
          );
        })}
      </g>

      {/* Traveling signals */}
      {[0, 1, 2, 3, 4].map((i) => {
        const progress = ((frame * 0.02 + i * 0.2) % 1);
        const connIndex = Math.floor(seededRandom(i * 999) * connections.length);
        const conn = connections[connIndex] || connections[0];

        if (!conn) return null;

        const x = interpolate(progress, [0, 1], [conn.x1, conn.x2]);
        const y = interpolate(progress, [0, 1], [conn.y1, conn.y2]);
        const opacity = interpolate(progress, [0, 0.1, 0.9, 1], [0, 1, 1, 0]);

        return (
          <circle
            key={`signal-${i}`}
            cx={x}
            cy={y}
            r={3}
            fill={colors.primary.accent}
            opacity={opacity}
            filter="url(#brain2dGlow)"
            style={{ transform: `rotate(${rotation}deg)`, transformOrigin: `${centerX}px ${centerY}px` }}
          />
        );
      })}

      {/* Central core */}
      <circle
        cx={centerX}
        cy={centerY}
        r={20 + Math.sin(pulsePhase) * 3}
        fill={colors.gateway.L8}
        opacity={0.4}
        filter="url(#brain2dGlow)"
      />
      <circle
        cx={centerX}
        cy={centerY}
        r={10 + Math.sin(pulsePhase) * 2}
        fill={colors.gateway.L8}
        opacity={0.7}
      />
    </svg>
  );
};
