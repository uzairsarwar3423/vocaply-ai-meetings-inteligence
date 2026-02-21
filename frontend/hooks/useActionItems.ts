// useActionItems hook
// Vocaply Platform - Day 11
'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { ActionItem, ActionItemFilters, ActionItemUpdate, PaginationMeta } from '@/types/action-item';
import { actionItemsApi } from '@/lib/api/action-items';

const DEFAULT_FILTERS: ActionItemFilters = {
    search: '',
    status: 'all',
    priority: 'all',
    assignee_id: 'all',
    meeting_id: 'all',
    is_ai_generated: 'all',
};

interface UseActionItemsReturn {
    items: ActionItem[];
    pagination: PaginationMeta | null;
    isLoading: boolean;
    error: string | null;
    filters: ActionItemFilters;
    setFilters: (f: Partial<ActionItemFilters>) => void;
    resetFilters: () => void;
    page: number;
    setPage: (p: number) => void;
    sortBy: string;
    setSortBy: (s: string) => void;
    sortDir: 'asc' | 'desc';
    setSortDir: (d: 'asc' | 'desc') => void;
    refetch: () => void;
    updateItem: (id: string, data: ActionItemUpdate) => Promise<void>;
    deleteItem: (id: string) => Promise<void>;
    acceptItem: (id: string) => Promise<void>;
    rejectItem: (id: string) => Promise<void>;
    bulkDelete: (ids: string[]) => Promise<void>;
    bulkUpdateStatus: (ids: string[], status: ActionItem['status']) => Promise<void>;
    selectedIds: Set<string>;
    toggleSelect: (id: string) => void;
    selectAll: () => void;
    clearSelection: () => void;
}

export function useActionItems(initialMeetingId?: string): UseActionItemsReturn {
    const [items, setItems] = useState<ActionItem[]>([]);
    const [pagination, setPagination] = useState<PaginationMeta | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filters, setFiltersState] = useState<ActionItemFilters>({
        ...DEFAULT_FILTERS,
        meeting_id: initialMeetingId || 'all',
    });
    const [page, setPage] = useState(1);
    const [sortBy, setSortBy] = useState('created_at');
    const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const fetchItems = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const params: Record<string, any> = {
                page,
                per_page: 20,
                sort_by: sortBy,
                sort_dir: sortDir,
            };
            if (filters.search) params.search = filters.search;
            if (filters.status !== 'all') params.status = filters.status;
            if (filters.priority !== 'all') params.priority = filters.priority;
            if (filters.assignee_id !== 'all') params.assignee_id = filters.assignee_id;
            if (filters.meeting_id !== 'all') params.meeting_id = filters.meeting_id;
            if (filters.is_ai_generated !== 'all') params.is_ai_generated = filters.is_ai_generated;

            const result = await actionItemsApi.list(params);
            setItems(result.data);
            setPagination(result.pagination);
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Failed to load action items');
        } finally {
            setIsLoading(false);
        }
    }, [filters, page, sortBy, sortDir]);

    // Debounce on search change
    useEffect(() => {
        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => {
            fetchItems();
        }, filters.search ? 400 : 0);
        return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
    }, [fetchItems]);

    const setFilters = useCallback((f: Partial<ActionItemFilters>) => {
        setFiltersState(prev => ({ ...prev, ...f }));
        setPage(1); // Reset to first page on filter change
    }, []);

    const resetFilters = useCallback(() => {
        setFiltersState(DEFAULT_FILTERS);
        setPage(1);
    }, []);

    // ── CRUD ────────────────────────────────────────────────────────
    const updateItem = useCallback(async (id: string, data: ActionItemUpdate) => {
        const updated = await actionItemsApi.update(id, data);
        setItems(prev => prev.map(item => item.id === id ? updated : item));
    }, []);

    const deleteItem = useCallback(async (id: string) => {
        await actionItemsApi.delete(id);
        setItems(prev => prev.filter(item => item.id !== id));
        setSelectedIds(prev => { const next = new Set(prev); next.delete(id); return next; });
    }, []);

    const acceptItem = useCallback(async (id: string) => {
        const updated = await actionItemsApi.accept(id);
        setItems(prev => prev.map(item => item.id === id ? updated : item));
    }, []);

    const rejectItem = useCallback(async (id: string) => {
        const updated = await actionItemsApi.reject(id);
        setItems(prev => prev.map(item => item.id === id ? updated : item));
    }, []);

    // ── BULK OPERATIONS ───────────────────────────────────────────────
    const bulkDelete = useCallback(async (ids: string[]) => {
        await Promise.all(ids.map(id => actionItemsApi.delete(id)));
        setItems(prev => prev.filter(item => !ids.includes(item.id)));
        setSelectedIds(new Set());
    }, []);

    const bulkUpdateStatus = useCallback(async (ids: string[], status: ActionItem['status']) => {
        const updated = await Promise.all(
            ids.map(id => actionItemsApi.update(id, { status }))
        );
        const updatedMap = new Map(updated.map(u => [u.id, u]));
        setItems(prev => prev.map(item => updatedMap.get(item.id) || item));
        setSelectedIds(new Set());
    }, []);

    // ── SELECTION ─────────────────────────────────────────────────────
    const toggleSelect = useCallback((id: string) => {
        setSelectedIds(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id); else next.add(id);
            return next;
        });
    }, []);

    const selectAll = useCallback(() => {
        setSelectedIds(new Set(items.map(i => i.id)));
    }, [items]);

    const clearSelection = useCallback(() => {
        setSelectedIds(new Set());
    }, []);

    return {
        items, pagination, isLoading, error,
        filters, setFilters, resetFilters,
        page, setPage,
        sortBy, setSortBy,
        sortDir, setSortDir,
        refetch: fetchItems,
        updateItem, deleteItem, acceptItem, rejectItem,
        bulkDelete, bulkUpdateStatus,
        selectedIds, toggleSelect, selectAll, clearSelection,
    };
}
