import { useState, useEffect, useCallback, useRef } from 'react';
import { TranscriptSegment, TranscriptMetadata, TranscriptBookmark, TranscriptFilters } from '@/types/transcript';
import { apiClient as api } from '@/lib/api/client';

// --- Speaker color palette (teal-first brand palette) ---
const SPEAKER_COLORS = [
    '#00ACAC', // primary teal
    '#FF9070', // secondary coral
    '#6366F1', // indigo
    '#8B5CF6', // violet
    '#EC4899', // pink
    '#F59E0B', // amber
    '#10B981', // emerald
    '#0EA5E9', // sky
];

function assignSpeakerColors(segments: TranscriptSegment[]) {
    const map: Record<string, string> = {};
    let idx = 0;
    for (const seg of segments) {
        const key = seg.speaker_id || seg.speaker_name || 'unknown';
        if (!map[key]) {
            map[key] = SPEAKER_COLORS[idx % SPEAKER_COLORS.length];
            idx++;
        }
    }
    return map;
}

export const useTranscript = (meetingId: string) => {
    const [segments, setSegments] = useState<TranscriptSegment[]>([]);
    const [metadata, setMetadata] = useState<TranscriptMetadata | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filters, setFilters] = useState<TranscriptFilters>({ search: '' });
    const [bookmarks, setBookmarks] = useState<TranscriptBookmark[]>([]);
    const [speakerColors, setSpeakerColors] = useState<Record<string, string>>({});
    const [speakerNames, setSpeakerNames] = useState<Record<string, string>>({});
    const [editingSegmentId, setEditingSegmentId] = useState<string | null>(null);

    useEffect(() => {
        if (!meetingId) return;
        const fetchTranscript = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const [segResponse, metaResponse] = await Promise.allSettled([
                    api.get(`/transcripts/${meetingId}`),
                    api.get(`/transcripts/${meetingId}/metadata`),
                ]);

                if (segResponse.status === 'fulfilled') {
                    const segs: TranscriptSegment[] = segResponse.value.data?.segments || segResponse.value.data || [];
                    setSegments(segs);
                    setSpeakerColors(assignSpeakerColors(segs));
                    // Build initial name map from data
                    const nameMap: Record<string, string> = {};
                    for (const s of segs) {
                        const key = s.speaker_id || 'unknown';
                        if (s.speaker_name && !nameMap[key]) nameMap[key] = s.speaker_name;
                    }
                    setSpeakerNames(nameMap);
                }

                if (metaResponse.status === 'fulfilled') {
                    setMetadata(metaResponse.value.data);
                }
            } catch (err: any) {
                setError(err?.response?.data?.detail || 'Failed to load transcript');
            } finally {
                setIsLoading(false);
            }
        };
        fetchTranscript();
    }, [meetingId]);

    // Filtered + display-name applied segments
    const filteredSegments = segments.filter((seg) => {
        const speakerKey = seg.speaker_id || 'unknown';
        if (filters.speaker && filters.speaker !== 'all' && speakerKey !== filters.speaker) return false;
        if (filters.minConfidence != null && (seg.confidence ?? 1) < filters.minConfidence) return false;
        if (filters.search) {
            return seg.text.toLowerCase().includes(filters.search.toLowerCase());
        }
        return true;
    }).map((seg) => ({
        ...seg,
        speaker_name: speakerNames[seg.speaker_id || 'unknown'] || seg.speaker_name || seg.speaker_id || 'Unknown Speaker',
    }));

    const updateSpeakerName = useCallback((speakerId: string, name: string) => {
        setSpeakerNames((prev) => ({ ...prev, [speakerId]: name }));
    }, []);

    const addBookmark = useCallback((segment: TranscriptSegment, label: string) => {
        const bookmark: TranscriptBookmark = {
            id: `bm-${Date.now()}`,
            segment_id: segment.id,
            time: segment.start_time,
            label,
            created_at: new Date().toISOString(),
        };
        setBookmarks((prev) => [...prev, bookmark]);
    }, []);

    const removeBookmark = useCallback((bookmarkId: string) => {
        setBookmarks((prev) => prev.filter((b) => b.id !== bookmarkId));
    }, []);

    const updateSegmentText = useCallback(async (segmentId: string, newText: string) => {
        setSegments((prev) =>
            prev.map((s) =>
                s.id === segmentId
                    ? { ...s, text: newText, is_edited: true, original_text: s.original_text ?? s.text }
                    : s
            )
        );
        // persist if API available (fire and forget)
        try {
            await api.patch(`/transcripts/segments/${segmentId}`, { text: newText });
        } catch { /* no-op */ }
        setEditingSegmentId(null);
    }, []);

    return {
        segments: filteredSegments,
        allSegments: segments,
        metadata,
        isLoading,
        error,
        filters,
        setFilters,
        speakerColors,
        speakerNames,
        updateSpeakerName,
        bookmarks,
        addBookmark,
        removeBookmark,
        editingSegmentId,
        setEditingSegmentId,
        updateSegmentText,
    };
};
