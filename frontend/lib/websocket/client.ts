/**
 * WebSocket Client
 * Vocaply AI Meeting Intelligence – Day 14
 *
 * A thin, framework-agnostic WebSocket wrapper that provides:
 *  • Auto-reconnect with exponential backoff
 *  • JWT authentication handshake
 *  • Typed event subscription/unsubscription
 *  • Message queuing during disconnects
 *  • Heartbeat ping/pong
 */

import { ReconnectScheduler } from "./reconnect";
import {
    ClientEvent,
    ServerEvent,
    ServerEventType,
    ConnectionStatus,
    WSMessage,
    ChannelType,
} from "./events";

const WS_BASE_URL = (
    process.env.NEXT_PUBLIC_WS_URL ??
    (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1")
        .replace(/^http/, "ws")
        .replace(/\/api\/v1$/, "")
) + "/api/v1/ws";

// ── Types ──────────────────────────────────────────────────────────────────────

type EventHandler<T = unknown> = (data: T) => void;

interface QueuedMessage {
    event: string;
    data?: unknown;
    reqId?: string;
}

// ── Client ─────────────────────────────────────────────────────────────────────

export class VocalplyWebSocketClient {
    private ws: WebSocket | null = null;
    private status: ConnectionStatus = "IDLE";
    private scheduler: ReconnectScheduler;
    private pingTimer?: ReturnType<typeof setInterval>;
    private token: string | null = null;
    private queue: QueuedMessage[] = [];
    private listeners: Map<string, Set<EventHandler<any>>> = new Map();
    private statusListeners: Set<(s: ConnectionStatus) => void> = new Set();

    constructor() {
        this.scheduler = new ReconnectScheduler({
            initialDelayMs: 1_000,
            maxDelayMs: 30_000,
            maxAttempts: 15,
            jitter: 0.3,
        });
    }

    // ── Public API ─────────────────────────────────────────────────────────────

    /** Open the connection.  Retains `token` for re-authentication on reconnect. */
    connect(token: string): void {
        this.token = token;
        this._open();
    }

    /** Gracefully close the connection and stop reconnect attempts. */
    disconnect(): void {
        this.scheduler.cancel();
        this._stopPing();
        this.setStatus("DISCONNECTED");
        if (this.ws) {
            this.ws.onclose = null; // prevent reconnect
            this.ws.close();
            this.ws = null;
        }
    }

    /** Subscribe to a server event. Returns an unsubscribe function. */
    on<T = unknown>(event: ServerEventType | string, handler: EventHandler<T>): () => void {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event)!.add(handler as EventHandler<unknown>);
        return () => this.off(event, handler);
    }

    /** Remove a previously registered event handler. */
    off<T = unknown>(event: string, handler: EventHandler<T>): void {
        this.listeners.get(event)?.delete(handler as EventHandler<unknown>);
    }

    /** Subscribe to connection-status changes. */
    onStatusChange(cb: (s: ConnectionStatus) => void): () => void {
        this.statusListeners.add(cb);
        return () => this.statusListeners.delete(cb);
    }

    /** Subscribe to a channel (e.g. "meeting", "action_items"). */
    subscribe(channel: ChannelType, resourceId?: string): void {
        this.send(ClientEvent.SUBSCRIBE, { channel, resource_id: resourceId });
    }

    /** Unsubscribe from a channel. */
    unsubscribe(channel: ChannelType, resourceId?: string): void {
        this.send(ClientEvent.UNSUBSCRIBE, { channel, resource_id: resourceId });
    }

    get connectionStatus(): ConnectionStatus {
        return this.status;
    }

    get isAuthenticated(): boolean {
        return this.status === "AUTHENTICATED";
    }

    // ── Internal helpers ───────────────────────────────────────────────────────

    private _open(): void {
        if (this.ws) {
            this.ws.onclose = null;
            this.ws.close();
            this.ws = null;
        }

        this.setStatus(this.scheduler.currentAttempt > 0 ? "RECONNECTING" : "CONNECTING");

        try {
            this.ws = new WebSocket(WS_BASE_URL);
        } catch (err) {
            console.error("[WS] Failed to construct WebSocket:", err);
            this._scheduleReconnect();
            return;
        }

        this.ws.onopen = this._onOpen.bind(this);
        this.ws.onmessage = this._onMessage.bind(this);
        this.ws.onerror = this._onError.bind(this);
        this.ws.onclose = this._onClose.bind(this);
    }

    private _onOpen(): void {
        this.setStatus("CONNECTED");
        // Authenticate immediately
        if (this.token) {
            this._rawSend(ClientEvent.AUTHENTICATE, { token: this.token });
        }
    }

    private _onMessage(ev: MessageEvent): void {
        let msg: WSMessage;
        try {
            msg = JSON.parse(ev.data as string);
        } catch {
            console.warn("[WS] Invalid JSON:", ev.data);
            return;
        }

        if (msg.event === ServerEvent.AUTHENTICATED) {
            this.setStatus("AUTHENTICATED");
            this.scheduler.reset();
            this._startPing();
            this._flushQueue();
        }

        this._emit(msg.event, msg.data);
    }

    private _onError(ev: Event): void {
        console.error("[WS] Socket error", ev);
    }

    private _onClose(ev: CloseEvent): void {
        this._stopPing();
        if (this.status !== "DISCONNECTED") {
            this.setStatus("RECONNECTING");
            this._scheduleReconnect();
        }
    }

    private _scheduleReconnect(): void {
        if (this.scheduler.exhausted) {
            this.setStatus("FAILED");
            console.error("[WS] Max reconnect attempts reached.");
            return;
        }

        const delay = this.scheduler.schedule(() => this._open());
        console.info(`[WS] Reconnecting in ${delay}ms (attempt ${this.scheduler.currentAttempt})`);
    }

    // ── Send ──────────────────────────────────────────────────────────────────

    private send(event: string, data?: unknown, reqId?: string): void {
        if (this.ws?.readyState === WebSocket.OPEN && this.status === "AUTHENTICATED") {
            this._rawSend(event, data, reqId);
        } else {
            // Queue for delivery once authenticated
            if (this.queue.length < 500) {
                this.queue.push({ event, data, reqId });
            }
        }
    }

    private _rawSend(event: string, data?: unknown, reqId?: string): void {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
        const msg: WSMessage = { event, data, request_id: reqId };
        this.ws.send(JSON.stringify(msg));
    }

    private _flushQueue(): void {
        while (this.queue.length > 0) {
            const { event, data, reqId } = this.queue.shift()!;
            this._rawSend(event, data, reqId);
        }
    }

    // ── Heartbeat ─────────────────────────────────────────────────────────────

    private _startPing(): void {
        this._stopPing();
        this.pingTimer = setInterval(() => {
            this._rawSend(ClientEvent.PING);
        }, 25_000);
    }

    private _stopPing(): void {
        if (this.pingTimer !== undefined) {
            clearInterval(this.pingTimer);
            this.pingTimer = undefined;
        }
    }

    // ── Status & event emission ────────────────────────────────────────────────

    private setStatus(s: ConnectionStatus): void {
        this.status = s;
        this.statusListeners.forEach(cb => cb(s));
    }

    private _emit(event: string, data?: unknown): void {
        this.listeners.get(event)?.forEach(h => h(data));
    }
}

// ── Singleton exported for use across the app ──────────────────────────────────

export const wsClient = new VocalplyWebSocketClient();
