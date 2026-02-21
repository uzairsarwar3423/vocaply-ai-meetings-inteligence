"use client";

/**
 * ConnectionStatusIndicator
 * Vocaply AI Meeting Intelligence – Day 14
 *
 * A small pill / dot that shows the current WebSocket connection status.
 * Drop it anywhere in the UI (e.g. the dashboard header or sidebar footer).
 */

import { useWebSocket } from "../../hooks/useWebSocket";
import { ConnectionStatus } from "../../lib/websocket/events";

const STATUS_MAP: Record<
    ConnectionStatus,
    { label: string; dotColor: string; pillBg: string; textColor: string }
> = {
    IDLE: { label: "Offline", dotColor: "bg-slate-400", pillBg: "bg-slate-100 dark:bg-slate-800", textColor: "text-slate-500 dark:text-slate-400" },
    CONNECTING: { label: "Connecting…", dotColor: "bg-amber-400", pillBg: "bg-amber-50  dark:bg-amber-950", textColor: "text-amber-600 dark:text-amber-400" },
    CONNECTED: { label: "Connecting…", dotColor: "bg-amber-400", pillBg: "bg-amber-50  dark:bg-amber-950", textColor: "text-amber-600 dark:text-amber-400" },
    AUTHENTICATED: { label: "Live", dotColor: "bg-emerald-500", pillBg: "bg-emerald-50 dark:bg-emerald-950", textColor: "text-emerald-600 dark:text-emerald-400" },
    RECONNECTING: { label: "Reconnecting…", dotColor: "bg-amber-400", pillBg: "bg-amber-50  dark:bg-amber-950", textColor: "text-amber-600 dark:text-amber-400" },
    DISCONNECTED: { label: "Disconnected", dotColor: "bg-red-400", pillBg: "bg-red-50    dark:bg-red-950", textColor: "text-red-500   dark:text-red-400" },
    FAILED: { label: "Connection failed", dotColor: "bg-red-600", pillBg: "bg-red-50    dark:bg-red-950", textColor: "text-red-600   dark:text-red-400" },
};

interface Props {
    /** Show text label next to the dot. Defaults to true. */
    showLabel?: boolean;
    /** Extra CSS classes for the wrapper. */
    className?: string;
}

export function ConnectionStatusIndicator({ showLabel = true, className = "" }: Props) {
    const { status } = useWebSocket();
    const cfg = STATUS_MAP[status];
    const isPulsing = status === "CONNECTING" || status === "RECONNECTING";

    return (
        <span
            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${cfg.pillBg} ${cfg.textColor} ${className}`}
            title={`WebSocket: ${cfg.label}`}
        >
            {/* animated dot */}
            <span className="relative flex h-2 w-2">
                {isPulsing && (
                    <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${cfg.dotColor}`} />
                )}
                <span className={`relative inline-flex rounded-full h-2 w-2 ${cfg.dotColor}`} />
            </span>
            {showLabel && <span>{cfg.label}</span>}
        </span>
    );
}
