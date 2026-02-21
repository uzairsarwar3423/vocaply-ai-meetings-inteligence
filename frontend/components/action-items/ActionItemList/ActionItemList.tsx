// ActionItemList — paginated list view
'use client';

import React from 'react';
import { ActionItem, ActionItemUpdate } from '@/types/action-item';
import { ActionItemCard } from '../ActionItemCard/ActionItemCard';
import { ListX } from 'lucide-react';

interface ActionItemListProps {
    items: ActionItem[];
    selectedIds: Set<string>;
    onToggleSelect: (id: string) => void;
    onSelectAll: () => void;
    onUpdate: (id: string, data: ActionItemUpdate) => void;
    onDelete: (id: string) => void;
    onAccept?: (id: string) => void;
    onReject?: (id: string) => void;
    isLoading?: boolean;
}

const SkeletonRow = () => (
    <div className="bg-white rounded-2xl border border-neutral-100 flex items-center gap-4 px-5 py-3.5 animate-pulse">
        <div className="w-4 h-4 bg-neutral-100 rounded" />
        <div className="w-5 h-5 bg-neutral-100 rounded-full" />
        <div className="flex-1 h-4 bg-neutral-100 rounded-lg" />
        <div className="w-16 h-5 bg-neutral-100 rounded-full" />
        <div className="w-20 h-5 bg-neutral-100 rounded-full" />
        <div className="w-14 h-5 bg-neutral-100 rounded-full" />
        <div className="w-7 h-7 bg-neutral-100 rounded-full" />
    </div>
);

export const ActionItemList: React.FC<ActionItemListProps> = ({
    items,
    selectedIds,
    onToggleSelect,
    onSelectAll,
    onUpdate,
    onDelete,
    onAccept,
    onReject,
    isLoading,
}) => {
    if (isLoading) {
        return (
            <div className="space-y-2">
                {Array.from({ length: 6 }).map((_, i) => <SkeletonRow key={i} />)}
            </div>
        );
    }

    if (items.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="w-16 h-16 rounded-2xl bg-neutral-100 flex items-center justify-center mb-4">
                    <ListX className="w-8 h-8 text-neutral-300" />
                </div>
                <h3 className="font-bold text-neutral-600 mb-1">No action items found</h3>
                <p className="text-sm text-neutral-400 max-w-xs">
                    Try adjusting your filters, or run AI analysis on a meeting to extract action items automatically.
                </p>
            </div>
        );
    }

    const allSelected = items.length > 0 && items.every(i => selectedIds.has(i.id));

    return (
        <div className="flex flex-col gap-1.5">
            {/* List header */}
            <div className="flex items-center gap-4 px-5 py-2 text-[11px] font-bold text-neutral-400 uppercase tracking-wide">
                <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={onSelectAll}
                    className="w-4 h-4 rounded accent-primary cursor-pointer"
                />
                <span className="w-5" /> {/* complete btn spacer */}
                <span className="flex-1">Title</span>
                <span className="w-16">Priority</span>
                <span className="w-20">Status</span>
                <span className="w-16">Due</span>
                <span className="w-7">Who</span>
                <span className="w-7" />
                <span className="w-4" />
            </div>

            {items.map(item => (
                <ActionItemCard
                    key={item.id}
                    item={item}
                    viewMode="list"
                    isSelected={selectedIds.has(item.id)}
                    onToggleSelect={onToggleSelect}
                    onUpdate={onUpdate}
                    onDelete={onDelete}
                    onAccept={onAccept}
                    onReject={onReject}
                />
            ))}
        </div>
    );
};
