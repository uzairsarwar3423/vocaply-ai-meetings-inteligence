/**
 * FilePreview
 * Vocaply Platform
 */

"use client";

import React from "react";
import { UploadFile } from "@/hooks/useFileUpload";
import UploadProgress from "./UploadProgress";

// ── Helpers ────────────────────────────────────────────────────────────

const formatBytes = (b: number): string => {
    if (b < 1024) return `${b} B`;
    if (b < 1024 ** 2) return `${(b / 1024).toFixed(1)} KB`;
    if (b < 1024 ** 3) return `${(b / 1024 ** 2).toFixed(1)} MB`;
    return `${(b / 1024 ** 3).toFixed(1)} GB`;
};

const fileTypeIcon = (file: File): string => {
    if (file.type.startsWith("audio/")) return "🎵";
    if (file.type.startsWith("video/")) return "🎬";
    return "📄";
};

// ── Component ──────────────────────────────────────────────────────────

interface FilePreviewProps {
    uf: UploadFile;
    onCancel: () => void;
    onRetry: () => void;
    onRemove: () => void;
}

export default function FilePreview({
    uf,
    onCancel,
    onRetry,
    onRemove,
}: FilePreviewProps) {
    const isActive = ["validating", "requesting_url", "uploading", "completing"].includes(uf.status);
    const isFailed = uf.status === "failed";
    const isDone = uf.status === "completed";
    const isCancelled = uf.status === "cancelled";

    const statusColor: Record<string, string> = {
        idle: "#9FB3B3",
        validating: "#0EA5E9",
        requesting_url: "#0EA5E9",
        uploading: "#00ACAC",
        completing: "#00ACAC",
        completed: "#10B981",
        failed: "#F43F5E",
        cancelled: "#9FB3B3",
    };

    const statusLabel: Record<string, string> = {
        idle: "Queued",
        validating: "Validating…",
        requesting_url: "Preparing…",
        uploading: `${uf.progress}%`,
        completing: "Finishing…",
        completed: "Done",
        failed: "Failed",
        cancelled: "Cancelled",
    };

    return (
        <div
            style={{
                background: "white",
                border: `1px solid ${isFailed ? "#FFE4E6" : "#E5EBEB"}`,
                borderRadius: "0.75rem",
                padding: "1rem",
            }}
            onClick={e => e.stopPropagation()}
        >
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                {/* Icon */}
                <span style={{ fontSize: "1.5rem" }}>{fileTypeIcon(uf.file)}</span>

                {/* Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{
                        fontWeight: 500,
                        color: "#0D1A1A",
                        marginBottom: "0.25rem",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                    }}>
                        {uf.file.name}
                    </p>
                    <div style={{ display: "flex", gap: "1rem", fontSize: "0.75rem", color: "#6B8585" }}>
                        <span>{formatBytes(uf.file.size)}</span>
                        {isActive && uf.speed && (
                            <span>{formatBytes(uf.speed)}/s</span>
                        )}
                        {isActive && uf.eta && uf.eta > 0 && (
                            <span>{uf.eta < 60 ? `${Math.round(uf.eta)}s` : `${Math.round(uf.eta / 60)}m`} left</span>
                        )}
                    </div>

                    {/* Progress bar */}
                    {isActive && (
                        <UploadProgress progress={uf.progress} status={uf.status} />
                    )}

                    {/* Error message */}
                    {isFailed && uf.error && (
                        <p style={{ fontSize: "0.75rem", color: "#F43F5E", marginTop: "0.25rem" }}>
                            {uf.error}
                        </p>
                    )}
                </div>

                {/* Status badge */}
                <span style={{
                    fontSize: "0.75rem",
                    fontWeight: 600,
                    color: statusColor[uf.status] ?? "#9FB3B3",
                    whiteSpace: "nowrap",
                }}>
                    {isDone && "✓ "}
                    {statusLabel[uf.status]}
                </span>

                {/* Actions */}
                <div style={{ display: "flex", gap: "0.25rem" }}>
                    {isActive && (
                        <ActionBtn onClick={onCancel} label="✕" title="Cancel" color="#6B8585" />
                    )}
                    {isFailed && (
                        <ActionBtn onClick={onRetry} label="↺" title="Retry" color="#00ACAC" />
                    )}
                    {(isDone || isCancelled || isFailed) && (
                        <ActionBtn onClick={onRemove} label="🗑" title="Remove" color="#9FB3B3" />
                    )}
                </div>
            </div>
        </div>
    );
}

function ActionBtn({ onClick, label, title, color }: {
    onClick: () => void; label: string; title: string; color: string;
}) {
    return (
        <button
            onClick={(e) => { e.stopPropagation(); onClick(); }}
            title={title}
            style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                border: "none",
                background: "transparent",
                color,
                cursor: "pointer",
                fontSize: "0.875rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
            }}
        >
            {label}
        </button>
    );
}
