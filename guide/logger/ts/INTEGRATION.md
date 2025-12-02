# TypeScript Logbot Integration

Build-time instrumentation for TypeScript/JavaScript projects using unplugin.

## Integration Strategy

### Option 1: Symlink (Recommended)

Create symlink in your TypeScript project:

```sh
cd my-ts-project
mkdir -p plugins
ln -s /Users/m/guide/src/guide/plugins/typescript/logbot plugins/logbot
```

Import in `vite.config.ts`:

```typescript
import { vite as logBot } from './plugins/logbot';

export default defineConfig({
  plugins: [
    logBot(),
    // ... other plugins
  ],
});
```

### Option 2: Direct Import

For monorepos or when guide is in parent directory:

```typescript
import { vite as logBot } from '../../guide/src/guide/plugins/typescript/logbot';
```

### Option 3: NPM Package (Future)

Publish as `@guide/logbot-ts` and install:

```sh
npm install @guide/logbot-ts
```

```typescript
import { vite as logBot } from '@guide/logbot-ts';
```

## Configuration

### Via mission.yaml (Preferred)

Add logging config to `mission.yaml`:

```yaml
id: my-project
name: My Project
guide: typescript
logging:
  enabled: true
  level: debug
  patterns:
    include:
      - /\/src\/api\//
      - /\/src\/.*\.ts$/
    exclude:
      - /node_modules/
      - /\.spec\.ts$/
    functionPatterns:
      - /^(get|set|fetch|create|update|delete|process|handle|init)/i
  capture:
    args: true
    return: true
    timing: true
    errors: true
  storage:
    maxEntries: 1000
    maxAgeMs: 604800000  # 7 days
```

The plugin will auto-detect `mission.yaml` in project root and use those settings.

### Via config.ts (Override)

Edit `plugins/logbot/config.ts` directly for project-specific overrides.

## Runtime API

Global `logbot` is available in browser (no imports needed):

```typescript
// View logs
const logs = await logbot.getEntries(100);
console.table(logs);

// Export logs
await logbot.export();

// Clear logs
await logbot.clear();
```

## Build-Time vs Runtime

Key difference from Python logbot:

- Python: Runtime instrumentation via import hooks
  (config loaded at process start)
- TypeScript: Build-time instrumentation via unplugin
  (config baked into build)

This means:

- TS logging config is read ONCE during build
- Changing mission.yaml requires rebuild
- But zero runtime overhead (instrumentation already done)

## Multi-Project Setup

For monorepo with shared guide:

```text
workspace/
  guide/
    src/guide/plugins/typescript/logbot/
  project-a/
    plugins/logbot → ../../guide/src/guide/plugins/typescript/logbot
    mission.yaml
    vite.config.ts
  project-b/
    plugins/logbot → ../../guide/src/guide/plugins/typescript/logbot
    mission.yaml
    vite.config.ts
```

Each project:

1. Symlinks to shared logbot implementation
2. Has own mission.yaml with project-specific logging config
3. Imports plugin in build config

## Signal Integration (Future)

Like Python logbot, TS logbot events can feed into Signals:

```typescript
// Hypothetical: mission.yaml configures signal emission
logging:
  emit_signals: true
  signal_endpoint: http://localhost:8000/api/signals

// Logbot automatically POSTs structured events
// Tests can analyze signals for ∆Vision → ∆Design feedback
```

## GuideType Polymorphism

Same mission schema, different backends:

```yaml
guide: python  # Uses plugins/python/logbot (structlog)
guide: typescript  # Uses plugins/typescript/logbot (unplugin)
guide: rust  # Uses plugins/rust/logbot (tracing)
```

All expose similar APIs (configure, instrument, timed, traced) but implementation differs by ecosystem.
