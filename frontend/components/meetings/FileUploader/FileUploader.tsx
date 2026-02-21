/**
 * FileUploader
 * Vocaply Platform - Day 6
 *
 * Drag-and-drop upload zone with queue, progress bars, cancel & retry.
 */

"use client";

import React from "react";
import { useFileUpload, UploadFile } from "@/hooks/useFileUpload";
import FilePreview from "./FilePreview";

// ── Props ──────────────────────────────────────────────────────────────

interface FileUploaderProps {
    meetingId: string;
    maxFiles?: number;
    maxSizeMB?: number;
    onSuccess?: (file: UploadFile) => void;
    className?: string;
}

// ── Component ──────────────────────────────────────────────────────────

export default function FileUploader({
    meetingId,
    maxFiles = 5,
    maxSizeMB = 500,
    onSuccess,
    className = "",
}: FileUploaderProps) {
    const {
        files, isDragging, isUploading,
        removeFile, cancelFile, retryFile, clearAll,
        getRootProps, getInputProps,
    } = useFileUpload({ meetingId, maxFiles, maxSizeMB, onSuccess });

    const hasFiles = files.length > 0;

    return (
        <div className={`w-full ${className}`}>
            {/* ── Drop Zone ── */}
            <div
                {...getRootProps()}
                style={{
                    border: `2px dashed ${isDragging ? "#00ACAC" : "#D1DCDC"}`,
                    borderRadius: "1rem",
                    padding: hasFiles ? "1.5rem" : "3rem 2rem",
                    background: isDragging ? "rgba(0,172,172,0.04)" : "#F8FAFA",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    textAlign: "center",
                }}
            >
                <input {...getInputProps()} />

                {!hasFiles && (
                    <>
                        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>
                            {isDragging ? "📂" : "🎙️"}
                        </div>
                        <p style={{ fontSize: "1.125rem", fontWeight: 600, color: "#0D1A1A", marginBottom: "0.5rem" }}>
                            {isDragging ? "Drop files here" : "Drag & drop your recording"}
                        </p>
                        <p style={{ color: "#6B8585", fontSize: "0.875rem", marginBottom: "1.5rem" }}>
                            MP3, WAV, M4A, MP4, WebM — up to {maxSizeMB} MB
                        </p>
                        <button
                            style={{
                                padding: "0.75rem 2rem",
                                background: "linear-gradient(90deg, #FF9070, #E85A35)",
                                color: "white",
                                border: "none",
                                borderRadius: "0.5rem",
                                fontWeight: 600,
                                cursor: "pointer",
                                fontSize: "1rem",
                            }}
                        >
                            Browse Files
                        </button>
                    </>
                )}

                {hasFiles && (
                    <div style={{ textAlign: "left" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                            <span style={{ fontWeight: 600, color: "#0D1A1A" }}>
                                {files.length} file{files.length !== 1 ? "s" : ""}
                            </span>
                            <div style={{ display: "flex", gap: "0.75rem" }}>
                                <label
                                    style={{ color: "#00ACAC", cursor: "pointer", fontSize: "0.875rem", fontWeight: 500 }}
                                >
                                    + Add more
                                    <input {...getInputProps()} style={{ display: "none" }} />
                                </label>
                                {!isUploading && (
                                    <button
                                        onClick={(e) => { e.stopPropagation(); clearAll(); }}
                                        style={{ color: "#6B8585", fontSize: "0.875rem", background: "none", border: "none", cursor: "pointer" }}
                                    >
                                        Clear all
                                    </button>
                                )}
                            </div>
                        </div>

                        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                            {files.map(uf => (
                                <FilePreview
                                    key={uf.id}
                                    uf={uf}
                                    onCancel={() => cancelFile(uf.id)}
                                    onRetry={() => retryFile(uf.id)}
                                    onRemove={() => removeFile(uf.id)}
                                />
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* ── Hint ── */}
            <p style={{ fontSize: "0.75rem", color: "#9FB3B3", textAlign: "center", marginTop: "0.75rem" }}>
                Files are uploaded directly to secure storage • Never stored on our servers temporarily
            </p>
        </div>
    );
}