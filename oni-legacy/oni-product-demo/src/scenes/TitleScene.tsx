/**
 * Title Scene - Retro meets Future
 * "The future we were promised, finally delivered."
 *
 * Inspired by: Bland (retro stripes) + Starcloud (space frontier)
 * Result: Neural signal stripe + Earth horizon + void
 */

import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, random } from 'remotion';

// Generate consistent stars
const generateStars = (count: number, seed: string) => {
  return Array.from({ length: count }, (_, i) => ({
    x: random(`${seed}-x-${i}`) * 100,
    y: random(`${seed}-y-${i}`) * 70, // Keep stars in upper 70%
    size: random(`${seed}-size-${i}`) * 1.5 + 0.5,
    opacity: random(`${seed}-opacity-${i}`) * 0.6 + 0.2,
  }));
};

const stars = generateStars(80, 'oni-stars');

export const TitleScene: React.FC = () => {
  const frame = useCurrentFrame();

  // Apple ease - glacial, inevitable
  const appleEase = (t: number) => 1 - Math.pow(1 - t, 4);

  // === TIMING (at 30fps) ===
  // Stars: 0-60 frames - fade in the void
  // ONI: 40-160 frames (4 seconds) - hero emerges
  // Stripe: 180-280 frames - the signature draws
  // Tagline: 260-320 frames

  // Stars fade in
  const starsOpacity = interpolate(frame, [0, 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Earth horizon glow
  const horizonOpacity = interpolate(frame, [20, 80], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // ONI fade
  const oniRaw = interpolate(frame, [40, 160], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const oniOpacity = appleEase(oniRaw);
  const oniY = interpolate(oniOpacity, [0, 1], [40, 0]);

  // ONI pulsing glow effect - white outline that pulses
  const pulseSpeed = 0.12;
  const pulseIntensity = 0.4 + 0.2 * Math.sin(frame * pulseSpeed);
  const glowSize = 8 + 6 * Math.sin(frame * pulseSpeed);

  // Neural stripe draws from left to right - starts sooner
  const stripeRaw = interpolate(frame, [100, 200], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const stripeProgress = appleEase(stripeRaw);

  // Tagline
  const taglineRaw = interpolate(frame, [260, 320], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const taglineOpacity = appleEase(taglineRaw);
  const taglineY = interpolate(taglineOpacity, [0, 1], [20, 0]);

  // Subtle star twinkle
  const twinkle = (seed: number) => {
    return 0.7 + 0.3 * Math.sin(frame * 0.05 + seed * 10);
  };

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#000000',
        overflow: 'hidden',
      }}
    >
      {/* Stars - subtle depth */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: starsOpacity * 0.7,
        }}
      >
        {stars.map((star, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${star.x}%`,
              top: `${star.y}%`,
              width: star.size,
              height: star.size,
              borderRadius: '50%',
              backgroundColor: '#ffffff',
              opacity: star.opacity * twinkle(i),
            }}
          />
        ))}
      </div>

      {/* Earth horizon glow - atmospheric blue line at bottom */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 200,
          background: `linear-gradient(to top,
            rgba(30, 100, 180, 0.15) 0%,
            rgba(30, 140, 220, 0.08) 30%,
            transparent 100%
          )`,
          opacity: horizonOpacity,
        }}
      />

      {/* Thin atmospheric line */}
      <div
        style={{
          position: 'absolute',
          bottom: 80,
          left: 0,
          right: 0,
          height: 1,
          background: `linear-gradient(90deg,
            transparent 0%,
            rgba(100, 180, 255, 0.3) 20%,
            rgba(100, 180, 255, 0.5) 50%,
            rgba(100, 180, 255, 0.3) 80%,
            transparent 100%
          )`,
          opacity: horizonOpacity,
        }}
      />

      {/* Content container */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* ONI - Bold, warm, confident with pulsing glow */}
        <div
          style={{
            position: 'relative',
            fontSize: 200,
            fontWeight: 600,
            fontFamily: "'SF Pro Display', -apple-system, 'Helvetica Neue', sans-serif",
            letterSpacing: '0.1em',
            color: '#ffffff',
            opacity: oniOpacity,
            transform: `translateY(${oniY}px)`,
            textShadow: `
              0 0 ${glowSize}px rgba(255, 255, 255, ${pulseIntensity}),
              0 0 ${glowSize * 2}px rgba(255, 255, 255, ${pulseIntensity * 0.6}),
              0 0 ${glowSize * 3}px rgba(200, 220, 255, ${pulseIntensity * 0.4}),
              0 0 ${glowSize * 5}px rgba(150, 200, 255, ${pulseIntensity * 0.2})
            `,
          }}
        >
          ONI
          {/* Electron with comet trail - 3D orbit around ONI */}
          {(() => {
            const orbitSpeed = 0.06;
            const orbitRadiusX = 320;
            const orbitRadiusZ = 150;
            const orbitRadiusY = 20;

            // Trail: array of past positions
            const trailLength = 12;
            const trailElements = [];

            for (let i = trailLength; i >= 0; i--) {
              const trailDelay = i * 0.08;
              const t = frame * orbitSpeed - trailDelay;

              const electronX = Math.sin(t) * orbitRadiusX;
              const electronZ = Math.cos(t) * orbitRadiusZ;
              const electronY = Math.sin(t * 2) * orbitRadiusY;

              const isBehind = electronZ < 0;
              const depthScale = 0.6 + 0.4 * ((electronZ + orbitRadiusZ) / (orbitRadiusZ * 2));
              const depthOpacity = 0.4 + 0.6 * ((electronZ + orbitRadiusZ) / (orbitRadiusZ * 2));

              // Trail fades out
              const trailFade = 1 - (i / trailLength);
              const trailScale = trailFade * 0.8 + 0.2;

              // Pulsing glow for main electron
              const isMain = i === 0;
              const glowPulse = isMain ? 0.7 + 0.3 * Math.sin(frame * 0.15) : 0.5;
              const sizePulse = isMain ? 12 + 4 * Math.sin(frame * 0.12) : 6 * trailScale;

              const opacity = oniOpacity * depthOpacity * trailFade * (isMain ? 1 : 0.6);

              trailElements.push(
                <div
                  key={i}
                  style={{
                    position: 'absolute',
                    left: '50%',
                    top: '50%',
                    width: sizePulse * depthScale * trailScale,
                    height: sizePulse * depthScale * trailScale,
                    borderRadius: '50%',
                    background: isMain
                      ? `radial-gradient(circle at 30% 30%,
                          rgba(180, 240, 255, 1) 0%,
                          rgba(100, 200, 255, 0.95) 20%,
                          rgba(50, 160, 255, 0.9) 50%,
                          rgba(20, 120, 255, 0.7) 100%
                        )`
                      : `radial-gradient(circle,
                          rgba(100, 180, 255, ${0.8 * trailFade}) 0%,
                          rgba(60, 140, 255, ${0.4 * trailFade}) 50%,
                          transparent 100%
                        )`,
                    transform: `translate(${electronX}px, ${electronY}px) scale(${depthScale})`,
                    opacity: opacity,
                    zIndex: isBehind ? -1 : 1,
                    boxShadow: isMain
                      ? `
                        0 0 ${8 * glowPulse * depthScale}px rgba(150, 220, 255, 1),
                        0 0 ${16 * glowPulse * depthScale}px rgba(100, 200, 255, 0.9),
                        0 0 ${32 * glowPulse * depthScale}px rgba(70, 170, 255, 0.7),
                        0 0 ${50 * glowPulse * depthScale}px rgba(50, 150, 255, 0.5),
                        0 0 ${80 * glowPulse * depthScale}px rgba(30, 130, 255, 0.3)
                      `
                      : `0 0 ${8 * trailFade * depthScale}px rgba(80, 160, 255, ${0.5 * trailFade})`,
                    filter: `blur(${isBehind ? 1.5 : 0}px)`,
                  }}
                />
              );
            }

            return <>{trailElements}</>;
          })()}
        </div>

        {/* Neural stripe - the signature */}
        <div
          style={{
            width: 400,
            height: 4,
            marginTop: 48,
            marginBottom: 48,
            borderRadius: 2,
            background: `linear-gradient(90deg,
              #0a2463 0%,
              #1e5aa8 25%,
              #00b4d8 50%,
              #48cae4 75%,
              #ffffff 100%
            )`,
            opacity: stripeProgress,
            clipPath: `inset(0 ${(1 - stripeProgress) * 100}% 0 0)`,
          }}
        />

        {/* Tagline */}
        <div
          style={{
            fontSize: 32,
            fontWeight: 300,
            fontFamily: "'SF Pro Display', -apple-system, 'Helvetica Neue', sans-serif",
            letterSpacing: '0.03em',
            color: '#ffffff',
            opacity: taglineOpacity,
            transform: `translateY(${taglineY}px)`,
          }}
        >
          The mind is the last frontier worth protecting.
        </div>
      </div>
    </AbsoluteFill>
  );
};
