import { createUnplugin } from 'unplugin';
import { instrumentCode } from './instrumentor';
import { logConfig } from './config';

export const logBotPlugin = createUnplugin(() => ({
  name: 'log-bot',
  enforce: 'pre',

  transformInclude(id) {
    if (!logConfig.enabled) {
      return false;
    }

    if (id.includes('node_modules')) {
      return false;
    }

    if (!/\.(ts|tsx|js|jsx)$/.test(id)) {
      return false;
    }

    if (id.includes('plugins/log-bot')) {
      return false;
    }

    return true;
  },

  transform(code, id) {
    const result = instrumentCode({ filePath: id, code });

    if (!result) {
      return null;
    }

    return {
      code: result.code,
      map: result.map,
    };
  },
}));

export const vite = logBotPlugin.vite;
export const webpack = logBotPlugin.webpack;
export const rollup = logBotPlugin.rollup;
export const esbuild = logBotPlugin.esbuild;

export { logbot } from './logger';
export { logConfig } from './config';
export type { Logger, LogEntry, LogLevel, LogConfig } from './types';
