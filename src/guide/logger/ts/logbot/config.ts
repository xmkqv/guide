import type { LogConfig } from './types';

const isProd = process.env.NODE_ENV === 'production';
const isDev = process.env.NODE_ENV === 'development';
const isDebug = process.env.DEBUG === 'true';

export const logConfig: LogConfig = {
  // Enable in all environments except test
  // Can be overridden by DEBUG=true flag
  enabled: process.env.NODE_ENV !== 'test' || isDebug,

  level: isProd ? 'info' : 'debug',

  patterns: {
    // File filtering uses cascading logic:
    // 1. exclude patterns are hard vetoes (skip file immediately)
    // 2. include patterns must match (if defined)
    // 3. filePatterns must match (if defined)
    // All conditions use AND logic: file must pass all checks

    // When DEBUG=true, instrument more broadly for debugging
    // Otherwise, only instrument specific paths
    include: isDebug
      ? [/\/src\//]  // Everything in src when debugging
      : [
          /\/src\/api\//,
          /\/src\/.*\.ts$/,
        ],

    // Files matching exclude patterns are NEVER instrumented (hard veto)
    exclude: [
      /node_modules/,
      /\.spec\.ts$/,
      /\.test\.ts$/,
      /test-setup\.ts$/,
      /\/dev\//,
    ],

    // Only instrument functions matching these patterns
    // If empty or undefined, all named functions are instrumented
    functionPatterns: [
      /^(get|set|fetch|create|update|delete|process|handle|init|sync)/i,
      /^async\s+function/,
    ],

    // Additional file-level filter applied after include check
    // Must match one of these patterns (if defined)
    filePatterns: [
      /\/api\/rw\//,
      /\/sync\//,
      /\/write\//,
      /\/auth\//,
    ],
  },

  capture: {
    args: !isProd,
    return: !isProd,
    timing: true,
    errors: true,
    stack: !isProd,
  },

  sampling: {
    // Sampling ONLY applies to functions matching highFrequencyPatterns
    // All other functions are logged 100% of the time
    // Example: onClick sampled at 10%, fetchUser logged always
    enabled: isProd,
    rate: 0.1,
    highFrequencyPatterns: [
      /^on[A-Z]/,
      /^handle(Click|Mouse|Scroll|Resize)/,
    ],
  },

  storage: {
    // Rotation triggers when EITHER limit is exceeded (whichever hits first)
    // In production with high traffic, maxEntries typically triggers before maxAgeMs
    // Environment-aware: production needs larger buffer for meaningful observability
    maxEntries: isProd ? 50000 : 1000,
    maxAgeMs: isProd
      ? (24 * 60 * 60 * 1000)      // 1 day in production
      : (7 * 24 * 60 * 60 * 1000), // 7 days in development
    cleanupThreshold: 0.8,  // Trigger rotation at 80% storage quota
    dbName: 'qx_logbot',
    storeName: 'entries',
    prefix: 'log-bot',
  },

  project: {
    name: 'qx',
    rootPaths: ['/qx-ui/src/', '/qx-ts/src/', '/src/'],
    loggerImportPath: '/plugins/log-bot/logger',
  },

  performance: {
    // Warn when functions exceed these thresholds
    warnThreshold: 1000,   // 1 second
    errorThreshold: 5000,  // 5 seconds
  },
};
