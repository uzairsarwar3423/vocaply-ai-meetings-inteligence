'use client';

import { useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle2, XCircle, Radio, Clock, AlertTriangle } from 'lucide-react';

type BotStatus =
    | 'initializing'
    | 'assigned'
    | 'joining'
    | 'in_meeting'
    | 'recording'
    | 'leaving'
    | 'completed'
    | 'failed'
    | 'terminated';

interface BotStatusProps {
    status: BotStatus;
    participantCount?: number;
    isAlone?: boolean;
    error?: string | null;
    className?: string;
}

const statusConfig: Record<BotStatus, {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    variant: 'primary' | 'secondary' | 'error' | 'neutral' | 'success'; // Fixed variants
    color: string;
}> = {
    initializing: {
        label: 'Initializing',
        icon: Loader2,
        variant: 'secondary',
        color: 'text-gray-500',
    },
    assigned: {
        label: 'Assigned',
        icon: Clock,
        variant: 'secondary',
        color: 'text-blue-500',
    },
    joining: {
        label: 'Joining',
        icon: Loader2,
        variant: 'primary',
        color: 'text-blue-500',
    },
    in_meeting: {
        label: 'In Meeting',
        icon: Radio,
        variant: 'primary',
        color: 'text-green-500',
    },
    recording: {
        label: 'Recording',
        icon: Radio,
        variant: 'primary',
        color: 'text-red-500',
    },
    leaving: {
        label: 'Leaving',
        icon: Loader2,
        variant: 'secondary',
        color: 'text-gray-500',
    },
    completed: {
        label: 'Completed',
        icon: CheckCircle2,
        variant: 'success',
        color: 'text-green-600',
    },
    failed: {
        label: 'Failed',
        icon: XCircle,
        variant: 'error',
        color: 'text-red-500',
    },
    terminated: {
        label: 'Terminated',
        icon: XCircle,
        variant: 'neutral',
        color: 'text-gray-500',
    },
};

export default function BotStatus({
    status,
    participantCount = 0,
    isAlone = false,
    error,
    className = '',
}: BotStatusProps) {
    const [isAnimating, setIsAnimating] = useState(false);
    const config = statusConfig[status];
    const Icon = config.icon;

    useEffect(() => {
        setIsAnimating(true);
        const timer = setTimeout(() => setIsAnimating(false), 300);
        return () => clearTimeout(timer);
    }, [status]);

    const isActive = ['joining', 'in_meeting', 'recording'].includes(status);
    const isLoading = ['initializing', 'joining', 'leaving'].includes(status);

    return (
        <div className={`flex items-center gap-2 ${className}`}>
            <Badge
                variant={config.variant}
                className={`
          flex items-center gap-1.5 px-3 py-1.5
          transition-all duration-300
          ${isAnimating ? 'scale-110' : 'scale-100'}
        `}
            >
                <Icon
                    className={`
            h-4 w-4 
            ${config.color}
            ${isLoading ? 'animate-spin' : ''}
            ${status === 'recording' ? 'animate-pulse' : ''}
          `}
                />
                <span className="font-medium">{config.label}</span>
            </Badge>

            {isActive && participantCount > 0 && (
                <Badge variant="neutral" className="px-2 py-1">
                    <span className="text-xs">
                        {participantCount} {participantCount === 1 ? 'participant' : 'participants'}
                    </span>
                </Badge>
            )}

            {isActive && isAlone && (
                <Badge variant="warning" className="flex items-center gap-1 px-2 py-1 border-yellow-300 bg-yellow-50">
                    <AlertTriangle className="h-3 w-3 text-yellow-600" />
                    <span className="text-xs text-yellow-700">Bot is alone</span>
                </Badge>
            )}

            {error && status === 'failed' && (
                <span className="text-xs text-red-600 max-w-xs truncate" title={error}>
                    {error}
                </span>
            )}
        </div>
    );
}