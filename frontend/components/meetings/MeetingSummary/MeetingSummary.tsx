"use client";

import React, { useState } from "react";
import {
    Brain, Clock, RefreshCw, Download, Edit3,
    CheckCircle, ChevronDown, ChevronUp, Sparkles, Loader2
} from "lucide-react";
import { KeyPoints } from "./KeyPoints";
import { Decisions } from "./Decisions";
import { Topics } from "./Topics";

// ─────────────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────────────
export interface TopicItem {
    topic: string;
    sentiment?: "positive" | "neutral" | "negative";
    importance?: number;
}

export interface MeetingSummaryData {
    id: string;
    meeting_id: string;
    short_summary?: string;
    detailed_summary?: string;
    key_points: string[];
    decisions: string[];
    topics: TopicItem[];
    sentiment?: "positive" | "neutral" | "negative";
    sentiment_score?: number;
    model_version?: string;
    generation_time_seconds?: number;
    token_usage?: number;
    created_at: string;
    updated_at: string;
    // extras stored in __dict__
    next_steps?: string[];
    participant_insights?: { name: string; contribution: string; sentiment?: string }[];
}

interface MeetingSummaryProps {
    summary: MeetingSummaryData;
    isLoading?: boolean;
    onRegenerate?: () => void;
    onExport?: (format: "markdown" | "text") => void;
    onEdit?: () => void;
}

// ─────────────────────────────────────────────────────────────────────────────
// SENTIMENT BADGE
// ─────────────────────────────────────────────────────────────────────────────
const sentimentConfig = {
    positive: { color: "text-emerald-700 bg-emerald-50 border-emerald-200", label: "Positive", dot: "bg-emerald-500" },
    neutral: { color: "text-amber-700   bg-amber-50   border-amber-200", label: "Neutral", dot: "bg-amber-400" },
    negative: { color: "text-rose-700    bg-rose-50    border-rose-200", label: "Negative", dot: "bg-rose-500" },
};

