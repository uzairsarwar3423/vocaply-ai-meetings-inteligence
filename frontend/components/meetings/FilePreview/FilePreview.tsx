/**
 * FilePreview
 * Vocaply Platform - Day 6
 *
 * Shows a preview card for an audio/video file before or after upload.
 * Audio files: waveform placeholder + duration.
 * Video files: first-frame thumbnail via canvas.
 */

"use client";

import React, { useEffect, useRef, useState } from "react";

// ── Types ──────────────────────────────────────────────────────────────

interface FilePreviewProps {
    file: File;
    cdnUrl?: string;   // Set after upload completes
    className?: string;
    onRemove?: () => void;
}

// ── Helpers ────────────────────────────────────────────────────────────

const formatDuration = (seconds: number): string => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    return `${m}:${String(s).padStart(2, "0")}`;
};

const formatBytes = (b: number): string => {
    if (b < 1024 ** 2) return `${(b / 1024).toFixed(0)} KB`;
    if (b < 1024 ** 3) return `${(b / 1024 ** 2).toFixed(1)} MB`;
    return `${(b / 1024 ** 3).toFixed(1)} GB`;
};

// ── Component ──────────────────────────────────────────────────────────

export default function FilePreview({ file, cdnUrl, className = "", onRemove }: FilePreviewProps) {
    const [duration, setDuration] = useState<number | null>(null);
    const [thumbnail, setThumbnail] = useState<string | null>(null);
    const [objectUrl, setObjectUrl] = useState<string | null>(null);

    const isAudio = file.type.startsWith("audio/");
    const isVideo = file.type.startsWith("video/");

    // Create object URL for preview
    useEffect(() => {
        const url = URL.createObjectURL(file);
        setObjectUrl(url);
        return () => URL.revokeObjectURL(url);
    }, [file]);

    // Extract duration from audio/video
    useEffect(() => {
        if (!objectUrl) return;
        const el = isAudio
            ? new Audio(objectUrl)
            : document.createElement("video");

        el.preload = "metadata";
        el.onloadedmetadata = () => setDuration(el.duration);
        if (!isAudio) (el as HTMLVideoElement).src = objectUrl;
        else (el as HTMLAudioElement).src = objectUrl;
    }, [objectUrl, isAudio]);

    // Extract video thumbnail via canvas
    useEffect(() => {
        if (!isVideo || !objectUrl) return;
        const video = document.createElement("video");
        video.src = objectUrl;
        video.preload = "metadata";
        video.muted = true;
        video.onloadeddata = () => {
            video.currentTime = 1;  // Seek to 1s for better thumbnail
        };
        video.onseeked = () => {
            const canvas = document.createElement("canvas");
            canvas.width = 320;
            canvas.height = 180;
            const ctx = canvas.getContext("2d");
            ctx?.drawImage(video, 0, 0, 320, 180);
            setThumbnail(canvas.toDataURL("image/jpeg", 0.7));
        };
    }, [objectUrl, isVideo]);

    return (
        <div
            className={className}
            style={{
                background: "white",
                border: "1px solid #E5EBEB",
                borderRadius: "1rem",
                overflow: "hidden",
                position: "relative",
            }}
        >
            {/* Remove button */}
            {onRemove && (
                <button
                    onClick={onRemove}
                    style={{
                        position: "absolute",
                        top: "0.5rem",
                        right: "0.5rem",
                        width: "28px",
                        height: "28px",
                        borderRadius: "50%",
                        background: "rgba(0,0,0,0.5)",
                        color: "white",
                        border: "none",
                        cursor: "pointer",
                        zIndex: 10,
                        fontSize: "0.875rem",
                    }}
                >
                    ✕
                </button>
            )}

            {/* Video thumbnail */}
            {isVideo && thumbnail && (
                <div style={{ position: "relative" }}>
                    <img
                        src={thumbnail}
                        alt="Video preview"
                        style={{ width: "100%", display: "block", aspectRatio: "16/9", objectFit: "cover" }}
                    />
                    <div style={{
                        position: "absolute", inset: 0, display: "flex",
                        alignItems: "center", justifyContent: "center",
                    }}>
                        <div style={{
                            width: "48px", height: "48px", borderRadius: "50%",
                            background: "rgba(255,255,255,0.9)",
                            display: "flex", alignItems: "center", justifyContent: "center",
                            fontSize: "1.25rem",
                        }}>
                            ▶
                        </div>
                    </div>
                    {duration && (
                        <span style={{
                            position: "absolute", bottom: "0.5rem", right: "0.5rem",
                            background: "rgba(0,0,0,0.7)", color: "white",
                            borderRadius: "0.25rem", padding: "0.125rem 0.375rem",
                            fontSize: "0.75rem", fontWeight: 600,
                        }}>
                            {formatDuration(duration)}
                        </span>
                    )}
                </div>
            )}

            {/* Audio waveform placeholder */}
            {isAudio && (
                <div style={{
                    background: "linear-gradient(135deg, #E6F7F7 0%, #F8FAFA 100%)",
                    padding: "1.5rem",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "0.25rem",
                    height: "80px",
                }}>
                    {/* Fake waveform bars */}
                    {Array.from({ length: 30 }, (_, i) => (
                        <div
                            key={i}
                            style={{
                                width: "3px",
                                height: `${8 + Math.sin(i * 0.7) * 20 + Math.random() * 10}px`,
                                background: "#00ACAC",
                                borderRadius: "2px",
                                opacity: 0.6 + Math.random() * 0.4,
                            }}
                        />
                    ))}
                </div>
            )}

            {/* File info footer */}
            <div style={{ padding: "0.75rem 1rem", display: "flex", gap: "0.75rem", alignItems: "center" }}>
                <span style={{ fontSize: "1.5rem" }}>{isAudio ? "🎵" : "🎬"}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{
                        fontWeight: 500, color: "#0D1A1A", fontSize: "0.875rem",
                        whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                        marginBottom: "0.125rem",
                    }}>
                        {file.name}
                    </p>
                    <p style={{ color: "#6B8585", fontSize: "0.75rem" }}>
                        {formatBytes(file.size)}
                        {duration && ` • ${formatDuration(duration)}`}
                        {` • ${file.type.split("/")[1]?.toUpperCase()}`}
                    </p>
                </div>
                {cdnUrl && (
                    <span style={{
                        fontSize: "0.75rem", fontWeight: 600, color: "#10B981",
                        background: "#D1FAE5", padding: "0.25rem 0.625rem",
                        borderRadius: "9999px",
                    }}>
                        ✓ Uploaded
                    </span>
                )}
            </div>
        </div>
    );
}