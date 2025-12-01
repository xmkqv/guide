import type { LogEntry, Logger } from './types';
import { logConfig } from './config';

class LogBotLogger implements Logger {
  private dbName = 'qx_logbot';
  private storeName = 'entries';
  private db: IDBDatabase | null = null;
  private initPromise: Promise<void> | null = null;
  private writeQueue: LogEntry[] = [];
  private flushTimer: ReturnType<typeof setTimeout> | null = null;
  private fallbackToConsole = false;

  constructor() {
    this.initPromise = this.init();
  }

  private async init(): Promise<void> {
    if (typeof indexedDB === 'undefined') {
      console.warn('[log-bot] IndexedDB not available, falling back to console');
      this.fallbackToConsole = true;
      return;
    }

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        if (!db.objectStoreNames.contains(this.storeName)) {
          const store = db.createObjectStore(this.storeName, {
            keyPath: 'id',
            autoIncrement: true,
          });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('module', 'module', { unique: false });
          store.createIndex('level', 'level', { unique: false });
        }
      };
    });
  }

  private async ensureReady(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise;
    }
  }

  private shouldLog(functionName: string): boolean {
    if (!logConfig.enabled) return false;

    if (logConfig.sampling.enabled) {
      const isHighFrequency = logConfig.sampling.highFrequencyPatterns?.some(
        (pattern) => pattern.test(functionName),
      );

      if (isHighFrequency) {
        return Math.random() < logConfig.sampling.rate;
      }
    }

    return true;
  }

  private scheduleFlush(): void {
    if (this.flushTimer) return;

    this.flushTimer = setTimeout(() => {
      this.flush();
    }, 100);
  }

  private async flush(): Promise<void> {
    this.flushTimer = null;

    if (this.writeQueue.length === 0) return;

    const entries = [...this.writeQueue];
    this.writeQueue = [];

    if (this.fallbackToConsole) {
      for (const entry of entries) {
        const prefix = `[${entry.level}] ${entry.module}.${entry.functionName}`;
        if (entry.event === 'entry') {
          console.debug(`${prefix} →`, entry.args);
        } else if (entry.event === 'exit') {
          console.debug(`${prefix} ← ${entry.duration}ms`, entry.result);
        } else if (entry.event === 'error') {
          console.error(`${prefix} ✗`, entry.error);
        }
      }
      return;
    }

    if (!this.db) return;

    try {
      const transaction = this.db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);

      for (const entry of entries) {
        store.add(entry);
      }

      await new Promise<void>((resolve, reject) => {
        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
      });

      await this.checkQuota();
    } catch (error) {
      console.error('[log-bot] Failed to flush logs, falling back to console:', error);
      this.fallbackToConsole = true;
      for (const entry of entries) {
        console.log('[log-bot]', entry);
      }
    }
  }

  private async checkQuota(): Promise<void> {
    if (!this.db) return;

    if ('storage' in navigator && 'estimate' in navigator.storage) {
      try {
        const estimate = await navigator.storage.estimate();
        const percentUsed = (estimate.usage ?? 0) / (estimate.quota ?? 1);

        if (percentUsed > logConfig.storage.cleanupThreshold) {
          await this.rotate();
        }
      } catch (error) {
        console.error('Failed to check storage quota:', error);
      }
    }

    const count = await this.getCount();
    if (count > logConfig.storage.maxEntries) {
      await this.rotate();
    }
  }

  private async getCount(): Promise<number> {
    if (!this.db) return 0;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.count();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  private async rotate(): Promise<void> {
    if (!this.db) return;

    try {
      const transaction = this.db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const index = store.index('timestamp');

      const now = Date.now();
      const maxAge = logConfig.storage.maxAgeMs;
      const cutoffTime = now - maxAge;

      const range = IDBKeyRange.upperBound(cutoffTime);
      const request = index.openCursor(range);

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest<IDBCursorWithValue>).result;
        if (cursor) {
          cursor.delete();
          cursor.continue();
        }
      };

      await new Promise<void>((resolve, reject) => {
        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
      });

      const count = await this.getCount();
      if (count > logConfig.storage.maxEntries) {
        await this.deleteOldest(count - logConfig.storage.maxEntries);
      }
    } catch (error) {
      console.error('Failed to rotate logs:', error);
    }
  }

  private async deleteOldest(count: number): Promise<void> {
    if (!this.db) return;

    const transaction = this.db.transaction([this.storeName], 'readwrite');
    const store = transaction.objectStore(this.storeName);
    const index = store.index('timestamp');

    let deleted = 0;
    const request = index.openCursor();

    request.onsuccess = (event) => {
      const cursor = (event.target as IDBRequest<IDBCursorWithValue>).result;
      if (cursor && deleted < count) {
        cursor.delete();
        deleted++;
        cursor.continue();
      }
    };

    await new Promise<void>((resolve, reject) => {
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  entry(module: string, functionName: string, args?: unknown[]): void {
    if (!this.shouldLog(functionName)) return;

    const entry: LogEntry = {
      timestamp: Date.now(),
      level: logConfig.level,
      module,
      functionName,
      event: 'entry',
    };

    if (logConfig.capture.args && args) {
      try {
        entry.args = args;
      } catch {
        entry.args = ['<non-serializable>'];
      }
    }

    this.writeQueue.push(entry);
    this.scheduleFlush();
  }

  exit(module: string, functionName: string, result?: unknown, duration?: number): void {
    if (!this.shouldLog(functionName)) return;

    // Performance budget warnings
    if (duration !== undefined && logConfig.performance) {
      const { warnThreshold, errorThreshold } = logConfig.performance;

      if (errorThreshold && duration > errorThreshold) {
        console.error(
          `[log-bot] SLOW: ${module}.${functionName} took ${duration.toFixed(2)}ms (>${errorThreshold}ms threshold)`
        );
      } else if (warnThreshold && duration > warnThreshold) {
        console.warn(
          `[log-bot] Slow: ${module}.${functionName} took ${duration.toFixed(2)}ms (>${warnThreshold}ms threshold)`
        );
      }
    }

    const entry: LogEntry = {
      timestamp: Date.now(),
      level: logConfig.level,
      module,
      functionName,
      event: 'exit',
    };

    if (logConfig.capture.return && result !== undefined) {
      try {
        entry.result = result;
      } catch {
        entry.result = '<non-serializable>';
      }
    }

    if (logConfig.capture.timing && duration !== undefined) {
      entry.duration = duration;
    }

    this.writeQueue.push(entry);
    this.scheduleFlush();
  }

  error(module: string, functionName: string, error: Error): void {
    if (!logConfig.capture.errors) return;

    const entry: LogEntry = {
      timestamp: Date.now(),
      level: 'error',
      module,
      functionName,
      event: 'error',
      error: {
        message: error.message,
        stack: logConfig.capture.stack ? error.stack : undefined,
      },
    };

    this.writeQueue.push(entry);
    this.scheduleFlush();
  }

  async getEntries(limit = 100): Promise<LogEntry[]> {
    await this.ensureReady();
    if (!this.db) return [];

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const index = store.index('timestamp');

      const entries: LogEntry[] = [];
      const request = index.openCursor(null, 'prev');

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest<IDBCursorWithValue>).result;
        if (cursor && entries.length < limit) {
          entries.push(cursor.value);
          cursor.continue();
        } else {
          resolve(entries);
        }
      };

      request.onerror = () => reject(request.error);
    });
  }

  async clear(): Promise<void> {
    await this.ensureReady();
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async export(): Promise<void> {
    const entries = await this.getEntries(10000);

    const blob = new Blob([JSON.stringify(entries, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `qx-logbot-${Date.now()}.json`;
    a.click();

    URL.revokeObjectURL(url);
  }
}

export const logbot = new LogBotLogger();
