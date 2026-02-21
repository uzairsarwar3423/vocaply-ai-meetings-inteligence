// ConfidenceIndicator — visual confidence bar for AI-generated items
'use client';

import React from 'react';
import { Brain, TrendingUp } from 'lucide-react';

interface ConfidenceIndicatorProps {
    score: number; // 0 to 1
    size?: 'sm' | 'md' | 'lg';
    showLabel?: boolean;
    showIcon?: boolean;
}

function getLevel(score: number): { label: string; color: string; bg: string; bar: string; ring: string } {
    if (score >= 0.85) return {
        label: 'Very High',
        color: 'text-emerald-700',
        bg: 'bg-emerald-50',
        bar: 'bg-emerald-500',
        ring: 'ring-emerald-200',
    };
    if (score >= 0.65) return {
        label: 'High',
        color: 'text-teal-700',
        bg: 'bg-teal-50',
        bar: 'bg-teal-500',
        ring: 'ring-teal-200',
    };
    if (score >= 0.45) return {
        label: 'Medium',
        color: 'text-amber-700',
        bg: 'bg-amber-50',
        bar: 'bg-amber-500',
        ring: 'ring-amber-200',
    };
    return {
        label: 'Low',
        color: 'text-rose-700',
        bg: 'bg-rose-50',
        bar: 'bg-rose-400',
        ring: 'ring-rose-200',
    };
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
    score,
    size = 'md',
    showLabel = true,
    showIcon = true,
}) => {
    const pct = Math.round(score * 100);
    const level = getLevel(score);

    const sizeClasses = {
        sm: { wrap: 'gap-1.5 py-1 px-2', text: 'text-[10px]', bar: 'h-1', icon: 'w-3 h-3' },
        md: { wrap: 'gap-2 py-1.5 px-3', text: 'text-xs', bar: 'h-1.5', icon: 'w-3.5 h-3.5' },
        lg: { wrap: 'gap-2.5 py-2 px-4', text: 'text-sm', bar: 'h-2', icon: 'w-4 h-4' },
    }[size];

    return (
        <div
            className={`inline-flex flex-col ${sizeClasses.wrap} rounded-xl ${level.bg} ring-1 ${level.ring}`}
            title={`AI Confidence: ${pct}% (${level.label})`}
        >
            {/* Header row */}
            <div className="flex items-center justify-between gap-3">
                <div className={`flex items-center gap-1 font-semibold ${level.color} ${sizeClasses.text}`}>
                    {showIcon && <Brain className={sizeClasses.icon} />}
                    {showLabel && <span>AI Confidence</span>}
                </div>
                <div className={`flex items-center gap-0.5 font-bold ${level.color} ${sizeClasses.text}`}>
                    <TrendingUp className={`${sizeClasses.icon} opacity-60`} />
                    <span>{pct}%</span>
                </div>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-white/60 rounded-full overflow-hidden" style={{ height: sizeClasses.bar.includes('h-2') ? 8 : sizeClasses.bar.includes('h-1.5') ? 6 : 4 }}>
                <div
                    className={`${level.bar} rounded-full h-full transition-all duration-700 ease-out`}
                    style={{ width: `${pct}%` }}
                />
            </div>

            {showLabel && (
                <p className={`${sizeClasses.text} ${level.color} opacity-75 font-medium`}>{level.label} confidence</p>
            )}
        </div>
    );
};
