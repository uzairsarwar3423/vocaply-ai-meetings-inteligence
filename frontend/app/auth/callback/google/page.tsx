'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { authService } from '../../../../lib/auth/auth';

export default function GoogleCallbackPage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center min-h-screen bg-white">
                <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
                <h2 className="text-xl font-semibold mb-2 font-outfit">Authenticating with Google...</h2>
                <p className="text-gray-500 font-inter">Please wait while we finalize your sign-in.</p>
            </div>
        }>
            <GoogleCallbackContent />
        </Suspense>
    );
}

function GoogleCallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const hasProcessed = useRef(false);

    useEffect(() => {
        const handleCallback = async () => {
            if (hasProcessed.current) return;
            hasProcessed.current = true;

            const code = searchParams.get('code');

            if (!code) {
                toast.error('No authorization code received from Google.');
                router.push('/login');
                return;
            }

            try {
                await authService.handleGoogleCallback(code);
                toast.success('Welcome back!');
                router.push('/dashboard');
            } catch (error: any) {
                console.error('Google callback error:', error);
                const errorMessage = error.response?.data?.detail || 'An error occurred during Google authentication.';
                toast.error(errorMessage);
                router.push('/login');
            }
        };

        handleCallback();
    }, [router, searchParams]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-white">
            <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
            <h2 className="text-xl font-semibold mb-2 font-outfit">Authenticating with Google...</h2>
            <p className="text-gray-500 font-inter">Please wait while we finalize your sign-in.</p>
        </div>
    );
}
