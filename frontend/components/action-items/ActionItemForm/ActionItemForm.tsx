// ActionItemForm — full inline edit form for all fields
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { ActionItem, ActionItemUpdate } from '@/types/action-item';
import { StatusBadge } from '../StatusBadge/StatusBadge';
import { PriorityBadge } from '../PriorityBadge/PriorityBadge';
import {
    Calendar, User, Flag, Tag, ChevronDown,
    Check, X, RotateCcw, ArrowDown, ArrowRight, ArrowUp, Zap,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

const STATUS_OPTIONS = [
    { value: 'pending', label: 'Pending', color: 'text-amber-700 bg-amber-50 border-amber-200' },
    { value: 'in_progress', label: 'In Progress', color: 'text-blue-700 bg-blue-50 border-blue-200' },
    { value: 'completed', label: 'Completed', color: 'text-emerald-700 bg-emerald-50 border-emerald-200' },
    { value: 'cancelled', label: 'Cancelled', color: 'text-neutral-500 bg-neutral-50 border-neutral-200' },
] as const;

const PRIORITY_OPTIONS: {
    value: 'low' | 'medium' | 'high' | 'urgent';
    label: string;
    Icon: LucideIcon;
    color: string;
}[] = [
        { value: 'low', label: 'Low', Icon: ArrowDown, color: 'text-neutral-500' },
        { value: 'medium', label: 'Medium', Icon: ArrowRight, color: 'text-amber-500' },
        { value: 'high', label: 'High', Icon: ArrowUp, color: 'text-orange-500' },
        { value: 'urgent', label: 'Urgent', Icon: Zap, color: 'text-rose-500' },
    ];

const DUE_DATE_PRESETS = [
    { label: 'Today', days: 0 },
    { label: 'Tomorrow', days: 1 },
    { label: 'In 3 days', days: 3 },
    { label: 'Next week', days: 7 },
    { label: 'In 2 weeks', days: 14 },
    { label: 'Next month', days: 30 },
];

interface ActionItemFormProps {
    item: ActionItem;
    onSave: (data: ActionItemUpdate) => Promise<void>;
    onCancel: () => void;
    isSaving?: boolean;
}

function addDays(days: number): string {
    const d = new Date();
    d.setDate(d.getDate() + days);
    return d.toISOString().split('T')[0];
}

function toInputDate(iso?: string): string {
    if (!iso) return '';
    return iso.split('T')[0];
}

export const ActionItemForm: React.FC<ActionItemFormProps> = ({
    item,
    onSave,
    onCancel,
    isSaving = false,
}) => {
    const [title, setTitle] = useState(item.title);
    const [description, setDescription] = useState(item.description || '');
    const [status, setStatus] = useState(item.status);
    const [priority, setPriority] = useState(item.priority);
    const [assigneeName, setAssigneeName] = useState(item.assignee_name || '');
    const [assigneeEmail, setAssigneeEmail] = useState(item.assignee_email || '');
    const [dueDate, setDueDate] = useState(toInputDate(item.due_date));
    const [showDatePresets, setShowDatePresets] = useState(false);
    const titleRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        titleRef.current?.focus();
    }, []);

    const isDirty =
        title !== item.title ||
        description !== (item.description || '') ||
        status !== item.status ||
        priority !== item.priority ||
        assigneeName !== (item.assignee_name || '') ||
        assigneeEmail !== (item.assignee_email || '') ||
        dueDate !== toInputDate(item.due_date);

    const handleReset = () => {
        setTitle(item.title);
        setDescription(item.description || '');
        setStatus(item.status);
        setPriority(item.priority);
        setAssigneeName(item.assignee_name || '');
        setAssigneeEmail(item.assignee_email || '');
        setDueDate(toInputDate(item.due_date));
    };

    const handleSave = async () => {
        if (!title.trim() || isSaving) return;
        const payload: ActionItemUpdate = {
            title: title.trim(),
            description: description.trim() || undefined,
            status,
            priority,
            assignee_name: assigneeName.trim() || undefined,
            assignee_email: assigneeEmail.trim() || undefined,
            due_date: dueDate ? new Date(dueDate).toISOString() : null,
        };
        await onSave(payload);
    };

    const inputBase = 'w-full bg-white border border-neutral-200 rounded-xl px-3 py-2.5 text-sm text-neutral-800 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-neutral-400';
    const labelBase = 'block text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-1.5';

    return (
        <div className="space-y-5">
            {/* Title */}
            <div>
                <label className={labelBase}>Title *</label>
                <input
                    ref={titleRef}
                    type="text"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    className={`${inputBase} font-semibold text-base`}
                    placeholder="Action item title"
                    maxLength={500}
                />
                {title.length > 450 && (
                    <p className="text-[10px] text-neutral-400 mt-1 text-right">{title.length}/500</p>
                )}
            </div>

            {/* Description */}
            <div>
                <label className={labelBase}>Description</label>
                <textarea
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                    className={`${inputBase} resize-none leading-relaxed`}
                    placeholder="Add a detailed description... supports plain text"
                    rows={4}
                    maxLength={2000}
                />
                <p className="text-[10px] text-neutral-400 mt-1 text-right">{description.length}/2000</p>
            </div>

            {/* Status & Priority row */}
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className={labelBase}><Tag className="inline w-3 h-3 mr-1" />Status</label>
                    <div className="relative">
                        <select
                            value={status}
                            onChange={e => setStatus(e.target.value as ActionItem['status'])}
                            className={`${inputBase} appearance-none pr-8 cursor-pointer`}
                        >
                            {STATUS_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 pointer-events-none" />
                    </div>
                </div>
                <div>
                    <label className={labelBase}><Flag className="inline w-3 h-3 mr-1" />Priority</label>
                    <div className="relative">
                        {/* Icon preview beside the select */}
                        {(() => {
                            const active = PRIORITY_OPTIONS.find(o => o.value === priority);
                            const ActiveIcon = active?.Icon ?? Flag;
                            return (
                                <ActiveIcon className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none ${active?.color ?? 'text-neutral-400'}`} />
                            );
                        })()}
                        <select
                            value={priority}
                            onChange={e => setPriority(e.target.value as ActionItem['priority'])}
                            className={`${inputBase} appearance-none pl-9 pr-8 cursor-pointer`}
                        >
                            {PRIORITY_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 pointer-events-none" />
                    </div>
                </div>
            </div>

            {/* Assignee */}
            <div>
                <label className={labelBase}><User className="inline w-3 h-3 mr-1" />Assignee</label>
                <div className="grid grid-cols-2 gap-3">
                    <input
                        type="text"
                        value={assigneeName}
                        onChange={e => setAssigneeName(e.target.value)}
                        placeholder="Full name"
                        className={inputBase}
                    />
                    <input
                        type="email"
                        value={assigneeEmail}
                        onChange={e => setAssigneeEmail(e.target.value)}
                        placeholder="email@company.com"
                        className={inputBase}
                    />
                </div>
            </div>

            {/* Due Date */}
            <div>
                <label className={labelBase}><Calendar className="inline w-3 h-3 mr-1" />Due Date</label>
                <div className="space-y-2">
                    <div className="flex items-center gap-2">
                        <input
                            type="date"
                            value={dueDate}
                            onChange={e => setDueDate(e.target.value)}
                            className={`${inputBase} flex-1`}
                            min={new Date().toISOString().split('T')[0]}
                        />
                        {dueDate && (
                            <button
                                onClick={() => setDueDate('')}
                                className="p-2.5 rounded-xl border border-neutral-200 text-neutral-400 hover:text-rose-500 hover:border-rose-200 transition-colors"
                                title="Clear due date"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        )}
                        <button
                            onClick={() => setShowDatePresets(v => !v)}
                            className={`px-3 py-2.5 rounded-xl border text-xs font-semibold transition-colors ${showDatePresets ? 'border-primary text-primary bg-primary/5' : 'border-neutral-200 text-neutral-500 hover:border-primary/30'}`}
                        >
                            Presets
                        </button>
                    </div>

                    {showDatePresets && (
                        <div className="flex flex-wrap gap-2">
                            {DUE_DATE_PRESETS.map(preset => (
                                <button
                                    key={preset.label}
                                    onClick={() => { setDueDate(addDays(preset.days)); setShowDatePresets(false); }}
                                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition-colors ${dueDate === addDays(preset.days)
                                        ? 'border-primary bg-primary/10 text-primary'
                                        : 'border-neutral-200 text-neutral-600 hover:border-primary/30 hover:bg-primary/5'
                                        }`}
                                >
                                    {preset.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-between pt-2 border-t border-neutral-100">
                <button
                    onClick={handleReset}
                    disabled={!isDirty}
                    className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-neutral-500 rounded-lg hover:bg-neutral-100 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                >
                    <RotateCcw className="w-3.5 h-3.5" /> Undo changes
                </button>
                <div className="flex gap-2">
                    <button
                        onClick={onCancel}
                        className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-neutral-600 rounded-xl border border-neutral-200 hover:bg-neutral-50 transition-colors"
                    >
                        <X className="w-4 h-4" /> Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={!title.trim() || isSaving}
                        className="flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-primary rounded-xl hover:bg-primary/90 transition-all shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/25 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSaving
                            ? <><div className="w-4 h-4 border-2 border-white/50 border-t-white rounded-full animate-spin" /> Saving…</>
                            : <><Check className="w-4 h-4" /> Save Changes</>
                        }
                    </button>
                </div>
            </div>
        </div>
    );
};
