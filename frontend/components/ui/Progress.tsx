'use client';

import * as React from 'react';

interface ProgressProps {
    value?: number;
    max?: number;
    className?: string;
}

export function Progress({ value = 0, max = 100, className = '' }: ProgressProps) {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

    return (
        <div
            className={`relative h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800 ${className}`}
        >
            <div
                className="h-full w-full flex-1 bg-green-500 transition-all duration-300"
                style={{ transform: `translateX(-${100 - percentage}%)` }}
            />
        </div>
    );
}
