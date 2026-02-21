'use client';

import React, { useEffect, useRef } from 'react';
import { TranscriptSegment, TranscriptBookmark } from '@/types/transcript';
import TranscriptLine from './TranscriptLine';
import { FileText } from 'lucide-react';

interface TranscriptViewerProps {
    segments: (TranscriptSegment & { speaker_name: string })[];
    speakerColors: Record<string, string>;
    searchQuery: string;
    activeSegmentId: string | null;
    autoScroll: boolean;
    editingSegmentId: string | null;
    bookmarks: TranscriptBookmark[];
    onSeek: (time: number) => void;
    onRenameSpeaker: (speakerId: string, name: string) => void;
    onStartEdit: (id: string) => void;
    onCancelEdit: () => void;
    onSaveEdit: (id: string, text: string) => void;
    onBookmark: (segment: TranscriptSegment, label: string) => void;
}

export default function TranscriptViewer({
    segments,
    speakerColors,
    searchQuery,
    activeSegmentId,
    autoScroll,
    editingSegmentId,
    bookmarks,
    onSeek,
    onRenameSpeaker,
    onStartEdit,
    onCancelEdit,
    onSaveEdit,
    onBookmark,
}: TranscriptViewerProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    // Auto-scroll active segment into view
    useEffect(() => {
        if (!autoScroll || !activeSegmentId) return;
        const el = document.getElementById(`seg-${activeSegmentId}`);
        el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, [activeSegmentId, autoScroll]);

    if (segments.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-20 text-neutral-400 gap-4">
                <FileText className="w-10 h-10 opacity-30" />
                <p className="text-sm font-medium">
                    {searchQuery ? 'No matching transcript lines found.' : 'No transcript available yet.'}
                </p>
            </div>
        );
    }

    const bookmarkedIds = new Set(bookmarks.map((b) => b.segment_id));

    return (
        <div
            ref={containerRef}
            className="space-y-1 pb-6"
        >
            {segments.map((segment) => (
                <TranscriptLine
                    key={segment.id}
                    segment={segment}
                    speakerColor={speakerColors[segment.speaker_id || 'unknown'] || '#6B8585'}
                    searchQuery={searchQuery}
                    isActive={segment.id === activeSegmentId}
                    isEditing={segment.id === editingSegmentId}
                    isBookmarked={bookmarkedIds.has(segment.id)}
                    onSeek={onSeek}
                    onRenameSpaker={onRenameSpeaker}
                    onStartEdit={onStartEdit}
                    onCancelEdit={onCancelEdit}
                    onSaveEdit={onSaveEdit}
                    onBookmark={onBookmark}
                />
            ))}
        </div>
    );
}
