// Action Items Page
// Day 11: Kanban board + list view
'use client';

import React, { useState } from 'react';
import { useActionItems } from '@/hooks/useActionItems';
import { KanbanBoard } from '@/components/action-items/KanbanBoard/KanbanBoard';
import { ActionItemList } from '@/components/action-items/ActionItemList/ActionItemList';
import { ActionItemFilters } from '@/components/action-items/Filters/ActionItemFilters';
import { FilterChips } from '@/components/action-items/Filters/FilterChips';
import { BulkActions } from '@/components/action-items/BulkActions/BulkActions';
import {
    LayoutGrid, List, RefreshCw, ChevronLeft, ChevronRight,
    CheckSquare, Clock, RotateCcw, TrendingUp, Brain,
    ArrowUpDown, ArrowUp, ArrowDown,
} from 'lucide-react';

// ── Sort control ───────────────────────────────────────────────────
const SORT_OPTIONS = [
    { value: 'created_at', label: 'Created Date' },
    { value: 'due_date', label: 'Due Date' },
    { value: 'priority', label: 'Priority' },
    { value: 'updated_at', label: 'Last Updated' },
];

// ── Summary stat card ─────────────────────────────────────────────
function StatCard({
    label, value, Icon, colorClass, bgClass,
}: {
    label: string;
    value: number;
    Icon: React.FC<{ className?: string }>;
    colorClass: string;
    bgClass: string;
}) {
    return (
        <div className="bg-white rounded-2xl border border-neutral-100 p-4 flex items-center gap-3.5 shadow-sm hover:shadow-md transition-shadow">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${bgClass}`}>
                <Icon className={`w-5 h-5 ${colorClass}`} />
            </div>
            <div>
                <p className="text-2xl font-black text-neutral-800 leading-none">{value}</p>
                <p className="text-xs text-neutral-500 font-medium mt-0.5">{label}</p>
            </div>
        </div>
    );
}

// ── Page ───────────────────────────────────────────────────────────
export default function ActionItemsPage() {
    const [viewMode, setViewMode] = useState<'kanban' | 'list'>('kanban');

    const {
        items,
        pagination,
        isLoading,
        error,
        filters,
        setFilters,
        resetFilters,
        page,
        setPage,
        sortBy,
        setSortBy,
        sortDir,
        setSortDir,
        refetch,
        updateItem,
        deleteItem,
        acceptItem,
        rejectItem,
        bulkDelete,
        bulkUpdateStatus,
        selectedIds,
        toggleSelect,
        selectAll,
        clearSelection,
    } = useActionItems();

    // ── Derived stats from current page ────────────────────────────
    const stats = {
        pending: items.filter(i => i.status === 'pending').length,
        in_progress: items.filter(i => i.status === 'in_progress').length,
        completed: items.filter(i => i.status === 'completed').length,
        ai_items: items.filter(i => i.is_ai_generated).length,
    };

    const handleSortToggle = (field: string) => {
        if (sortBy === field) {
            setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(field);
            setSortDir('desc');
        }
    };

    const SortIcon = sortDir === 'asc' ? ArrowUp : ArrowDown;

    return (
        <div className="flex flex-col gap-6 pb-24">
            {/* ── Header ─────────────────────────── */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-black font-outfit text-neutral-900">Action Items</h1>
                    <p className="text-sm text-neutral-500 mt-0.5">
                        Track and manage tasks extracted from your meetings
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    {/* Refresh */}
                    <button
                        id="action-items-refresh"
                        onClick={refetch}
                        disabled={isLoading}
                        className="h-9 w-9 flex items-center justify-center rounded-xl border border-neutral-200 text-neutral-500 hover:text-primary hover:border-primary/30 hover:bg-primary/5 transition-all disabled:opacity-40"
                        title="Refresh"
                    >
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </button>

                    {/* View toggle */}
                    <div className="flex bg-neutral-100 rounded-xl p-1 gap-0.5">
                        <button
                            id="view-kanban"
                            onClick={() => setViewMode('kanban')}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold transition-all ${viewMode === 'kanban'
                                ? 'bg-white text-primary shadow-sm'
                                : 'text-neutral-500 hover:text-neutral-700'
                                }`}
                        >
                            <LayoutGrid className="w-4 h-4" />
                            Kanban
                        </button>
                        <button
                            id="view-list"
                            onClick={() => setViewMode('list')}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold transition-all ${viewMode === 'list'
                                ? 'bg-white text-primary shadow-sm'
                                : 'text-neutral-500 hover:text-neutral-700'
                                }`}
                        >
                            <List className="w-4 h-4" />
                            List
                        </button>
                    </div>
                </div>
            </div>

            {/* ── Stats row ──────────────────────── */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <StatCard label="Pending" value={stats.pending} Icon={Clock}
                    colorClass="text-amber-600" bgClass="bg-amber-50" />
                <StatCard label="In Progress" value={stats.in_progress} Icon={RotateCcw}
                    colorClass="text-blue-600" bgClass="bg-blue-50" />
                <StatCard label="Completed" value={stats.completed} Icon={CheckSquare}
                    colorClass="text-emerald-600" bgClass="bg-emerald-50" />
                <StatCard label="AI Generated" value={stats.ai_items} Icon={Brain}
                    colorClass="text-primary" bgClass="bg-primary/10" />
            </div>

            {/* ── Filters ────────────────────────── */}
            <div>
                <ActionItemFilters
                    filters={filters}
                    onChange={setFilters}
                    onReset={resetFilters}
                    totalCount={pagination?.total_items ?? items.length}
                    filteredCount={items.length}
                />
                <FilterChips filters={filters} onChange={setFilters} />
            </div>

            {/* ── Sort bar (list view only) ───────── */}
            {viewMode === 'list' && (
                <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold text-neutral-400 uppercase tracking-wide">Sort by:</span>
                    {SORT_OPTIONS.map(opt => (
                        <button
                            key={opt.value}
                            onClick={() => handleSortToggle(opt.value)}
                            className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-all ${sortBy === opt.value
                                ? 'bg-primary/10 text-primary border-primary/20'
                                : 'bg-white text-neutral-500 border-neutral-200 hover:border-primary/30 hover:text-primary'
                                }`}
                        >
                            {opt.label}
                            {sortBy === opt.value && <SortIcon className="w-3 h-3" />}
                        </button>
                    ))}
                </div>
            )}

            {/* ── Error ──────────────────────────── */}
            {error && (
                <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-sm text-rose-600 font-medium">
                    {error}
                </div>
            )}

            {/* ── Main content ─────────────────────── */}
            {viewMode === 'kanban' ? (
                <KanbanBoard
                    items={items}
                    selectedIds={selectedIds}
                    onToggleSelect={toggleSelect}
                    onUpdate={updateItem}
                    onDelete={deleteItem}
                    onAccept={acceptItem}
                    onReject={rejectItem}
                />
            ) : (
                <ActionItemList
                    items={items}
                    selectedIds={selectedIds}
                    onToggleSelect={toggleSelect}
                    onSelectAll={selectAll}
                    onUpdate={updateItem}
                    onDelete={deleteItem}
                    onAccept={acceptItem}
                    onReject={rejectItem}
                    isLoading={isLoading}
                />
            )}

            {/* ── Pagination (list view) ────────── */}
            {viewMode === 'list' && pagination && pagination.total_pages > 1 && (
                <div className="flex items-center justify-between mt-2">
                    <p className="text-sm text-neutral-500">
                        Page <span className="font-bold text-neutral-700">{pagination.page}</span> of {pagination.total_pages}
                        {' · '}
                        <span className="font-bold text-neutral-700">{pagination.total_items}</span> total
                    </p>

                    <div className="flex items-center gap-2">
                        <button
                            id="action-items-prev-page"
                            disabled={!pagination.has_prev}
                            onClick={() => setPage(page - 1)}
                            className="h-9 px-3 flex items-center gap-1.5 text-sm font-semibold rounded-xl border border-neutral-200 text-neutral-600 hover:border-primary/30 hover:text-primary disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                        >
                            <ChevronLeft className="w-4 h-4" />
                            Prev
                        </button>

                        {/* Page numbers */}
                        {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                            const p = Math.max(1, Math.min(
                                pagination.total_pages - 4,
                                pagination.page - 2
                            )) + i;
                            return (
                                <button
                                    key={p}
                                    onClick={() => setPage(p)}
                                    className={`w-9 h-9 rounded-xl text-sm font-bold transition-all ${p === pagination.page
                                        ? 'bg-primary text-white shadow-md shadow-primary/25'
                                        : 'border border-neutral-200 text-neutral-600 hover:border-primary/30 hover:text-primary'
                                        }`}
                                >
                                    {p}
                                </button>
                            );
                        })}

                        <button
                            id="action-items-next-page"
                            disabled={!pagination.has_next}
                            onClick={() => setPage(page + 1)}
                            className="h-9 px-3 flex items-center gap-1.5 text-sm font-semibold rounded-xl border border-neutral-200 text-neutral-600 hover:border-primary/30 hover:text-primary disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                        >
                            Next
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}

            {/* ── Bulk action floating bar ──────── */}
            <BulkActions
                selectedCount={selectedIds.size}
                totalCount={items.length}
                onSelectAll={selectAll}
                onClearSelection={clearSelection}
                onBulkStatus={status => bulkUpdateStatus([...selectedIds], status)}
                onBulkDelete={() => bulkDelete([...selectedIds])}
            />
        </div>
    );
}
