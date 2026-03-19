'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { apiClient } from '@/lib/api/client';

export default function GoogleCallbackPage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
                <h2 className="text-xl font-semibold mb-2">Verifying with Google...</h2>
                <p className="text-neutral-500">Please wait while we finalize your account connection.</p>
            </div>
        }>
            <GoogleCallbackContent />
        </Suspense>
    );
}

function GoogleCallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { toast } = useToast();
    const [status, setStatus] = useState('Verifying with Google...');
    const hasProcessed = useRef(false);

    useEffect(() => {
        const handleCallback = async () => {
            if (hasProcessed.current) return;
            hasProcessed.current = true;
            const code = searchParams.get('code');
            const state = searchParams.get('state');

            if (!code) {
                toast({
                    title: 'OAuth Error',
                    description: 'No authorization code received from Google.',
                    variant: 'destructive',
                });
                router.push('/integrations');
                return;
            }

            try {
                // The backend API expects code and state. 
                // Using apiClient ensures the Authorization header (Bearer token) is sent, 
                // identifying which user the Google account should be linked to.
                await apiClient.get(`/integrations/google/callback?code=${code}&state=${state}`);

                toast({
                    title: 'Success!',
                    description: 'Google account connected successfully.',
                });
                // Redirect back to integrations page to see the updated status
                router.push('/integrations');
            } catch (error: any) {
                console.error('Google callback error:', error);
                const errorMessage = error.response?.data?.detail || 'An error occurred during Google integration.';

                toast({
                    title: 'Connection Failed',
                    description: errorMessage,
                    variant: 'destructive',
                });
                router.push('/integrations');
            }
        };

        handleCallback();
    }, [router, searchParams, toast]);

    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
            <h2 className="text-xl font-semibold mb-2">{status}</h2>
            <p className="text-neutral-500">Please wait while we finalize your account connection.</p>
        </div>
    );
}
