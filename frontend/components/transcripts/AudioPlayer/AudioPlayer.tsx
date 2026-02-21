'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, SkipBack, SkipForward } from 'lucide-react';

interface AudioPlayerProps {
    currentTime: number;
    duration: number;
    isPlaying: boolean;
    playbackRate: number;
    volume: number;
    hasAudio: boolean;
    onTogglePlay: () => void;
    onSeek: (time: number) => void;
    onPlaybackRateChange: (rate: number) => void;
    onVolumeChange: (vol: number) => void;
}

const RATES = [0.5, 0.75, 1, 1.25, 1.5, 2];

function formatTime(secs: number) {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function AudioPlayer({
    currentTime,
    duration,
    isPlaying,
    playbackRate,
    volume,
    hasAudio,
    onTogglePlay,
    onSeek,
    onPlaybackRateChange,
    onVolumeChange,
}: AudioPlayerProps) {
    const progressRef = useRef<HTMLDivElement>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [hoverTime, setHoverTime] = useState<number | null>(null);
    const [showVolumeSlider, setShowVolumeSlider] = useState(false);

    const progress = duration ? (currentTime / duration) * 100 : 0;

    const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!progressRef.current || !duration) return;
        const rect = progressRef.current.getBoundingClientRect();
        const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        onSeek(ratio * duration);
    };

    const handleHover = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!progressRef.current || !duration) return;
        const rect = progressRef.current.getBoundingClientRect();
        const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        setHoverTime(ratio * duration);
    };

    if (!hasAudio) {
        return (
            <div className="flex items-center gap-3 px-5 py-4 bg-neutral-50 border border-dashed border-neutral-200 rounded-xl text-sm text-neutral-400">
                <Volume2 className="w-4 h-4" />
                No audio recording available for this meeting.
            </div>
        );
    }

    return (
        <div className="bg-white border border-neutral-100 rounded-2xl shadow-sm overflow-hidden">
            {/* Timeline scrubber */}
            <div
                ref={progressRef}
                className="relative h-1.5 bg-neutral-100 cursor-pointer group"
                onClick={handleSeek}
                onMouseMove={handleHover}
                onMouseLeave={() => setHoverTime(null)}
            >
                <div
                    className="absolute left-0 top-0 h-full bg-gradient-to-r from-primary-500 to-primary-400 transition-all duration-100"
                    style={{ width: `${progress}%` }}
                />
                {/* Hover tooltip */}
                {hoverTime != null && (
                    <div
                        className="absolute -top-7 text-xs bg-neutral-800 text-white px-1.5 py-0.5 rounded pointer-events-none select-none"
                        style={{ left: `calc(${(hoverTime / duration) * 100}% - 16px)` }}
                    >
                        {formatTime(hoverTime)}
                    </div>
                )}
                {/* Scrubber thumb */}
                <div
                    className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-primary-500 rounded-full shadow opacity-0 group-hover:opacity-100 transition-opacity"
                    style={{ left: `calc(${progress}% - 6px)` }}
                />
            </div>

            {/* Controls */}
            <div className="flex items-center gap-3 px-5 py-3">
                {/* Skip back 10s */}
                <button
                    onClick={() => onSeek(Math.max(0, currentTime - 10))}
                    className="text-neutral-400 hover:text-neutral-600 transition-colors"
                    title="Rewind 10s"
                >
                    <SkipBack className="w-4 h-4" />
                </button>

                {/* Play / Pause */}
                <button
                    onClick={onTogglePlay}
                    className="w-9 h-9 rounded-full bg-primary-500 hover:bg-primary-600 text-white flex items-center justify-center shadow-sm transition-colors"
                >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                </button>

                {/* Skip forward 10s */}
                <button
                    onClick={() => onSeek(Math.min(duration, currentTime + 10))}
                    className="text-neutral-400 hover:text-neutral-600 transition-colors"
                    title="Forward 10s"
                >
                    <SkipForward className="w-4 h-4" />
                </button>

                {/* Time */}
                <span className="text-xs text-neutral-500 tabular-nums">
                    {formatTime(currentTime)} / {formatTime(duration)}
                </span>

                <div className="flex-1" />

                {/* Playback rate */}
                <div className="relative">
                    <select
                        value={playbackRate}
                        onChange={(e) => onPlaybackRateChange(Number(e.target.value))}
                        className="text-xs text-neutral-600 bg-neutral-100 hover:bg-neutral-200 rounded-lg px-2 py-1 cursor-pointer border-0 outline-none appearance-none pr-5"
                    >
                        {RATES.map((r) => (
                            <option key={r} value={r}>{r}×</option>
                        ))}
                    </select>
                </div>

                {/* Volume */}
                <div className="relative flex items-center gap-1">
                    <button
                        onClick={() => setShowVolumeSlider((v) => !v)}
                        className="text-neutral-400 hover:text-neutral-600 transition-colors"
                    >
                        {volume === 0 ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                    </button>
                    {showVolumeSlider && (
                        <input
                            type="range"
                            min={0}
                            max={1}
                            step={0.05}
                            value={volume}
                            onChange={(e) => onVolumeChange(Number(e.target.value))}
                            className="w-20 accent-primary-500"
                        />
                    )}
                </div>
            </div>
        </div>
    );
}
