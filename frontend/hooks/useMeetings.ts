import { useState, useEffect, useCallback } from 'react';
import { Meeting, MeetingFilters, MeetingStatus, CreateMeetingDTO } from '@/types/meeting';
import { apiClient as api } from '@/lib/api/client';

export const useMeetings = (): {
    meetings: Meeting[];
    totalMeetings: number;
    totalPages: number;
    currentPage: number;
    setCurrentPage: (page: number) => void;
    isLoading: boolean;
    error: string | null;
    filters: any; // Using dynamic filters to match backend expectation
    setFilters: (filters: any) => void;
    createMeeting: (data: CreateMeetingDTO) => Promise<void>;
    deleteMeeting: (id: string) => Promise<void>;
    updateMeeting: (id: string, updates: Partial<Meeting>) => Promise<void>;
    itemsPerPage: number;
} => {
    const [meetings, setMeetings] = useState<Meeting[]>([]);
    const [totalMeetings, setTotalMeetings] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(6);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [filters, setFilters] = useState<any>({
        search: '',
        status: 'all',
        dateRange: 'all',
        platform: 'all',
    });

    const fetchMeetings = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Build query params
            const params: any = {
                page: currentPage,
                per_page: itemsPerPage,
            };

            if (filters.search) params.q = filters.search;
            if (filters.status && filters.status !== 'all') params.status = [filters.status];
            if (filters.platform && filters.platform !== 'all') params.platform = [filters.platform];

            // Map date range to backend date_from if needed
            if (filters.dateRange === 'today') {
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                params.date_from = today.toISOString();
            } else if (filters.dateRange === 'week') {
                const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                params.date_from = weekAgo.toISOString();
            } else if (filters.dateRange === 'month') {
                const monthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
                params.date_from = monthAgo.toISOString();
            }

            const endpoint = filters.search ? "/meetings/search" : "/meetings";
            const response = await api.get(endpoint, { params });

            const { data: items, pagination } = response.data;

            const mappedItems = items.map((m: any) => ({
                ...m,
                startTime: m.scheduled_start,
                endTime: m.scheduled_end,
                duration: m.duration_minutes ? m.duration_minutes * 60 : 0,
                attendees: m.attendees || Array(m.participant_count || 0).fill({ email: 'attendee@vocaply.ai' })
            }));

            setMeetings(mappedItems);
            setTotalMeetings(pagination.total_items);
            setTotalPages(pagination.total_pages);
        } catch (err: any) {
            console.error("Failed to fetch meetings:", err);
            setError(err.response?.data?.detail || "Failed to load meetings");
        } finally {
            setIsLoading(false);
        }
    }, [currentPage, itemsPerPage, filters]);

    useEffect(() => {
        fetchMeetings();
    }, [fetchMeetings]);

    const createMeeting = async (data: CreateMeetingDTO) => {
        setIsLoading(true);
        try {
            // Transform frontend DTO → backend MeetingCreate schema
            const payload: Record<string, any> = {
                title: data.title,
                description: data.description || undefined,
                platform: data.platform,
                scheduled_start: data.startTime || undefined,
                scheduled_end: (data as any).endTime || undefined,
                meeting_url: (data as any).meetingUrl || undefined,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
                bot_enabled: false,
                // Convert email strings OR objects → {email, name, role} objects
                attendees: (data.attendees || []).map((a: string | { name?: string; email: string }) => {
                    if (typeof a === 'string') return { email: a, name: undefined, role: 'attendee' };
                    return { email: a.email, name: a.name || undefined, role: 'attendee' };
                }),
            };
            // Strip undefined keys so Pydantic doesn't see null for Optional fields
            Object.keys(payload).forEach(k => payload[k] === undefined && delete payload[k]);

            await api.post("/meetings", payload);
            await fetchMeetings();
        } catch (err: any) {
            console.error("Failed to create meeting:", err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    const deleteMeeting = async (id: string) => {
        setIsLoading(true);
        try {
            await api.delete(`/meetings/${id}`);
            await fetchMeetings();
        } catch (err: any) {
            console.error("Failed to delete meeting:", err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    const updateMeeting = async (id: string, updates: Partial<Meeting>) => {
        setIsLoading(true);
        try {
            await api.patch(`/meetings/${id}`, updates);
            await fetchMeetings();
        } catch (err: any) {
            console.error("Failed to update meeting:", err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    return {
        meetings,
        totalMeetings,
        totalPages,
        currentPage,
        setCurrentPage,
        isLoading,
        error,
        filters,
        setFilters,
        createMeeting,
        deleteMeeting,
        updateMeeting,
        itemsPerPage
    };
};
