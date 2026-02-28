'use client';

import { toast as sonnerToast } from 'sonner';

/**
 * Compatibility wrapper for Shadcn/UI useToast hook
 * using sonner as the backend.
 */
export function useToast() {
    return {
        toast: ({ title, description, variant, ...props }: any) => {
            const toastFn = variant === 'destructive' ? sonnerToast.error : sonnerToast.success;

            return toastFn(title || 'Notification', {
                description: description,
                ...props,
            });
        },
        dismiss: (id?: string | number) => sonnerToast.dismiss(id),
    };
}

export const toast = sonnerToast;
