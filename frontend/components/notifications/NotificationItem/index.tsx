"use client";

import { useCallback } from "react";
import {
    Bell, AlertTriangle, Clock, Newspaper, Zap,
} from "lucide-react";
import { Notification, notificationsApi } from "../../../lib/api/notifications";

interface Props {
    notification: Notification;
    onRead: (id: string) => void;
}

// ── Icon by type ─────────────────────────────────────────────────

const TYPE_CONFIG: Record<
    Notification["type"],
    { icon: React.ReactNode; color: string; bg: string }
> = {
    action_item_assigned: {
        icon: <Zap size={16} />,
        color: "#6c47ff",
        bg: "rgba(108,71,255,0.12)",
    },
    reminder: {
        icon: <Clock size={16} />,
        color: "#f59e0b",
        bg: "rgba(245,158,11,0.12)",
    },
    overdue: {
        icon: <AlertTriangle size={16} />,
        color: "#ef4444",
        bg: "rgba(239,68,68,0.12)",
    },
    daily_digest: {
        icon: <Newspaper size={16} />,
        color: "#06b6d4",
        bg: "rgba(6,182,212,0.12)",
    },
    system: {
        icon: <Bell size={16} />,
        color: "#9ca3af",
        bg: "rgba(156,163,175,0.1)",
    },
};

// ── Relative time ───────────────────────────────────────────────

function relativeTime(isoString: string): string {
    const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

// ─────────────────────────────────────────────────────────────────

export default function NotificationItem({ notification, onRead }: Props) {
    const { icon, color, bg } =
        TYPE_CONFIG[notification.type] ?? TYPE_CONFIG.system;

    const handleClick = useCallback(async () => {
        if (notification.is_read) return;
        try {
            await notificationsApi.markAsRead(notification.id);
            onRead(notification.id);
        } catch {
            // silently ignore
        }
    }, [notification.id, notification.is_read, onRead]);

    return (
        <div
            onClick={handleClick}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === "Enter" && handleClick()}
            style={{
                display: "flex",
                gap: "12px",
                padding: "14px 20px",
                borderBottom: "1px solid rgba(255,255,255,0.04)",
                cursor: notification.is_read ? "default" : "pointer",
                borderLeft: notification.is_read
                    ? "3px solid transparent"
                    : `3px solid ${color}`,
                background: notification.is_read
                    ? "transparent"
                    : "rgba(255,255,255,0.015)",
                transition: "background 0.15s ease",
            }}
            onMouseEnter={(e) => {
                (e.currentTarget as HTMLDivElement).style.background =
                    "rgba(255,255,255,0.04)";
            }}
            onMouseLeave={(e) => {
                (e.currentTarget as HTMLDivElement).style.background = notification.is_read
                    ? "transparent"
                    : "rgba(255,255,255,0.015)";
            }}
        >
            {/* Icon */}
            <div
                style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "10px",
                    background: bg,
                    color: color,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                }}
            >
                {icon}
            </div>

            {/* Content */}
            <div style={{ flex: 1, minWidth: 0 }}>
                <p
                    style={{
                        margin: "0 0 3px",
                        fontSize: "13px",
                        fontWeight: notification.is_read ? 400 : 600,
                        color: notification.is_read ? "#9ca3af" : "#e5e7eb",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                    }}
                >
                    {notification.title}
                </p>
                {notification.body && (
                    <p
                        style={{
                            margin: "0 0 5px",
                            fontSize: "12px",
                            color: "#6b7280",
                            lineHeight: 1.4,
                            display: "-webkit-box",
                            WebkitLineClamp: "2",
                            WebkitBoxOrient: "vertical",
                            overflow: "hidden",
                        } as React.CSSProperties}
                    >
                        {notification.body}
                    </p>
                )}
                <span style={{ fontSize: "11px", color: "#4b5563" }}>
                    {relativeTime(notification.created_at)}
                </span>
            </div>

            {/* Unread dot */}
            {!notification.is_read && (
                <div
                    aria-hidden
                    style={{
                        width: "7px",
                        height: "7px",
                        borderRadius: "50%",
                        background: color,
                        flexShrink: 0,
                        marginTop: "4px",
                        boxShadow: `0 0 6px ${color}80`,
                    }}
                />
            )}
        </div>
    );
}
