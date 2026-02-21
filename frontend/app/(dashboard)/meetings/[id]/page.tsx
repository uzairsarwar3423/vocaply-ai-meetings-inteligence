"use client";

import React, { use } from 'react';
import { useRouter } from 'next/navigation';
import { useMeeting } from '@/hooks/useMeeting';
import { useMeetingSummary } from '@/hooks/useMeetingSummary';
import { StatusBadge } from '@/components/meetings/StatusBadge/StatusBadge';
import { MeetingSummary } from '@/components/meetings/MeetingSummary';
import { SummaryExport } from '@/components/meetings/SummaryExport/SummaryExport';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Video, Calendar, Clock, FileText, Download, UploadCloud, Brain, Sparkles } from 'lucide-react';
import { formatDuration } from '@/utils/formatters';
import FileUploader from '@/components/meetings/FileUploader/FileUploader';

interface MeetingDetailPageProps {
    params: Promise<{ id: string }>;
}

export default function MeetingDetail({ params }: MeetingDetailPageProps) {
    const { id } = use(params);
    const router = useRouter();
    const { meeting, isLoading, error } = useMeeting(id);
    const {
        summary,
        isLoading: isSummaryLoading,
        isGenerating: isSummaryGenerating,
        triggerGenerate,
        triggerRegenerate,
        editSummary,
    } = useMeetingSummary(id);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                <span className="text-neutral-500 font-medium">Loading meeting data...</span>
            </div>
        );
    }

    if (error || !meeting) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
                <h2 className="text-xl font-semibold text-neutral-900">Meeting Not Found</h2>
                <Button variant="outline" onClick={() => router.push('/meetings')}>
                    <ArrowLeft className="w-4 h-4 mr-2" /> Back to Meetings
                </Button>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8 max-w-5xl">
            <Button
                variant="ghost"
                className="mb-6 -ml-2 text-neutral-500 hover:text-neutral-900"
                onClick={() => router.push('/meetings')}
            >
                <ArrowLeft className="w-4 h-4 mr-2" /> Back to Meetings
            </Button>

            <div className="bg-white rounded-2xl shadow-sm border border-neutral-100 overflow-hidden">
                <div className="p-8 border-b border-neutral-100">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <h1 className="text-2xl font-bold font-outfit text-neutral-900">{meeting.title}</h1>
                                <StatusBadge status={meeting.status} />
                            </div>
                            <div className="flex flex-wrap text-sm text-neutral-500 gap-4 mt-1">
                                <div className="flex items-center gap-1.5">
                                    <Video className="w-4 h-4" />
                                    <span className="capitalize">{meeting.platform.replace('_', ' ')}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <Calendar className="w-4 h-4" />
                                    <span>{new Date(meeting.startTime).toLocaleDateString()}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <Clock className="w-4 h-4" />
                                    <span>
                                        {new Date(meeting.startTime).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })} -
                                        {meeting.endTime ? new Date(meeting.endTime).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : formatDuration(meeting.duration || 0)}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div className="flex gap-3">
                            <Button variant="outline">
                                <Download className="w-4 h-4 mr-2" /> Export
                            </Button>
                            <Button variant="outline" onClick={() => router.push(`/meetings/${meeting.id}/transcripts`)}>
                                <FileText className="w-4 h-4 mr-2" /> View Transcript
                            </Button>
                            <Button>
                                View Recording
                            </Button>
                        </div>
                    </div>
                </div>

                <div className="p-8 grid md:grid-cols-3 gap-8">
                    <div className="md:col-span-2 space-y-6">
                        {meeting.description && (
                            <section>
                                <h3 className="text-sm font-semibold text-neutral-900 uppercase tracking-wider mb-2">About</h3>
                                <p className="text-neutral-600 leading-relaxed text-sm">
                                    {meeting.description}
                                </p>
                            </section>
                        )}

                        <section className="bg-neutral-50 rounded-xl p-6 border border-dashed border-neutral-200">
                            <h3 className="flex items-center text-sm font-semibold text-neutral-900 uppercase tracking-wider mb-4">
                                <UploadCloud className="w-4 h-4 mr-2 text-primary-500" />
                                Upload Recording
                            </h3>
                            <FileUploader
                                meetingId={meeting.id}
                                onSuccess={(file) => {
                                    console.log("File uploaded successfully:", file);
                                    // TODO: Trigger meeting status update or transcription
                                    window.location.reload(); // Simple reload to fetch updated meeting state
                                }}
                            />
                        </section>

                        {/* ── AI Summary Section ── */}
                        <section>
                            <h3 className="flex items-center text-sm font-bold text-neutral-900 uppercase tracking-wider mb-4">
                                <Brain className="w-4 h-4 mr-2 text-primary" />
                                AI Meeting Summary
                            </h3>

                            {summary ? (
                                <>
                                    <MeetingSummary
                                        summary={summary}
                                        isLoading={isSummaryGenerating}
                                        onRegenerate={triggerRegenerate}
                                        onExport={(fmt) => {
                                            // handled inside SummaryExport
                                        }}
                                    />
                                    <div className="mt-4">
                                        <SummaryExport
                                            summaryId={summary.id}
                                            meetingTitle={meeting.title}
                                        />
                                    </div>
                                </>
                            ) : isSummaryLoading || isSummaryGenerating ? (
                                <MeetingSummary summary={null as any} isLoading />
                            ) : (
                                <div className="bg-gradient-to-br from-primary/5 to-violet-50 rounded-3xl border border-primary/10 p-8 text-center">
                                    <div className="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                        <Sparkles className="w-7 h-7 text-primary" />
                                    </div>
                                    <h4 className="font-bold text-neutral-800 mb-1">No Summary Yet</h4>
                                    <p className="text-sm text-neutral-500 mb-5">
                                        Generate an AI summary from your meeting transcript.
                                    </p>
                                    <Button
                                        onClick={triggerGenerate}
                                        className="px-6 py-2.5 bg-primary text-white font-bold rounded-2xl shadow-primary hover:shadow-xl transition-all"
                                    >
                                        <Brain className="w-4 h-4 mr-2" />
                                        Generate AI Summary
                                    </Button>
                                </div>
                            )}
                        </section>
                    </div>

                    <div className="space-y-6">
                        <section>
                            <h3 className="text-sm font-semibold text-neutral-900 uppercase tracking-wider mb-4">Attendees ({meeting.attendees.length})</h3>
                            <div className="space-y-3">
                                {meeting.attendees.map((attendee, i) => (
                                    <div key={i} className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-secondary-100 text-secondary-700 flex items-center justify-center text-xs font-bold ring-2 ring-white">
                                            {typeof attendee === 'string' ? attendee.slice(0, 2).toUpperCase() : attendee.email.slice(0, 2).toUpperCase()}
                                        </div>
                                        <span className="text-sm text-neutral-700 truncate" title={typeof attendee === 'string' ? attendee : attendee.email}>
                                            {typeof attendee === 'string' ? attendee : attendee.name || attendee.email}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </div>
    );
}
