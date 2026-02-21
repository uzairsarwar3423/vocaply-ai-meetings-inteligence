"use client";

/**
 * useWebSocket Hook
 * Vocaply AI Meeting Intelligence – Day 14
 *
 * Manages the global WebSocket connection lifecycle for the current user.
 * Connects on mount (when a token is available), reconnects automatically,
 * and exposes the connection status + an `on` helper for event subscriptions.
 */

import { useEffect, useCallback, useState } from "react";
import { useAuthStore } from "../store/authStore";
import { wsClient } from "../lib/websocket/client";
import { ServerEventType, ConnectionStatus, ChannelType } from "../lib/websocket/events";

export interface UseWebSocketReturn {
    status: ConnectionStatus;
    isConnected: boolean;
    isAuthenticated: boolean;
    /** Subscribe to a server event; returns an unsubscribe fn. */
    on: <T = unknown>(event: ServerEventType | string, handler: (data: T) => void) => () => void;
    /** Subscribe to a channel. */
    subscribe: (channel: ChannelType, resourceId?: string) => void;
    /** Unsubscribe from a channel. */
    unsubscribe: (channel: ChannelType, resourceId?: string) => void;
}

export function useWebSocket(): UseWebSocketReturn {
    const tokens = useAuthStore(s => s.tokens);
    const [status, setStatus] = useState<ConnectionStatus>(wsClient.connectionStatus);

    // ── Track status changes ─────────────────────────────────────────────────
    useEffect(() => {
        const unsub = wsClient.onStatusChange(setStatus);
        return unsub;
    }, []);

    // ── Connect / disconnect when token changes ───────────────────────────────
    useEffect(() => {
        const token = tokens?.access_token;
        if (!token) {
            wsClient.disconnect();
            return;
        }

        wsClient.connect(token);
        return () => {
            // Don't disconnect on every re-render; only when the component
            // that "owns" the connection unmounts (typically the root layout).
        };
    }, [tokens?.access_token]);

    const on = useCallback(
        <T = unknown>(event: ServerEventType | string, handler: (data: T) => void) =>
            wsClient.on(event, handler),
        []
    );

    const subscribe = useCallback(
        (channel: ChannelType, resourceId?: string) => wsClient.subscribe(channel, resourceId),
        []
    );

    const unsubscribe = useCallback(
        (channel: ChannelType, resourceId?: string) => wsClient.unsubscribe(channel, resourceId),
        []
    );

    return {
        status,
        isConnected: status !== "IDLE" && status !== "DISCONNECTED" && status !== "FAILED",
        isAuthenticated: status === "AUTHENTICATED",
        on,
        subscribe,
        unsubscribe,
    };
}
