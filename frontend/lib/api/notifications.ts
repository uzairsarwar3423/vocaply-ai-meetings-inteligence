/**
 * Notifications API Client
 * Vocaply Platform - Day 26: Notifications & Reminders
 */

import { apiClient } from "./client";

// ─── Types ────────────────────────────────────────────────────────

export interface Notification {
    id: string;
    type: "action_item_assigned" | "reminder" | "overdue" | "daily_digest" | "system";
    title: string;
    body: string | null;
    is_read: boolean;
    metadata_: Record<string, unknown> | null;
    created_at: string;
}

export interface NotificationListResponse {
    data: Notification[];
    pagination: {
        page: number;
        per_page: number;
        total_items: number;
        total_pages: number;
    };
}

export interface UnreadCountResponse {
    count: number;
}

export interface MarkReadResponse {
    success: boolean;
    message: string;
}

// ─── API Calls ────────────────────────────────────────────────────

export const notificationsApi = {
    /**
     * List paginated notifications for the current user.
     */
    getNotifications: async (params?: {
        page?: number;
        per_page?: number;
        unread_only?: boolean;
    }): Promise<NotificationListResponse> => {
        const response = await apiClient.get("/notifications", { params });
        return response.data;
    },

    /**
     * Get unread notification count.
     */
    getUnreadCount: async (): Promise<UnreadCountResponse> => {
        const response = await apiClient.get("/notifications/unread-count");
        return response.data;
    },

    /**
     * Mark a single notification as read.
     */
    markAsRead: async (notificationId: string): Promise<void> => {
        await apiClient.post(`/notifications/${notificationId}/read`);
    },

    /**
     * Mark all notifications as read.
     */
    markAllAsRead: async (): Promise<MarkReadResponse> => {
        const response = await apiClient.post("/notifications/read-all");
        return response.data;
    },
};
