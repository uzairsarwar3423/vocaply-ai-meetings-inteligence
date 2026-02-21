/**
 * WebSocket Event Types
 * Vocaply AI Meeting Intelligence – Day 14
 *
 * Canonical event names and payload types that mirror the backend's
 * `core/websocket.py` definitions.  Import from here instead of
 * using raw strings throughout the app.
 */

// ── Client → Server ────────────────────────────────────────────────────────────

export const ClientEvent = {
    AUTHENTICATE: "authenticate",
    SUBSCRIBE: "subscribe",
    UNSUBSCRIBE: "unsubscribe",
    PING: "ping",
} as const;

export type ClientEventType = (typeof ClientEvent)[keyof typeof ClientEvent];

// ── Server → Client ────────────────────────────────────────────────────────────

export const ServerEvent = {
    // lifecycle
    CONNECTED: "connected",
    AUTHENTICATED: "authenticated",
    SUBSCRIBED: "subscribed",
    UNSUBSCRIBED: "unsubscribed",
    PONG: "pong",
    ERROR: "error",
    // meeting
    MEETING_UPDATED: "meeting_updated",
    // action items
    ACTION_ITEM_CREATED: "action_item_created",
    ACTION_ITEM_UPDATED: "action_item_updated",
    // notifications
    NOTIFICATION_RECEIVED: "notification_received",
    // bot / transcript
    BOT_STATUS_CHANGED: "bot_status_changed",
    TRANSCRIPT_CHUNK: "transcript_chunk",
} as const;

export type ServerEventType = (typeof ServerEvent)[keyof typeof ServerEvent];

// ── Subscription channels ──────────────────────────────────────────────────────

export const Channel = {
    MEETING: "meeting",
    ACTION_ITEMS: "action_items",
    NOTIFICATIONS: "notifications",
} as const;

export type ChannelType = (typeof Channel)[keyof typeof Channel];

// ── Connection state ───────────────────────────────────────────────────────────

export type ConnectionStatus =
    | "IDLE"
    | "CONNECTING"
    | "CONNECTED"
    | "AUTHENTICATED"
    | "RECONNECTING"
    | "DISCONNECTED"
    | "FAILED";

// ── Message envelope ───────────────────────────────────────────────────────────

export interface WSMessage<T = unknown> {
    event: string;
    data?: T;
    request_id?: string;
}

// ── Payload types ──────────────────────────────────────────────────────────────

export interface ConnectedPayload { connection_id: string; message: string }
export interface AuthenticatedPayload { user_id: string; company_id: string }
export interface SubscribedPayload { channel: string; resource_id?: string }
export interface PongPayload { ts: string }

export interface ErrorPayload {
    code: string;
    message: string;
    detail?: unknown;
}

export interface MeetingUpdatedPayload {
    id: string;
    title?: string;
    status?: string;
    [key: string]: unknown;
}

export interface ActionItemPayload {
    id: string;
    title: string;
    meeting_id: string;
    assignee_id?: string;
    status?: string;
    [key: string]: unknown;
}

export interface NotificationPayload {
    id: string;
    type: string;
    title: string;
    message: string;
    data?: unknown;
}

export interface BotStatusPayload {
    meeting_id: string;
    status: string;
    detail?: string;
}

export interface TranscriptChunkPayload {
    meeting_id: string;
    speaker?: string;
    text: string;
    start_time: number;
    is_final: boolean;
}
