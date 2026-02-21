'use client';

import React, { useCallback, useRef } from 'react';
import { Search, X, ChevronDown } from 'lucide-react';
import { TranscriptFilters } from '@/types/transcript';

interface TranscriptSearchProps {
    filters: TranscriptFilters;
    onChange: (filters: TranscriptFilters) => void;
    speakers: { id: string; name: string }[];
    totalCount: number;
    filteredCount: number;
}

export default function TranscriptSearch({
    filters,
    onChange,
    speakers,
    totalCount,
    filteredCount,
}: TranscriptSearchProps) {
    const inputRef = useRef<HTMLInputElement>(null);

    const setSearch = useCallback(
        (search: string) => onChange({ ...filters, search }),
        [filters, onChange]
    );

    const setSpeaker = useCallback(
        (speaker: string) => onChange({ ...filters, speaker }),
        [filters, onChange]
    );

    const clearAll = () => onChange({ search: '', speaker: 'all' });

    const hasFilters = !!filters.search || (!!filters.speaker && filters.speaker !== 'all');

    return (
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
            {/* Search box */}
            <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 pointer-events-none" />
                <input
                    ref={inputRef}
                    type="text"
                    placeholder="Search transcript..."
                    value={filters.search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full pl-9 pr-8 py-2 text-sm bg-white border border-neutral-200 rounded-lg outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 text-neutral-700 placeholder-neutral-400 transition"
                />
                {filters.search && (
                    <button
                        onClick={() => setSearch('')}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 transition-colors"
                    >
                        <X className="w-3.5 h-3.5" />
                    </button>
                )}
            </div>

            {/* Speaker filter */}
            {speakers.length > 1 && (
                <div className="relative">
                    <select
                        value={filters.speaker || 'all'}
                        onChange={(e) => setSpeaker(e.target.value)}
                        className="appearance-none w-full sm:w-44 pl-3 pr-7 py-2 text-sm bg-white border border-neutral-200 rounded-lg outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 text-neutral-700 cursor-pointer transition"
                    >
                        <option value="all">All speakers</option>
                        {speakers.map((s) => (
                            <option key={s.id} value={s.id}>{s.name}</option>
                        ))}
                    </select>
                    <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-400 pointer-events-none" />
                </div>
            )}

            {/* Results summary + clear */}
            <div className="flex items-center gap-2 text-xs text-neutral-500 whitespace-nowrap">
                {hasFilters ? (
                    <>
                        <span>{filteredCount} / {totalCount} lines</span>
                        <button
                            onClick={clearAll}
                            className="underline hover:text-neutral-700 transition-colors"
                        >
                            Clear
                        </button>
                    </>
                ) : (
                    <span>{totalCount} lines</span>
                )}
            </div>
        </div>
    );
}
