"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Bell } from "lucide-react";
import { notificationsApi } from "../../../lib/api/notifications";
import NotificationList from "../NotificationList";

export default function NotificationBell() {
    const [unreadCount, setUnreadCount] = useState(0);
    const [isOpen, setIsOpen] = useState(false);
    const [mounted, setMounted] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    // ── Fetch unread count ──────────────────────────────────────────
    const fetchUnreadCount = useCallback(async () => {
        try {
            const { count } = await notificationsApi.getUnreadCount();
            setUnreadCount(count);
        } catch {
            // Silently ignore — user may not be logged in yet
        }
    }, []);

    useEffect(() => {
        setMounted(true);
        fetchUnreadCount();

        // Poll every 30 seconds
        const interval = setInterval(fetchUnreadCount, 30_000);
        return () => clearInterval(interval);
    }, [fetchUnreadCount]);

    // ── Close on outside click ──────────────────────────────────────
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        }
        if (isOpen) {
            document.addEventListener("mousedown", handleClickOutside);
        }
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [isOpen]);

    const handleMarkAllRead = useCallback(async () => {
        await notificationsApi.markAllAsRead();
        setUnreadCount(0);
    }, []);

    const handleNotificationRead = useCallback(() => {
        setUnreadCount((c) => Math.max(0, c - 1));
    }, []);

    if (!mounted) return null;

    return (
        <div ref={containerRef} className="relative" style={{ userSelect: "none" }}>
            {/* Bell Button */}
            <button
                onClick={() => setIsOpen((o) => !o)}
                aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}
                style={{
                    position: "relative",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: "40px",
                    height: "40px",
                    borderRadius: "10px",
                    border: "1px solid rgba(255,255,255,0.08)",
                    background: isOpen
                        ? "rgba(108,71,255,0.15)"
                        : "rgba(255,255,255,0.04)",
                    cursor: "pointer",
                    color: isOpen ? "#a78bfa" : "#9ca3af",
                    transition: "all 0.2s ease",
                }}
                onMouseEnter={(e) => {
                    if (!isOpen) {
                        (e.currentTarget as HTMLButtonElement).style.background =
                            "rgba(255,255,255,0.08)";
                        (e.currentTarget as HTMLButtonElement).style.color = "#e5e7eb";
                    }
                }}
                onMouseLeave={(e) => {
                    if (!isOpen) {
                        (e.currentTarget as HTMLButtonElement).style.background =
                            "rgba(255,255,255,0.04)";
                        (e.currentTarget as HTMLButtonElement).style.color = "#9ca3af";
                    }
                }}
            >
                <Bell size={18} />

                {/* Badge */}
                {unreadCount > 0 && (
                    <span
                        aria-hidden
                        style={{
                            position: "absolute",
                            top: "-4px",
                            right: "-4px",
                            minWidth: "18px",
                            height: "18px",
                            padding: "0 4px",
                            borderRadius: "9px",
                            background: "linear-gradient(135deg, #6c47ff 0%, #4f8eff 100%)",
                            color: "#fff",
                            fontSize: "10px",
                            fontWeight: 700,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            lineHeight: 1,
                            border: "1.5px solid #0f1117",
                            boxShadow: "0 0 8px rgba(108,71,255,0.6)",
                        }}
                    >
                        {unreadCount > 99 ? "99+" : unreadCount}
                    </span>
                )}
            </button>

            {/* Dropdown */}
            {isOpen && (
                <div
                    style={{
                        position: "absolute",
                        top: "calc(100% + 8px)",
                        right: 0,
                        width: "380px",
                        maxWidth: "calc(100vw - 24px)",
                        zIndex: 9999,
                        borderRadius: "16px",
                        background: "#1a1d27",
                        border: "1px solid rgba(255,255,255,0.08)",
                        boxShadow: "0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(108,71,255,0.1)",
                        overflow: "hidden",
                        animation: "slideDown 0.15s ease",
                    }}
                >
                    <style>{`
            @keyframes slideDown {
              from { opacity: 0; transform: translateY(-8px); }
              to   { opacity: 1; transform: translateY(0); }
            }
          `}</style>
                    <NotificationList
                        onMarkAllRead={handleMarkAllRead}
                        onNotificationRead={handleNotificationRead}
                    />
                </div>
            )}
        </div>
    );
}
