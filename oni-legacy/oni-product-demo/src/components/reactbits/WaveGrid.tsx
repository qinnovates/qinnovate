/**
 * WaveGrid - Tech-inspired vector waves
 * Clean lines flowing like calm electric water
 * Abstract, geometric, minimal
 */

import React, { useRef, useEffect } from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

interface WaveGridProps {
  lineCount?: number;
  color?: string;
  secondaryColor?: string;
  amplitude?: number;
  speed?: number;
  strokeWidth?: number;
  showNodes?: boolean;
  nodeSize?: number;
  glow?: boolean;
  glowIntensity?: number;
}

export const WaveGrid: React.FC<WaveGridProps> = ({
  lineCount = 12,
  color = '#0099dd',
  secondaryColor = '#0066aa',
  amplitude = 40,
  speed = 0.3,
  strokeWidth = 1.5,
  showNodes = true,
  nodeSize = 3,
  glow = true,
  glowIntensity = 15,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, width, height);

    const time = (frame / fps) * speed;
    const points = 80; // Resolution
    const centerY = height / 2;
    const verticalSpacing = height / (lineCount + 1);

    // Fade in
    const fadeIn = interpolate(frame, [0, 45], [0, 1], {
      extrapolateRight: 'clamp',
    });

    // Draw each wave line
    for (let line = 0; line < lineCount; line++) {
      const lineY = verticalSpacing * (line + 1);
      const lineProgress = line / (lineCount - 1); // 0 to 1

      // Distance from center (0 at center, 1 at edges)
      const distFromCenter = Math.abs(lineProgress - 0.5) * 2;

      // Lines closer to center have more amplitude
      const lineAmplitude = amplitude * (1 - distFromCenter * 0.6);

      // Phase offset creates wave propagation effect
      const phaseOffset = line * 0.15;

      // Staggered fade in from center
      const lineFadeDelay = Math.abs(line - lineCount / 2) * 3;
      const lineFade = interpolate(frame - lineFadeDelay, [0, 30], [0, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });

      // Color interpolation based on position
      const colorMix = lineProgress;

      // Build path points
      const pathPoints: { x: number; y: number }[] = [];

      for (let i = 0; i <= points; i++) {
        const x = (i / points) * width;
        const xNorm = i / points;

        // Multiple sine waves combined for organic feel
        const wave1 = Math.sin((xNorm * 2 + time + phaseOffset) * Math.PI * 2);
        const wave2 = Math.sin((xNorm * 4 + time * 1.3 + phaseOffset) * Math.PI * 2) * 0.3;
        const wave3 = Math.sin((xNorm * 1 + time * 0.7) * Math.PI * 2) * 0.2;

        // Combine waves
        const combinedWave = wave1 + wave2 + wave3;

        // Edge fade - waves diminish at edges
        const edgeFade = Math.pow(Math.sin(xNorm * Math.PI), 0.5);

        const y = lineY + combinedWave * lineAmplitude * edgeFade;

        pathPoints.push({ x, y });
      }

      // Draw the wave line
      ctx.beginPath();
      ctx.moveTo(pathPoints[0].x, pathPoints[0].y);

      // Use quadratic curves for smoother lines
      for (let i = 1; i < pathPoints.length - 1; i++) {
        const xc = (pathPoints[i].x + pathPoints[i + 1].x) / 2;
        const yc = (pathPoints[i].y + pathPoints[i + 1].y) / 2;
        ctx.quadraticCurveTo(pathPoints[i].x, pathPoints[i].y, xc, yc);
      }
      ctx.lineTo(pathPoints[pathPoints.length - 1].x, pathPoints[pathPoints.length - 1].y);

      // Line style
      const opacity = (0.3 + (1 - distFromCenter) * 0.5) * fadeIn * lineFade;

      // Glow effect
      if (glow) {
        ctx.shadowColor = colorMix < 0.5 ? color : secondaryColor;
        ctx.shadowBlur = glowIntensity * (1 - distFromCenter * 0.5);
      }

      ctx.strokeStyle = colorMix < 0.5 ? color : secondaryColor;
      ctx.lineWidth = strokeWidth * (1 - distFromCenter * 0.3);
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.globalAlpha = opacity;
      ctx.stroke();

      // Draw nodes at intervals
      if (showNodes && lineFade > 0.5) {
        const nodeInterval = Math.floor(points / 8);
        for (let i = nodeInterval; i < points - nodeInterval; i += nodeInterval) {
          const point = pathPoints[i];

          // Node pulse based on time
          const nodePulse = 0.7 + Math.sin(time * 3 + i * 0.5 + line) * 0.3;
          const currentNodeSize = nodeSize * nodePulse * (1 - distFromCenter * 0.5);

          // Outer glow
          if (glow) {
            ctx.beginPath();
            ctx.arc(point.x, point.y, currentNodeSize * 2, 0, Math.PI * 2);
            ctx.fillStyle = colorMix < 0.5 ? color : secondaryColor;
            ctx.globalAlpha = opacity * 0.2;
            ctx.fill();
          }

          // Inner node
          ctx.beginPath();
          ctx.arc(point.x, point.y, currentNodeSize, 0, Math.PI * 2);
          ctx.fillStyle = '#ffffff';
          ctx.globalAlpha = opacity * 0.9;
          ctx.fill();
        }
      }
    }

    // Reset
    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;

  }, [frame, width, height, fps, lineCount, color, secondaryColor, amplitude, speed, strokeWidth, showNodes, nodeSize, glow, glowIntensity]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
      }}
    />
  );
};

export default WaveGrid;
