// Action Items API functions
import { apiClient as api } from '@/lib/api/client';
import {
    ActionItem,
    ActionItemUpdate,
    ActionItemsResponse,
    ActionItemStats,
} from '@/types/action-item';

export const actionItemsApi = {
    /** List action items with filters + pagination */
    list: async (params: Record<string, any> = {}): Promise<ActionItemsResponse> => {
        const res = await api.get('/action-items', { params });
        return res.data;
    },

    /** Get single action item */
    get: async (id: string): Promise<ActionItem> => {
        const res = await api.get(`/action-items/${id}`);
        return res.data;
    },

    /** PATCH update */
    update: async (id: string, data: ActionItemUpdate): Promise<ActionItem> => {
        const res = await api.patch(`/action-items/${id}`, data);
        return res.data;
    },

    /** Delete */
    delete: async (id: string): Promise<void> => {
        await api.delete(`/action-items/${id}`);
    },

    /** Accept an AI-generated item */
    accept: async (id: string): Promise<ActionItem> => {
        const res = await api.post(`/action-items/${id}/accept`);
        return res.data.item;
    },

    /** Reject (cancel) an AI-generated item */
    reject: async (id: string): Promise<ActionItem> => {
        const res = await api.post(`/action-items/${id}/reject`);
        return res.data.item;
    },

    /** Get aggregate stats */
    stats: async (meetingId?: string): Promise<ActionItemStats> => {
        const res = await api.get('/action-items/stats/summary', {
            params: meetingId ? { meeting_id: meetingId } : {},
        });
        return res.data;
    },

    /** Trigger AI analysis for a meeting */
    triggerAnalysis: async (
        meetingId: string,
        options?: { force_rerun?: boolean; features?: string[] }
    ): Promise<{ task_id: string; status: string; message: string }> => {
        const res = await api.post(`/meetings/${meetingId}/analyze`, options || {});
        return res.data;
    },
};
