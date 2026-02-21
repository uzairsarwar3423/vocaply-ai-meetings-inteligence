// Priority Badge component
import React from 'react';
import { ActionItemPriority } from '@/types/action-item';
import { Signal, Zap } from 'lucide-react';

interface PriorityBadgeProps {
    priority: ActionItemPriority;
    size?: 'sm' | 'md';
}

const CONFIG: Record<ActionItemPriority, {
    label: string;
    classes: string;
    barColors: [string, string, string];  // 3 bars, filled count
    filled: number;
}> = {
    low: {
        label: 'Low',
        classes: 'text-slate-500',
        barColors: ['bg-slate-300', 'bg-slate-200', 'bg-slate-200'],
        filled: 1,
    },
    medium: {
        label: 'Medium',
        classes: 'text-amber-600',
        barColors: ['bg-amber-400', 'bg-amber-400', 'bg-amber-200'],
        filled: 2,
    },
    high: {
        label: 'High',
        classes: 'text-orange-600',
        barColors: ['bg-orange-500', 'bg-orange-500', 'bg-orange-500'],
        filled: 3,
    },
    urgent: {
        label: 'Urgent',
        classes: 'text-rose-600',
        barColors: ['bg-rose-500', 'bg-rose-500', 'bg-rose-500'],
        filled: 3,
    },
};

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority, size = 'md' }) => {
    const cfg = CONFIG[priority] ?? CONFIG.medium;
    const isUrgent = priority === 'urgent';

    return (
        <span className={`inline-flex items-center gap-1.5 font-semibold ${cfg.classes} ${size === 'sm' ? 'text-[10px]' : 'text-xs'
            }`}>
            {isUrgent ? (
                <Zap className={`${size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} fill-current`} />
            ) : (
                <span className="flex items-end gap-px">
                    {cfg.barColors.map((color, i) => (
                        <span
                            key={i}
                            className={`${color} rounded-sm ${size === 'sm' ? 'w-[3px]' : 'w-1'}`}
                            style={{ height: `${(i + 1) * (size === 'sm' ? 3 : 4)}px` }}
                        />
                    ))}
                </span>
            )}
            {cfg.label}
        </span>
    );
};
