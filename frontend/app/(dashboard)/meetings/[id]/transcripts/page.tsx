'use client';

import React, { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, SlidersHorizontal, Scroll, Bookmark, Info } from 'lucide-react';
import { useTranscript } from '@/hooks/useTranscript';
import { useAudioSync } from '@/hooks/useAudioSync';
import { useMeeting } from '@/hooks/useMeeting';

import { TranscriptViewer } from '@/components/transcripts/TranscriptViewer';
import TranscriptSearch from '@/components/transcripts/TranscriptSearch/TranscriptSearch';
import TranscriptTimeline from '@/components/transcripts/TranscriptTimeline/TranscriptTimeline';
import TranscriptExport from '@/components/transcripts/TranscriptExport/TranscriptExport';
import AudioPlayer from '@/components/transcripts/AudioPlayer/AudioPlayer';

interface Props {
    params: Promise<{ id: string }>;
}

// Derive speaker list from segments
function getSpeakers(segments: { speaker_id?: string; speaker_name: string }[]) {
    const map: Record<string, string> = {};
    for (const s of segments) {
        const id = s.speaker_id || 'unknown';
        if (!map[id]) map[id] = s.speaker_name;
    }
    return Object.entries(map).map(([id, name]) => ({ id, name }));
}

export default function TranscriptPage({ params }: Props) {
    const { id } = use(params);
    const router = useRouter();

    const { meeting } = useMeeting(id);
    const {
        segments,
        allSegments,
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
    } = useTranscript(id);

    const {
        hasAudio,
        currentTime,
        duration,
        isPlaying,
        playbackRate,
        volume,
        activeSegmentId,
        togglePlayPause,
        seekTo,
        changePlaybackRate,
        changeVolume,
    } = useAudioSync(meeting?.recordingUrl, allSegments);

    const [autoScroll, setAutoScroll] = useState(true);
    const [showStats, setShowStats] = useState(false);

    const speakers = getSpeakers(segments);
    const bookmarkedTimes = bookmarks.map((b) => b.time);

    // ─── Loading / Error ────────────────────────────────────────────────────────
    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
                <div className="relative w-12 h-12">
                    <div className="absolute inset-0 rounded-full border-4 border-primary-100" />
                    <div className="absolute inset-0 rounded-full border-4 border-primary-500 border-t-transparent animate-spin" />
                </div>
                <p className="text-neutral-500 font-medium">Loading transcript…</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center px-4">
                <div className="w-14 h-14 rounded-full bg-red-50 flex items-center justify-center">
                    <Info className="w-6 h-6 text-red-400" />
                </div>
                <h2 className="text-lg font-semibold text-neutral-800">Transcript Unavailable</h2>
                <p className="text-sm text-neutral-500 max-w-xs">{error}</p>
                <button
                    onClick={() => router.back()}
                    className="flex items-center gap-1.5 px-4 py-2 text-sm bg-neutral-100 rounded-lg hover:bg-neutral-200 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" /> Go back
                </button>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto px-4 py-6 space-y-4">
            {/* ── Header ───────────────────────────────────────────────────────── */}
            <div className="flex items-center justify-between gap-3 flex-wrap">
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => router.back()}
                        className="flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-800 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back
                    </button>
                    <div className="h-4 w-px bg-neutral-200" />
                    <div>
                        <h1 className="text-xl font-bold text-neutral-900 font-outfit">
                            {meeting?.title ?? 'Meeting Transcript'}
                        </h1>
                        {metadata && (
                            <p className="text-xs text-neutral-500 mt-0.5">
                                {metadata.speaker_count} speaker{metadata.speaker_count !== 1 ? 's' : ''} ·{' '}
                                {metadata.total_words.toLocaleString()} words ·{' '}
                                {Math.round(metadata.total_duration_seconds / 60)} min
                                {metadata.average_confidence != null && (
                                    <> · {Math.round(metadata.average_confidence * 100)}% confidence</>
                                )}
                            </p>
                        )}
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-wrap">
                    {/* Auto-scroll toggle */}
                    <button
                        onClick={() => setAutoScroll((v) => !v)}
                        title={autoScroll ? 'Disable auto-scroll' : 'Enable auto-scroll'}
                        className={`flex items-center gap-1.5 px-3 py-2 text-xs rounded-lg border transition-colors ${autoScroll
                                ? 'bg-primary-50 border-primary-200 text-primary-600'
                                : 'bg-white border-neutral-200 text-neutral-500'
                            }`}
                    >
                        <Scroll className="w-3.5 h-3.5" />
                        Auto-scroll
                    </button>

                    {/* Bookmarks count */}
                    {bookmarks.length > 0 && (
                        <span className="flex items-center gap-1 px-3 py-2 text-xs bg-amber-50 border border-amber-200 text-amber-600 rounded-lg">
                            <Bookmark className="w-3.5 h-3.5" />
                            {bookmarks.length} bookmark{bookmarks.length !== 1 ? 's' : ''}
                        </span>
                    )}

                    <TranscriptExport
                        segments={segments}
                        meetingTitle={meeting?.title ?? 'transcript'}
                    />
                </div>
            </div>

            {/* ── Audio Player ─────────────────────────────────────────────────── */}
            <AudioPlayer
                currentTime={currentTime}
                duration={duration}
                isPlaying={isPlaying}
                playbackRate={playbackRate}
                volume={volume}
                hasAudio={hasAudio}
                onTogglePlay={togglePlayPause}
                onSeek={seekTo}
                onPlaybackRateChange={changePlaybackRate}
                onVolumeChange={changeVolume}
            />

            {/* ── Timeline ─────────────────────────────────────────────────────── */}
            {(hasAudio || allSegments.length > 0) && (
                <TranscriptTimeline
                    segments={segments}
                    currentTime={currentTime}
                    duration={duration || (allSegments.at(-1)?.end_time ?? 0)}
                    speakerColors={speakerColors}
                    bookmarkedTimes={bookmarkedTimes}
                    onSeek={seekTo}
                />
            )}

            {/* __ Search & Filters ─────────────────────────────────────────────── */}
            <TranscriptSearch
                filters={filters}
                onChange={setFilters}
                speakers={speakers}
                totalCount={allSegments.length}
                filteredCount={segments.length}
            />

            {/* ── Keyboard hint ────────────────────────────────────────────────── */}
            {hasAudio && (
                <p className="text-xs text-neutral-400 text-right">
                    Press <kbd className="px-1 py-0.5 bg-neutral-100 rounded text-neutral-500 font-mono">Space</kbd> to play/pause · Click a timestamp to jump
                </p>
            )}

            {/* ── Transcript body ──────────────────────────────────────────────── */}
            <div className="bg-white rounded-2xl border border-neutral-100 shadow-sm overflow-hidden">
                <div className="px-4 py-2 border-b border-neutral-50 flex items-center gap-2 bg-neutral-50/60">
                    <span className="text-xs text-neutral-400 font-medium uppercase tracking-wider">Transcript</span>
                    {isPlaying && (
                        <span className="flex items-center gap-1 text-xs text-primary-500 font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-pulse" />
                            Live
                        </span>
                    )}
                </div>

                <div className="p-4 max-h-[65vh] overflow-y-auto scroll-smooth">
                    <TranscriptViewer
                        segments={segments}
                        speakerColors={speakerColors}
                        searchQuery={filters.search}
                        activeSegmentId={activeSegmentId}
                        autoScroll={autoScroll}
                        editingSegmentId={editingSegmentId}
                        bookmarks={bookmarks}
                        onSeek={seekTo}
                        onRenameSpeaker={updateSpeakerName}
                        onStartEdit={setEditingSegmentId}
                        onCancelEdit={() => setEditingSegmentId(null)}
                        onSaveEdit={updateSegmentText}
                        onBookmark={addBookmark}
                    />
                </div>
            </div>

            {/* ── Bookmarks panel ─────────────────────────────────────────────── */}
            {bookmarks.length > 0 && (
                <div className="bg-amber-50 border border-amber-100 rounded-2xl overflow-hidden">
                    <div className="px-4 py-2.5 border-b border-amber-100 flex items-center justify-between">
                        <span className="flex items-center gap-1.5 text-sm font-semibold text-amber-700">
                            <Bookmark className="w-4 h-4" />
                            Bookmarks ({bookmarks.length})
                        </span>
                    </div>
                    <div className="divide-y divide-amber-100">
                        {bookmarks.map((bm) => {
                            const seg = allSegments.find((s) => s.id === bm.segment_id);
                            return (
                                <div key={bm.id} className="flex items-start gap-3 px-4 py-3">
                                    <button
                                        onClick={() => seekTo(bm.time)}
                                        className="text-xs font-mono text-amber-600 hover:text-amber-800 whitespace-nowrap mt-0.5"
                                    >
                                        {Math.floor(bm.time / 60)}:{Math.floor(bm.time % 60).toString().padStart(2, '0')}
                                    </button>
                                    <p className="flex-1 text-sm text-neutral-700 line-clamp-2">{seg?.text}</p>
                                    <button
                                        onClick={() => removeBookmark(bm.id)}
                                        className="text-xs text-neutral-400 hover:text-red-500 transition-colors whitespace-nowrap mt-0.5"
                                    >
                                        Remove
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
