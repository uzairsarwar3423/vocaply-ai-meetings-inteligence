// ActionItemHeader — top header bar for the detail view
'use client';

import React from 'react';
import Link from 'next/link';
import { ActionItem } from '@/types/action-item';
import { StatusBadge } from '../StatusBadge/StatusBadge';
import { PriorityBadge } from '../PriorityBadge/PriorityBadge';
import {
    ArrowLeft, Edit3, Trash2, Share2, Brain, Copy, CheckCircle2,
    ExternalLink,
} from 'lucide-react';

interface ActionItemHeaderProps {
    item: ActionItem;
    isEditing: boolean;
    isSaving: boolean;
    onEdit: () => void;
    onDelete: () => void;
    onToggleComplete: () => void;
}

export const ActionItemHeader: React.FC<ActionItemHeaderProps> = ({
    item,
    isEditing,
    isSaving,
    onEdit,
    onDelete,
    onToggleComplete,
}) => {
    const [copied, setCopied] = React.useState(false);

    const handleShare = async () => {
        const url = window.location.href;
        try {
            await navigator.clipboard.writeText(url);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            // fallback: noop
        }
    };

    const isCompleted = item.status === 'completed';

    return (
        <div className="bg-white border-b border-neutral-100 px-6 py-4">
            <div className="max-w-5xl mx-auto">
                {/* Breadcrumb */}
                <div className="flex items-center gap-2 mb-4">
                    <Link
                        href="/action-items"
                        className="flex items-center gap-1.5 text-sm text-neutral-500 hover:text-primary transition-colors font-medium"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Action Items
                    </Link>
                    <span className="text-neutral-300">/</span>
                    <span className="text-sm text-neutral-700 font-medium truncate max-w-[300px]">
                        {item.title}
                    </span>
                </div>

                {/* Main row */}
                <div className="flex items-start gap-4">
                    {/* Complete toggle */}
                    <button
                        onClick={onToggleComplete}
                        className={`flex-shrink-0 w-7 h-7 rounded-full border-2 flex items-center justify-center transition-all mt-0.5 ${isCompleted
                                ? 'border-emerald-500 bg-emerald-500 text-white shadow-md shadow-emerald-200'
                                : 'border-neutral-300 hover:border-emerald-400 hover:shadow-sm'
                            }`}
                        title={isCompleted ? 'Mark incomplete' : 'Mark complete'}
                    >
                        {isCompleted && <CheckCircle2 className="w-4 h-4" />}
                    </button>

                    {/* Title + badges */}
                    <div className="flex-1 min-w-0">
                        <h1 className={`text-xl font-bold text-neutral-900 leading-tight mb-2 ${isCompleted ? 'line-through text-neutral-400' : ''}`}>
                            {item.title}
                        </h1>
                        <div className="flex items-center gap-2 flex-wrap">
                            <StatusBadge status={item.status} size="sm" />
                            <PriorityBadge priority={item.priority} size="sm" />
                            {item.is_ai_generated && (
                                <span className="inline-flex items-center gap-1 text-[11px] bg-primary/8 text-primary px-2 py-0.5 rounded-full font-semibold border border-primary/15">
                                    <Brain className="w-3 h-3" />
                                    AI Generated · {Math.round((item.confidence_score || 0) * 100)}%
                                </span>
                            )}
                            <span className="text-xs text-neutral-400">
                                Created {new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                            </span>
                        </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                        {/* Share */}
                        <button
                            onClick={handleShare}
                            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-neutral-600 border border-neutral-200 rounded-xl hover:bg-neutral-50 transition-colors"
                            title="Copy link"
                        >
                            {copied ? (
                                <><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Copied!</>
                            ) : (
                                <><Share2 className="w-3.5 h-3.5" /> Share</>
                            )}
                        </button>

                        {/* Meeting link */}
                        <Link
                            href={`/meetings/${item.meeting_id}`}
                            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-neutral-600 border border-neutral-200 rounded-xl hover:bg-neutral-50 hover:text-primary transition-colors"
                            title="View source meeting"
                        >
                            <ExternalLink className="w-3.5 h-3.5" /> Meeting
                        </Link>

                        {/* Edit */}
                        {!isEditing && (
                            <button
                                onClick={onEdit}
                                className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-primary border border-primary/20 bg-primary/5 rounded-xl hover:bg-primary/10 transition-colors"
                                title="Edit (E)"
                            >
                                <Edit3 className="w-3.5 h-3.5" /> Edit
                            </button>
                        )}

                        {/* Delete */}
                        <button
                            onClick={onDelete}
                            className="p-2 rounded-xl border border-neutral-200 text-neutral-400 hover:text-rose-500 hover:border-rose-200 hover:bg-rose-50 transition-all"
                            title="Delete action item"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
