// FilterChips — active filter chip pills
'use client';

import React from 'react';
import { ActionItemFilters } from '@/types/action-item';
import { X } from 'lucide-react';

interface FilterChipsProps {
    filters: ActionItemFilters;
    onChange: (f: Partial<ActionItemFilters>) => void;
}

interface Chip {
    key: keyof ActionItemFilters;
    label: string;
    value: any;
    defaultValue: any;
}

export const FilterChips: React.FC<FilterChipsProps> = ({ filters, onChange }) => {
    const chips: Chip[] = (
        [
            { key: 'search' as keyof ActionItemFilters, label: `"${filters.search}"`, value: filters.search, defaultValue: '' },
            { key: 'status' as keyof ActionItemFilters, label: `Status: ${filters.status}`, value: filters.status, defaultValue: 'all' },
            { key: 'priority' as keyof ActionItemFilters, label: `Priority: ${filters.priority}`, value: filters.priority, defaultValue: 'all' },
            {
                key: 'is_ai_generated' as keyof ActionItemFilters,
                label: filters.is_ai_generated === true ? '🤖 AI only' : '✏️ Manual only',
                value: filters.is_ai_generated,
                defaultValue: 'all',
            },
        ]
    ).filter((c): c is Chip => Boolean(c.value) && c.value !== c.defaultValue);

    if (chips.length === 0) return null;

    return (
        <div className="flex flex-wrap gap-2 mt-2">
            {chips.map(chip => (
                <button
                    key={chip.key}
                    onClick={() => onChange({ [chip.key]: chip.defaultValue } as Partial<ActionItemFilters>)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold bg-primary/8 text-primary border border-primary/20 pl-3 pr-2 py-1 rounded-full hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-all group"
                >
                    {chip.label}
                    <X className="w-3 h-3 opacity-60 group-hover:opacity-100" />
                </button>
            ))}
        </div>
    );
};
