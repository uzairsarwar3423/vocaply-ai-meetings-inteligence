/**
 * UploadProgress
 * Vocaply Platform - Day 6
 */

"use client";

import React from "react";
import { UploadStatus } from "@/hooks/useFileUpload";

interface UploadProgressProps {
    progress: number;
    status: UploadStatus;
    height?: number;
    showLabel?: boolean;
}

export default function UploadProgress({
    progress,
    status,
    height = 4,
    showLabel = false,
}: UploadProgressProps) {
    const isCompleting = status === "completing";
    const isCompleted = status === "completed";

    const barColor =
        isCompleted ? "#10B981" :
            isCompleting ? "#00ACAC" :
                status === "failed" ? "#F43F5E" :
                    "#00ACAC";

    return (
        <div style={{ marginTop: "0.5rem" }}>
            {/* Track */}
            <div
                style={{
                    width: "100%",
                    height: `${height}px`,
                    background: "#E5EBEB",
                    borderRadius: `${height}px`,
                    overflow: "hidden",
                }}
            >
                {/* Fill */}
                <div
                    style={{
                        width: `${progress}%`,
                        height: "100%",
                        background: barColor,
                        borderRadius: `${height}px`,
                        transition: "width 0.3s ease",
                        // Animate shimmer on uploading
                        backgroundImage: status === "uploading"
                            ? `linear-gradient(90deg, ${barColor} 0%, #00CFCF 50%, ${barColor} 100%)`
                            : undefined,
                        backgroundSize: "200% 100%",
                        animation: status === "uploading" ? "shimmer 1.5s infinite" : undefined,
                    }}
                />
            </div>

            {showLabel && (
                <div style={{ display: "flex", justifyContent: "space-between", marginTop: "0.25rem" }}>
                    <span style={{ fontSize: "0.75rem", color: "#6B8585" }}>
                        {status === "completing" ? "Finalising…" : `${progress}%`}
                    </span>
                </div>
            )}

            <style>{`
        @keyframes shimmer {
          0%   { background-position: -200% 0; }
          100% { background-position:  200% 0; }
        }
      `}</style>
        </div>
    );
}