// KanbanColumn — single status column
'use client';

import React from 'react';
import { ActionItem, ActionItemStatus, ActionItemUpdate } from '@/types/action-item';
import { ActionItemCard } from '../ActionItemCard/ActionItemCard';
import { LucideIcon } from 'lucide-react';

interface KanbanColumnProps {
    id: ActionItemStatus;
    title: string;
    icon: LucideIcon;
    items: ActionItem[];
    colorClass: string;
    dotColor: string;
    isOver: boolean;
    onDragOver: (e: React.DragEvent) => void;
    onDragLeave: () => void;
    onDrop: (e: React.DragEvent) => void;
    onDragStart: (e: React.DragEvent, itemId: string) => void;
    onDragEnd: () => void;
    onUpdate: (id: string, data: ActionItemUpdate) => void;
    onDelete: (id: string) => void;
    onAccept?: (id: string) => void;
    onReject?: (id: string) => void;
    selectedIds: Set<string>;
    onToggleSelect: (id: string) => void;
}

export const KanbanColumn: React.FC<KanbanColumnProps> = ({
    id, title, icon: Icon, items, colorClass, dotColor,
    isOver, onDragOver, onDragLeave, onDrop,
    onDragStart, onDragEnd,
    onUpdate, onDelete, onAccept, onReject,
    selectedIds, onToggleSelect,
}) => {
    return (
        <div
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            className={`flex flex-col min-h-[200px] rounded-2xl border-2 transition-all duration-200 ${isOver
                ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10 scale-[1.01]'
                : 'border-transparent bg-neutral-50/80'
                }`}
        >
            {/* Column header */}
            <div className="flex items-center gap-2.5 px-4 py-3.5 border-b border-neutral-100">
                <Icon className="w-5 h-5 text-neutral-500" />
                <div className="flex items-center gap-2 flex-1">
                    <span className={`w-2 h-2 rounded-full ${dotColor}`} />
                    <h3 className="font-bold text-sm text-neutral-700">{title}</h3>
                </div>
                <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${colorClass}`}>
                    {items.length}
                </span>
            </div>

            {/* Cards */}
            <div className="flex-1 p-3 space-y-2.5 overflow-y-auto max-h-[calc(100vh-280px)]">
                {items.length === 0 ? (
                    <div className={`h-20 rounded-xl border-2 border-dashed flex items-center justify-center transition-all ${isOver ? 'border-primary/40 bg-primary/5' : 'border-neutral-200'
                        }`}>
                        <p className="text-xs text-neutral-400 font-medium">
                            {isOver ? 'Drop here' : 'No items'}
                        </p>
                    </div>
                ) : (
                    items.map(item => (
                        <ActionItemCard
                            key={item.id}
                            item={item}
                            viewMode="kanban"
                            draggable
                            isSelected={selectedIds.has(item.id)}
                            onToggleSelect={onToggleSelect}
                            onUpdate={onUpdate}
                            onDelete={onDelete}
                            onAccept={onAccept}
                            onReject={onReject}
                            onDragStart={e => onDragStart(e, item.id)}
                            onDragEnd={onDragEnd}
                        />
                    ))
                )}
            </div>
        </div>
    );
};
