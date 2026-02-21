// ActionItemMenu — ellipsis context menu for a single action item card
'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { ActionItem } from '@/types/action-item';
import {
    MoreVertical, CheckCircle2, RotateCcw, Trash2,
    ThumbsUp, ThumbsDown, ExternalLink, Edit2, Eye
} from 'lucide-react';

interface ActionItemMenuProps {
    item: ActionItem;
    onUpdate: (id: string, data: Partial<ActionItem>) => void;
    onDelete: (id: string) => void;
    onAccept?: (id: string) => void;
    onReject?: (id: string) => void;
    onEdit?: (item: ActionItem) => void;
}

export const ActionItemMenu: React.FC<ActionItemMenuProps> = ({
    item,
    onUpdate,
    onDelete,
    onAccept,
    onReject,
    onEdit,
}) => {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, []);

    const action = (fn: () => void) => {
        fn();
        setOpen(false);
    };

    return (
        <div ref={ref} className="relative" onClick={e => e.stopPropagation()}>
            <button
                id={`action-menu-btn-${item.id}`}
                onClick={() => setOpen(o => !o)}
                className="w-7 h-7 rounded-lg flex items-center justify-center text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100 transition-all opacity-0 group-hover:opacity-100"
                aria-label="Action item options"
            >
                <MoreVertical className="w-4 h-4" />
            </button>

            {open && (
                <div className="absolute right-0 top-9 z-50 w-48 bg-white rounded-xl shadow-xl border border-neutral-100 py-1 animate-in fade-in-0 zoom-in-95 duration-100">
                    {/* View details */}
                    <Link
                        href={`/action-items/${item.id}`}
                        className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
                        onClick={() => setOpen(false)}
                    >
                        <Eye className="w-4 h-4" />
                        View Details
                    </Link>
                    <div className="border-t border-neutral-100 my-1" />
                    {/* Quick status changes */}
                    {item.status !== 'completed' && (
                        <button
                            className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-emerald-600 hover:bg-emerald-50 transition-colors"
                            onClick={() => action(() => onUpdate(item.id, { status: 'completed' }))}
                        >
                            <CheckCircle2 className="w-4 h-4" />
                            Mark Complete
                        </button>
                    )}
                    {item.status === 'pending' && (
                        <button
                            className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 transition-colors"
                            onClick={() => action(() => onUpdate(item.id, { status: 'in_progress' }))}
                        >
                            <RotateCcw className="w-4 h-4" />
                            Start Progress
                        </button>
                    )}

                    {/* Edit */}
                    {onEdit && (
                        <button
                            className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
                            onClick={() => action(() => onEdit(item))}
                        >
                            <Edit2 className="w-4 h-4" />
                            Edit
                        </button>
                    )}

                    {/* AI accept/reject */}
                    {item.is_ai_generated && item.status !== 'cancelled' && (
                        <>
                            <div className="border-t border-neutral-100 my-1" />
                            {onAccept && (
                                <button
                                    className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-primary hover:bg-primary/5 transition-colors"
                                    onClick={() => action(() => onAccept(item.id))}
                                >
                                    <ThumbsUp className="w-4 h-4" />
                                    Accept AI Item
                                </button>
                            )}
                            {onReject && (
                                <button
                                    className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-amber-600 hover:bg-amber-50 transition-colors"
                                    onClick={() => action(() => onReject(item.id))}
                                >
                                    <ThumbsDown className="w-4 h-4" />
                                    Reject AI Item
                                </button>
                            )}
                        </>
                    )}

                    <div className="border-t border-neutral-100 my-1" />
                    <button
                        className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-rose-600 hover:bg-rose-50 transition-colors"
                        onClick={() => action(() => onDelete(item.id))}
                    >
                        <Trash2 className="w-4 h-4" />
                        Delete
                    </button>
                </div>
            )}
        </div>
    );
};
