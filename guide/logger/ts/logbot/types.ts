export type LogLevel = 'trace' | 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  id?: number;
  timestamp: number;
  level: LogLevel;
  module: string;
  functionName: string;
  event: 'entry' | 'exit' | 'error';
  args?: unknown[];
  result?: unknown;
  error?: {
    message: string;
    stack?: string;
  };
  duration?: number;
}

export interface InstrumentationPattern {
  include?: RegExp[];
  exclude?: RegExp[];
  functionPatterns?: RegExp[];
  filePatterns?: RegExp[];
}

export interface LogConfig {
  enabled: boolean;
  level: LogLevel;
  patterns: InstrumentationPattern;
  capture: {
    args: boolean;
    return: boolean;
    timing: boolean;
    errors: boolean;
    stack: boolean;
  };
  sampling: {
    enabled: boolean;
    rate: number;
    highFrequencyPatterns?: RegExp[];
  };
  storage: {
    maxEntries: number;
    maxAgeMs: number;
    cleanupThreshold: number;
    dbName?: string;
    storeName?: string;
    prefix?: string;
  };
  project?: {
    name?: string;
    rootPaths?: string[];
    moduleNameTransform?: (filePath: string) => string;
    loggerImportPath?: string;
  };
  performance?: {
    warnThreshold?: number;
    errorThreshold?: number;
  };
}

export interface Logger {
  entry(module: string, functionName: string, args?: unknown[]): void;
  exit(module: string, functionName: string, result?: unknown, duration?: number): void;
  error(module: string, functionName: string, error: Error): void;
  getEntries(limit?: number): Promise<LogEntry[]>;
  clear(): Promise<void>;
  export(): Promise<void>;
}
