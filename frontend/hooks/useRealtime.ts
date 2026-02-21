"use client";

/**
 * useRealtime Hook
 * Vocaply AI Meeting Intelligence – Day 14
 *
 * High-level hook for real-time event handling.  Components import this
 * hook to react to specific server events without worrying about the
 * underlying WebSocket connection.
 *
 * Usage example:
 *
 *   const { onMeetingUpdated, onTranscriptChunk } = useRealtime({
 *     channels: ["meeting"],
 *     meetingId: "abc-123",
 *   });
 *
 *   onMeetingUpdated((data) => console.log("meeting changed", data));
 *   onTranscriptChunk((chunk) => appendChunk(chunk));
 */

import { useEffect, useCallback, useRef } from "react";
import { toast } from "sonner";

import { useWebSocket } from "./useWebSocket";
import {
    Channel,
    ChannelType,
    ServerEvent,
    MeetingUpdatedPayload,
    ActionItemPayload,
    NotificationPayload,
    BotStatusPayload,
    TranscriptChunkPayload,
} from "../lib/websocket/events";

// ── Config ─────────────────────────────────────────────────────────────────────

interface UseRealtimeOptions {
    /** Channels to subscribe to on mount and unsubscribe on unmount. */
    channels?: ChannelType[];
    /** When provided, restricts meeting-scoped events to this meeting. */
    meetingId?: string;
    /** When true, notification toasts are shown automatically. */
    autoToastNotifications?: boolean;
}

// ── Handler registrar types ────────────────────────────────────────────────────

type Unsub = () => void;
type Handler<T> = (data: T) => void;

// ── Hook ───────────────────────────────────────────────────────────────────────

export function useRealtime(options: UseRealtimeOptions = {}) {
    const {
        channels = [],
        meetingId,
        autoToastNotifications = false,
    } = options;

    const { on, subscribe, unsubscribe, isAuthenticated, status } = useWebSocket();

    // ── Subscribe to requested channels on mount ────────────────────────────────
    useEffect(() => {
        if (!isAuthenticated || channels.length === 0) return;

        channels.forEach(ch => subscribe(ch, meetingId));

        return () => {
            channels.forEach(ch => unsubscribe(ch, meetingId));
        };
    }, [isAuthenticated, channels.join(","), meetingId]);

    // ── Auto notification toasts ────────────────────────────────────────────────
    useEffect(() => {
        if (!autoToastNotifications) return;
        const unsub = on<NotificationPayload>(ServerEvent.NOTIFICATION_RECEIVED, (n) => {
            toast(n.title, { description: n.message });
        });
        return unsub;
    }, [autoToastNotifications, on]);

    // ── Typed event registrars ─────────────────────────────────────────────────

    const onMeetingUpdated = useCallback(
        (handler: Handler<MeetingUpdatedPayload>): Unsub => {
            return on<MeetingUpdatedPayload>(ServerEvent.MEETING_UPDATED, (data) => {
                if (meetingId && data.id !== meetingId) return;
                handler(data);
            });
        },
        [on, meetingId]
    );

    const onActionItemCreated = useCallback(
        (handler: Handler<ActionItemPayload>): Unsub => {
            return on<ActionItemPayload>(ServerEvent.ACTION_ITEM_CREATED, handler);
        },
        [on]
    );

    const onActionItemUpdated = useCallback(
        (handler: Handler<ActionItemPayload>): Unsub => {
            return on<ActionItemPayload>(ServerEvent.ACTION_ITEM_UPDATED, handler);
        },
        [on]
    );

    const onNotificationReceived = useCallback(
        (handler: Handler<NotificationPayload>): Unsub => {
            return on<NotificationPayload>(ServerEvent.NOTIFICATION_RECEIVED, handler);
        },
        [on]
    );

    const onBotStatusChanged = useCallback(
        (handler: Handler<BotStatusPayload>): Unsub => {
            return on<BotStatusPayload>(ServerEvent.BOT_STATUS_CHANGED, (data) => {
                if (meetingId && data.meeting_id !== meetingId) return;
                handler(data);
            });
        },
        [on, meetingId]
    );

    const onTranscriptChunk = useCallback(
        (handler: Handler<TranscriptChunkPayload>): Unsub => {
            return on<TranscriptChunkPayload>(ServerEvent.TRANSCRIPT_CHUNK, (data) => {
                if (meetingId && data.meeting_id !== meetingId) return;
                handler(data);
            });
        },
        [on, meetingId]
    );

    return {
        /** WebSocket connection / auth status. */
        status,
        isAuthenticated,

        onMeetingUpdated,
        onActionItemCreated,
        onActionItemUpdated,
        onNotificationReceived,
        onBotStatusChanged,
        onTranscriptChunk,
    };
}
