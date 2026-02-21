// Action Item Detail Page
// Vocaply Platform - Day 12
// Path: app/(dashboard)/action-items/[id]/page.tsx
'use client';

import React, { useEffect, useState, use } from 'react';
import { ActionItemDetail } from '@/components/action-items/ActionItemDetail';
import { actionItemsApi } from '@/lib/api/action-items';
import { ActionItem, ActionItemUpdate } from '@/types/action-item';

interface Params {
    id: string;
}

export default function ActionItemDetailPage({ params }: { params: Promise<Params> }) {
    const { id } = use(params);

    const [item, setItem] = useState<ActionItem | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch the action item on mount
    useEffect(() => {
        if (!id) return;
        let cancelled = false;
        const fetch = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const data = await actionItemsApi.get(id);
                if (!cancelled) setItem(data);
            } catch (err: any) {
                if (!cancelled) {
                    setError(
                        err?.response?.status === 404
                            ? 'Action item not found or you don\'t have permission to view it.'
                            : err?.response?.data?.detail || 'Failed to load action item.'
                    );
                }
            } finally {
                if (!cancelled) setIsLoading(false);
            }
        };
        fetch();
        return () => { cancelled = true; };
    }, [id]);

    // Optimistic update handler
    const handleUpdate = async (itemId: string, data: ActionItemUpdate) => {
        // Optimistic local update - exclude null values that don't match ActionItem types
        const optimisticPatch: Partial<ActionItem> = {
            ...data,
            // ActionItem.due_date is string | undefined, not string | null
            due_date: data.due_date === null ? undefined : data.due_date,
            updated_at: new Date().toISOString(),
        };
        setItem(prev => prev ? { ...prev, ...optimisticPatch } : prev);
        try {
            const updated = await actionItemsApi.update(itemId, data);
            setItem(updated);
        } catch (err: any) {
            // Revert on failure
            setError(err?.response?.data?.detail || 'Failed to update. Please try again.');
            // Re-fetch to restore true state
            try {
                const fresh = await actionItemsApi.get(itemId);
                setItem(fresh);
            } catch {
                // ignore
            }
        }
    };

    // Delete handler
    const handleDelete = async (itemId: string) => {
        await actionItemsApi.delete(itemId);
        // Navigation handled in ActionItemDetail component (router.push)
    };

    return (
        <div className="-m-8 min-h-full bg-neutral-50">
            {item ? (
                <ActionItemDetail
                    item={item}
                    onUpdate={handleUpdate}
                    onDelete={handleDelete}
                    isLoading={false}
                    error={error}
                />
            ) : (
                <ActionItemDetail
                    item={{} as ActionItem}
                    onUpdate={handleUpdate}
                    onDelete={handleDelete}
                    isLoading={isLoading}
                    error={error}
                />
            )}
        </div>
    );
}
