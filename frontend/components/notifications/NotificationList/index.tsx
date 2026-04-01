"use client";

import { useEffect, useState, useCallback } from "react";
import { CheckCheck, Inbox } from "lucide-react";
import { Notification, notificationsApi } from "../../../lib/api/notifications";
import NotificationItem from "../NotificationItem";

interface Props {
    onMarkAllRead: () => void;
    onNotificationRead: () => void;
}

export default function NotificationList({ onMarkAllRead, onNotificationRead }: Props) {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(true);
    const [marking, setMarking] = useState(false);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            const res = await notificationsApi.getNotifications({ per_page: 20 });
            setNotifications(res.data);
        } catch {
            setNotifications([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { load(); }, [load]);

    const handleMarkAll = async () => {
        setMarking(true);
        await notificationsApi.markAllAsRead();
        setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
        onMarkAllRead();
        setMarking(false);
    };

    const handleItemRead = (id: string) => {
        setNotifications((prev) =>
            prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
        );
        onNotificationRead();
    };

    const hasUnread = notifications.some((n) => !n.is_read);

    return (
        <div style={{ display: "flex", flexDirection: "column", maxHeight: "480px" }}>
            {/* Header */}
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "16px 20px 12px",
                    borderBottom: "1px solid rgba(255,255,255,0.06)",
                }}
            >
                <span
                    style={{
                        fontSize: "14px",
                        fontWeight: 600,
                        color: "#f9fafb",
                        letterSpacing: "-0.2px",
                    }}
                >
                    Notifications
                </span>

                {hasUnread && (
                    <button
                        onClick={handleMarkAll}
                        disabled={marking}
                        title="Mark all as read"
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "5px",
                            padding: "5px 10px",
                            borderRadius: "8px",
                            border: "1px solid rgba(108,71,255,0.3)",
                            background: "rgba(108,71,255,0.1)",
                            color: "#a78bfa",
                            fontSize: "12px",
                            fontWeight: 500,
                            cursor: marking ? "wait" : "pointer",
                            transition: "all 0.15s ease",
                        }}
                    >
                        <CheckCheck size={13} />
                        {marking ? "Marking…" : "Mark all read"}
                    </button>
                )}
            </div>

            {/* Body */}
            <div style={{ overflowY: "auto", flex: 1 }}>
                {loading ? (
                    <SkeletonRows />
                ) : notifications.length === 0 ? (
                    <EmptyState />
                ) : (
                    notifications.map((n) => (
                        <NotificationItem
                            key={n.id}
                            notification={n}
                            onRead={handleItemRead}
                        />
                    ))
                )}
            </div>
        </div>
    );
}

// ── Empty State ────────────────────────────────────────────────────

function EmptyState() {
    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: "48px 24px",
                gap: "12px",
            }}
        >
            <div
                style={{
                    width: "48px",
                    height: "48px",
                    borderRadius: "14px",
                    background: "rgba(108,71,255,0.1)",
                    border: "1px solid rgba(108,71,255,0.2)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#6c47ff",
                }}
            >
                <Inbox size={22} />
            </div>
            <p style={{ color: "#6b7280", fontSize: "14px", margin: 0, textAlign: "center" }}>
                You&apos;re all caught up!<br />
                <span style={{ fontSize: "12px", color: "#4b5563" }}>No notifications yet.</span>
            </p>
        </div>
    );
}

// ── Loading Skeleton ────────────────────────────────────────────────

function SkeletonRows() {
    return (
        <div style={{ padding: "8px 0" }}>
            {[1, 2, 3].map((i) => (
                <div
                    key={i}
                    style={{
                        display: "flex",
                        gap: "12px",
                        padding: "14px 20px",
                        borderBottom: "1px solid rgba(255,255,255,0.04)",
                    }}
                >
                    <div
                        style={{
                            width: "36px",
                            height: "36px",
                            borderRadius: "10px",
                            background: "rgba(255,255,255,0.06)",
                            flexShrink: 0,
                            animation: "pulse 1.2s ease infinite",
                        }}
                    />
                    <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "8px" }}>
                        <div
                            style={{
                                height: "12px",
                                borderRadius: "6px",
                                background: "rgba(255,255,255,0.06)",
                                width: "60%",
                                animation: "pulse 1.2s ease infinite",
                            }}
                        />
                        <div
                            style={{
                                height: "10px",
                                borderRadius: "6px",
                                background: "rgba(255,255,255,0.04)",
                                width: "85%",
                                animation: "pulse 1.2s ease infinite",
                            }}
                        />
                    </div>
                    <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }`}</style>
                </div>
            ))}
        </div>
    );
}
