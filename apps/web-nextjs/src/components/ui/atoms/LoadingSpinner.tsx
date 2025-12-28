'use client'

import React from 'react'

interface LoadingSpinnerProps {
  /** Size in pixels */
  size?: number
  /** Custom colors for light/dark mode */
  colors?: {
    light: {
      background: string
      ring: string
      accent: string
      text: string
    }
    dark: {
      background: string
      ring: string
      accent: string
      text: string
    }
  }
  /** Whether to show app branding */
  showBranding?: boolean
  /** Custom brand text */
  brandText?: string
  /** Animation speed multiplier (higher = faster) */
  speed?: number
  /** Theme preference (auto-detected if not provided) */
  theme?: 'light' | 'dark' | 'auto'
}

/**
 * Professional loading spinner component
 *
 * Features:
 * - Dual-ring animation (outer pulse + inner spin)
 * - Theme-aware colors
 * - Configurable size and speed
 * - Optional branding
 * - Consistent with industry standards (GitHub, Linear, etc.)
 */
export function LoadingSpinner({
  size = 32,
  colors,
  showBranding = false,
  brandText = 'Next Watch',
  speed = 1,
  theme = 'auto',
}: LoadingSpinnerProps) {
  // Auto-detect theme if not specified
  const isDark =
    theme === 'auto'
      ? typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches
      : theme === 'dark'

  // Default GitHub-style colors
  const defaultColors = {
    light: {
      background: '***REMOVED***ffffff',
      ring: '***REMOVED***d1d9e0',
      accent: '***REMOVED***0969da',
      text: '***REMOVED***656d76',
    },
    dark: {
      background: '***REMOVED***0d1117',
      ring: '***REMOVED***30363d',
      accent: '***REMOVED***58a6ff',
      text: '***REMOVED***7d8590',
    },
  }

  const currentColors = colors || defaultColors
  const themeColors = isDark ? currentColors.dark : currentColors.light

  // Calculate animation durations based on speed
  const spinDuration = 0.8 / speed // Faster base spin
  const pulseDuration = 1.8 / speed // Faster pulse

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Spinner container */}
      <div
        style={{
          position: 'relative',
          width: `${size}px`,
          height: `${size}px`,
        }}
      >
        {/* Outer pulsing ring */}
        <div
          style={{
            position: 'absolute',
            width: `${size}px`,
            height: `${size}px`,
            border: `2px solid ${themeColors.ring}`,
            borderRadius: '50%',
            animation: `spinner-pulse ${pulseDuration}s ease-in-out infinite`,
          }}
        />

        {/* Inner spinning ring */}
        <div
          style={{
            position: 'absolute',
            width: `${size}px`,
            height: `${size}px`,
            border: '2px solid transparent',
            borderTop: `2px solid ${themeColors.accent}`,
            borderRadius: '50%',
            animation: `spinner-spin ${spinDuration}s linear infinite`,
          }}
        />
      </div>

      {/* Optional branding */}
      {showBranding && (
        <div
          style={{
            marginTop: `${size * 0.5}px`,
            color: themeColors.text,
            fontSize: `${size * 0.4375}px`, // Proportional to spinner size
            fontWeight: 500,
            opacity: 0.7,
            fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
          }}
        >
          {brandText}
        </div>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes spinner-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @keyframes spinner-pulse {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 0.6;
            transform: scale(1.05);
          }
        }
      `}</style>
    </div>
  )
}

/**
 * Preset configurations for common use cases
 */
export const LoadingSpinnerPresets = {
  /** Small spinner for inline loading */
  small: { size: 20, speed: 1.2 },

  /** Medium spinner for card/component loading */
  medium: { size: 32, speed: 1.0 },

  /** Large spinner for page/app loading */
  large: { size: 48, speed: 0.8, showBranding: true },

  /** Extra large for full-screen loading */
  xlarge: { size: 64, speed: 0.6, showBranding: true },
}

export default LoadingSpinner
