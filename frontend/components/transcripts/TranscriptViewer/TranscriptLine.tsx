'use client';

import React, { useState, useRef } from 'react';
import { Edit2, Check, X, Bookmark, Clock, AlertTriangle } from 'lucide-react';
import { TranscriptSegment } from '@/types/transcript';
import { SpeakerLabel } from './SpeakerLabel';

function formatTime(secs: number) {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}

function highlightText(text: string, query: string) {
    if (!query) return <>{text}</>;
    const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
    return (
        <>
            {parts.map((part, i) =>
                part.toLowerCase() === query.toLowerCase()
                    ? <mark key={i} className="bg-amber-200 text-amber-900 rounded-sm px-0.5">{part}</mark>
                    : part
            )}
        </>
    );
}

interface TranscriptLineProps {
    segment: TranscriptSegment & { speaker_name: string };
    speakerColor: string;
    searchQuery: string;
    isActive: boolean;
    isEditing: boolean;
    isBookmarked: boolean;
    onSeek: (time: number) => void;
    onRenameSpaker: (speakerId: string, name: string) => void;
    onStartEdit: (id: string) => void;
    onCancelEdit: () => void;
    onSaveEdit: (id: string, text: string) => void;
    onBookmark: (segment: TranscriptSegment, label: string) => void;
}

export default function TranscriptLine({
    segment,
    speakerColor,
    searchQuery,
    isActive,
    isEditing,
    isBookmarked,
    onSeek,
    onRenameSpaker,
    onStartEdit,
    onCancelEdit,
    onSaveEdit,
    onBookmark,
}: TranscriptLineProps) {
    const [editDraft, setEditDraft] = useState(segment.text);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleStartEdit = () => {
        setEditDraft(segment.text);
        onStartEdit(segment.id);
    };

    const confidence = segment.confidence ?? 1;
    const lowConf = confidence < 0.7;

    return (
        <div
            id={`seg-${segment.id}`}
            className={`group relative flex gap-4 px-4 py-3 rounded-xl transition-all duration-200 ${isActive
                    ? 'bg-primary-50 border border-primary-100 shadow-sm'
                    : 'hover:bg-neutral-50 border border-transparent'
                } ${segment.is_edited ? 'ring-1 ring-amber-200' : ''}`}
        >
            {/* Timeline gutter */}
            <div className="flex-shrink-0 w-12 flex flex-col items-end pt-0.5 gap-1">
                <button
                    onClick={() => onSeek(segment.start_time)}
                    className="text-xs text-neutral-400 hover:text-primary-500 font-mono tabular-nums transition-colors"
                    title={`Jump to ${formatTime(segment.start_time)}`}
                >
                    {formatTime(segment.start_time)}
                </button>
                {lowConf && (
                    <span title={`Low confidence: ${Math.round(confidence * 100)}%`}>
                        <AlertTriangle className="w-3 h-3 text-amber-400" />
                    </span>
                )}
            </div>

            {/* Speaker avatar dot */}
            <div className="flex-shrink-0 mt-1">
                <div
                    className="w-2.5 h-2.5 rounded-full mt-1"
                    style={{ backgroundColor: speakerColor }}
                />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <SpeakerLabel
                        speakerId={segment.speaker_id || 'unknown'}
                        speakerName={segment.speaker_name}
                        color={speakerColor}
                        onRename={onRenameSpaker}
                    />
                    {segment.is_edited && (
                        <span className="text-xs text-amber-500 font-medium">(edited)</span>
                    )}
                </div>

                {isEditing ? (
                    <div className="space-y-2">
                        <textarea
                            ref={textareaRef}
                            value={editDraft}
                            autoFocus
                            onChange={(e) => setEditDraft(e.target.value)}
                            className="w-full text-sm text-neutral-700 border border-primary-300 rounded-lg p-2 resize-none outline-none focus:ring-2 focus:ring-primary-200"
                            rows={Math.max(2, Math.ceil(editDraft.length / 80))}
                        />
                        <div className="flex gap-2">
                            <button
                                onClick={() => onSaveEdit(segment.id, editDraft)}
                                className="flex items-center gap-1 text-xs px-3 py-1.5 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                            >
                                <Check className="w-3 h-3" /> Save
                            </button>
                            <button
                                onClick={onCancelEdit}
                                className="flex items-center gap-1 text-xs px-3 py-1.5 bg-neutral-100 text-neutral-600 rounded-lg hover:bg-neutral-200 transition-colors"
                            >
                                <X className="w-3 h-3" /> Cancel
                            </button>
                        </div>
                    </div>
                ) : (
                    <p className={`text-sm leading-relaxed ${lowConf ? 'text-neutral-400' : 'text-neutral-700'}`}>
                        {highlightText(segment.text, searchQuery)}
                    </p>
                )}
            </div>

            {/* Action buttons (visible on hover) */}
            {!isEditing && (
                <div className="flex-shrink-0 flex items-start gap-1 opacity-0 group-hover:opacity-100 transition-opacity pt-0.5">
                    <button
                        onClick={handleStartEdit}
                        className="p-1 rounded-md text-neutral-400 hover:text-primary-500 hover:bg-primary-50 transition-colors"
                        title="Edit transcript"
                    >
                        <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                        onClick={() => onBookmark(segment, `Bookmark @ ${formatTime(segment.start_time)}`)}
                        className={`p-1 rounded-md transition-colors ${isBookmarked
                                ? 'text-amber-500 bg-amber-50'
                                : 'text-neutral-400 hover:text-amber-500 hover:bg-amber-50'
                            }`}
                        title={isBookmarked ? 'Bookmarked' : 'Bookmark this section'}
                    >
                        <Bookmark className="w-3.5 h-3.5" />
                    </button>
                </div>
            )}
        </div>
    );
}
