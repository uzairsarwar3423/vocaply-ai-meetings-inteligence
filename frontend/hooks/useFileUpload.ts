/**
 * useFileUpload
 * Vocaply Platform - Day 6
 *
 * Full upload lifecycle: drag-drop → validate → presigned URL → B2 → confirm
 * Multipart for > 100 MB. Supports cancel, retry, progress, resumption.
 */

import { useState, useCallback, useRef } from "react";
import axios, { AxiosProgressEvent, CancelTokenSource } from "axios";
import { apiClient as api } from "@/lib/api/client";

// ── Types ──────────────────────────────────────────────────────────────

export type UploadStatus =
    | "idle" | "validating" | "requesting_url" | "uploading"
    | "completing" | "completed" | "failed" | "cancelled";

export interface UploadFile {
    id: string;
    file: File;
    meetingId: string;
    status: UploadStatus;
    progress: number;        // 0–100
    bytesUploaded: number;
    uploadId?: string;
    s3Key?: string;
    cdnUrl?: string;
    error?: string;
    startedAt?: Date;
    completedAt?: Date;
    speed?: number;        // bytes/s
    eta?: number;        // seconds remaining
}

export interface UseFileUploadOptions {
    meetingId: string;
    maxFiles?: number;
    maxSizeMB?: number;
    onSuccess?: (file: UploadFile) => void;
    onError?: (file: UploadFile, error: string) => void;
    onProgress?: (file: UploadFile) => void;
}

// ── Constants ──────────────────────────────────────────────────────────

const MULTIPART_THRESHOLD = 100 * 1024 * 1024;  // 100 MB
const PART_SIZE = 50 * 1024 * 1024;  // 50 MB
const MAX_CONCURRENT_PARTS = 3;

const ALLOWED_TYPES = new Set([
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav",
    "audio/m4a", "audio/x-m4a", "audio/ogg", "audio/webm",
    "audio/aac", "audio/flac",
    "video/mp4", "video/webm", "video/quicktime", "video/x-msvideo",
]);

// ── Hook ───────────────────────────────────────────────────────────────

