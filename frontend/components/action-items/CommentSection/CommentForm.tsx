// CommentForm — textarea with @mention support
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, AtSign } from 'lucide-react';

interface CommentFormProps {
    onSubmit: (content: string, mentions: string[]) => Promise<void>;
    isSubmitting: boolean;
    placeholder?: string;
    autoFocus?: boolean;
}

// Extract @mentions from text
function extractMentions(text: string): string[] {
    const matches = text.match(/@(\S+)/g) || [];
    return matches.map(m => m.slice(1));
}

export const CommentForm: React.FC<CommentFormProps> = ({
    onSubmit,
    isSubmitting,
    placeholder = 'Add a comment... Use @ to mention someone',
    autoFocus = false,
}) => {
    const [value, setValue] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (autoFocus && textareaRef.current) {
            textareaRef.current.focus();
        }
    }, [autoFocus]);

    // Auto-resize textarea
    useEffect(() => {
        const ta = textareaRef.current;
        if (ta) {
            ta.style.height = 'auto';
            ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
        }
    }, [value]);

    const handleSubmit = async () => {
        const trimmed = value.trim();
        if (!trimmed || isSubmitting) return;
        const mentions = extractMentions(trimmed);
        await onSubmit(trimmed, mentions);
        setValue('');
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="flex items-end gap-3">
            <div className="flex-1 relative">
                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={e => setValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                    rows={1}
                    className={`
                        w-full resize-none bg-neutral-50 border rounded-2xl px-4 py-3 pr-10 text-sm text-neutral-700 
                        placeholder:text-neutral-400 transition-all focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary focus:bg-white
                        ${value ? 'border-primary/40' : 'border-neutral-200'}
                    `}
                    style={{ minHeight: 44, maxHeight: 120 }}
                />
                <button
                    type="button"
                    onClick={() => {
                        const ta = textareaRef.current;
                        if (ta) {
                            const pos = ta.selectionStart;
                            const newVal = value.slice(0, pos) + '@' + value.slice(pos);
                            setValue(newVal);
                            setTimeout(() => {
                                ta.setSelectionRange(pos + 1, pos + 1);
                                ta.focus();
                            }, 0);
                        }
                    }}
                    className="absolute right-3 bottom-3 text-neutral-400 hover:text-primary transition-colors"
                    title="Mention someone"
                >
                    <AtSign className="w-4 h-4" />
                </button>
            </div>
            <button
                onClick={handleSubmit}
                disabled={!value.trim() || isSubmitting}
                className={`
                    flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all
                    ${value.trim() && !isSubmitting
                        ? 'bg-primary text-white shadow-md shadow-primary/20 hover:bg-primary/90 hover:scale-105 active:scale-95'
                        : 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
                    }
                `}
                title="Send comment (Enter)"
            >
                {isSubmitting
                    ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    : <Send className="w-4 h-4" />
                }
            </button>
        </div>
    );
};