function SentimentBadge({ sentiment }: { sentiment?: string }) {
    const cfg = sentimentConfig[(sentiment as keyof typeof sentimentConfig) ?? "neutral"] ?? sentimentConfig.neutral;
    return (
        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${cfg.color}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
            {cfg.label}
        </span>
    );
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────────────────────────
export const MeetingSummary: React.FC<MeetingSummaryProps> = ({
    summary,
    isLoading = false,
    onRegenerate,
    onExport,
    onEdit,
}) => {
    const [showDetails, setShowDetails] = useState(true);
    const [exportOpen, setExportOpen] = useState(false);

    if (isLoading) {
        return (
            <div className="bg-white rounded-3xl border border-neutral-100 p-10 flex flex-col items-center gap-4 text-center shadow-sm">
                <div className="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center">
                    <Loader2 className="w-7 h-7 text-primary animate-spin" />
                </div>
                <p className="text-neutral-500 font-medium">Generating AI summary…</p>
                <p className="text-xs text-neutral-400">This usually takes 15–30 seconds</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* ─── Header Card ─── */}
            <div className="bg-gradient-to-br from-primary/5 via-white to-violet-50 rounded-3xl border border-primary/10 p-6 shadow-sm">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                    <div className="flex items-center gap-3">
                        <div className="w-11 h-11 bg-primary/10 rounded-2xl flex items-center justify-center flex-shrink-0">
                            <Brain className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                            <p className="text-xs font-bold text-primary uppercase tracking-widest">AI Summary</p>
                            {summary.model_version && (
                                <p className="text-xs text-neutral-400 mt-0.5 flex items-center gap-1">
                                    <Sparkles className="w-3 h-3" /> {summary.model_version}
                                </p>
                            )}
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 flex-wrap">
                        {summary.sentiment && <SentimentBadge sentiment={summary.sentiment} />}

                        {onEdit && (
                            <button
                                onClick={onEdit}
                                className="p-2 text-neutral-400 hover:text-primary hover:bg-primary/5 rounded-xl transition-all"
                                title="Edit summary"
                            >
                                <Edit3 className="w-4 h-4" />
                            </button>
                        )}

                        {/* Export dropdown */}
                        {onExport && (
                            <div className="relative">
                                <button
                                    onClick={() => setExportOpen(v => !v)}
                                    className="flex items-center gap-1.5 px-3 py-2 text-xs font-bold text-neutral-500 hover:text-primary hover:bg-primary/5 rounded-xl border border-neutral-200 hover:border-primary/20 transition-all"
                                >
                                    <Download className="w-3.5 h-3.5" />
                                    Export
                                </button>
                                {exportOpen && (
                                    <div className="absolute right-0 top-full mt-1 bg-white rounded-2xl border border-neutral-100 shadow-xl z-10 py-1 min-w-[130px]">
                                        {(["markdown", "text"] as const).map(fmt => (
                                            <button
                                                key={fmt}
                                                onClick={() => { onExport(fmt); setExportOpen(false); }}
                                                className="block w-full text-left px-4 py-2 text-sm text-neutral-700 hover:bg-primary/5 hover:text-primary transition-all capitalize"
                                            >
                                                {fmt === "markdown" ? "Markdown (.md)" : "Plain Text (.txt)"}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {onRegenerate && (
                            <button
                                onClick={onRegenerate}
                                className="flex items-center gap-1.5 px-3 py-2 text-xs font-bold text-white bg-primary hover:bg-primary/90 rounded-xl shadow-sm transition-all"
                            >
                                <RefreshCw className="w-3.5 h-3.5" />
                                Regenerate
                            </button>
                        )}
                    </div>
                </div>

                {/* TL;DR */}
                {summary.short_summary && (
                    <blockquote className="mt-5 pl-4 border-l-4 border-primary/30 text-neutral-700 italic text-sm font-medium leading-relaxed">
                        {summary.short_summary}
                    </blockquote>
                )}

                {/* Meta */}
                {(summary.generation_time_seconds || summary.token_usage) && (
                    <div className="mt-4 flex items-center gap-4 text-xs text-neutral-400">
                        {summary.generation_time_seconds && (
                            <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {summary.generation_time_seconds}s generation time
                            </span>
                        )}
                        {summary.token_usage && (
                            <span className="flex items-center gap-1">
                                <Sparkles className="w-3 h-3" />
                                {summary.token_usage.toLocaleString()} tokens
                            </span>
                        )}
                    </div>
                )}
            </div>

            {/* ─── Executive Overview ─── */}
            {summary.detailed_summary && (
                <div className="bg-white rounded-3xl border border-neutral-100 shadow-sm overflow-hidden">
                    <button
                        onClick={() => setShowDetails(v => !v)}
                        className="w-full flex items-center justify-between px-6 py-4 hover:bg-neutral-50 transition-all"
                    >
                        <h3 className="font-bold text-neutral-800">Executive Overview</h3>
                        {showDetails ? <ChevronUp className="w-4 h-4 text-neutral-400" /> : <ChevronDown className="w-4 h-4 text-neutral-400" />}
                    </button>
                    {showDetails && (
                        <div
                            className="px-6 pb-6 text-sm text-neutral-600 leading-relaxed prose prose-sm max-w-none border-t border-neutral-50 pt-4"
                            dangerouslySetInnerHTML={{ __html: markdownToHtml(summary.detailed_summary) }}
                        />
                    )}
                </div>
            )}

            {/* ─── 3-column grid for structured data ─── */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                <KeyPoints points={summary.key_points} />
                <Decisions decisions={summary.decisions} nextSteps={summary.next_steps} />
                <Topics topics={summary.topics} />
            </div>
        </div>
    );
};

// ─────────────────────────────────────────────────────────────────────────────
// MINIMAL MARKDOWN → HTML
// ─────────────────────────────────────────────────────────────────────────────
function markdownToHtml(md: string): string {
    return md
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/^### (.+)$/gm, "<h3 class='font-bold text-neutral-800 mt-3 mb-1'>$1</h3>")
        .replace(/^## (.+)$/gm, "<h2 class='font-bold text-neutral-900 mt-4 mb-1 text-base'>$1</h2>")
        .replace(/\n\n/g, "</p><p class='mt-2'>")
        .replace(/^/, "<p>")
        .replace(/$/, "</p>");
}
