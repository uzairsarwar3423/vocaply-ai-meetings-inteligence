// ActionItemDetail — orchestrator for the full detail view
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ActionItem, ActionItemUpdate } from '@/types/action-item';
import { ActionItemHeader } from './ActionItemHeader';
import { ActionItemBody } from './ActionItemBody';
import { ActionItemForm } from '../ActionItemForm/ActionItemForm';
import { CommentSection } from '../CommentSection/CommentSection';
import { RelatedMeeting } from '../RelatedMeeting/RelatedMeeting';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { useComments } from '@/hooks/useComments';
import { useAuthStore } from '@/store/authStore';
import { Loader2, AlertTriangle, X, Keyboard } from 'lucide-react';

interface ActionItemDetailProps {
    item: ActionItem;
    onUpdate: (id: string, data: ActionItemUpdate) => Promise<void>;
    onDelete: (id: string) => Promise<void>;
    isLoading?: boolean;
    error?: string | null;
}

// Delete confirmation modal
const DeleteModal: React.FC<{ onConfirm: () => void; onCancel: () => void; isDeleting: boolean }> = ({
    onConfirm, onCancel, isDeleting,
}) => (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 p-6 animate-in fade-in zoom-in-95 duration-200">
            <div className="w-12 h-12 bg-rose-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-6 h-6 text-rose-500" />
            </div>
            <h3 className="text-lg font-bold text-neutral-900 text-center mb-2">Delete Action Item?</h3>
            <p className="text-sm text-neutral-500 text-center mb-6">This action cannot be undone. The action item will be permanently removed.</p>
            <div className="flex gap-3">
                <button
                    onClick={onCancel}
                    className="flex-1 py-2.5 font-semibold text-sm border border-neutral-200 rounded-xl hover:bg-neutral-50 transition-colors"
                >
                    Cancel
                </button>
                <button
                    onClick={onConfirm}
                    disabled={isDeleting}
                    className="flex-1 py-2.5 font-semibold text-sm bg-rose-500 text-white rounded-xl hover:bg-rose-600 transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
                >
                    {isDeleting
                        ? <><Loader2 className="w-4 h-4 animate-spin" /> Deleting…</>
                        : 'Delete'
                    }
                </button>
            </div>
        </div>
    </div>
);

// Keyboard shortcuts toast
const ShortcutsToast: React.FC<{ onClose: () => void }> = ({ onClose }) => (
    <div className="fixed bottom-6 right-6 z-40 bg-neutral-900 text-white rounded-2xl shadow-2xl p-4 w-64 animate-in slide-in-from-bottom-4 duration-300">
        <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
                <Keyboard className="w-4 h-4 text-neutral-400" />
                <span className="text-xs font-bold text-neutral-300 uppercase tracking-wider">Keyboard Shortcuts</span>
            </div>
            <button onClick={onClose} className="text-neutral-500 hover:text-white transition-colors">
                <X className="w-3.5 h-3.5" />
            </button>
        </div>
        <div className="space-y-1.5 text-xs">
            {[
                { key: 'E', desc: 'Edit action item' },
                { key: 'C', desc: 'Focus comment box' },
                { key: '?', desc: 'Show shortcuts' },
                { key: 'Esc', desc: 'Cancel editing' },
            ].map(sk => (
                <div key={sk.key} className="flex items-center justify-between">
                    <span className="text-neutral-400">{sk.desc}</span>
                    <kbd className="bg-neutral-800 border border-neutral-700 px-1.5 py-0.5 rounded text-[10px] font-mono">{sk.key}</kbd>
                </div>
            ))}
        </div>
    </div>
);

