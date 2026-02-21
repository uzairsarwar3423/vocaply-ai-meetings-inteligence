'use client';

import React, { useState } from 'react';
import { Download, FileText, File, FileCode, ChevronDown, Copy, Check } from 'lucide-react';
import { TranscriptSegment } from '@/types/transcript';
import { ExportFormat } from '@/types/transcript';

interface TranscriptExportProps {
    segments: (TranscriptSegment & { speaker_name: string })[];
    meetingTitle: string;
}

function formatTime(secs: number) {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}

function buildTxt(segments: (TranscriptSegment & { speaker_name: string })[]) {
    return segments
        .map((s) => `[${formatTime(s.start_time)}] ${s.speaker_name}: ${s.text}`)
        .join('\n\n');
}

function buildSrt(segments: (TranscriptSegment & { speaker_name: string })[]) {
    function toSrtTime(secs: number) {
        const h = Math.floor(secs / 3600);
        const m = Math.floor((secs % 3600) / 60);
        const s = Math.floor(secs % 60);
        const ms = Math.round((secs % 1) * 1000);
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')},${ms.toString().padStart(3, '0')}`;
    }
    return segments
        .map((s, i) =>
            `${i + 1}\n${toSrtTime(s.start_time)} --> ${toSrtTime(s.end_time)}\n${s.speaker_name}: ${s.text}`
        )
        .join('\n\n');
}

function downloadBlob(content: string, filename: string, mime: string) {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

export default function TranscriptExport({ segments, meetingTitle }: TranscriptExportProps) {
    const [open, setOpen] = useState(false);
    const [copied, setCopied] = useState(false);

    const safeTitle = meetingTitle.replace(/[/\\?%*:|"<>]/g, '-');

    const handleExport = (format: ExportFormat) => {
        setOpen(false);
        if (format === 'txt') {
            downloadBlob(buildTxt(segments), `${safeTitle}.txt`, 'text/plain');
        } else if (format === 'srt') {
            downloadBlob(buildSrt(segments), `${safeTitle}.srt`, 'text/plain');
        } else if (format === 'pdf') {
            // For PDF we open a print dialog on a formatted page
            const win = window.open('', '_blank');
            if (!win) return;
            win.document.write(`
        <html><head><title>${safeTitle}</title>
        <style>body{font-family:sans-serif;max-width:800px;margin:40px auto;line-height:1.7}
        .speaker{font-weight:600;color:#00ACAC}.time{color:#888;font-size:.85em}
        p{margin:0 0 1em}</style></head><body>
        <h1>${meetingTitle}</h1>
        ${segments.map(s => `<p><span class="time">[${formatTime(s.start_time)}]</span> <span class="speaker">${s.speaker_name}:</span> ${s.text}</p>`).join('')}
        </body></html>`);
            win.document.close();
            win.print();
        } else if (format === 'docx') {
            // DOCX-like: rich text in html, saved as .doc (broad compat)
            const html = `<html><body>${segments.map(s => `<p><strong>[${formatTime(s.start_time)}] ${s.speaker_name}:</strong> ${s.text}</p>`).join('')}</body></html>`;
            downloadBlob(html, `${safeTitle}.doc`, 'application/msword');
        }
    };

    const handleCopy = async () => {
        const text = buildTxt(segments);
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative flex items-center gap-2">
            {/* Copy to clipboard */}
            <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 px-3 py-2 text-sm border border-neutral-200 rounded-lg bg-white hover:bg-neutral-50 text-neutral-600 transition-colors"
                title="Copy full transcript to clipboard"
            >
                {copied ? <Check className="w-4 h-4 text-primary-500" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy'}
            </button>

            {/* Export dropdown */}
            <div className="relative">
                <button
                    onClick={() => setOpen((v) => !v)}
                    className="flex items-center gap-1.5 px-3 py-2 text-sm bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors shadow-sm"
                >
                    <Download className="w-4 h-4" />
                    Export
                    <ChevronDown className="w-3.5 h-3.5" />
                </button>

                {open && (
                    <>
                        <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
                        <div className="absolute right-0 top-full mt-1 w-44 bg-white border border-neutral-100 rounded-xl shadow-lg z-20 overflow-hidden">
                            {([
                                { format: 'txt', label: 'Text (.txt)', Icon: FileText },
                                { format: 'pdf', label: 'PDF (.pdf)', Icon: File },
                                { format: 'docx', label: 'Word (.doc)', Icon: FileCode },
                                { format: 'srt', label: 'Subtitles (.srt)', Icon: FileCode },
                            ] as { format: ExportFormat; label: string; Icon: React.ElementType }[]).map(({ format, label, Icon }) => (
                                <button
                                    key={format}
                                    onClick={() => handleExport(format)}
                                    className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors text-left"
                                >
                                    <Icon className="w-4 h-4 text-neutral-400" />
                                    {label}
                                </button>
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
