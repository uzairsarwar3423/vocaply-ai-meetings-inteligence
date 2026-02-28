'use client';

import * as React from 'react';
import { Button } from './button';

interface AlertDialogProps {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children: React.ReactNode;
}

export function AlertDialog({ open, onOpenChange, children }: AlertDialogProps) {
    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <div
                className="bg-white dark:bg-gray-950 rounded-lg shadow-xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in duration-200"
                onKeyDown={(e) => {
                    if (e.key === 'Escape') onOpenChange?.(false);
                }}
            >
                {children}
            </div>
        </div>
    );
}

export function AlertDialogContent({ children }: { children: React.ReactNode }) {
    return <div className="p-6">{children}</div>;
}

export function AlertDialogHeader({ children }: { children: React.ReactNode }) {
    return <div className="space-y-2 mb-4">{children}</div>;
}

export function AlertDialogTitle({ children }: { children: React.ReactNode }) {
    return <h3 className="text-lg font-semibold leading-none tracking-tight">{children}</h3>;
}

export function AlertDialogDescription({ children }: { children: React.ReactNode }) {
    return <div className="text-sm text-gray-500 dark:text-gray-400">{children}</div>;
}

export function AlertDialogFooter({ children }: { children: React.ReactNode }) {
    return <div className="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2">{children}</div>;
}

export function AlertDialogCancel({
    children,
    onClick
}: {
    children: React.ReactNode;
    onClick?: () => void;
}) {
    return (
        <Button
            variant="outline"
            onClick={onClick}
            className="mt-2 sm:mt-0"
        >
            {children}
        </Button>
    );
}

export function AlertDialogAction({
    children,
    onClick
}: {
    children: React.ReactNode;
    onClick?: () => void;
}) {
    return (
        <Button
            variant="primary"
            onClick={onClick}
        >
            {children}
        </Button>
    );
}