export function useFileUpload({
    meetingId,
    maxFiles = 5,
    maxSizeMB = 500,
    onSuccess,
    onError,
    onProgress,
}: UseFileUploadOptions) {
    const [files, setFiles] = useState<UploadFile[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const cancelMap = useRef<Record<string, CancelTokenSource>>({});

    // ── State helpers ──────────────────────────────────
    const updateFile = useCallback((id: string, patch: Partial<UploadFile>) => {
        setFiles(prev => prev.map(f => f.id === id ? { ...f, ...patch } : f));
    }, []);

    // ── Client-side validation ─────────────────────────
    const validate = (file: File): string | null => {
        if (file.size === 0) return "File is empty";
        if (file.size > maxSizeMB * 1024 * 1024)
            return `File exceeds ${maxSizeMB} MB limit`;
        if (!ALLOWED_TYPES.has(file.type))
            return `"${file.type}" is not supported. Upload audio or video files.`;
        return null;
    };

    // ── Add files to queue ─────────────────────────────
    const addFiles = useCallback((incoming: FileList | File[]) => {
        const arr = Array.from(incoming);
        const room = maxFiles - files.length;
        if (room <= 0) { alert(`Maximum ${maxFiles} files`); return; }

        const toAdd: UploadFile[] = arr.slice(0, room).map(file => ({
            id: crypto.randomUUID(), file, meetingId,
            status: "idle", progress: 0, bytesUploaded: 0,
        }));

        setFiles(prev => [...prev, ...toAdd]);
        toAdd.forEach(f => upload(f));
    }, [files, maxFiles, meetingId]);

    // ── Upload dispatcher ──────────────────────────────
    const upload = async (uf: UploadFile) => {
        updateFile(uf.id, { status: "validating" });
        const err = validate(uf.file);
        if (err) {
            updateFile(uf.id, { status: "failed", error: err });
            onError?.(uf, err);
            return;
        }
        if (uf.file.size > MULTIPART_THRESHOLD) {
            await uploadMultipart(uf);
        } else {
            await uploadSingle(uf);
        }
    };

    // ── Single upload (< 100 MB) ───────────────────────
    const uploadSingle = async (uf: UploadFile) => {
        const { id, file } = uf;
        try {
            updateFile(id, { status: "requesting_url" });
            const { data } = await api.post("/upload/presigned-url", {
                meeting_id: meetingId, file_name: file.name,
                file_size: file.size, content_type: file.type,
            });

            updateFile(id, { status: "uploading", uploadId: data.upload_id, s3Key: data.s3_key, startedAt: new Date() });

            const ct = axios.CancelToken.source();
            cancelMap.current[id] = ct;
            let lastLoaded = 0, lastTime = Date.now();

            await axios.put(data.upload_url, file, {
                headers: { "Content-Type": file.type },
                cancelToken: ct.token,
                onUploadProgress: (e: AxiosProgressEvent) => {
                    if (!e.total) return;
                    const now = Date.now();
                    const speed = ((e.loaded - lastLoaded) / ((now - lastTime) / 1000)) || 0;
                    const eta = speed > 0 ? (e.total - e.loaded) / speed : 0;
                    const progress = Math.round((e.loaded / e.total) * 100);
                    lastLoaded = e.loaded; lastTime = now;
                    const patch = { progress, bytesUploaded: e.loaded, speed, eta };
                    updateFile(id, patch);
                    onProgress?.({ ...uf, ...patch });
                },
            });

            updateFile(id, { status: "completing", progress: 100 });
            const { data: done } = await api.post("/upload/complete", { upload_id: data.upload_id });

            const patch = { status: "completed" as UploadStatus, cdnUrl: done.cdn_url, completedAt: new Date(), progress: 100 };
            updateFile(id, patch);
            onSuccess?.({ ...uf, ...patch });
        } catch (e: any) {
            if (axios.isCancel(e)) {
                updateFile(id, { status: "cancelled", progress: 0 });
            } else {
                const msg = e?.response?.data?.detail ?? e.message ?? "Upload failed";
                updateFile(id, { status: "failed", error: msg });
                onError?.(uf, msg);
            }
        } finally {
            delete cancelMap.current[id];
        }
    };

    // ── Multipart upload (> 100 MB) ────────────────────
    const uploadMultipart = async (uf: UploadFile) => {
        const { id, file } = uf;
        try {
            updateFile(id, { status: "requesting_url" });
            const { data: init } = await api.post("/upload/multipart-init", {
                meeting_id: meetingId, file_name: file.name,
                file_size: file.size, content_type: file.type,
            });

            updateFile(id, { status: "uploading", uploadId: init.upload_id, s3Key: init.s3_key, startedAt: new Date() });

            const { upload_id, part_urls, part_size } = init;
            let totalDone = 0;

            // Process parts in batches
            const batches: typeof part_urls[] = [];
            for (let i = 0; i < part_urls.length; i += MAX_CONCURRENT_PARTS)
                batches.push(part_urls.slice(i, i + MAX_CONCURRENT_PARTS));

            for (const batch of batches) {
                await Promise.all(batch.map(async ({ part_number, upload_url }: { part_number: number; upload_url: string }) => {
                    const start = (part_number - 1) * part_size;
                    const blob = file.slice(start, Math.min(start + part_size, file.size));
                    const ct = axios.CancelToken.source();
                    cancelMap.current[`${id}_${part_number}`] = ct;

                    const resp = await axios.put(upload_url, blob, {
                        headers: { "Content-Type": file.type },
                        cancelToken: ct.token,
                        onUploadProgress: (e: AxiosProgressEvent) => {
                            const overall = Math.round(((totalDone + (e.loaded ?? 0)) / file.size) * 100);
                            updateFile(id, { progress: Math.min(overall, 99), bytesUploaded: totalDone + (e.loaded ?? 0) });
                        },
                    });

                    const etag = resp.headers["etag"] ?? resp.headers["ETag"] ?? "";
                    await api.post("/upload/multipart-upload", { upload_id, part_number, etag });
                    totalDone += blob.size;
                }));
            }

            updateFile(id, { status: "completing", progress: 100 });
            const { data: done } = await api.post("/upload/multipart-complete", { upload_id });

            const patch = { status: "completed" as UploadStatus, cdnUrl: done.cdn_url, completedAt: new Date(), progress: 100 };
            updateFile(id, patch);
            onSuccess?.({ ...uf, ...patch });
        } catch (e: any) {
            if (axios.isCancel(e)) {
                updateFile(id, { status: "cancelled", progress: 0 });
            } else {
                const msg = e?.response?.data?.detail ?? e.message ?? "Upload failed";
                updateFile(id, { status: "failed", error: msg });
                onError?.(uf, msg);
            }
        }
    };

    // ── Controls ───────────────────────────────────────
    const removeFile = useCallback((id: string) => {
        cancelMap.current[id]?.cancel();
        setFiles(prev => prev.filter(f => f.id !== id));
    }, []);

    const cancelFile = useCallback((id: string) => {
        Object.entries(cancelMap.current).forEach(([k, v]) => {
            if (k === id || k.startsWith(`${id}_`)) v.cancel("Cancelled");
        });
        updateFile(id, { status: "cancelled", progress: 0 });
    }, [updateFile]);

    const retryFile = useCallback((id: string) => {
        const uf = files.find(f => f.id === id);
        if (!uf) return;
        const reset = { status: "idle" as UploadStatus, progress: 0, error: undefined, bytesUploaded: 0 };
        updateFile(id, reset);
        upload({ ...uf, ...reset });
    }, [files]);

    const clearAll = useCallback(() => {
        Object.values(cancelMap.current).forEach(c => c.cancel());
        cancelMap.current = {};
        setFiles([]);
    }, []);

    // ── Drag & drop ────────────────────────────────────
    const onDragEnter = useCallback((e: React.DragEvent) => { e.preventDefault(); setIsDragging(true); }, []);
    const onDragLeave = useCallback((e: React.DragEvent) => { e.preventDefault(); setIsDragging(false); }, []);
    const onDragOver = useCallback((e: React.DragEvent) => { e.preventDefault(); }, []);
    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault(); setIsDragging(false);
        if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
    }, [addFiles]);

    const getRootProps = () => ({
        onDragEnter, onDragLeave, onDragOver, onDrop,
        onClick: () => document.getElementById("vocaply-upload-input")?.click()
    });
    const getInputProps = () => ({
        id: "vocaply-upload-input", type: "file",
        multiple: maxFiles > 1, accept: "audio/*,video/*",
        style: { display: "none" },
        onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
            if (e.target.files) { addFiles(e.target.files); e.target.value = ""; }
        },
    });

    return {
        files, isDragging,
        isUploading: files.some(f => ["validating", "requesting_url", "uploading", "completing"].includes(f.status)),
        addFiles, removeFile, cancelFile, retryFile, clearAll,
        getRootProps, getInputProps,
    };
}