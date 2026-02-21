// ActionItemCard — single card component
'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ActionItem, ActionItemUpdate } from '@/types/action-item';
import { StatusBadge } from '../StatusBadge/StatusBadge';
import { PriorityBadge } from '../PriorityBadge/PriorityBadge';
import { ActionItemMenu } from './ActionItemMenu';
import {
    Calendar, User, CheckCircle2, Brain, Quote,
    ExternalLink, Clock,
} from 'lucide-react';

// ── Helpers ────────────────────────────────────────────────────────

function getDueDateStatus(dueDate?: string): 'overdue' | 'due-soon' | 'upcoming' | null {
    if (!dueDate) return null;
    const due = new Date(dueDate);
    const now = new Date();
    const diffDays = (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
    if (diffDays < 0) return 'overdue';
    if (diffDays <= 2) return 'due-soon';
    return 'upcoming';
}

function formatDueDate(dueDate: string): string {
    const due = new Date(dueDate);
    const now = new Date();
    const diffDays = Math.floor((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return 'Due tomorrow';
    if (diffDays === -1) return '1 day overdue';
    if (diffDays < 0) return `${Math.abs(diffDays)}d overdue`;
    if (diffDays < 7) return `${diffDays}d left`;
    return due.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function getInitials(name?: string, email?: string): string {
    if (name) return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    if (email) return email[0].toUpperCase();
    return '?';
}

// ── Props ──────────────────────────────────────────────────────────

interface ActionItemCardProps {
    item: ActionItem;
    isSelected?: boolean;
    onToggleSelect?: (id: string) => void;
    onUpdate: (id: string, data: ActionItemUpdate) => void;
    onDelete: (id: string) => void;
    onAccept?: (id: string) => void;
    onReject?: (id: string) => void;
    draggable?: boolean;
    onDragStart?: (e: React.DragEvent) => void;
    onDragEnd?: () => void;
    viewMode?: 'kanban' | 'list';
}

// ── Component ──────────────────────────────────────────────────────

export const ActionItemCard: React.FC<ActionItemCardProps> = ({
    item,
    isSelected = false,
    onToggleSelect,
    onUpdate,
    onDelete,
    onAccept,
    onReject,
    draggable = false,
    onDragStart,
    onDragEnd,
    viewMode = 'kanban',
}) => {
    const [expanded, setExpanded] = useState(false);
    const dueDateStatus = getDueDateStatus(item.due_date);
    const isCompleted = item.status === 'completed';

    const dueDateClasses = {
        overdue: 'text-rose-600 bg-rose-50 border-rose-200',
        'due-soon': 'text-amber-600 bg-amber-50 border-amber-200',
        upcoming: 'text-neutral-500 bg-neutral-50 border-neutral-200',
    };

    const cardClasses = [
        'bg-white rounded-2xl border transition-all duration-200 group relative',
        viewMode === 'list' ? 'flex items-center gap-4 px-5 py-3.5 hover:shadow-md' : 'p-4 hover:shadow-lg hover:-translate-y-0.5',
        isSelected ? 'border-primary ring-2 ring-primary/20' : 'border-neutral-100 hover:border-neutral-200',
        isCompleted ? 'opacity-60' : '',
    ].join(' ');

    // ── LIST VIEW ───────────────────────────────────────────────────
    if (viewMode === 'list') {
        return (
            <div
                className={cardClasses}
                draggable={draggable}
                onDragStart={onDragStart}
                onDragEnd={onDragEnd}
            >
                {/* Checkbox */}
                {onToggleSelect && (
                    <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => onToggleSelect(item.id)}
                        onClick={e => e.stopPropagation()}
                        className="w-4 h-4 rounded accent-primary flex-shrink-0 cursor-pointer"
                    />
                )}

                {/* Quick complete */}
                <button
                    onClick={() => onUpdate(item.id, {
                        status: item.status === 'completed' ? 'pending' : 'completed'
                    })}
                    className={`flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${isCompleted
                            ? 'border-emerald-500 bg-emerald-500 text-white'
                            : 'border-neutral-300 hover:border-emerald-500'
                        }`}
                    title="Toggle complete"
                >
                    {isCompleted && <CheckCircle2 className="w-3 h-3" />}
                </button>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className={`font-semibold text-sm text-neutral-800 truncate ${isCompleted ? 'line-through text-neutral-400' : ''}`}>
                            {item.title}
                        </span>
                        {item.is_ai_generated && (
                            <span title={`AI confidence: ${Math.round((item.confidence_score || 0) * 100)}%`}>
                                <Brain className="w-3.5 h-3.5 text-primary/60 flex-shrink-0" />
                            </span>
                        )}
                    </div>
                </div>

                {/* Meta */}
                <div className="flex items-center gap-3 flex-shrink-0">
                    <PriorityBadge priority={item.priority} size="sm" />
                    <StatusBadge status={item.status} size="sm" />

                    {item.due_date && dueDateStatus && (
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${dueDateClasses[dueDateStatus]}`}>
                            {formatDueDate(item.due_date)}
                        </span>
                    )}

                    {(item.assignee_name || item.assignee_email) && (
                        <div
                            className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center text-[10px] font-bold text-primary flex-shrink-0"
                            title={item.assignee_name || item.assignee_email}
                        >
                            {getInitials(item.assignee_name, item.assignee_email)}
                        </div>
                    )}

                    <ActionItemMenu
                        item={item}
                        onUpdate={onUpdate}
                        onDelete={onDelete}
                        onAccept={onAccept}
                        onReject={onReject}
                    />
                </div>

                {/* Meeting link */}
                <Link
                    href={`/meetings/${item.meeting_id}`}
                    onClick={e => e.stopPropagation()}
                    className="flex-shrink-0 text-neutral-300 hover:text-primary transition-colors opacity-0 group-hover:opacity-100"
                    title="View meeting"
                >
                    <ExternalLink className="w-3.5 h-3.5" />
                </Link>
            </div>
        );
    }

    // ── KANBAN CARD VIEW ─────────────────────────────────────────────
    return (
        <div
            className={cardClasses}
            draggable={draggable}
            onDragStart={onDragStart}
            onDragEnd={onDragEnd}
        >
            {/* Top row */}
            <div className="flex items-start justify-between gap-2 mb-2.5">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                    {onToggleSelect && (
                        <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => onToggleSelect(item.id)}
                            onClick={e => e.stopPropagation()}
                            className="w-3.5 h-3.5 rounded accent-primary flex-shrink-0 cursor-pointer mt-0.5"
                        />
                    )}
                    <PriorityBadge priority={item.priority} size="sm" />
                </div>

                <div className="flex items-center gap-1">
                    {item.is_ai_generated && (
                        <span
                            className="inline-flex items-center gap-1 text-[9px] bg-primary/8 text-primary px-1.5 py-0.5 rounded-full font-semibold border border-primary/15"
                            title={`AI confidence: ${Math.round((item.confidence_score || 0) * 100)}%`}
                        >
                            <Brain className="w-2.5 h-2.5" />
                            {Math.round((item.confidence_score || 0) * 100)}%
                        </span>
                    )}
                    <ActionItemMenu
                        item={item}
                        onUpdate={onUpdate}
                        onDelete={onDelete}
                        onAccept={onAccept}
                        onReject={onReject}
                    />
                </div>
            </div>

            {/* Title + quick complete */}
            <div className="flex items-start gap-2 mb-2.5">
                <button
                    onClick={() => onUpdate(item.id, {
                        status: item.status === 'completed' ? 'pending' : 'completed'
                    })}
                    className={`flex-shrink-0 mt-0.5 w-4.5 h-4.5 rounded-full border-2 flex items-center justify-center transition-all ${isCompleted
                            ? 'border-emerald-500 bg-emerald-500 text-white'
                            : 'border-neutral-300 hover:border-emerald-500'
                        }`}
                    style={{ width: 18, height: 18 }}
                    title="Toggle complete"
                >
                    {isCompleted && <CheckCircle2 className="w-2.5 h-2.5" />}
                </button>

                <p
                    className={`text-sm font-semibold leading-snug ${isCompleted ? 'line-through text-neutral-400' : 'text-neutral-800'
                        }`}
                >
                    {item.title}
                </p>
            </div>

            {/* Description (collapsible) */}
            {item.description && (
                <p
                    className={`text-xs text-neutral-500 mb-2.5 leading-relaxed ${expanded ? '' : 'line-clamp-2'
                        } cursor-pointer`}
                    onClick={() => setExpanded(e => !e)}
                >
                    {item.description}
                </p>
            )}

            {/* Transcript quote */}
            {item.transcript_quote && expanded && (
                <div className="bg-neutral-50 rounded-lg p-2.5 mb-2.5 border border-neutral-100">
                    <div className="flex items-start gap-1.5">
                        <Quote className="w-3 h-3 text-neutral-400 flex-shrink-0 mt-0.5" />
                        <p className="text-[11px] text-neutral-500 italic line-clamp-3">
                            {item.transcript_quote}
                        </p>
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between gap-2 mt-auto pt-2.5 border-t border-neutral-50">
                {/* Assignee */}
                {(item.assignee_name || item.assignee_email) ? (
                    <div className="flex items-center gap-1.5">
                        <div
                            className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-[10px] font-bold text-primary"
                            title={item.assignee_name || item.assignee_email}
                        >
                            {getInitials(item.assignee_name, item.assignee_email)}
                        </div>
                        <span className="text-[11px] text-neutral-500 max-w-[80px] truncate">
                            {item.assignee_name || item.assignee_email?.split('@')[0]}
                        </span>
                    </div>
                ) : (
                    <span className="text-[11px] text-neutral-400 flex items-center gap-1">
                        <User className="w-3 h-3" /> Unassigned
                    </span>
                )}

                {/* Due date */}
                {item.due_date && dueDateStatus ? (
                    <span className={`inline-flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded-full border ${dueDateClasses[dueDateStatus]}`}>
                        <Clock className="w-2.5 h-2.5" />
                        {formatDueDate(item.due_date)}
                    </span>
                ) : (
                    <Link
                        href={`/meetings/${item.meeting_id}`}
                        onClick={e => e.stopPropagation()}
                        className="text-neutral-300 hover:text-primary transition-colors opacity-0 group-hover:opacity-100"
                        title="View meeting"
                    >
                        <ExternalLink className="w-3.5 h-3.5" />
                    </Link>
                )}
            </div>
        </div>
    );
};
