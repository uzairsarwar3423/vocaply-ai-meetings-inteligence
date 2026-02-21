/**
 * Exponential-backoff Reconnect Scheduler
 * Vocaply AI Meeting Intelligence – Day 14
 *
 * Handles the timing of WebSocket reconnect attempts so the client
 * gradually backs off rather than hammering the server.
 */

export interface ReconnectOptions {
    /** Initial delay in ms (default: 1 000) */
    initialDelayMs?: number;
    /** Maximum delay cap in ms (default: 30 000) */
    maxDelayMs?: number;
    /** Jitter fraction 0–1 added to each delay (default: 0.3) */
    jitter?: number;
    /** Maximum number of attempts before giving up (default: Infinity) */
    maxAttempts?: number;
    /** Backoff multiplier (default: 2) */
    multiplier?: number;
}

export class ReconnectScheduler {
    private attempt = 0;
    private timerId?: ReturnType<typeof setTimeout>;

    private readonly initialDelayMs: number;
    private readonly maxDelayMs: number;
    private readonly jitter: number;
    private readonly maxAttempts: number;
    private readonly multiplier: number;

    constructor(opts: ReconnectOptions = {}) {
        this.initialDelayMs = opts.initialDelayMs ?? 1_000;
        this.maxDelayMs = opts.maxDelayMs ?? 30_000;
        this.jitter = opts.jitter ?? 0.3;
        this.maxAttempts = opts.maxAttempts ?? Infinity;
        this.multiplier = opts.multiplier ?? 2;
    }

    /** Returns true when no more retries should be made. */
    get exhausted(): boolean {
        return this.attempt >= this.maxAttempts;
    }

    get currentAttempt(): number {
        return this.attempt;
    }

    /**
     * Schedule the next reconnect call.
     * @param onReconnect  Callback to invoke when the timer fires.
     * @returns            Scheduled delay in ms, or -1 if exhausted.
     */
    schedule(onReconnect: () => void): number {
        this.cancel();

        if (this.exhausted) return -1;

        const baseDelay = Math.min(
            this.initialDelayMs * Math.pow(this.multiplier, this.attempt),
            this.maxDelayMs
        );
        const jitterMs = baseDelay * this.jitter * Math.random();
        const delay = Math.floor(baseDelay + jitterMs);

        this.attempt++;

        this.timerId = setTimeout(onReconnect, delay);
        return delay;
    }

    /** Reset the attempt counter (call after a successful connection). */
    reset(): void {
        this.cancel();
        this.attempt = 0;
    }

    /** Cancel any pending reconnect timer. */
    cancel(): void {
        if (this.timerId !== undefined) {
            clearTimeout(this.timerId);
            this.timerId = undefined;
        }
    }
}
