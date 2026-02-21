'use client';

import React from 'react';
import { TranscriptSegment } from '@/types/transcript';

function formatTime(secs: number) {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}

interface TranscriptTimelineProps {
    segments: (TranscriptSegment & { speaker_name: string })[];
    currentTime: number;
    duration: number;
    speakerColors: Record<string, string>;
    bookmarkedTimes: number[];
    onSeek: (time: number) => void;
}

export default function TranscriptTimeline({
    segments,
    currentTime,
    duration,
    speakerColors,
    bookmarkedTimes,
    onSeek,
}: TranscriptTimelineProps) {
    if (!duration) return null;

    const toPercent = (t: number) => `${Math.max(0, Math.min(100, (t / duration) * 100))}%`;

    return (
        <div className="bg-white border border-neutral-100 rounded-xl px-4 py-3">
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-2">
                <span>0:00</span>
                <span className="text-neutral-600 font-medium">Timeline</span>
                <span>{formatTime(duration)}</span>
            </div>

            {/* Speaker track */}
            <div className="relative h-5 bg-neutral-100 rounded-full overflow-hidden cursor-pointer mb-2"
                onClick={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    const ratio = (e.clientX - rect.left) / rect.width;
                    onSeek(ratio * duration);
                }}
            >
                {/* Segments by speaker */}
                {segments.map((seg) => (
                    <div
                        key={seg.id}
                        className="absolute top-0 h-full rounded-sm opacity-70 hover:opacity-100 transition-opacity"
                        style={{
                            left: toPercent(seg.start_time),
                            width: `calc(${toPercent(seg.end_time)} - ${toPercent(seg.start_time)})`,
                            backgroundColor: speakerColors[seg.speaker_id || 'unknown'] || '#6B8585',
                            minWidth: '2px',
                        }}
                        title={`${seg.speaker_name}: ${formatTime(seg.start_time)} — ${formatTime(seg.end_time)}`}
                    />
                ))}

                {/* Bookmark markers */}
                {bookmarkedTimes.map((t, i) => (
                    <div
                        key={i}
                        className="absolute top-0 h-full w-0.5 bg-amber-400 z-10"
                        style={{ left: toPercent(t) }}
                        title={`Bookmark @ ${formatTime(t)}`}
                    />
                ))}

                {/* Playhead */}
                <div
                    className="absolute top-0 h-full w-0.5 bg-neutral-800 z-20 pointer-events-none"
                    style={{ left: toPercent(currentTime) }}
                />
            </div>

            {/* Speaker legend */}
            <div className="flex flex-wrap gap-x-4 gap-y-1">
                {Object.entries(
                    segments.reduce<Record<string, string>>((acc, seg) => {
                        const key = seg.speaker_id || 'unknown';
                        if (!acc[key]) acc[key] = seg.speaker_name;
                        return acc;
                    }, {})
                ).map(([id, name]) => (
                    <div key={id} className="flex items-center gap-1.5 text-xs text-neutral-500">
                        <div
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: speakerColors[id] || '#6B8585' }}
                        />
                        {name}
                    </div>
                ))}
            </div>
        </div>
    );
}
