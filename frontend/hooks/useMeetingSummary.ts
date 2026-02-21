"use client";

import { useState, useEffect, useCallback } from "react";
import { apiClient } from "@/lib/api/client";
import type { MeetingSummaryData } from "@/components/meetings/MeetingSummary";

interface UseMeetingSummaryReturn {
    summary: MeetingSummaryData | null;
    isLoading: boolean;
    isGenerating: boolean;
    error: string | null;
    fetchSummary: () => Promise<void>;
    triggerGenerate: () => Promise<void>;
    triggerRegenerate: () => Promise<void>;
    editSummary: (updates: Partial<MeetingSummaryData>) => Promise<void>;
}

export function useMeetingSummary(meetingId: string): UseMeetingSummaryReturn {
    const [summary, setSummary] = useState<MeetingSummaryData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchSummary = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const res = await apiClient.get(`/meetings/${meetingId}/summary`);
            setSummary(res.data);
        } catch (err: any) {
            if (err?.response?.status === 404) {
                setSummary(null); // No summary yet — normal state
            } else {
                setError(err?.response?.data?.detail ?? "Failed to load summary");
            }
        } finally {
            setIsLoading(false);
        }
    }, [meetingId]);

    useEffect(() => {
        if (meetingId) fetchSummary();
    }, [fetchSummary, meetingId]);

    const triggerGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        try {
            await apiClient.post(`/meetings/${meetingId}/summarize`);
            // Poll every 4s for up to 60s until summary appears
            let attempts = 0;
            const interval = setInterval(async () => {
                attempts++;
                try {
                    const res = await apiClient.get(`/meetings/${meetingId}/summary`);
                    setSummary(res.data);
                    clearInterval(interval);
                    setIsGenerating(false);
                } catch {
                    if (attempts >= 15) {
                        clearInterval(interval);
                        setIsGenerating(false);
                        setError("Summary generation timed out. Please try again.");
                    }
                }
            }, 4000);
        } catch (err: any) {
            setIsGenerating(false);
            setError(err?.response?.data?.detail ?? "Failed to start summary generation");
        }
    };

    const triggerRegenerate = async () => {
        if (!summary) return;
        setIsGenerating(true);
        setError(null);
        try {
            await apiClient.post(`/summaries/${summary.id}/regenerate`);
            // Poll same as generate
            let attempts = 0;
            const interval = setInterval(async () => {
                attempts++;
                try {
                    const res = await apiClient.get(`/meetings/${meetingId}/summary`);
                    setSummary(res.data);
                    if (res.data.updated_at !== summary.updated_at) {
                        clearInterval(interval);
                        setIsGenerating(false);
                    }
                } catch {
                    /* continue polling */
                }
                if (attempts >= 15) {
                    clearInterval(interval);
                    setIsGenerating(false);
                }
            }, 4000);
        } catch (err: any) {
            setIsGenerating(false);
            setError(err?.response?.data?.detail ?? "Failed to regenerate summary");
        }
    };

    const editSummary = async (updates: Partial<MeetingSummaryData>) => {
        if (!summary) return;
        try {
            const res = await apiClient.put(`/summaries/${summary.id}`, updates);
            setSummary(res.data);
        } catch (err: any) {
            setError(err?.response?.data?.detail ?? "Failed to save edits");
        }
    };

    return {
        summary,
        isLoading,
        isGenerating,
        error,
        fetchSummary,
        triggerGenerate,
        triggerRegenerate,
        editSummary,
    };
}
