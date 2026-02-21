// KanbanBoard — three-column board (Pending / In Progress / Completed)
'use client';

import React, { useMemo } from 'react';
import { ActionItem, ActionItemStatus, ActionItemUpdate } from '@/types/action-item';
import { KanbanColumn } from './KanbanColumn';
import { useDragDrop } from '@/hooks/useDragDrop';
import { Clock, RotateCcw, CheckCircle2, LucideIcon } from 'lucide-react';

interface KanbanBoardProps {
    items: ActionItem[];
    selectedIds: Set<string>;
    onToggleSelect: (id: string) => void;
    onUpdate: (id: string, data: ActionItemUpdate) => void;
    onDelete: (id: string) => void;
    onAccept?: (id: string) => void;
    onReject?: (id: string) => void;
}

const COLUMNS: {
    id: ActionItemStatus;
    title: string;
    icon: LucideIcon;
    colorClass: string;
    dotColor: string;
}[] = [
        {
            id: 'pending',
            title: 'Pending',
            icon: Clock,
            colorClass: 'bg-amber-100 text-amber-700',
            dotColor: 'bg-amber-400',
        },
        {
            id: 'in_progress',
            title: 'In Progress',
            icon: RotateCcw,
            colorClass: 'bg-blue-100 text-blue-700',
            dotColor: 'bg-blue-500',
        },
        {
            id: 'completed',
            title: 'Completed',
            icon: CheckCircle2,
            colorClass: 'bg-emerald-100 text-emerald-700',
            dotColor: 'bg-emerald-500',
        },
    ];

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
    items,
    selectedIds,
    onToggleSelect,
    onUpdate,
    onDelete,
    onAccept,
    onReject,
}) => {
    const {
        handleDragStart,
        handleDragOver,
        handleDragLeave,
        handleDrop,
        handleDragEnd,
        isOverColumn,
    } = useDragDrop();

    // Group items by status (exclude cancelled from the board)
    const grouped = useMemo(() => {
        const map: Record<string, ActionItem[]> = {
            pending: [],
            in_progress: [],
            completed: [],
        };
        for (const item of items) {
            if (item.status in map) {
                map[item.status].push(item);
            }
        }
        return map;
    }, [items]);

    const handleStatusChange = (id: string, newStatus: ActionItemStatus) => {
        onUpdate(id, { status: newStatus });
    };

    const cancelledCount = items.filter(i => i.status === 'cancelled').length;

    return (
        <div className="flex flex-col gap-3">
            {cancelledCount > 0 && (
                <p className="text-xs text-neutral-400 text-right font-medium">
                    {cancelledCount} cancelled item{cancelledCount > 1 ? 's' : ''} hidden
                </p>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {COLUMNS.map(col => (
                    <KanbanColumn
                        key={col.id}
                        {...col}
                        items={grouped[col.id] || []}
                        isOver={isOverColumn(col.id)}
                        onDragOver={e => handleDragOver(e, col.id)}
                        onDragLeave={handleDragLeave}
                        onDrop={e => handleDrop(e, col.id, handleStatusChange)}
                        onDragStart={handleDragStart}
                        onDragEnd={handleDragEnd}
                        onUpdate={onUpdate}
                        onDelete={onDelete}
                        onAccept={onAccept}
                        onReject={onReject}
                        selectedIds={selectedIds}
                        onToggleSelect={onToggleSelect}
                    />
                ))}
            </div>
        </div>
    );
};
