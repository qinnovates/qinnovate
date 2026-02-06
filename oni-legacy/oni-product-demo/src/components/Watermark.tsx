import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { colors, typography } from "../data/oni-theme";

interface WatermarkProps {
  /**
   * Position of watermark on screen
   * @default "bottom-right"
   */
  position?: "bottom-right" | "bottom-left" | "top-right" | "top-left";

  /**
   * Opacity of the watermark (0-1)
   * @default 0.6
   */
  opacity?: number;

  /**
   * Delay before watermark fades in (in frames)
   * @default 30
   */
  fadeInDelay?: number;

  /**
   * Duration of fade-in animation (in frames)
   * @default 20
   */
  fadeInDuration?: number;
}

/**
 * Watermark component for ONI demo videos
 *
 * Displays: "© 2026 Kevin Qi • ONI Neuroassurance Stack"
 *
 * - Copyright (©) protects the video content itself
 */
export const Watermark: React.FC<WatermarkProps> = ({
  position = "bottom-right",
  opacity = 0.6,
  fadeInDelay = 30,
  fadeInDuration = 20,
}) => {
  const frame = useCurrentFrame();
  const year = new Date().getFullYear();

  // Fade in animation
  const fadeOpacity = interpolate(
    frame,
    [fadeInDelay, fadeInDelay + fadeInDuration],
    [0, opacity],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Position styles
  const positionStyles: Record<string, React.CSSProperties> = {
    "bottom-right": { bottom: 24, right: 32 },
    "bottom-left": { bottom: 24, left: 32 },
    "top-right": { top: 24, right: 32 },
    "top-left": { top: 24, left: 32 },
  };

  return (
    <div
      style={{
        position: "absolute",
        ...positionStyles[position],
        opacity: fadeOpacity,
        display: "flex",
        alignItems: "center",
        gap: 10,
        zIndex: 1000,
      }}
    >
      {/* Copyright */}
      <span
        style={{
          fontFamily: typography.fontFamily.body,
          fontSize: 14,
          color: colors.text.secondary,
          letterSpacing: "0.01em",
        }}
      >
        © {year} Kevin Qi
      </span>

      {/* Separator */}
      <span
        style={{
          fontSize: 14,
          color: colors.text.muted,
        }}
      >
        •
      </span>

      {/* Brand with trademark */}
      <span
        style={{
          fontFamily: typography.fontFamily.heading,
          fontSize: 15,
          fontWeight: 600,
          color: colors.text.primary,
          letterSpacing: "0.02em",
        }}
      >
        ONI Neuroassurance Stack
      </span>
    </div>
  );
};

export default Watermark;
