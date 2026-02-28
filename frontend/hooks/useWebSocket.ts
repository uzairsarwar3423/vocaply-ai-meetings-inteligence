/**
 * useWebSocket Hook - Unified for Day 14 & Day 19
 * Vocaply AI Meeting Intelligence
 * 
 * Provides WebSocket connections with:
 * - Singleton connection management
 * - JWT authentication
 * - Channel-based subscriptions
 * - Auto-reconnect with exponential backoff
 * - Type-safe event handlers
 */

'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';
import {
    ClientEvent,
    ServerEvent,
    ConnectionStatus,
    WSMessage
} from '../lib/websocket/events';

type EventHandler<T = any> = (data: T) => void;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// TYPE DEFINITIONS FOR EVENTS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export interface BotEventData {
    bot_id?: string;
    meeting_id?: string;
    status?: string;
    participant_count?: number;
    is_alone?: boolean;
    recording_url?: string;
    error?: string;
    joined_at?: string;
    left_at?: string;
    detail?: string;
}

export interface ParticipantEventData {
    user_id?: string;
    user_name?: string;
    current_count?: number;
}

export interface RecordingEventData {
    recording_url?: string;
    audio_info?: any;
}

// Global connection state to share across hook instances
let globalWs: WebSocket | null = null;
let globalHandlers: Map<string, Set<EventHandler>> = new Map();
let globalStatus: ConnectionStatus = 'IDLE';
let globalAuthenticated = false;
let reconnectAttempts = 0;
let reconnectTimeout: NodeJS.Timeout | null = null;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MAIN WEBSOCKET HOOK
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export function useWebSocket() {
    const { tokens } = useAuthStore();
    const [status, setStatus] = useState<ConnectionStatus>(globalStatus);
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(globalAuthenticated);
    const [, setTick] = useState(0); // For forcing re-renders

    const connect = useCallback(() => {
        if (typeof window === 'undefined' || globalWs?.readyState === WebSocket.OPEN || globalWs?.readyState === WebSocket.CONNECTING) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // The backend endpoint is at /api/v1/ws
        const wsUrl = `${protocol}//${window.location.host}/api/v1/ws`;

        console.log('[WebSocket] Connecting to:', wsUrl);
        globalStatus = 'CONNECTING';
        setStatus('CONNECTING');

        const ws = new WebSocket(wsUrl);
        globalWs = ws;

        ws.onopen = () => {
            console.log('[WebSocket] Connected');
            globalStatus = 'CONNECTED';
            setStatus('CONNECTED');
            reconnectAttempts = 0;

            // Attempt authentication if token is available
            if (tokens?.access_token) {
                send(ClientEvent.AUTHENTICATE, { token: tokens.access_token });
            }
        };

        ws.onmessage = (event) => {
            try {
                const message: WSMessage = JSON.parse(event.data);
                const { event: eventType, data } = message;

                // Handle internal lifecycle events
                if (eventType === ServerEvent.AUTHENTICATED) {
                    globalAuthenticated = true;
                    setIsAuthenticated(true);
                    globalStatus = 'AUTHENTICATED';
                    setStatus('AUTHENTICATED');
                } else if (eventType === ServerEvent.ERROR) {
                    console.error('[WebSocket] Server Error:', data);
                }

                // Call registered handlers
                const handlers = globalHandlers.get(eventType);
                if (handlers) {
                    handlers.forEach(handler => handler(data));
                }
            } catch (error) {
                console.error('[WebSocket] Message parse error:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('[WebSocket] Error:', error);
            globalStatus = 'FAILED';
            setStatus('FAILED');
        };

        ws.onclose = () => {
            console.log('[WebSocket] Disconnected');
            globalWs = null;
            globalAuthenticated = false;
            setIsAuthenticated(false);

            if (globalStatus !== 'IDLE') {
                globalStatus = 'DISCONNECTED';
                setStatus('DISCONNECTED');

                // Reconnect logic
                const maxAttempts = 5;
                if (reconnectAttempts < maxAttempts) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
                    reconnectTimeout = setTimeout(() => {
                        reconnectAttempts++;
                        connect();
                    }, delay);
                }
            }
        };
    }, [tokens?.access_token]);

    useEffect(() => {
        connect();
        return () => {
            // We don't close the global socket on unmount, 
            // but we might want to clear timeouts
        };
    }, [connect]);

    const on = useCallback(<T = any>(event: string, handler: EventHandler<T>) => {
        if (!globalHandlers.has(event)) {
            globalHandlers.set(event, new Set());
        }
        globalHandlers.get(event)!.add(handler);

        return () => {
            globalHandlers.get(event)?.delete(handler);
        };
    }, []);

    const off = useCallback((event: string, handler: EventHandler) => {
        globalHandlers.get(event)?.delete(handler);
    }, []);

    const send = useCallback((event: string, data: any) => {
        if (globalWs?.readyState === WebSocket.OPEN) {
            globalWs.send(JSON.stringify({ event, data }));
        } else {
            console.warn('[WebSocket] Cannot send, socket not open:', event);
        }
    }, []);

    const subscribe = useCallback((channel: string, resourceId?: string) => {
        send(ClientEvent.SUBSCRIBE, { channel, resource_id: resourceId });
    }, [send]);

    const unsubscribe = useCallback((channel: string, resourceId?: string) => {
        send(ClientEvent.UNSUBSCRIBE, { channel, resource_id: resourceId });
    }, [send]);

    return {
        on,
        off,
        send,
        subscribe,
        unsubscribe,
        isConnected: globalStatus === 'CONNECTED' || globalStatus === 'AUTHENTICATED',
        isAuthenticated,
        status
    };
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// CONVENIENCE HOOKS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export function useMeetingWebSocket(meetingId: string) {
    const ws = useWebSocket();

    useEffect(() => {
        if (ws.isAuthenticated && meetingId) {
            ws.subscribe('meeting', meetingId);
            return () => ws.unsubscribe('meeting', meetingId);
        }
    }, [ws.isAuthenticated, meetingId, ws.subscribe, ws.unsubscribe]);

    return ws;
}

export function useBotEvents(
    meetingId: string,
    handlers: {
        onUpdate?: (data: BotEventData) => void;
        onJoined?: (data: BotEventData) => void;
        onLeft?: (data: BotEventData) => void;
        onError?: (data: BotEventData) => void;
    }
) {
    const ws = useMeetingWebSocket(meetingId);

    useEffect(() => {
        const unsubs: (() => void)[] = [];

        if (handlers.onUpdate) unsubs.push(ws.on('bot.update', handlers.onUpdate));
        if (handlers.onUpdate) unsubs.push(ws.on(ServerEvent.BOT_STATUS_CHANGED, handlers.onUpdate));
        if (handlers.onJoined) unsubs.push(ws.on('bot.joined', handlers.onJoined));
        if (handlers.onLeft) unsubs.push(ws.on('bot.left', handlers.onLeft));
        if (handlers.onError) unsubs.push(ws.on('bot.error', handlers.onError));

        return () => unsubs.forEach(unsub => unsub());
    }, [ws.isConnected, meetingId]);
}

export function useRecordingEvents(
    meetingId: string,
    handlers: {
        onStarted?: (data: BotEventData) => void;
        onCompleted?: (data: RecordingEventData) => void;
    }
) {
    const ws = useMeetingWebSocket(meetingId);

    useEffect(() => {
        const unsubs: (() => void)[] = [];

        if (handlers.onStarted) unsubs.push(ws.on('recording.started', handlers.onStarted));
        if (handlers.onCompleted) unsubs.push(ws.on('recording.completed', handlers.onCompleted));
        if (handlers.onCompleted) unsubs.push(ws.on(ServerEvent.TRANSCRIPT_CHUNK, handlers.onCompleted));

        return () => unsubs.forEach(unsub => unsub());
    }, [ws.isConnected, meetingId]);
}

export function useParticipantEvents(
    meetingId: string,
    handlers: {
        onJoined?: (data: ParticipantEventData) => void;
        onLeft?: (data: ParticipantEventData) => void;
        onCountChanged?: (data: ParticipantEventData) => void;
    }
) {
    const ws = useMeetingWebSocket(meetingId);

    useEffect(() => {
        const unsubs: (() => void)[] = [];

        if (handlers.onJoined) unsubs.push(ws.on('participant.joined', handlers.onJoined));
        if (handlers.onLeft) unsubs.push(ws.on('participant.left', handlers.onLeft));
        if (handlers.onCountChanged) unsubs.push(ws.on('participant.count_changed', handlers.onCountChanged));

        return () => unsubs.forEach(unsub => unsub());
    }, [ws.isConnected, meetingId]);
}