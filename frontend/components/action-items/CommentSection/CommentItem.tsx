// CommentItem — renders a single comment
'use client';

import React, { useState } from 'react';
import { Comment } from '@/hooks/useComments';
import { MoreHorizontal, Edit3, Trash2, Check, X } from 'lucide-react';

interface CommentItemProps {
    comment: Comment;
    currentUserEmail: string;
    onEdit: (id: string, content: string) => Promise<void>;
    onDelete: (id: string) => Promise<void>;
}

function timeAgo(dateStr: string): string {
    const now = new Date();
    const past = new Date(dateStr);
    const diffMs = now.getTime() - past.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    if (diffSecs < 60) return 'just now';
    const diffMins = Math.floor(diffSecs / 60);
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;
    return past.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function renderContent(content: string): React.ReactNode {
    // Highlight @mentions
    const parts = content.split(/(@\S+)/g);
    return parts.map((part, i) =>
        part.startsWith('@')
            ? <span key={i} className="text-primary font-semibold">{part}</span>
            : <span key={i}>{part}</span>
    );
}

export const CommentItem: React.FC<CommentItemProps> = ({
    comment,
    currentUserEmail,
    onEdit,
    onDelete,
}) => {
    const isOwn = comment.author_email === currentUserEmail;
    const [isEditing, setIsEditing] = useState(false);
    const [editText, setEditText] = useState(comment.content);
    const [menuOpen, setMenuOpen] = useState(false);
    const [saving, setSaving] = useState(false);

    const handleSave = async () => {
        if (!editText.trim() || editText === comment.content) {
            setIsEditing(false);
            return;
        }
        setSaving(true);
        await onEdit(comment.id, editText.trim());
        setSaving(false);
        setIsEditing(false);
    };

    return (
        <div className="flex items-start gap-3 group">
            {/* Avatar */}
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary flex-shrink-0">
                {comment.author_initials}
            </div>

            <div className="flex-1 min-w-0">
                {/* Header */}
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-neutral-800">{comment.author_name}</span>
                    <span className="text-[10px] text-neutral-400">{timeAgo(comment.created_at)}</span>
                    {comment.is_edited && (
                        <span className="text-[10px] text-neutral-400 italic">(edited)</span>
                    )}
                </div>

                {/* Content / Edit mode */}
                {isEditing ? (
                    <div className="space-y-2">
                        <textarea
                            value={editText}
                            onChange={e => setEditText(e.target.value)}
                            className="w-full text-sm text-neutral-700 bg-white border border-primary rounded-xl px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-primary/20"
                            rows={2}
                            autoFocus
                            onKeyDown={e => {
                                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSave(); }
                                if (e.key === 'Escape') setIsEditing(false);
                            }}
                        />
                        <div className="flex gap-2">
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="flex items-center gap-1 px-2.5 py-1 bg-primary text-white text-xs font-semibold rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                            >
                                <Check className="w-3 h-3" /> Save
                            </button>
                            <button
                                onClick={() => setIsEditing(false)}
                                className="flex items-center gap-1 px-2.5 py-1 bg-neutral-100 text-neutral-600 text-xs font-semibold rounded-lg hover:bg-neutral-200 transition-colors"
                            >
                                <X className="w-3 h-3" /> Cancel
                            </button>
                        </div>
                    </div>
                ) : (
                    <p className="text-sm text-neutral-600 leading-relaxed">
                        {renderContent(comment.content)}
                    </p>
                )}
            </div>

            {/* Actions (only for own comments) */}
            {isOwn && !isEditing && (
                <div className="relative opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                    <button
                        onClick={() => setMenuOpen(v => !v)}
                        className="p-1 rounded-lg hover:bg-neutral-100 transition-colors"
                    >
                        <MoreHorizontal className="w-3.5 h-3.5 text-neutral-400" />
                    </button>
                    {menuOpen && (
                        <div className="absolute right-0 top-7 w-36 bg-white rounded-xl shadow-lg border border-neutral-100 z-20 overflow-hidden">
                            <button
                                className="flex items-center gap-2 w-full px-3 py-2 text-xs text-neutral-600 hover:bg-neutral-50 transition-colors"
                                onClick={() => { setIsEditing(true); setMenuOpen(false); }}
                            >
                                <Edit3 className="w-3.5 h-3.5" /> Edit
                            </button>
                            <button
                                className="flex items-center gap-2 w-full px-3 py-2 text-xs text-rose-600 hover:bg-rose-50 transition-colors"
                                onClick={() => { onDelete(comment.id); setMenuOpen(false); }}
                            >
                                <Trash2 className="w-3.5 h-3.5" /> Delete
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
