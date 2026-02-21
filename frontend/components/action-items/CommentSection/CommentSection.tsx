// CommentSection — full comments & activity panel
'use client';

import React, { useState } from 'react';
import { MessageSquare, Activity } from 'lucide-react';
import { CommentItem } from './CommentItem';
import { CommentForm } from './CommentForm';
import type { Comment, ActivityEntry } from '@/hooks/useComments';

interface CommentSectionProps {
    comments: Comment[];
    activity: ActivityEntry[];
    isSubmitting: boolean;
    currentUserEmail: string;
    onAddComment: (content: string, mentions?: string[]) => Promise<void>;
    onEditComment: (id: string, content: string) => Promise<void>;
    onDeleteComment: (id: string) => Promise<void>;
}

type Tab = 'comments' | 'activity';

export const CommentSection: React.FC<CommentSectionProps> = ({
    comments,
    activity,
    isSubmitting,
    currentUserEmail,
    onAddComment,
    onEditComment,
    onDeleteComment,
}) => {
    const [tab, setTab] = useState<Tab>('comments');

    return (
        <div className="rounded-2xl border border-neutral-100 bg-white overflow-hidden">
            {/* Tab bar */}
            <div className="flex border-b border-neutral-100">
                <button
                    onClick={() => setTab('comments')}
                    className={`flex items-center gap-2 px-5 py-3.5 text-sm font-semibold transition-colors border-b-2 -mb-px ${tab === 'comments'
                            ? 'border-primary text-primary'
                            : 'border-transparent text-neutral-500 hover:text-neutral-700'
                        }`}
                >
                    <MessageSquare className="w-4 h-4" />
                    Comments
                    {comments.length > 0 && (
                        <span className="bg-primary/10 text-primary text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                            {comments.length}
                        </span>
                    )}
                </button>
                <button
                    onClick={() => setTab('activity')}
                    className={`flex items-center gap-2 px-5 py-3.5 text-sm font-semibold transition-colors border-b-2 -mb-px ${tab === 'activity'
                            ? 'border-primary text-primary'
                            : 'border-transparent text-neutral-500 hover:text-neutral-700'
                        }`}
                >
                    <Activity className="w-4 h-4" />
                    Activity
                    {activity.length > 0 && (
                        <span className="bg-neutral-100 text-neutral-600 text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                            {activity.length}
                        </span>
                    )}
                </button>
            </div>

            <div className="p-4">
                {tab === 'comments' ? (
                    <div className="space-y-4">
                        {/* Comment list */}
                        {comments.length === 0 ? (
                            <div className="text-center py-8">
                                <MessageSquare className="w-8 h-8 text-neutral-200 mx-auto mb-2" />
                                <p className="text-sm text-neutral-400">No comments yet. Be the first!</p>
                            </div>
                        ) : (
                            <div className="space-y-4 mb-4">
                                {comments.map(comment => (
                                    <CommentItem
                                        key={comment.id}
                                        comment={comment}
                                        currentUserEmail={currentUserEmail}
                                        onEdit={onEditComment}
                                        onDelete={onDeleteComment}
                                    />
                                ))}
                            </div>
                        )}

                        {/* Comment form */}
                        <CommentForm
                            onSubmit={onAddComment}
                            isSubmitting={isSubmitting}
                        />
                    </div>
                ) : (
                    <ActivityLog entries={activity} />
                )}
            </div>
        </div>
    );
};

// Inline ActivityLog for simplicity
function ActivityLog({ entries }: { entries: ActivityEntry[] }) {
    if (entries.length === 0) {
        return (
            <div className="text-center py-8">
                <Activity className="w-8 h-8 text-neutral-200 mx-auto mb-2" />
                <p className="text-sm text-neutral-400">No activity yet.</p>
            </div>
        );
    }
    return (
        <div className="space-y-3">
            {[...entries].reverse().map(entry => (
                <ActivityItem key={entry.id} entry={entry} />
            ))}
        </div>
    );
}

function ActivityItem({ entry }: { entry: ActivityEntry }) {
    const actionLabel: Record<ActivityEntry['action'], string> = {
        created: 'created this action item',
        status_changed: `changed status to "${entry.new_value}"`,
        priority_changed: `changed priority to "${entry.new_value}"`,
        assigned: `assigned to "${entry.new_value}"`,
        due_date_changed: `set due date to "${entry.new_value}"`,
        title_edited: 'edited the title',
        description_edited: 'updated the description',
        commented: 'left a comment',
    };

    const actionColors: Record<ActivityEntry['action'], string> = {
        created: 'bg-emerald-500',
        status_changed: 'bg-primary',
        priority_changed: 'bg-amber-500',
        assigned: 'bg-blue-500',
        due_date_changed: 'bg-purple-500',
        title_edited: 'bg-neutral-400',
        description_edited: 'bg-neutral-400',
        commented: 'bg-secondary',
    };

    const timeAgo = (dateStr: string): string => {
        const now = new Date();
        const past = new Date(dateStr);
        const diffMs = now.getTime() - past.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        const diffH = Math.floor(diffMins / 60);
        if (diffH < 24) return `${diffH}h ago`;
        return `${Math.floor(diffH / 24)}d ago`;
    };

    return (
        <div className="flex items-start gap-3">
            <div className={`w-2 h-2 rounded-full ${actionColors[entry.action]} flex-shrink-0 mt-1.5`} />
            <div className="flex-1 min-w-0">
                <p className="text-xs text-neutral-600">
                    <span className="font-semibold text-neutral-800">{entry.actor_name}</span>{' '}
                    {actionLabel[entry.action]}
                </p>
                <p className="text-[10px] text-neutral-400 mt-0.5">{timeAgo(entry.created_at)}</p>
            </div>
        </div>
    );
}
