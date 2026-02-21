"use client";

import React from "react";
import { Tag, TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { TopicItem } from "./MeetingSummary";

interface TopicsProps {
    topics: TopicItem[];
}

const sentimentStyles = {
    positive: {
        bg: "bg-emerald-50 border-emerald-200",
        text: "text-emerald-700",
        icon: <TrendingUp className="w-3 h-3 text-emerald-500" />,
    },
    neutral: {
        bg: "bg-neutral-50 border-neutral-200",
        text: "text-neutral-600",
        icon: <Minus className="w-3 h-3 text-neutral-400" />,
    },
    negative: {
        bg: "bg-rose-50 border-rose-200",
        text: "text-rose-700",
        icon: <TrendingDown className="w-3 h-3 text-rose-500" />,
    },
};

export const Topics: React.FC<TopicsProps> = ({ topics }) => {
    if (!topics || topics.length === 0) {
        return (
            <div className="bg-white rounded-3xl border border-neutral-100 p-5 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 bg-amber-50 rounded-xl flex items-center justify-center">
                        <Tag className="w-4 h-4 text-amber-500" />
                    </div>
                    <h4 className="font-bold text-neutral-800 text-sm">Topics Discussed</h4>
                </div>
                <p className="text-xs text-neutral-400 italic">No topics identified.</p>
            </div>
        );
    }

    // Sort by importance desc
    const sorted = [...topics].sort((a, b) => (b.importance ?? 0.5) - (a.importance ?? 0.5));

    return (
        <div className="bg-white rounded-3xl border border-neutral-100 p-5 shadow-sm h-full">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-amber-50 rounded-xl flex items-center justify-center">
                        <Tag className="w-4 h-4 text-amber-500" />
                    </div>
                    <h4 className="font-bold text-neutral-800 text-sm">Topics Discussed</h4>
                </div>
                <span className="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
                    {topics.length}
                </span>
            </div>

            <div className="flex flex-wrap gap-2">
                {sorted.map((t, i) => {
                    const sentiment = (t.sentiment ?? "neutral") as keyof typeof sentimentStyles;
                    const style = sentimentStyles[sentiment] ?? sentimentStyles.neutral;
                    const width = Math.max(20, Math.round((t.importance ?? 0.5) * 100));

                    return (
                        <div
                            key={i}
                            className={`group relative flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-semibold cursor-default transition-all hover:scale-105 ${style.bg} ${style.text}`}
                            title={`Importance: ${width}% | Sentiment: ${sentiment}`}
                        >
                            {style.icon}
                            {t.topic}
                            {/* importance bar on hover */}
                            <div className="absolute bottom-0 left-0 h-0.5 rounded-full bg-current opacity-0 group-hover:opacity-30 transition-all"
                                style={{ width: `${width}%` }} />
                        </div>
                    );
                })}
            </div>

            {/* Sentiment summary */}
            <div className="mt-4 pt-3 border-t border-neutral-50 grid grid-cols-3 gap-1 text-center">
                {(["positive", "neutral", "negative"] as const).map(s => {
                    const count = topics.filter(t => (t.sentiment ?? "neutral") === s).length;
                    const st = sentimentStyles[s];
                    return (
                        <div key={s} className={`rounded-2xl px-2 py-1.5 ${st.bg}`}>
                            <p className={`text-xs font-bold capitalize ${st.text}`}>{s}</p>
                            <p className={`text-lg font-black ${st.text}`}>{count}</p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
