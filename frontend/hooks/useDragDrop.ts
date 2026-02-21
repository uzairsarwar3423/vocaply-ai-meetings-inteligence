// useDragDrop hook — for Kanban column drag-and-drop
// Vocaply Platform - Day 11
'use client';

import { useState, useCallback } from 'react';
import { ActionItem } from '@/types/action-item';

export interface DragState {
    draggedId: string | null;
    overColumnId: string | null;
}

interface UseDragDropReturn {
    dragState: DragState;
    handleDragStart: (e: React.DragEvent, itemId: string) => void;
    handleDragOver: (e: React.DragEvent, columnId: string) => void;
    handleDragLeave: () => void;
    handleDrop: (e: React.DragEvent, columnId: string, onStatusChange: (id: string, status: ActionItem['status']) => void) => void;
    handleDragEnd: () => void;
    isDragging: boolean;
    isOverColumn: (columnId: string) => boolean;
}

export function useDragDrop(): UseDragDropReturn {
    const [dragState, setDragState] = useState<DragState>({
        draggedId: null,
        overColumnId: null,
    });

    const handleDragStart = useCallback((e: React.DragEvent, itemId: string) => {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', itemId);
        setDragState(prev => ({ ...prev, draggedId: itemId }));
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent, columnId: string) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        setDragState(prev =>
            prev.overColumnId !== columnId ? { ...prev, overColumnId: columnId } : prev
        );
    }, []);

    const handleDragLeave = useCallback(() => {
        setDragState(prev => ({ ...prev, overColumnId: null }));
    }, []);

    const handleDrop = useCallback(
        (
            e: React.DragEvent,
            columnId: string,
            onStatusChange: (id: string, status: ActionItem['status']) => void
        ) => {
            e.preventDefault();
            const itemId = e.dataTransfer.getData('text/plain');
            if (itemId && columnId) {
                onStatusChange(itemId, columnId as ActionItem['status']);
            }
            setDragState({ draggedId: null, overColumnId: null });
        },
        []
    );

    const handleDragEnd = useCallback(() => {
        setDragState({ draggedId: null, overColumnId: null });
    }, []);

    const isOverColumn = useCallback(
        (columnId: string) => dragState.overColumnId === columnId,
        [dragState.overColumnId]
    );

    return {
        dragState,
        handleDragStart,
        handleDragOver,
        handleDragLeave,
        handleDrop,
        handleDragEnd,
        isDragging: dragState.draggedId !== null,
        isOverColumn,
    };
}
