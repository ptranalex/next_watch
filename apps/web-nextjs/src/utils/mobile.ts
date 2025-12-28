/**
 * Mobile utilities for handling browser-specific issues and optimizations
 */
import { createLogger } from '@/utils/logging'

// Create logger for mobile utilities
const logger = createLogger('MobileUtils')

/**
 * Fixes the viewport height issues on mobile browsers
 * iOS Safari and some other mobile browsers don't handle 100vh correctly
 * This function sets a CSS variable that can be used instead of 100vh
 */
export function setupMobileViewportHeight() {
  if (typeof window === 'undefined') return

  const setAppHeight = () => {
    const doc = document.documentElement
    const height = `${window.innerHeight}px`
    doc.style.setProperty('--app-height', height)
    logger.debug(`Setting app height: ${height}`)
  }

  try {
    // Set initial height
    setAppHeight()

    // Update on resize and orientation change
    window.addEventListener('resize', setAppHeight)
    window.addEventListener('orientationchange', setAppHeight)

    // Clean up when the app unmounts (for hot reloading in dev)
    if (process.env.NODE_ENV === 'development') {
      return () => {
        window.removeEventListener('resize', setAppHeight)
        window.removeEventListener('orientationchange', setAppHeight)
      }
    }

    logger.info('Mobile viewport height fix initialized')
  } catch (error) {
    logger.error('Failed to setup mobile viewport height fix', error)
  }
}

/**
 * Determines if the current device is an iOS device
 */
export function isIOSDevice(): boolean {
  if (typeof window === 'undefined') return false

  const userAgent = window.navigator.userAgent.toLowerCase()
  return /iphone|ipad|ipod/.test(userAgent)
}

/**
 * Determines if the current device is a touch device
 */
export function isTouchDevice(): boolean {
  if (typeof window === 'undefined') return false

  return (
    'ontouchstart' in window ||
    navigator.maxTouchPoints > 0 ||
    // Some IE/Edge versions use msMaxTouchPoints instead
    // Using interface augmentation to handle the type safely
    ('msMaxTouchPoints' in navigator &&
      (navigator as Navigator & { msMaxTouchPoints: number }).msMaxTouchPoints > 0)
  )
}

/**
 * Applies all mobile-specific fixes and optimizations
 * Call this function on app initialization
 */
export function initializeMobileOptimizations() {
  if (typeof window === 'undefined') return

  try {
    // Fix viewport height
    setupMobileViewportHeight()

    // Log mobile environment for debugging
    logger.info(`Device detected:
      iOS: ${isIOSDevice()},
      Touch: ${isTouchDevice()},
      UserAgent: ${window.navigator.userAgent}
    `)

    // Add mobile-specific body class for CSS targeting
    if (isTouchDevice()) {
      document.body.classList.add('touch-device')
    }

    if (isIOSDevice()) {
      document.body.classList.add('ios-device')
    }
  } catch (error) {
    logger.error('Failed to initialize mobile optimizations', error)
  }
}
