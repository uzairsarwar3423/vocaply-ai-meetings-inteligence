"use client";

import React, { useState } from "react";
import {
    Download, FileText, FileCode, Copy, Check,
    Loader2, AlertCircle
} from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface SummaryExportProps {
    summaryId: string;
    meetingTitle?: string;
}

type ExportFormat = "markdown" | "text";

const formats = [
    {
        key: "markdown" as ExportFormat,
        label: "Markdown",
        ext: ".md",
        icon: <FileCode className="w-4 h-4" />,
        desc: "Perfect for Notion, GitHub, Confluence",
    },
    {
        key: "text" as ExportFormat,
        label: "Plain Text",
        ext: ".txt",
        icon: <FileText className="w-4 h-4" />,
        desc: "Universal format for any editor",
    },
];

export const SummaryExport: React.FC<SummaryExportProps> = ({
    summaryId,
    meetingTitle = "meeting-summary",
}) => {
    const [loading, setLoading] = useState<ExportFormat | null>(null);
    const [copied, setCopied] = useState<ExportFormat | null>(null);
    const [error, setError] = useState<string | null>(null);

    const fetchContent = async (fmt: ExportFormat): Promise<string> => {
        const res = await apiClient.get(`/summaries/${summaryId}/export/${fmt}`, {
            responseType: "text",
        });
        return typeof res.data === "string" ? res.data : JSON.stringify(res.data);
    };

    const handleDownload = async (fmt: ExportFormat) => {
        setLoading(fmt);
        setError(null);
        try {
            const content = await fetchContent(fmt);
            const ext = formats.find(f => f.key === fmt)?.ext ?? ".txt";
            const filename = `${meetingTitle.replace(/\s+/g, "-").toLowerCase()}${ext}`;
            const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (e: any) {
            setError(e?.response?.data?.detail ?? "Export failed. Please try again.");
        } finally {
            setLoading(null);
        }
    };

    const handleCopy = async (fmt: ExportFormat) => {
        setLoading(fmt);
        setError(null);
        try {
            const content = await fetchContent(fmt);
            await navigator.clipboard.writeText(content);
            setCopied(fmt);
            setTimeout(() => setCopied(null), 2000);
        } catch (e: any) {
            setError("Failed to copy to clipboard.");
        } finally {
            setLoading(null);
        }
    };

    return (
        <div className="bg-white rounded-3xl border border-neutral-100 shadow-sm overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 border-b border-neutral-50 flex items-center gap-3">
                <div className="w-9 h-9 bg-primary/10 rounded-xl flex items-center justify-center">
                    <Download className="w-5 h-5 text-primary" />
                </div>
                <div>
                    <h3 className="font-bold text-neutral-800 text-sm">Export Summary</h3>
                    <p className="text-xs text-neutral-400">Download or copy the summary</p>
                </div>
            </div>

            <div className="p-4 space-y-3">
                {error && (
                    <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 rounded-2xl text-sm text-rose-700">
                        <AlertCircle className="w-4 h-4 flex-shrink-0" />
                        {error}
                    </div>
                )}

                {formats.map(fmt => {
                    const isLoading = loading === fmt.key;
                    const isCopied = copied === fmt.key;

                    return (
                        <div
                            key={fmt.key}
                            className="flex items-center justify-between p-4 bg-neutral-50 rounded-2xl hover:bg-primary/5 transition-all border border-transparent hover:border-primary/10"
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-9 h-9 bg-white rounded-xl flex items-center justify-center shadow-sm text-neutral-500">
                                    {fmt.icon}
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-neutral-800">{fmt.label} <span className="text-neutral-400 font-normal">{fmt.ext}</span></p>
                                    <p className="text-xs text-neutral-400">{fmt.desc}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-2">
                                {/* Copy */}
                                <button
                                    onClick={() => handleCopy(fmt.key)}
                                    disabled={isLoading}
                                    className="p-2 text-neutral-400 hover:text-primary hover:bg-primary/10 rounded-xl transition-all disabled:opacity-50"
                                    title="Copy to clipboard"
                                >
                                    {isCopied
                                        ? <Check className="w-4 h-4 text-emerald-500" />
                                        : isLoading
                                            ? <Loader2 className="w-4 h-4 animate-spin" />
                                            : <Copy className="w-4 h-4" />
                                    }
                                </button>

                                {/* Download */}
                                <button
                                    onClick={() => handleDownload(fmt.key)}
                                    disabled={isLoading}
                                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-primary bg-primary/10 hover:bg-primary hover:text-white rounded-xl transition-all disabled:opacity-50"
                                >
                                    {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                                    Download
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
