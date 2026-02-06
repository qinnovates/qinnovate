/**
 * ONI Framework Design System
 * Color palette optimized for trust, curiosity, and investment psychology
 *
 * Psychology-backed color choices:
 * - Deep blue-purple: Trust + Innovation
 * - Cyan accents: Openness + Futuristic
 * - Purple highlights: Curiosity + Forward-thinking
 */

export const colors = {
  // Primary palette - blue-purple for trust + innovation
  primary: {
    dark: '#080b16',       // Deep blue-purple background (trust + depth)
    darkPurple: '#0d0f1a', // Subtle purple undertone
    main: '#1a1a3e',       // Blue-purple midtone (innovation)
    light: '#2d2d5a',      // Lighter purple-blue
    accent: '#00e5ff',     // Cyan accent (openness, futuristic)
    accentPurple: '#a855f7', // Purple accent (curiosity, creativity)
  },

  // Layer colors - 14-layer model
  // Source of truth: MAIN/resources/brand/brand.json > layers section
  // MUST MATCH: docs/index.html, LayerStack.tsx
  silicon: {
    L1: '#1e3a5f',  // Physical Carrier - dark blue
    L2: '#1e4d6f',  // Signal Processing
    L3: '#1e5f7f',  // Protocol
    L4: '#1e6f8f',  // Transport
    L5: '#1e7f9f',  // Session
    L6: '#1e8faf',  // Presentation
    L7: '#2d9fbf',  // Application Interface - teal
  },

  gateway: {
    L8: '#d97706',  // Neural Gateway - amber (bridge)
  },

  biology: {
    L9:  '#14532d',  // Signal Processing (Filtering) - dark green
    L10: '#166534',  // Neural Protocol (Encoding)
    L11: '#15803d',  // Cognitive Transport (Delivery)
    L12: '#16a34a',  // Cognitive Session (Context)
    L13: '#22c55e',  // Semantic Layer (Intent)
    L14: '#4ade80',  // Identity Layer (Self) - light green
  },

  // Security states
  security: {
    safe: '#00c853',
    warning: '#ffc107',
    danger: '#f44336',
    blocked: '#ff1744',
  },

  // Text colors
  text: {
    primary: '#ffffff',
    secondary: 'rgba(255, 255, 255, 0.75)',
    muted: 'rgba(255, 255, 255, 0.5)',
  },

  // Psychology-optimized gradients
  gradients: {
    // Main background - trust (blue) + innovation (purple)
    background: 'radial-gradient(ellipse at center, #1a1a3e 0%, #0d0f1a 50%, #080b16 100%)',
    backgroundSubtle: 'radial-gradient(ellipse at 50% 30%, #1a1a3e15 0%, #080b16 70%)',

    // Title gradient - premium feel
    title: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #a855f7 100%)',

    // Text gradients
    textPremium: 'linear-gradient(180deg, #ffffff 0%, rgba(200,210,230,0.9) 100%)',
    textAccent: 'linear-gradient(90deg, #00e5ff, #a855f7)',

    // Layer gradients (matched to GitHub Pages)
    silicon: 'linear-gradient(180deg, #2d9fbf 0%, #1e3a5f 100%)',
    biology: 'linear-gradient(180deg, #4ade80 0%, #14532d 100%)',
    gateway: 'linear-gradient(180deg, #f59e0b 0%, #b45309 100%)',

    // Innovation/TARA scenes - purple emphasis
    innovation: 'radial-gradient(ellipse at 70% 50%, #7c3aed20 0%, #080b16 70%)',

    // CTA gradient - action-oriented
    cta: 'linear-gradient(135deg, #00e5ff 0%, #a855f7 100%)',
  },

  // Glow colors for effects
  glow: {
    cyan: '#00e5ff',
    purple: '#a855f7',
    blue: '#667eea',
  },
};

export const typography = {
  fontFamily: {
    heading: "'Inter', 'Segoe UI', sans-serif",
    body: "'Inter', 'Segoe UI', sans-serif",
    mono: "'Fira Code', 'Consolas', monospace",
  },
  fontSize: {
    title: 72,
    subtitle: 36,
    heading: 48,
    subheading: 32,
    body: 24,
    small: 18,
    formula: 28,
  },
};

export const spacing = {
  xs: 8,
  sm: 16,
  md: 24,
  lg: 32,
  xl: 48,
  xxl: 64,
};

export const animation = {
  // Spring configs
  spring: {
    gentle: { mass: 1, damping: 20, stiffness: 100 },
    bouncy: { mass: 1, damping: 15, stiffness: 150 },
    stiff: { mass: 1, damping: 25, stiffness: 200 },
  },
  // Timing in frames (30fps)
  timing: {
    fast: 10,
    medium: 20,
    slow: 30,
  },
};

// Video settings
export const videoConfig = {
  fps: 30,
  width: 1920,
  height: 1080,
  durationInSeconds: 231, // 3:51
  durationInFrames: 6930, // 3:51 at 30fps
};

// Scene timestamps (in frames at 30fps)
export const sceneTimestamps = {
  coldOpen: { start: 0, end: 8 * 30 },           // 0:00-0:08 (240 frames)
  title: { start: 8 * 30, end: 15 * 30 },         // 0:08-0:15 (210 frames)
  problem: { start: 15 * 30, end: 40 * 30 },      // 0:15-0:40 (750 frames)
  layers: { start: 40 * 30, end: 80 * 30 },       // 0:40-1:20 (1200 frames)
  coherence: { start: 80 * 30, end: 110 * 30 },   // 1:20-1:50 (900 frames)
  tara: { start: 110 * 30, end: 145 * 30 },       // 1:50-2:25 (1050 frames)
  academic: { start: 145 * 30, end: 164 * 30 },   // 2:25-2:44 (570 frames) - shortened to match 19s audio
  cta: { start: 164 * 30, end: 184 * 30 },        // 2:44-3:04 (600 frames) - shortened to match 17s voiceover
  credits: { start: 184 * 30, end: 231 * 30 },    // 3:04-3:51 (1410 frames) - finale with CTA at 3:39
};
