"use client";

import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface ExportButtonProps {
    days?: number;
}

export default function ExportButton({ days = 30 }: ExportButtonProps) {
    const [isExporting, setIsExporting] = useState(false);

    const handleExport = async () => {
        setIsExporting(true);
        try {
            const res = await apiClient.get(`/analytics/export?days=${days}`, {
                responseType: "blob",
            });
            const blob = new Blob([res.data], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `vocaply-analytics-${days}d.json`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Export failed", err);
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <button
            onClick={handleExport}
            disabled={isExporting}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white border border-neutral-200 text-neutral-600 hover:text-primary hover:border-primary/30 hover:bg-primary/5 transition-all text-xs font-bold shadow-sm disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
        >
            {isExporting ? (
                <Loader2 size={14} className="animate-spin" />
            ) : (
                <Download size={14} />
            )}
            <span>{isExporting ? "Exporting…" : "Export JSON"}</span>
        </button>
    );
}
