// RelatedMeeting — shows the parent meeting context for an action item
'use client';

import Link from 'next/link';
import { Video, Calendar, Clock, ExternalLink, Users, MonitorPlay, Monitor, Mic, Globe } from 'lucide-react';
import React from 'react';

// Lucide icon per platform
const PLATFORM_ICONS: Record<string, React.FC<{ className?: string }>> = {
    zoom: MonitorPlay,
    google_meet: Monitor,
    teams: Monitor,
    other: Mic,
};

interface RelatedMeetingProps {
    meetingId: string;
    meetingTitle?: string;
    meetingDate?: string;
    platform?: string;
    participantCount?: number;
    transcriptStartTime?: number; // seconds
    transcriptQuote?: string;
}

function formatMeetingDate(dateStr?: string): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
}

function formatTimestamp(seconds?: number): string {
    if (!seconds && seconds !== 0) return '';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}



export const RelatedMeeting: React.FC<RelatedMeetingProps> = ({
    meetingId,
    meetingTitle,
    meetingDate,
    platform,
    participantCount,
    transcriptStartTime,
    transcriptQuote,
}) => {
    const hasTimestamp = transcriptStartTime !== undefined && transcriptStartTime !== null;

    return (
        <div className="rounded-2xl border border-neutral-100 bg-white overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-neutral-50 flex items-center gap-2">
                <div className="w-8 h-8 bg-primary/10 rounded-xl flex items-center justify-center">
                    <Video className="w-4 h-4 text-primary" />
                </div>
                <div>
                    <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">Source Meeting</p>
                </div>
            </div>

            <div className="p-4 space-y-3">
                {/* Meeting title */}
                <Link
                    href={`/meetings/${meetingId}`}
                    className="group flex items-start gap-2 hover:text-primary transition-colors"
                >
                    <div className="flex-1">
                        <p className="font-semibold text-neutral-800 group-hover:text-primary transition-colors leading-snug">
                            {meetingTitle || 'Untitled Meeting'}
                        </p>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-neutral-400 group-hover:text-primary mt-0.5 flex-shrink-0 transition-colors" />
                </Link>

                {/* Meta row */}
                <div className="flex items-center gap-3 flex-wrap">
                    {platform && (() => {
                        const PlatformIcon = PLATFORM_ICONS[platform] ?? Globe;
                        return (
                            <span className="inline-flex items-center gap-1 text-xs text-neutral-500">
                                <PlatformIcon className="w-3 h-3" />
                                <span className="capitalize">{platform.replace('_', ' ')}</span>
                            </span>
                        );
                    })()}
                    {meetingDate && (
                        <span className="inline-flex items-center gap-1 text-xs text-neutral-500">
                            <Calendar className="w-3 h-3" />
                            {formatMeetingDate(meetingDate)}
                        </span>
                    )}
                    {participantCount !== undefined && participantCount > 0 && (
                        <span className="inline-flex items-center gap-1 text-xs text-neutral-500">
                            <Users className="w-3 h-3" />
                            {participantCount} participants
                        </span>
                    )}
                </div>

                {/* Timestamp link */}
                {hasTimestamp && (
                    <Link
                        href={`/meetings/${meetingId}?t=${Math.floor(transcriptStartTime!)}`}
                        className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary/5 text-primary rounded-lg text-xs font-semibold hover:bg-primary/10 transition-colors border border-primary/10"
                    >
                        <Clock className="w-3.5 h-3.5" />
                        Jump to {formatTimestamp(transcriptStartTime)} in recording
                        <ExternalLink className="w-3 h-3 opacity-60" />
                    </Link>
                )}

                {/* Transcript quote */}
                {transcriptQuote && (
                    <blockquote className="mt-1 border-l-2 border-primary/30 pl-3 py-1">
                        <p className="text-xs text-neutral-500 italic leading-relaxed line-clamp-4">
                            &ldquo;{transcriptQuote}&rdquo;
                        </p>
                    </blockquote>
                )}
            </div>
        </div>
    );
};
