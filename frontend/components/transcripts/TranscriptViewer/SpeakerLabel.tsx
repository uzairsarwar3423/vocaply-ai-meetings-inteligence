'use client';

import React, { useState } from 'react';
import { Edit2, Check, X, Bookmark, AlertCircle } from 'lucide-react';
import { TranscriptSegment } from '@/types/transcript';

interface SpeakerLabelProps {
    speakerId: string;
    speakerName: string;
    color: string;
    onRename: (speakerId: string, newName: string) => void;
}

export function SpeakerLabel({ speakerId, speakerName, color, onRename }: SpeakerLabelProps) {
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState(speakerName);

    const commit = () => {
        if (draft.trim()) onRename(speakerId, draft.trim());
        setEditing(false);
    };

    if (editing) {
        return (
            <span className="flex items-center gap-1">
                <input
                    autoFocus
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') commit(); if (e.key === 'Escape') setEditing(false); }}
                    className="text-xs font-semibold border border-primary-300 rounded px-1 py-0.5 outline-none w-28"
                    style={{ color }}
                />
                <button onClick={commit} className="text-primary-500 hover:text-primary-700"><Check className="w-3 h-3" /></button>
                <button onClick={() => setEditing(false)} className="text-neutral-400 hover:text-neutral-600"><X className="w-3 h-3" /></button>
            </span>
        );
    }

    return (
        <span
            className="flex items-center gap-1 text-xs font-semibold cursor-pointer group"
            style={{ color }}
            onClick={() => { setDraft(speakerName); setEditing(true); }}
            title="Click to rename speaker"
        >
            {speakerName}
            <Edit2 className="w-2.5 h-2.5 opacity-0 group-hover:opacity-60 transition-opacity" />
        </span>
    );
}
