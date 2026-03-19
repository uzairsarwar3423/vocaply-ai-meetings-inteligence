'use client';

import { Suspense, useEffect, useState, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { apiClient } from '@/lib/api/client';

function ZoomCallbackHandler() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { toast } = useToast();
    const [status, setStatus] = useState('Verifying with Zoom...');
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
                    description: 'No authorization code received from Zoom.',
                    variant: 'destructive',
                });
                router.push('/integrations');
                return;
            }

            try {
                await apiClient.get(`/integrations/zoom/callback?code=${code}&state=${state}`);

                toast({
                    title: 'Success!',
                    description: 'Zoom account connected successfully.',
                });
                router.push('/integrations');
            } catch (error: any) {
                console.error('Zoom callback error:', error);
                const errorMessage = error.response?.data?.detail || 'An error occurred during Zoom configuration.';

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

export default function ZoomCallbackPage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
                <h2 className="text-xl font-semibold mb-2">Loading...</h2>
            </div>
        }>
            <ZoomCallbackHandler />
        </Suspense>
    );
}
