// ActionItemFilters — search + filter controls
'use client';

import React from 'react';
import { ActionItemFilters as FiltersType } from '@/types/action-item';
import { Search, X, SlidersHorizontal } from 'lucide-react';

interface ActionItemFiltersProps {
    filters: FiltersType;
    onChange: (f: Partial<FiltersType>) => void;
    onReset: () => void;
    totalCount: number;
    filteredCount: number;
}

const STATUS_OPTIONS = [
    { value: 'all', label: 'All Statuses' },
    { value: 'pending', label: 'Pending' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
];

const PRIORITY_OPTIONS = [
    { value: 'all', label: 'All Priorities' },
    { value: 'urgent', label: '⚡ Urgent' },
    { value: 'high', label: '🔴 High' },
    { value: 'medium', label: '🟡 Medium' },
    { value: 'low', label: '🟢 Low' },
];

const AI_OPTIONS = [
    { value: 'all', label: 'All Items' },
    { value: 'true', label: '🤖 AI Generated' },
    { value: 'false', label: '✏️ Manual' },
];

const selectClass =
    'h-9 pl-3 pr-8 text-sm rounded-xl border border-neutral-200 bg-white text-neutral-700 font-medium appearance-none focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all cursor-pointer';

export const ActionItemFilters: React.FC<ActionItemFiltersProps> = ({
    filters,
    onChange,
    onReset,
    totalCount,
    filteredCount,
}) => {
    const hasActiveFilters =
        filters.search ||
        filters.status !== 'all' ||
        filters.priority !== 'all' ||
        filters.is_ai_generated !== 'all';

    return (
        <div className="bg-white rounded-2xl border border-neutral-100 p-4 shadow-sm">
            <div className="flex flex-wrap items-center gap-3">
                {/* Search */}
                <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                    <input
                        id="action-items-search"
                        type="text"
                        value={filters.search}
                        onChange={e => onChange({ search: e.target.value })}
                        placeholder="Search action items…"
                        className="w-full h-9 pl-9 pr-4 text-sm rounded-xl border border-neutral-200 bg-neutral-50 text-neutral-800 placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary focus:bg-white transition-all"
                    />
                    {filters.search && (
                        <button
                            onClick={() => onChange({ search: '' })}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                        >
                            <X className="w-3.5 h-3.5" />
                        </button>
                    )}
                </div>

                {/* Status */}
                <div className="relative">
                    <select
                        id="action-items-status-filter"
                        value={filters.status}
                        onChange={e => onChange({ status: e.target.value as any })}
                        className={selectClass}
                    >
                        {STATUS_OPTIONS.map(o => (
                            <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                    </select>
                    <span className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-400">▾</span>
                </div>

                {/* Priority */}
                <div className="relative">
                    <select
                        id="action-items-priority-filter"
                        value={filters.priority}
                        onChange={e => onChange({ priority: e.target.value as any })}
                        className={selectClass}
                    >
                        {PRIORITY_OPTIONS.map(o => (
                            <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                    </select>
                    <span className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-400">▾</span>
                </div>

                {/* AI generated */}
                <div className="relative">
                    <select
                        id="action-items-ai-filter"
                        value={String(filters.is_ai_generated)}
                        onChange={e => {
                            const v = e.target.value;
                            onChange({ is_ai_generated: v === 'all' ? 'all' : v === 'true' });
                        }}
                        className={selectClass}
                    >
                        {AI_OPTIONS.map(o => (
                            <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                    </select>
                    <span className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-400">▾</span>
                </div>

                {/* Reset */}
                {hasActiveFilters && (
                    <button
                        id="action-items-reset-filters"
                        onClick={onReset}
                        className="h-9 px-3 text-sm font-medium text-neutral-500 hover:text-rose-600 flex items-center gap-1.5 rounded-xl hover:bg-rose-50 transition-all border border-neutral-200"
                    >
                        <X className="w-3.5 h-3.5" />
                        Clear
                    </button>
                )}

                {/* Count */}
                <span className="ml-auto text-xs text-neutral-400 font-medium hidden sm:block">
                    {filteredCount}{totalCount !== filteredCount ? `/${totalCount}` : ''} item{filteredCount !== 1 ? 's' : ''}
                </span>
            </div>
        </div>
    );
};
