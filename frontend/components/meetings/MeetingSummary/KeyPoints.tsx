"use client";

import React from "react";
import { MessageSquare, TrendingUp } from "lucide-react";

interface KeyPointsProps {
    points: string[];
}

export const KeyPoints: React.FC<KeyPointsProps> = ({ points }) => {
    if (!points || points.length === 0) {
        return (
            <div className="bg-white rounded-3xl border border-neutral-100 p-5 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 bg-blue-50 rounded-xl flex items-center justify-center">
                        <MessageSquare className="w-4 h-4 text-blue-500" />
                    </div>
                    <h4 className="font-bold text-neutral-800 text-sm">Key Discussion Points</h4>
                </div>
                <p className="text-xs text-neutral-400 italic">No key points extracted.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-3xl border border-neutral-100 p-5 shadow-sm h-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-50 rounded-xl flex items-center justify-center">
                        <MessageSquare className="w-4 h-4 text-blue-500" />
                    </div>
                    <h4 className="font-bold text-neutral-800 text-sm">Key Discussion Points</h4>
                </div>
                <span className="text-xs font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded-full">
                    {points.length}
                </span>
            </div>

            {/* Points */}
            <ul className="space-y-2.5">
                {points.map((point, i) => (
                    <li key={i} className="flex items-start gap-3 group">
                        <div className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 text-blue-600 text-xs font-bold flex items-center justify-center mt-0.5 group-hover:bg-blue-500 group-hover:text-white transition-all">
                            {i + 1}
                        </div>
                        <p className="text-sm text-neutral-600 leading-relaxed">{point}</p>
                    </li>
                ))}
            </ul>

            {/* Footer indicator */}
            {points.length > 5 && (
                <div className="mt-3 pt-3 border-t border-neutral-50 flex items-center gap-1.5 text-xs text-neutral-400">
                    <TrendingUp className="w-3 h-3" />
                    {points.length} discussion points identified
                </div>
            )}
        </div>
    );
};
