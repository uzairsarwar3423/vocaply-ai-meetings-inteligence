// StatusBadge for Action Items
import React from 'react';
import { ActionItemStatus } from '@/types/action-item';
import { Clock, RotateCcw, CheckCircle2, XCircle } from 'lucide-react';

interface StatusBadgeProps {
    status: ActionItemStatus;
    size?: 'sm' | 'md';
}

const CONFIG: Record<ActionItemStatus, {
    label: string;
    classes: string;
    dot: string;
    Icon: React.FC<{ className?: string }>;
}> = {
    pending: {
        label: 'Pending',
        classes: 'bg-amber-50 text-amber-700 border-amber-200',
        dot: 'bg-amber-400',
        Icon: Clock,
    },
    in_progress: {
        label: 'In Progress',
        classes: 'bg-blue-50 text-blue-700 border-blue-200',
        dot: 'bg-blue-500',
        Icon: RotateCcw,
    },
    completed: {
        label: 'Completed',
        classes: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        dot: 'bg-emerald-500',
        Icon: CheckCircle2,
    },
    cancelled: {
        label: 'Cancelled',
        classes: 'bg-neutral-100 text-neutral-500 border-neutral-200',
        dot: 'bg-neutral-400',
        Icon: XCircle,
    },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
    const cfg = CONFIG[status] ?? CONFIG.pending;
    const { Icon } = cfg;

    return (
        <span
            className={`inline-flex items-center gap-1.5 border font-semibold rounded-full ${cfg.classes} ${size === 'sm' ? 'text-[10px] px-2 py-0.5' : 'text-xs px-2.5 py-1'
                }`}
        >
            <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
            {cfg.label}
        </span>
    );
};
