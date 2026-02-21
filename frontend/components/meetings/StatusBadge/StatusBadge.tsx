
import React from 'react';
import { Badge } from '@/components/ui/badge';
import { MeetingStatus } from '@/types/meeting';

interface StatusBadgeProps {
    status: MeetingStatus;
}

const statusConfig: Record<MeetingStatus, { label: string; variant: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'neutral' }> = {
    scheduled: { label: 'Scheduled', variant: 'warning' },
    completed: { label: 'Completed', variant: 'success' },
    processing: { label: 'Processing', variant: 'info' },
    live: { label: 'Live', variant: 'error' },
    failed: { label: 'Failed', variant: 'error' },
    cancelled: { label: 'Cancelled', variant: 'neutral' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
    const config = statusConfig[status];
    return (
        <Badge variant={config.variant}>
            {status === 'live' && <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 animate-pulse" />}
            {config.label}
        </Badge>
    );
};
