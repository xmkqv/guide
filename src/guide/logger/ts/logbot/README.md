# log-bot

Universal automatic function instrumentation plugin built with unplugin.

## Features

- Universal bundler support (Vite, Webpack, Rollup, esbuild)
- Automatic function entry/exit logging
- Zero manual log calls required
- Pattern-based selective instrumentation
- IndexedDB storage with automatic rotation
- Configurable sampling for production
- Source map preservation
- Worker-compatible

## Installation

Dependencies are already installed:
- unplugin
- @babel/parser
- @babel/traverse
- @babel/generator
- @babel/types

## Usage

### Vite

```typescript
import { vite as logBot } from './plugins/log-bot';

export default defineConfig({
  plugins: [
    logBot(), // Must be first
    // ... other plugins
  ],
});
```

### Webpack

```javascript
const { webpack: logBot } = require('./plugins/log-bot');

module.exports = {
  plugins: [
    logBot(),
  ],
};
```

### Rollup

```javascript
import { rollup as logBot } from './plugins/log-bot';

export default {
  plugins: [
    logBot(),
  ],
};
```

### esbuild

```javascript
import { esbuild as logBot } from './plugins/log-bot';

require('esbuild').build({
  plugins: [
    logBot(),
  ],
});
```

## Configuration

Edit `plugins/log-bot/config.ts` to customize:

### File Patterns

```typescript
patterns: {
  include: [
    /\/src\/api\//,
    /\/src\/.*\.ts$/,
  ],
  exclude: [
    /node_modules/,
    /\.spec\.ts$/,
    /\/dev\//,
  ],
}
```

### Function Patterns

```typescript
functionPatterns: [
  /^(get|set|fetch|create|update|delete|process|handle|init|sync)/i,
]
```

### Capture Settings

```typescript
capture: {
  args: process.env.NODE_ENV !== 'production',
  return: process.env.NODE_ENV !== 'production',
  timing: true,
  errors: true,
  stack: process.env.NODE_ENV !== 'production',
}
```

### Sampling

```typescript
sampling: {
  enabled: process.env.NODE_ENV === 'production',
  rate: 0.1,
  highFrequencyPatterns: [
    /^on[A-Z]/,
    /^handle(Click|Mouse|Scroll|Resize)/,
  ],
}
```

### Storage Management

```typescript
storage: {
  maxEntries: 1000,
  maxAgeMs: 7 * 24 * 60 * 60 * 1000,
  cleanupThreshold: 0.8,
}
```

## Accessing Logs

The logger is globally available (no imports needed):

### View Recent Logs

```typescript
const entries = await logbot.getEntries(100);
console.table(entries);
```

### Export Logs

```typescript
await logbot.export();
```

### Clear Logs

```typescript
await logbot.clear();
```

### Browser DevTools

Open IndexedDB in DevTools:
- Application tab → Storage → IndexedDB → qx_logbot → entries

## How It Works

1. unplugin intercepts all `.ts`/`.tsx`/`.js`/`.jsx` files during build
2. Babel parses code into AST
3. Plugin wraps matching functions with:
   - Entry log (function name, module, args)
   - Try-catch for error logging
   - Exit log (return value, timing)
4. Logger batches writes to IndexedDB (100ms flush)
5. Automatic rotation when quota/count exceeded

## Example Output

```json
{
  "timestamp": 1234567890,
  "level": "debug",
  "module": "qx.sync.electric",
  "functionName": "createFluxShape",
  "event": "entry",
  "args": [{"offset": 0, "scopeId": "abc123"}]
}
```

```json
{
  "timestamp": 1234567950,
  "level": "debug",
  "module": "qx.sync.electric",
  "functionName": "createFluxShape",
  "event": "exit",
  "result": {"success": true},
  "duration": 60
}
```

## Performance

- Build-time transformation: No runtime overhead
- Batched IndexedDB writes: 100ms flush interval
- Sampling in production: 90% reduction in log volume
- Pattern filtering: Only instruments matching functions

## Universal Bundler Support

Unlike traditional bundler-specific plugins, log-bot uses unplugin to provide a single implementation that works across:
- Vite
- Webpack
- Rollup
- esbuild

This means:
- Write once, run everywhere
- Easy migration between bundlers
- Consistent behavior across build tools
- Single codebase to maintain

## Differences from auto-logger

- Universal bundler support via unplugin (vs Vite-only)
- Exports separate adapters for each bundler
- Uses `logbot` global instead of `logger`
- Separate IndexedDB database (`qx_logbot` vs `qx_logs`)
- Can run alongside auto-logger for comparison

## Debugging

If functions are not being instrumented:

1. Check file patterns match your files
2. Check function names match patterns
3. Verify `enabled: true` in config
4. Check browser console for plugin errors
5. Verify plugin is listed first in plugins array

## Disabling

Set `enabled: false` in `plugins/log-bot/config.ts` or remove plugin from build config.

## TypeScript

Global types can be declared in `env.d.ts`:
- `logbot` - Logger instance
- `__logStart_*` - Timing variables
- `__logResult` - Return value capture
- `__logError` - Error capture

No imports needed in your code.
