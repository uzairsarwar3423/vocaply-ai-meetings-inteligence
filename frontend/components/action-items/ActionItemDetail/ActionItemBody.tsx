// ActionItemBody — main content area with metadata and description
'use client';

import React from 'react';
import { ActionItem } from '@/types/action-item';
import {
    User, Calendar, Clock, AlertCircle, Tag, Flag, Brain,
    Quote, CheckCircle2, XCircle,
} from 'lucide-react';

interface ActionItemBodyProps {
    item: ActionItem;
    isEditing: boolean;
}

function formatDate(isoStr?: string): string {
    if (!isoStr) return '—';
    const d = new Date(isoStr);
    return d.toLocaleDateString(undefined, { weekday: 'short', month: 'long', day: 'numeric', year: 'numeric' });
}

function getDueDateStatus(dueDate?: string): 'overdue' | 'due-soon' | 'upcoming' | null {
    if (!dueDate) return null;
    const due = new Date(dueDate);
    const now = new Date();
    const diffDays = (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
    if (diffDays < 0) return 'overdue';
    if (diffDays <= 2) return 'due-soon';
    return 'upcoming';
}

interface MetaRowProps {
    icon: React.ReactNode;
    label: string;
    value: React.ReactNode;
    danger?: boolean;
}

const MetaRow: React.FC<MetaRowProps> = ({ icon, label, value, danger }) => (
    <div className="flex items-start gap-3 py-3 border-b border-neutral-50 last:border-0">
        <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${danger ? 'bg-rose-50 text-rose-500' : 'bg-neutral-100 text-neutral-500'}`}>
            {icon}
        </div>
        <div className="flex-1 min-w-0">
            <p className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider mb-0.5">{label}</p>
            <div className="text-sm font-medium text-neutral-700">{value}</div>
        </div>
    </div>
);

export const ActionItemBody: React.FC<ActionItemBodyProps> = ({ item, isEditing }) => {
    const dueDateStatus = getDueDateStatus(item.due_date);
    const dueDanger = dueDateStatus === 'overdue';
    const dueDateClasses = {
        overdue: 'text-rose-600',
        'due-soon': 'text-amber-600',
        upcoming: 'text-neutral-700',
    };

    if (isEditing) return null; // Form takes over when editing

    return (
        <div className="space-y-6">
            {/* Description */}
            <div className="bg-white rounded-2xl border border-neutral-100 p-5">
                <h2 className="text-sm font-semibold text-neutral-500 uppercase tracking-wider mb-3">Description</h2>
                {item.description ? (
                    <p className="text-neutral-700 text-sm leading-relaxed whitespace-pre-wrap">{item.description}</p>
                ) : (
                    <p className="text-neutral-400 text-sm italic">No description added.</p>
                )}
            </div>

            {/* Metadata card */}
            <div className="bg-white rounded-2xl border border-neutral-100 p-5">
                <h2 className="text-sm font-semibold text-neutral-500 uppercase tracking-wider mb-2">Details</h2>

                <MetaRow
                    icon={<User className="w-3.5 h-3.5" />}
                    label="Assignee"
                    value={
                        item.assignee_name || item.assignee_email
                            ? (
                                <div className="flex items-center gap-2">
                                    <div className="w-5 h-5 bg-primary/10 rounded-full flex items-center justify-center text-[10px] font-bold text-primary">
                                        {(item.assignee_name || item.assignee_email || '?')[0].toUpperCase()}
                                    </div>
                                    <span>{item.assignee_name || item.assignee_email}</span>
                                </div>
                            )
                            : <span className="text-neutral-400">Unassigned</span>
                    }
                />

                <MetaRow
                    icon={<Calendar className="w-3.5 h-3.5" />}
                    label="Due Date"
                    danger={dueDanger}
                    value={
                        item.due_date
                            ? (
                                <span className={dueDateStatus ? dueDateClasses[dueDateStatus] : 'text-neutral-700'}>
                                    {formatDate(item.due_date)}
                                    {dueDateStatus === 'overdue' && (
                                        <span className="ml-2 inline-flex items-center gap-1 text-[10px] font-bold text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded-full">
                                            <AlertCircle className="w-2.5 h-2.5" /> OVERDUE
                                        </span>
                                    )}
                                    {dueDateStatus === 'due-soon' && (
                                        <span className="ml-2 text-[10px] font-bold text-amber-600">⚠ Due soon</span>
                                    )}
                                </span>
                            )
                            : <span className="text-neutral-400">No due date</span>
                    }
                />

                <MetaRow
                    icon={<Tag className="w-3.5 h-3.5" />}
                    label="Status"
                    value={<span className="capitalize">{item.status.replace('_', ' ')}</span>}
                />

                <MetaRow
                    icon={<Flag className="w-3.5 h-3.5" />}
                    label="Priority"
                    value={<span className="capitalize">{item.priority}</span>}
                />

                <MetaRow
                    icon={<Brain className="w-3.5 h-3.5" />}
                    label="Source"
                    value={
                        item.is_ai_generated
                            ? <span className="text-primary font-semibold">AI Generated · {Math.round((item.confidence_score || 0) * 100)}% confidence</span>
                            : 'Manually created'
                    }
                />

                <MetaRow
                    icon={<Clock className="w-3.5 h-3.5" />}
                    label="Last Updated"
                    value={formatDate(item.updated_at)}
                />

                {item.completed_at && (
                    <MetaRow
                        icon={<CheckCircle2 className="w-3.5 h-3.5" />}
                        label="Completed"
                        value={formatDate(item.completed_at)}
                    />
                )}
            </div>

            {/* Transcript quote */}
            {item.transcript_quote && (
                <div className="bg-white rounded-2xl border border-neutral-100 p-5">
                    <h2 className="text-sm font-semibold text-neutral-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Quote className="w-3.5 h-3.5" /> Source Quote
                    </h2>
                    <blockquote className="border-l-3 border-primary/30 pl-4 py-1">
                        <p className="text-sm text-neutral-600 italic leading-relaxed">&ldquo;{item.transcript_quote}&rdquo;</p>
                    </blockquote>
                    {item.transcript_start_time !== undefined && (
                        <p className="text-xs text-neutral-400 mt-2 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            At {Math.floor(item.transcript_start_time / 60)}:{(item.transcript_start_time % 60).toFixed(0).padStart(2, '0')} in the recording
                        </p>
                    )}
                </div>
            )}
        </div>
    );
};