export const ActionItemDetail: React.FC<ActionItemDetailProps> = ({
    item,
    onUpdate,
    onDelete,
    isLoading = false,
    error = null,
}) => {
    const router = useRouter();
    const { user } = useAuthStore();
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [showShortcuts, setShowShortcuts] = useState(false);
    const [saveError, setSaveError] = useState<string | null>(null);

    const currentUserName = user?.full_name || 'You';
    const currentUserEmail = user?.email || 'user@vocaply.com';

    const {
        comments,
        activity,
        isSubmitting: isCommentSubmitting,
        addComment,
        editComment,
        deleteComment,
        addActivity,
    } = useComments(item.id, currentUserName, currentUserEmail);

    // Register initial "created" activity
    useEffect(() => {
        addActivity({
            action_item_id: item.id,
            actor_name: 'System',
            actor_email: '',
            action: 'created',
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Keyboard shortcuts
    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            const tag = (e.target as HTMLElement).tagName;
            const editable = tag === 'INPUT' || tag === 'TEXTAREA' || (e.target as HTMLElement).isContentEditable;

            if (e.key === '?' && !editable) {
                setShowShortcuts(v => !v);
                return;
            }
            if (e.key === 'Escape') {
                setIsEditing(false);
                setShowShortcuts(false);
                return;
            }
            if (editable) return;

            if (e.key === 'e' || e.key === 'E') {
                e.preventDefault();
                setIsEditing(true);
            }
            if (e.key === 'c' || e.key === 'C') {
                e.preventDefault();
                document.querySelector<HTMLTextAreaElement>('textarea[placeholder*="comment"]')?.focus();
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, []);

    const handleSave = useCallback(async (data: ActionItemUpdate) => {
        setIsSaving(true);
        setSaveError(null);
        try {
            await onUpdate(item.id, data);
            // Track what changed in activity log
            if (data.status && data.status !== item.status) {
                addActivity({ action_item_id: item.id, actor_name: currentUserName, actor_email: currentUserEmail, action: 'status_changed', old_value: item.status, new_value: data.status });
            }
            if (data.priority && data.priority !== item.priority) {
                addActivity({ action_item_id: item.id, actor_name: currentUserName, actor_email: currentUserEmail, action: 'priority_changed', old_value: item.priority, new_value: data.priority });
            }
            if (data.title && data.title !== item.title) {
                addActivity({ action_item_id: item.id, actor_name: currentUserName, actor_email: currentUserEmail, action: 'title_edited' });
            }
            if (data.description !== undefined && data.description !== item.description) {
                addActivity({ action_item_id: item.id, actor_name: currentUserName, actor_email: currentUserEmail, action: 'description_edited' });
            }
            if (data.due_date !== undefined && data.due_date !== item.due_date) {
                addActivity({ action_item_id: item.id, actor_name: currentUserName, actor_email: currentUserEmail, action: 'due_date_changed', new_value: data.due_date || 'removed' });
            }
            setIsEditing(false);
        } catch {
            setSaveError('Failed to save changes. Please try again.');
        } finally {
            setIsSaving(false);
        }
    }, [item, onUpdate, addActivity, currentUserName, currentUserEmail]);

    const handleToggleComplete = useCallback(async () => {
        const newStatus = item.status === 'completed' ? 'pending' : 'completed';
        await handleSave({ status: newStatus });
    }, [item.status, handleSave]);

    const handleDelete = useCallback(async () => {
        setIsDeleting(true);
        try {
            await onDelete(item.id);
            router.push('/action-items');
        } catch {
            setIsDeleting(false);
            setShowDeleteModal(false);
        }
    }, [item.id, onDelete, router]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-3" />
                    <p className="text-sm text-neutral-500">Loading action item…</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto mb-3" />
                    <p className="text-sm text-neutral-600 font-medium">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <>
            {/* Header */}
            <ActionItemHeader
                item={item}
                isEditing={isEditing}
                isSaving={isSaving}
                onEdit={() => setIsEditing(true)}
                onDelete={() => setShowDeleteModal(true)}
                onToggleComplete={handleToggleComplete}
            />

            {/* Body */}
            <div className="max-w-5xl mx-auto px-6 py-8">
                {/* Save error */}
                {saveError && (
                    <div className="flex items-center gap-2 mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-sm text-rose-700">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                        {saveError}
                        <button onClick={() => setSaveError(null)} className="ml-auto"><X className="w-4 h-4" /></button>
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main column */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Edit form or body view */}
                        {isEditing ? (
                            <div className="bg-white rounded-2xl border border-primary/20 p-5 shadow-sm ring-1 ring-primary/5">
                                <h2 className="text-sm font-bold text-neutral-700 uppercase tracking-wider mb-4">Editing Action Item</h2>
                                <ActionItemForm
                                    item={item}
                                    onSave={handleSave}
                                    onCancel={() => setIsEditing(false)}
                                    isSaving={isSaving}
                                />
                            </div>
                        ) : (
                            <ActionItemBody item={item} isEditing={false} />
                        )}

                        {/* Comments & Activity */}
                        <CommentSection
                            comments={comments}
                            activity={activity}
                            isSubmitting={isCommentSubmitting}
                            currentUserEmail={currentUserEmail}
                            onAddComment={addComment}
                            onEditComment={editComment}
                            onDeleteComment={deleteComment}
                        />
                    </div>

                    {/* Sidebar column */}
                    <div className="space-y-4">
                        {/* AI Confidence */}
                        {item.is_ai_generated && item.confidence_score !== undefined && (
                            <div className="bg-white rounded-2xl border border-neutral-100 p-4">
                                <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">AI Analysis</p>
                                <ConfidenceIndicator score={item.confidence_score} size="md" />
                            </div>
                        )}

                        {/* Related meeting */}
                        <RelatedMeeting
                            meetingId={item.meeting_id}
                            transcriptStartTime={item.transcript_start_time}
                            transcriptQuote={item.transcript_quote}
                        />

                        {/* Keyboard shortcuts hint */}
                        <button
                            onClick={() => setShowShortcuts(v => !v)}
                            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl border border-neutral-100 text-xs text-neutral-400 hover:text-neutral-600 hover:bg-neutral-50 transition-colors"
                        >
                            <Keyboard className="w-3.5 h-3.5" />
                            Keyboard shortcuts (?)
                        </button>
                    </div>
                </div>
            </div>

            {/* Modals */}
            {showDeleteModal && (
                <DeleteModal
                    onConfirm={handleDelete}
                    onCancel={() => setShowDeleteModal(false)}
                    isDeleting={isDeleting}
                />
            )}

            {showShortcuts && (
                <ShortcutsToast onClose={() => setShowShortcuts(false)} />
            )}
        </>
    );
};
