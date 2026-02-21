// useComments hook
// Vocaply Platform - Day 12
'use client';

import { useState, useCallback } from 'react';

export interface Comment {
    id: string;
    action_item_id: string;
    author_name: string;
    author_email: string;
    author_initials: string;
    content: string;
    mentions: string[]; // email addresses mentioned
    created_at: string;
    updated_at: string;
    is_edited: boolean;
}

export interface ActivityEntry {
    id: string;
    action_item_id: string;
    actor_name: string;
    actor_email: string;
    action: 'created' | 'status_changed' | 'priority_changed' | 'assigned' | 'due_date_changed' | 'title_edited' | 'description_edited' | 'commented';
    old_value?: string;
    new_value?: string;
    created_at: string;
}

interface UseCommentsReturn {
    comments: Comment[];
    activity: ActivityEntry[];
    isLoading: boolean;
    isSubmitting: boolean;
    error: string | null;
    addComment: (content: string, mentions?: string[]) => Promise<void>;
    editComment: (id: string, content: string) => Promise<void>;
    deleteComment: (id: string) => Promise<void>;
    addActivity: (entry: Omit<ActivityEntry, 'id' | 'created_at'>) => void;
}

// Helper to generate a mock initials
function getInitials(name: string): string {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}

// For now, comments are stored locally (no dedicated API endpoint yet)
// This can be swapped to a real API when the backend endpoint is ready
export function useComments(actionItemId: string, currentUserName: string = 'You', currentUserEmail: string = 'user@vocaply.com'): UseCommentsReturn {
    const [comments, setComments] = useState<Comment[]>([]);
    const [activity, setActivity] = useState<ActivityEntry[]>([]);
    const [isLoading] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const addComment = useCallback(async (content: string, mentions: string[] = []) => {
        setIsSubmitting(true);
        setError(null);
        try {
            // Simulate API call
            await new Promise(r => setTimeout(r, 200));
            const newComment: Comment = {
                id: crypto.randomUUID(),
                action_item_id: actionItemId,
                author_name: currentUserName,
                author_email: currentUserEmail,
                author_initials: getInitials(currentUserName),
                content,
                mentions,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                is_edited: false,
            };
            setComments(prev => [...prev, newComment]);

            // Add to activity log
            setActivity(prev => [...prev, {
                id: crypto.randomUUID(),
                action_item_id: actionItemId,
                actor_name: currentUserName,
                actor_email: currentUserEmail,
                action: 'commented',
                new_value: content.slice(0, 80),
                created_at: new Date().toISOString(),
            }]);
        } catch {
            setError('Failed to add comment');
        } finally {
            setIsSubmitting(false);
        }
    }, [actionItemId, currentUserName, currentUserEmail]);

    const editComment = useCallback(async (id: string, content: string) => {
        setComments(prev => prev.map(c =>
            c.id === id ? { ...c, content, is_edited: true, updated_at: new Date().toISOString() } : c
        ));
    }, []);

    const deleteComment = useCallback(async (id: string) => {
        setComments(prev => prev.filter(c => c.id !== id));
    }, []);

    const addActivity = useCallback((entry: Omit<ActivityEntry, 'id' | 'created_at'>) => {
        setActivity(prev => [...prev, {
            ...entry,
            id: crypto.randomUUID(),
            created_at: new Date().toISOString(),
        }]);
    }, []);

    return {
        comments,
        activity,
        isLoading,
        isSubmitting,
        error,
        addComment,
        editComment,
        deleteComment,
        addActivity,
    };
}
