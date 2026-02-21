import { useState, useEffect } from 'react';
import { Meeting } from '@/types/meeting';
import { apiClient as api } from '@/lib/api/client';

export const useMeeting = (id: string) => {
    const [meeting, setMeeting] = useState<Meeting | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!id) return;

        const fetchMeeting = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const response = await api.get(`/meetings/${id}`);
                const m = response.data;
                setMeeting({
                    ...m,
                    startTime: m.scheduled_start,
                    endTime: m.scheduled_end,
                    duration: m.duration_minutes ? m.duration_minutes * 60 : 0
                });
            } catch (err: any) {
                console.error("Failed to fetch meeting:", err);
                setError(err.response?.data?.detail || "Failed to load meeting details");
            } finally {
                setIsLoading(false);
            }
        };

        fetchMeeting();
    }, [id]);

    return { meeting, isLoading, error };
};
