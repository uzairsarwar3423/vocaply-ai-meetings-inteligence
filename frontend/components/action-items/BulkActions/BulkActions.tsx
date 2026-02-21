// BulkActions toolbar — appears when items are selected
'use client';

import React from 'react';
import { ActionItemStatus } from '@/types/action-item';
import { CheckCircle2, RotateCcw, Clock, Trash2, X } from 'lucide-react';

interface BulkActionsProps {
    selectedCount: number;
    totalCount: number;
    onSelectAll: () => void;
    onClearSelection: () => void;
    onBulkStatus: (status: ActionItemStatus) => void;
    onBulkDelete: () => void;
}

export const BulkActions: React.FC<BulkActionsProps> = ({
    selectedCount,
    totalCount,
    onSelectAll,
    onClearSelection,
    onBulkStatus,
    onBulkDelete,
}) => {
    if (selectedCount === 0) return null;

    return (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 animate-in slide-in-from-bottom-4 duration-200">
            <div className="bg-neutral-900 text-white rounded-2xl shadow-2xl px-5 py-3 flex items-center gap-4">
                {/* Selected count + clear */}
                <div className="flex items-center gap-2">
                    <span className="w-6 h-6 bg-primary rounded-full flex items-center justify-center text-[11px] font-black">
                        {selectedCount}
                    </span>
                    <span className="text-sm font-semibold text-neutral-200">selected</span>
                    {selectedCount < totalCount && (
                        <button
                            onClick={onSelectAll}
                            className="text-xs text-neutral-400 hover:text-white underline transition-colors"
                        >
                            Select all {totalCount}
                        </button>
                    )}
                </div>

                <div className="w-px h-6 bg-neutral-700" />

                {/* Status actions */}
                <div className="flex items-center gap-2">
                    <button
                        id="bulk-mark-pending"
                        onClick={() => onBulkStatus('pending')}
                        className="flex items-center gap-1.5 text-xs font-semibold bg-amber-500/15 text-amber-400 hover:bg-amber-500/25 px-3 py-1.5 rounded-lg transition-all"
                    >
                        <Clock className="w-3.5 h-3.5" />
                        Pending
                    </button>
                    <button
                        id="bulk-mark-in-progress"
                        onClick={() => onBulkStatus('in_progress')}
                        className="flex items-center gap-1.5 text-xs font-semibold bg-blue-500/15 text-blue-400 hover:bg-blue-500/25 px-3 py-1.5 rounded-lg transition-all"
                    >
                        <RotateCcw className="w-3.5 h-3.5" />
                        In Progress
                    </button>
                    <button
                        id="bulk-mark-complete"
                        onClick={() => onBulkStatus('completed')}
                        className="flex items-center gap-1.5 text-xs font-semibold bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 px-3 py-1.5 rounded-lg transition-all"
                    >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Complete
                    </button>

                    <div className="w-px h-5 bg-neutral-700" />

                    <button
                        id="bulk-delete"
                        onClick={onBulkDelete}
                        className="flex items-center gap-1.5 text-xs font-semibold bg-rose-500/15 text-rose-400 hover:bg-rose-500/25 px-3 py-1.5 rounded-lg transition-all"
                    >
                        <Trash2 className="w-3.5 h-3.5" />
                        Delete
                    </button>
                </div>

                <div className="w-px h-6 bg-neutral-700" />

                {/* Close */}
                <button
                    onClick={onClearSelection}
                    className="text-neutral-400 hover:text-white transition-colors"
                >
                    <X className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
};
